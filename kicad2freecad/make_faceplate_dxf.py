#!/usr/bin/env python3
"""
make_faceplate_dxf.py

Generates a panel hole DXF from a KiCad PCB file without opening KiCad.
Reads footprint positions, maps them to correct panel hole diameters using
4ms faceplate conventions, adds Edge.Cuts circles, and exports DXF via kicad-cli.

Usage:
    python3 make_faceplate_dxf.py <input.kicad_pcb> <output.dxf>

Reference: ~/kicad/4ms-kicad-script/make_eurorack_faceplate/make_eurorack_fp.py
Hole sizes: ~/kicad/4ms-kicad-lib/footprints/4ms_Faceplate.pretty
"""

import sys
import os
import re
import subprocess
import tempfile
import uuid

# Footprint name → panel hole drill diameter (mm)
# Derived from 4ms_Faceplate.pretty .kicad_mod drill values
HOLE_SIZES = {
    # 16mm pots → 7.112mm
    'Potentiometer_Alps_RK09L_Double_Vertical': 7.112,
    'Pot_16mm_21Det_RV16AF-4A':  7.112,
    'Pot_16mm_NoDet_RV16AF-4A':  7.112,
    'Pot_16mm_CtrDet_RV16AF-4A': 7.112,
    # 9mm pots (metal collar) → 7.1mm
    'POT-9MM-ALPHA':  7.1,
    'Pot_9mm_DShaft': 7.1,
    # 9mm pots (plastic) → 6.604mm
    'POT-9MM-SONGHUEI':   6.604,
    'Pot_9mm_Knurl_Det':  6.604,
    'Pot_9mm_Knurl_NoDet': 6.604,
    '9mm_CtrDet_10k_DShaft': 6.604,
    'Pot_9mm_Dshaft_Det': 6.604,
    # Encoders (standard bushing) → 7.366mm
    'ENC_SPST_12mm':       7.366,
    'ENC_12mm_HollowShaft': 7.366,
    'ROTENC-12MM-BUT':     7.366,
    'PEC11R-4215F-N0024':  7.366,
    # Encoders (RGB, no bushing) → 7.112mm
    'RGB_ROTARY_ENCODER': 7.112,
    'ENC_RGB_SPST_12mm':  7.112,
    # 3.5mm jacks → 6.604mm
    'PJ301M-12':               6.604,
    'PJ366ST':                 6.604,
    'EighthInch_PJ398SM':      6.604,
    'EighthInch_Stereo_PJ366ST': 6.604,
    # 1/4" jacks → 10.0mm
    'QuarterInch_Mono_Switched':   10.0,
    'QuarterInch_Mono_Unswitched': 10.0,
    'Faceplate_Hole_Jack_Quarter_Inch': 10.0,
    # LEDs 3mm → 3.048mm
    'LED-C1-A2-3MM-VERT':    3.048,
    'LED_D3.0mm-3':          3.048,
    'LED-3MM-SQUARE-ANODE':  3.048,
    # Lightpipes / PLCC4 → 2.921mm
    'LED-PLCC4':          2.921,
    'LED_PLCC-4':         2.921,
    'LED_0603_1608Metric': 2.921,
    'PLCC4':              2.921,
    # Tactile buttons → 5.5mm
    'SW_TH_Tactile_Omron_B3F-100x': 5.5,
    # PB20 buttons → 9.5mm
    'Button_PB20B':       9.5,
    'Button_LED_PKS-01L-X': 9.5,
    # Sub-mini toggle → 4.953mm
    'Switch_Toggle_SPDT_SubMini': 4.953,
    # LED buttons
    'BUTTON-LED-PB61303':      7.747,
    'RGB-SPST-LED-TC002':      5.6642,
    'Button_RgbLED_SPST_TC002': 5.6642,
    # Trimmers → 3.175mm
    'TRIM-T73YE': 3.175,
}

# Footprint name → panel rectangular cutout (width_mm, height_mm)
# Used for switches that need square/rectangular openings instead of round holes.
RECT_SIZES = {
    # Cherry MX switch body only: 14×14mm
    'SW_Cherry_MX_PCB':          (14.0, 14.0),
    'SW_Cherry_MX_PCB_WithCap':  (14.0, 14.0),
    # Cherry MX with DSA 1u keycap: keycap base 18.2×18.2mm + 1mm clearance each side
    'SW_Cherry_MX_PCB_WithDSACap': (20.2, 20.2),
    # ER-TFT3.99-1 screen window cutout
    'Faceplate_Window_ER-TFT3.99-1': (94.03, 39.18),
}


def strip_board_edge_cuts(pcb_text):
    """
    Remove all board-level gr_* shapes on Edge.Cuts from PCB text.
    Footprint-level fp_* shapes are left alone.
    Prevents PCB boundary and any other existing Edge.Cuts graphics
    from appearing in the exported DXF alongside our panel holes.
    """
    shape_re = re.compile(r'\(gr_(?:rect|line|arc|circle|poly|curve)\s')
    result = []
    i = 0
    while i < len(pcb_text):
        m = shape_re.search(pcb_text, i)
        if not m:
            result.append(pcb_text[i:])
            break

        # Find end of this shape block
        depth = 0
        j = m.start()
        while j < len(pcb_text):
            if pcb_text[j] == '(':
                depth += 1
            elif pcb_text[j] == ')':
                depth -= 1
                if depth == 0:
                    break
            j += 1

        block = pcb_text[m.start():j + 1]

        if '"Edge.Cuts"' in block:
            # Drop this block, keep text up to it
            result.append(pcb_text[i:m.start()])
        else:
            result.append(pcb_text[i:j + 1])

        i = j + 1

    return ''.join(result)


def parse_footprints(pcb_text):
    """
    Extract footprint names and (at x y) positions from .kicad_pcb text.
    Returns list of dicts: {name, x, y}
    """
    results = []
    fp_start_re = re.compile(r'\(footprint\s+"([^"]+)"')
    at_re = re.compile(r'\(at\s+([-\d.]+)\s+([-\d.]+)')

    i = 0
    while i < len(pcb_text):
        m = fp_start_re.search(pcb_text, i)
        if not m:
            break

        fp_id = m.group(1)
        fp_name = fp_id.split(':')[-1] if ':' in fp_id else fp_id

        # Walk forward counting parens to find the end of this footprint block
        depth = 0
        j = m.start()
        while j < len(pcb_text):
            if pcb_text[j] == '(':
                depth += 1
            elif pcb_text[j] == ')':
                depth -= 1
                if depth == 0:
                    break
            j += 1

        fp_block = pcb_text[m.start():j + 1]

        at_m = at_re.search(fp_block)
        if at_m:
            x = float(at_m.group(1))
            y = float(at_m.group(2))
            results.append({'name': fp_name, 'x': x, 'y': y})

        i = m.end()

    return results


def make_rect_sexpr(x, y, width, height):
    """Return a KiCad s-expression gr_rect on Edge.Cuts, centered at (x, y)."""
    x0 = x - width / 2.0
    y0 = y - height / 2.0
    x1 = x + width / 2.0
    y1 = y + height / 2.0
    uid = str(uuid.uuid4())
    return (
        f'\t(gr_rect\n'
        f'\t\t(start {x0} {y0})\n'
        f'\t\t(end {x1} {y1})\n'
        f'\t\t(stroke (width 0.05) (type solid))\n'
        f'\t\t(fill none)\n'
        f'\t\t(layer "Edge.Cuts")\n'
        f'\t\t(uuid "{uid}")\n'
        f'\t)'
    )


def make_circle_sexpr(x, y, diameter):
    """Return a KiCad s-expression gr_circle on Edge.Cuts."""
    radius = diameter / 2.0
    end_x = x + radius
    uid = str(uuid.uuid4())
    return (
        f'\t(gr_circle\n'
        f'\t\t(center {x} {y})\n'
        f'\t\t(end {end_x} {y})\n'
        f'\t\t(stroke (width 0.05) (type solid))\n'
        f'\t\t(fill none)\n'
        f'\t\t(layer "Edge.Cuts")\n'
        f'\t\t(uuid "{uid}")\n'
        f'\t)'
    )


def main():
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <input.kicad_pcb> <output.dxf>')
        sys.exit(1)

    input_pcb = os.path.abspath(sys.argv[1])
    output_dxf = os.path.abspath(sys.argv[2])

    if not os.path.exists(input_pcb):
        print(f'Error: {input_pcb} not found')
        sys.exit(1)

    print(f'Reading {input_pcb}')
    with open(input_pcb, 'r') as f:
        pcb_text = f.read()

    footprints = parse_footprints(pcb_text)
    print(f'Found {len(footprints)} footprints')

    shapes = []
    skipped = []
    for fp in footprints:
        diameter = HOLE_SIZES.get(fp['name'])
        rect = RECT_SIZES.get(fp['name'])
        if diameter:
            shapes.append(make_circle_sexpr(fp['x'], fp['y'], diameter))
            print(f'  + {fp["name"]} → ⌀{diameter}mm at ({fp["x"]}, {fp["y"]})')
        elif rect:
            w, h = rect
            shapes.append(make_rect_sexpr(fp['x'], fp['y'], w, h))
            print(f'  + {fp["name"]} → {w}×{h}mm rect at ({fp["x"]}, {fp["y"]})')
        else:
            skipped.append(fp['name'])

    if skipped:
        print(f'\nSkipped (no panel hole mapping):')
        for s in sorted(set(skipped)):
            print(f'  - {s}')

    if not shapes:
        print('\nNo panel holes found — check footprint names against HOLE_SIZES / RECT_SIZES mapping.')
        sys.exit(1)

    # Strip existing board-level Edge.Cuts geometry (boundary rect etc.)
    pcb_text = strip_board_edge_cuts(pcb_text)

    # Insert shapes before the final closing paren of the file
    circles_text = '\n'.join(shapes)
    modified = pcb_text.rstrip()
    if modified.endswith(')'):
        modified = modified[:-1] + '\n' + circles_text + '\n)'
    else:
        modified += '\n' + circles_text

    # Write modified PCB back to the input file so KiCad shows the faceplate holes
    with open(input_pcb, 'w') as f:
        f.write(modified)
    print(f'Updated: {input_pcb}')

    # Also write to a temp file for kicad-cli DXF export
    with tempfile.NamedTemporaryFile(suffix='.kicad_pcb', delete=False, mode='w') as tmp:
        tmp.write(modified)
        tmp_path = tmp.name

    try:
        os.makedirs(os.path.dirname(output_dxf), exist_ok=True)
        cmd = [
            'kicad-cli', 'pcb', 'export', 'dxf',
            '--output', output_dxf,
            '--layers', 'Edge.Cuts',
            '--output-units', 'mm',
            '--drill-shape-opt', '0',
            '--mode-single',
            tmp_path
        ]
        print(f'\nRunning: {" ".join(cmd)}')
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f'kicad-cli error:\n{result.stderr}')
            sys.exit(1)
        print(f'Exported: {output_dxf}')
    finally:
        os.unlink(tmp_path)


if __name__ == '__main__':
    main()
