#!/usr/bin/env python3
"""
kicad_sync_from_coordinates.py  —  Illustration2KicadAutomation

Reads a Component Placement Coordinates spreadsheet (.xlsx) and syncs it
into a KiCad 10 project in two passes:

  Pass 1 — Schematic (.kicad_sch)
    • Updates the Display property of existing symbols to match the
      spreadsheet Display Name column
    • Adds new schematic symbols (staged off-canvas) for rows whose ref
      does not yet exist in the schematic

  Pass 2 — PCB (.kicad_pcb)
    • Moves existing footprints to the X/Y coordinates from the spreadsheet
    • Adds new footprints for any newly-added components

Spreadsheet column layout (row 1 = header, data starts row 2):
  A  Ref           — assigned ref (e.g. J200); blank = auto-assign
  B  Display Name  — label shown on schematic (e.g. "0_degrees")
  C  X             — panel X coordinate in mm (panel-center origin)
  D  Y             — panel Y coordinate in mm (panel-center origin)
  E  Component Type — Pot / Jack / LED / Button / Switch / Standoff / Connector
  F  Subtype        — friendly name matching the Options sheet
  G  KiCad Symbol   — VLOOKUP result (may be blank; subtype lookup used as fallback)
  H  Notes          — "IGNORE" skips the row; other notes are informational

Usage:
    python3 kicad_sync_from_coordinates.py  coordinates.xlsx  project.kicad_pro

The .kicad_sch and .kicad_pcb files are found automatically from the .kicad_pro
path — they must share the same directory and base name (standard KiCad layout).

Optional flags:
    --lib-sym  PATH   Symbol library root  (default: ~/kicad/4ms-kicad-lib/symbols)
    --lib-fp   PATH   Footprint lib root   (default: ~/kicad/4ms-kicad-lib/footprints)
    --sch-only        Only update the schematic
    --pcb-only        Only update the PCB

Backups are written as <file>.bak.<timestamp> alongside each modified file.

*** EXPERIMENTAL — See README.md ***
"""

import argparse
import os
import re
import shutil
import sys
import uuid as _uuid
from datetime import datetime
from openpyxl import load_workbook

# ---------------------------------------------------------------------------
# Default paths — Phase Mirror P2, used when no positional args are given.
# This lets you run the script bare during development without typing paths.
# ---------------------------------------------------------------------------
_HOME = os.path.expanduser("~")
_DEV_XLSX = f"{_HOME}/kicad/pcb-phase-mirror/artwork/phase-mirror-coordinates_p2.xlsx"
_DEV_PRO  = f"{_HOME}/kicad/pcb-phase-mirror/kicad/p2/phase-mirror.kicad_pro"
_LIB_SYM  = f"{_HOME}/kicad/4ms-kicad-lib/symbols"
_LIB_FP   = f"{_HOME}/kicad/4ms-kicad-lib/footprints"


def resolve_kicad_files(pro_path):
    """Given a .kicad_pro path, return (sch_path, pcb_path).
    KiCad convention: all three files share the same directory and base name."""
    pro_path = os.path.expanduser(os.path.abspath(pro_path))
    stem = os.path.splitext(pro_path)[0]
    sch = stem + ".kicad_sch"
    pcb = stem + ".kicad_pcb"
    missing = [p for p in (sch, pcb) if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError(
            f"Expected KiCad files not found alongside {pro_path}:\n"
            + "\n".join(f"  {p}" for p in missing)
        )
    return sch, pcb

# ---------------------------------------------------------------------------
# Subtype → KiCad symbol lib_id
# Used when the spreadsheet's VLOOKUP formula hasn't evaluated (data_only mode).
# Keep in sync with the OPTIONS dict in make_placement_template.py.
# ---------------------------------------------------------------------------
SUBTYPE_TO_SYM = {
    # Potentiometers
    "16mm No Detent 10k":             "4ms_Potentiometer:16mm_NoDet_10k",
    "16mm No Detent 100k":            "4ms_Potentiometer:16mm_NoDet_100k",
    "16mm Center Detent 10k":         "4ms_Potentiometer:16mm_CtrDet_10k",
    "16mm 21-Detent 10k":             "4ms_Potentiometer:16mm_21Det_10k",
    "9mm No Detent 100k Knurled":     "4ms_Potentiometer:9mm_NoDet_100k_Knurled_Lined",
    "9mm Center Detent 100k Knurled": "4ms_Potentiometer:9mm_CtrDet_100k_Knurled_Lined",
    "9mm No Detent 10k D-Shaft":      "4ms_Potentiometer:9mm_NoDet_10k_DShaft",
    "9mm Center Detent 10k D-Shaft":  "4ms_Potentiometer:9mm_CtrDet_10k_DShaft",
    "Slider LED 20mm 100k":           "4ms_Potentiometer:Pot_Slider_LED_20mm_100K",
    "Slider LED 30mm 10k":            "4ms_Potentiometer:Pot_Slider_LED_30mm_10K",
    "TrimPot TC33X 10k":              "4ms_Potentiometer:TrimPot_TC33X_10k",
    "TrimPot TC33X 50k":              "4ms_Potentiometer:TrimPot_TC33X_50k",
    "TrimPot TC33X 100k":             "4ms_Potentiometer:TrimPot_TC33X_100k",
    "TrimPot T73YE 10k":              "4ms_Potentiometer:TrimPot_T73YEt_10k",
    "TrimPot T73YE 100k":             "4ms_Potentiometer:TrimPot_T73YEt_100k",
    # Jacks
    "3.5mm Mono Switched":            "4ms_Jack:3.5mm_Mono_Switched",
    "3.5mm Mono Switched sm":         "4ms_Jack:3.5mm_Mono_Switched_sm",
    "3.5mm Stereo":                   "4ms_Jack:3.5mm_Stereo",
    "3.5mm Stereo Switched":          "4ms_Jack:3.5mm_Stereo_Switched_Jack",
    "3.5mm Stereo SMT Right Angle":   "4ms_Jack:3.5mm_Stereo_SMT_Right_Angle_Horizontal",
    "Barrel 2.1mm Right Angle":       "4ms_Jack:Barrel_2.1mm_Right_Angle",
    # LEDs
    "RGB PLCC4":                      "4ms_LED:RGB_CA_PLCC4",
    "RGB Right Angle":                "4ms_LED:RGB_CA_RightAngle",
    "Blue 0603":                      "4ms_LED:Blue_56mcd_0603",
    "Red 0603":                       "4ms_LED:Red_100mcd_0603",
    "Green 0603":                     "4ms_LED:Green_350mcd_0603",
    "Yellow 0603":                    "4ms_LED:Yellow_23mcd_0603",
    "White 0603":                     "4ms_LED:White_min200mcd_0603",
    "Dual SMD 4-pin":                 "4ms_LED:LED_Dual_SMD-4P",
    "Green 5mm TH":                   "4ms_LED:Green_5mm_TH",
    "Red 3mm TH":                     "4ms_LED:Red_3mm_TH",
    "Blue 3mm TH":                    "4ms_LED:Blue_3mm_TH",
    # Buttons
    "RGB 9mm Cap":                    "4ms_Switch:Button_SPST_RGB_9mmCap",
    "RGB 7mm Cap":                    "4ms_Switch:Button_SPST_RGB_7mmCap",
    "RGB 5.4mm Cap":                  "4ms_Switch:Button_SPST_RGB_5.4mmCap",
    "TL1105SPF Tactile SMT":          "4ms_Switch:Button_TL1105SPF160Q1RBLK",
    "TL1105JAF RA with Cap":          "4ms_Switch:Button_TL1105JAF160Q1RBLK",
    "PTS810":                         "4ms_Switch:Button_PTS810",
    # Switches
    "Toggle SPDT Sub-Mini 3-pos":     "4ms_Switch:Toggle_SPDT_SubMini_3pos",
    "Toggle SPDT Sub-Mini 2-pos":     "4ms_Switch:Toggle_SPDT_SubMini_2pos",
    "Encoder Rotary 11mm D-Shaft":    "4ms_Switch:Encoder_Rotary_11mm_SPST_DShaft",
}

# Ref designator prefix by component type (4ms conventions)
TYPE_PREFIX = {
    "Pot":       "POT",
    "Jack":      "J",
    "LED":       "LED",
    "Button":    "BUT",
    "Switch":    "SW",
    "Standoff":  "H",
    "Connector": "J",
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description=(
            "Sync a Component Placement spreadsheet into a KiCad 10 project.\n\n"
            "  python3 kicad_sync_from_coordinates.py  coordinates.xlsx  project.kicad_pro\n"
            "  python3 kicad_sync_from_coordinates.py  coordinates.xlsx  project.kicad_pro  --dry-run\n\n"
            "The .kicad_sch and .kicad_pcb are found automatically from the .kicad_pro path."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("xlsx",    nargs="?", default=_DEV_XLSX,
                   help="Coordinates spreadsheet (.xlsx)")
    p.add_argument("pro",     nargs="?", default=_DEV_PRO,
                   help="KiCad project file (.kicad_pro) — .kicad_sch and .kicad_pcb "
                        "are resolved from the same directory and base name")
    p.add_argument("--lib-sym", default=_LIB_SYM,
                   help="Symbol library root  (default: ~/kicad/4ms-kicad-lib/symbols)")
    p.add_argument("--lib-fp",  default=_LIB_FP,
                   help="Footprint library root  (default: ~/kicad/4ms-kicad-lib/footprints)")
    p.add_argument("--sch-only", action="store_true", help="Only update the schematic")
    p.add_argument("--pcb-only", action="store_true", help="Only update the PCB")
    args = p.parse_args()
    # Resolve .kicad_sch and .kicad_pcb from the .kicad_pro path
    args.xlsx = os.path.expanduser(os.path.abspath(args.xlsx))
    args.sch, args.pcb = resolve_kicad_files(args.pro)
    return args


# ---------------------------------------------------------------------------
# Spreadsheet reader
# ---------------------------------------------------------------------------

def read_spreadsheet(path):
    """Return list of component dicts from the Coordinates sheet."""
    wb = load_workbook(path, data_only=True)
    ws = wb.active
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if len(row) < 7:
            continue
        ref, display, x, y, comp_type, subtype, kicad_sym = row[:7]
        notes = row[7] if len(row) > 7 else ""

        def s(v): return str(v).strip() if v else ""

        ref, display, comp_type, subtype = s(ref), s(display), s(comp_type), s(subtype)
        kicad_sym, notes = s(kicad_sym), s(notes)

        if not display and not comp_type:
            continue
        if subtype == "Silkscreen Label" or notes.upper() == "IGNORE":
            continue

        # Resolve symbol from subtype when VLOOKUP formula is blank
        if not kicad_sym and subtype:
            kicad_sym = SUBTYPE_TO_SYM.get(subtype, "")

        try:
            x_f, y_f = float(x), float(y)
        except (TypeError, ValueError):
            x_f = y_f = 0.0

        rows.append(dict(ref=ref, display=display, x=x_f, y=y_f,
                         comp_type=comp_type, subtype=subtype,
                         kicad_sym=kicad_sym, notes=notes))
    return rows


# ---------------------------------------------------------------------------
# S-expression helpers
# ---------------------------------------------------------------------------

def find_block(text, keyword_pattern, from_pos=0):
    """Find the next balanced-paren block whose opening matches keyword_pattern.
    Returns (start, end) or None."""
    m = re.search(keyword_pattern, text[from_pos:])
    if not m:
        return None
    abs_start = from_pos + m.start()
    depth = 0
    for i in range(abs_start, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return (abs_start, i + 1)
    return None


def apply_replacements(text, replacements):
    """Apply (start, end, new_text) pairs from end to start to avoid offset drift."""
    for start, end, new_text in sorted(replacements, key=lambda r: r[0], reverse=True):
        text = text[:start] + new_text + text[end:]
    return text


# ---------------------------------------------------------------------------
# Schematic helpers
# ---------------------------------------------------------------------------

def detect_project_info(sch_text, sch_path):
    """Extract the schematic root UUID and project name from the schematic text."""
    # Root UUID is the first (uuid "...") at file level
    m = re.search(r'^\(uuid\s+"([^"]+)"\)', sch_text, re.MULTILINE)
    proj_uuid = m.group(1) if m else str(_uuid.uuid4())

    # Project name from the first (project "name" ...) block in any instances block
    m2 = re.search(r'\(project\s+"([^"]+)"', sch_text)
    proj_name = m2.group(1) if m2 else os.path.splitext(os.path.basename(sch_path))[0]

    return proj_uuid, proj_name


def parse_schematic_symbols(text):
    """Parse all top-level (symbol ...) instances. Returns list of dicts."""
    results = []
    pos = 0
    while True:
        r = find_block(text, r'(?m)^\t\(symbol\b', pos)
        if not r:
            break
        start, end = r
        block = text[start:end]
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        lib_m = re.search(r'\(lib_id\s+"([^"]+)"', block)
        fp_m  = re.search(r'\(property\s+"Footprint"\s+"([^"]+)"', block)
        results.append({
            "ref":       ref_m.group(1) if ref_m else "",
            "lib_id":    lib_m.group(1) if lib_m else "",
            "footprint": fp_m.group(1)  if fp_m  else "",
            "start": start, "end": end, "block": block,
        })
        pos = end
    return results


def update_display_in_block(block, new_display):
    """Set the Display property value; injects the property if absent."""
    pat = r'(\(property\s+"Display"\s+)"([^"]*)"'
    if re.search(pat, block):
        return re.sub(pat, rf'\1"{new_display}"', block, count=1)
    # Inject before the first (pin or (instances line
    inject = (
        f'\n\t\t(property "Display" "{new_display}"\n'
        f'\t\t\t(at 0 0 0)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t\t(italic yes)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t\t(justify right)\n'
        f'\t\t\t)\n'
        f'\t\t)'
    )
    m = re.search(r'\n\t+\((?:pin\s|instances)', block)
    if m:
        return block[:m.start()] + inject + block[m.start():]
    return block


def make_sch_symbol(template_block, new_ref, new_display,
                    proj_uuid, proj_name, sch_x, sch_y):
    """Clone a symbol block with a new ref, display name, position, and fresh UUIDs."""
    block = template_block

    # Reposition (at X Y [angle]) — first occurrence is the symbol placement
    block = re.sub(
        r'(\t\(symbol\b[^\n]*\n\t+)\(at\s+-?[\d.]+\s+-?[\d.]+(?:\s+-?[\d.]+)?\)',
        rf'\g<1>(at {sch_x:.2f} {sch_y:.2f} 0)',
        block, count=1,
    )
    # Drop mirror — cloned symbols start in canonical orientation
    block = re.sub(r'\n\t+\(mirror [xy]\)', '', block)
    # Reference
    block = re.sub(
        r'(\(property\s+"Reference"\s+)"[^"]*"',
        rf'\1"{new_ref}"', block, count=1,
    )
    # Display
    block = update_display_in_block(block, new_display)
    # Fresh UUIDs everywhere
    block = re.sub(r'\(uuid\s+"[^"]*"\)',
                   lambda _: f'(uuid "{_uuid.uuid4()}")', block)
    # Correct instances block
    block = re.sub(r'\(path\s+"/[^"]*"', f'(path "/{proj_uuid}"', block, count=1)
    block = re.sub(
        r'(\(path\s+"/[^"]*"\s*\n\s*\(reference\s+)"[^"]*"',
        rf'\1"{new_ref}"', block, count=1,
    )
    block = re.sub(
        r'\(project\s+"[^"]*"',
        f'(project "{proj_name}"', block, count=1,
    )
    return block


def load_sym_from_lib(lib_id, lib_sym_root):
    """Load a minimal schematic-instance block for lib_id from the .kicad_sym file.
    Returns (block_text, footprint_lib_id) or None."""
    if ':' not in lib_id:
        return None
    lib_name, sym_name = lib_id.split(':', 1)
    sym_file = os.path.join(lib_sym_root, f"{lib_name}.kicad_sym")
    if not os.path.exists(sym_file):
        return None
    with open(sym_file) as f:
        content = f.read()

    pat = r'(?m)^\t\(symbol\s+"' + re.escape(sym_name) + r'"'
    r = find_block(content, pat)
    if not r:
        return None
    lib_def = content[r[0]:r[1]]

    fp_m    = re.search(r'\(property\s+"Footprint"\s+"([^"]+)"', lib_def)
    val_m   = re.search(r'\(property\s+"Value"\s+"([^"]*)"', lib_def)
    desc_m  = re.search(r'\(property\s+"Description"\s+"([^"]*)"', lib_def)
    footprint = fp_m.group(1)  if fp_m   else ""
    value     = val_m.group(1) if val_m  else sym_name
    desc      = desc_m.group(1) if desc_m else ""

    pin_numbers = re.findall(r'\(number\s+"([^"]+)"', lib_def)
    pin_lines = "\n".join(
        f'\t\t(pin "{p}"\n\t\t\t(uuid "{_uuid.uuid4()}")\n\t\t)'
        for p in pin_numbers[:20]
    )

    # Build a minimal schematic symbol instance (position will be set by make_sch_symbol)
    block = (
        f'\t(symbol\n'
        f'\t\t(lib_id "{lib_id}")\n'
        f'\t\t(at 0 0 0)\n'
        f'\t\t(unit 1)\n'
        f'\t\t(body_style 1)\n'
        f'\t\t(exclude_from_sim no)\n'
        f'\t\t(in_bom yes)\n'
        f'\t\t(on_board yes)\n'
        f'\t\t(in_pos_files yes)\n'
        f'\t\t(dnp no)\n'
        f'\t\t(fields_autoplaced yes)\n'
        f'\t\t(uuid "{_uuid.uuid4()}")\n'
        f'\t\t(property "Reference" "REF"\n'
        f'\t\t\t(at 0 2.54 0)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects (font (size 1.524 1.524)))\n'
        f'\t\t)\n'
        f'\t\t(property "Value" "{value}"\n'
        f'\t\t\t(at 0 -2.54 0)\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects (font (size 1.524 1.524)))\n'
        f'\t\t)\n'
        f'\t\t(property "Footprint" "{footprint}"\n'
        f'\t\t\t(at 0 0 0)\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects (font (size 1.524 1.524)))\n'
        f'\t\t)\n'
        f'\t\t(property "Datasheet" ""\n'
        f'\t\t\t(at 0 0 0)\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects (font (size 1.524 1.524)))\n'
        f'\t\t)\n'
        f'\t\t(property "Description" "{desc}"\n'
        f'\t\t\t(at 0 0 0)\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects (font (size 1.524 1.524)))\n'
        f'\t\t)\n'
        f'\t\t(property "Display" ""\n'
        f'\t\t\t(at 0 2.54 0)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font (size 1.27 1.27) (italic yes))\n'
        f'\t\t\t\t(justify right)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        + (pin_lines + "\n" if pin_lines else "")
        + f'\t\t(instances\n'
        f'\t\t\t(project "PROJECT"\n'
        f'\t\t\t\t(path "/PROJ_UUID"\n'
        f'\t\t\t\t\t(reference "REF")\n'
        f'\t\t\t\t\t(unit 1)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)'
    )
    return block, footprint


# ---------------------------------------------------------------------------
# PCB helpers
# ---------------------------------------------------------------------------

def parse_pcb_footprints(text):
    """Parse all (footprint ...) blocks. Returns list of dicts."""
    results = []
    pos = 0
    while True:
        r = find_block(text, r'\(footprint\s+"', pos)
        if not r:
            break
        start, end = r
        block = text[start:end]
        fp_m  = re.search(r'\(footprint\s+"([^"]+)"', block)
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        results.append({
            "ref":       ref_m.group(1) if ref_m else "",
            "fp_lib_id": fp_m.group(1)  if fp_m  else "",
            "start": start, "end": end, "block": block,
        })
        pos = end
    return results


def update_pcb_position(block, x, y):
    """Replace the first (at X Y [angle]) in a footprint block; preserves rotation."""
    def _replace(m):
        angle = m.group(3).strip() if m.group(3) else ""
        return f'(at {x:.3f} {y:.3f} {angle})' if angle else f'(at {x:.3f} {y:.3f})'
    return re.sub(r'\(at\s+(-?[\d.]+)\s+(-?[\d.]+)(\s+-?[\d.]+)?\)',
                  _replace, block, count=1)


def load_footprint_from_lib(fp_lib_id, lib_fp_root):
    """Load a .kicad_mod file and return text ready to be inserted into a PCB."""
    if ':' not in fp_lib_id:
        return None
    lib, fp_name = fp_lib_id.split(':', 1)
    mod_path = os.path.join(lib_fp_root, f"{lib}.pretty", f"{fp_name}.kicad_mod")
    if not os.path.exists(mod_path):
        print(f"  WARNING: footprint not found: {mod_path}")
        return None
    with open(mod_path) as f:
        text = f.read()
    # Strip metadata only valid in standalone .kicad_mod files
    text = re.sub(r'\s*\(version\s+[^)]+\)', '', text)
    text = re.sub(r'\s*\(generator(?:_version)?\s+"[^"]+"\)', '', text)
    # Prefix the footprint name with its library
    text = re.sub(r'\(footprint\s+"[^"]*"', f'(footprint "{fp_lib_id}"', text, count=1)
    # Inject a placeholder (at 0 0) since .kicad_mod files have none
    text = re.sub(r'(\(footprint\s+"[^"]+"\s*\n)', r'\1\t(at 0 0)\n', text, count=1)
    return text


def make_pcb_footprint(template, ref, x, y):
    """Clone a footprint template with new position, ref, and fresh UUIDs."""
    block = re.sub(r'\(at\s+-?[\d.]+\s+-?[\d.]+(?:\s+-?[\d.]+)?\)',
                   f'(at {x:.3f} {y:.3f})', template, count=1)
    block = re.sub(r'(\(property\s+"Reference"\s+)"[^"]*"',
                   rf'\1"{ref}"', block, count=1)
    block = re.sub(r'\(uuid\s+"[^"]*"\)',
                   lambda _: f'(uuid "{_uuid.uuid4()}")', block)
    return block


# ---------------------------------------------------------------------------
# Ref auto-assignment
# ---------------------------------------------------------------------------

def assign_new_refs(rows, existing_refs):
    """Fill in blank refs by incrementing past the highest existing number per prefix."""
    max_nums = {}
    for ref in existing_refs:
        m = re.match(r'^([A-Za-z]+)(\d+)$', ref)
        if m:
            prefix, num = m.group(1), int(m.group(2))
            max_nums[prefix] = max(max_nums.get(prefix, 0), num)

    counters = dict(max_nums)
    result = []
    for row in rows:
        if row["ref"]:
            result.append(row)
        else:
            prefix = TYPE_PREFIX.get(row["comp_type"], "X")
            counters[prefix] = counters.get(prefix, 199) + 1
            result.append(dict(row, ref=f"{prefix}{counters[prefix]}"))
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_sch = not args.pcb_only
    run_pcb = not args.sch_only

    # ── Spreadsheet ─────────────────────────────────────────────────────────
    print(f"Reading spreadsheet: {args.xlsx}")
    rows = read_spreadsheet(args.xlsx)
    print(f"  {len(rows)} component rows")

    # ── Schematic ────────────────────────────────────────────────────────────
    print(f"\nReading schematic:   {args.sch}")
    with open(args.sch) as f:
        sch_text = f.read()

    proj_uuid, proj_name = detect_project_info(sch_text, args.sch)
    print(f"  Project: {proj_name!r}  UUID: {proj_uuid}")

    sch_symbols     = parse_schematic_symbols(sch_text)
    sch_ref_map     = {s["ref"]: s for s in sch_symbols}
    sch_lib_tmpl    = {}   # lib_id → first example block for cloning
    sym_to_fp       = {}   # lib_id → footprint lib_id (populated from schematic + lib)
    for s in sch_symbols:
        if s["lib_id"] and s["lib_id"] not in sch_lib_tmpl:
            sch_lib_tmpl[s["lib_id"]] = s["block"]
        if s["footprint"]:
            sym_to_fp[s["lib_id"]] = s["footprint"]
    print(f"  {len(sch_symbols)} symbols, {len(sch_lib_tmpl)} unique lib_ids")

    # ── PCB ──────────────────────────────────────────────────────────────────
    print(f"\nReading PCB:         {args.pcb}")
    with open(args.pcb) as f:
        pcb_text = f.read()

    pcb_fps         = parse_pcb_footprints(pcb_text)
    pcb_ref_map     = {fp["ref"]: fp for fp in pcb_fps}
    pcb_fp_tmpl     = {fp["fp_lib_id"]: fp["block"] for fp in pcb_fps}
    print(f"  {len(pcb_fps)} footprints")

    # ── Ref assignment ────────────────────────────────────────────────────────
    all_refs = set(sch_ref_map) | set(pcb_ref_map)
    rows = assign_new_refs(rows, all_refs)

    # ── Plan schematic changes ────────────────────────────────────────────────
    sch_updates    = []
    sch_new_blocks = []
    stage_x, stage_y, stage_col = 600.0, 50.0, 0

    if run_sch:
        print("\n--- Schematic ---")
        for row in rows:
            ref, display, kicad_sym = row["ref"], row["display"], row["kicad_sym"]
            if not ref:
                print(f"  SKIP  {display!r}: no ref")
                continue

            if ref in sch_ref_map:
                old = sch_ref_map[ref]["block"]
                new = update_display_in_block(old, display)
                if new != old:
                    sch_updates.append((sch_ref_map[ref]["start"],
                                        sch_ref_map[ref]["end"], new))
                    print(f"  UPDATE {ref}: Display → {display!r}")
                else:
                    print(f"  OK     {ref}: Display already {display!r}")
            else:
                if not kicad_sym:
                    print(f"  SKIP  {ref} ({display!r}): no KiCad symbol — add manually")
                    continue

                # Use an existing in-schematic symbol as template if possible
                template = sch_lib_tmpl.get(kicad_sym)
                lib_fp = sym_to_fp.get(kicad_sym, "")

                if template is None:
                    result = load_sym_from_lib(kicad_sym, args.lib_sym)
                    if result is None:
                        print(f"  SKIP  {ref} ({display!r}): {kicad_sym} not found in lib")
                        continue
                    template, lib_fp = result
                    if kicad_sym not in sym_to_fp and lib_fp:
                        sym_to_fp[kicad_sym] = lib_fp

                sx = stage_x + stage_col * 30
                new_sym = make_sch_symbol(template, ref, display,
                                          proj_uuid, proj_name, sx, stage_y)
                sch_new_blocks.append(new_sym)
                stage_col += 1
                if stage_col > 8:
                    stage_col = 0
                    stage_y += 25
                print(f"  ADD   {ref} ({display!r}) → {kicad_sym}")

    # ── Plan PCB changes ──────────────────────────────────────────────────────
    pcb_updates    = []
    pcb_new_blocks = []

    if run_pcb:
        print("\n--- PCB ---")
        for row in rows:
            ref, display, kicad_sym = row["ref"], row["display"], row["kicad_sym"]
            x, y = row["x"], row["y"]
            if not ref:
                continue

            if ref in pcb_ref_map:
                old = pcb_ref_map[ref]["block"]
                new = update_pcb_position(old, x, y)
                if new != old:
                    pcb_updates.append((pcb_ref_map[ref]["start"],
                                        pcb_ref_map[ref]["end"], new))
                    print(f"  MOVE  {ref}: ({x:.3f}, {y:.3f})")
                else:
                    print(f"  OK    {ref}: already at ({x:.3f}, {y:.3f})")
            else:
                if not kicad_sym:
                    print(f"  SKIP  {ref} ({display!r}): no symbol → can't look up footprint")
                    continue
                fp_id = sym_to_fp.get(kicad_sym, "")
                if not fp_id:
                    print(f"  SKIP  {ref} ({display!r}): footprint unknown for {kicad_sym}")
                    continue

                tmpl = pcb_fp_tmpl.get(fp_id) or load_footprint_from_lib(fp_id, args.lib_fp)
                if tmpl is None:
                    print(f"  SKIP  {ref} ({display!r}): can't load {fp_id}")
                    continue

                pcb_new_blocks.append(make_pcb_footprint(tmpl, ref, x, y))
                print(f"  ADD   {ref} ({display!r}) fp={fp_id} at ({x:.3f}, {y:.3f})")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\nSchematic: {len(sch_updates)} updates, {len(sch_new_blocks)} additions")
    print(f"PCB:       {len(pcb_updates)} updates, {len(pcb_new_blocks)} additions")

    if not any([sch_updates, sch_new_blocks, pcb_updates, pcb_new_blocks]):
        print("\nNothing to do.")
        return

    # ── Write schematic ───────────────────────────────────────────────────────
    if run_sch and (sch_updates or sch_new_blocks):
        bak = args.sch + f".bak.{ts}"
        shutil.copy2(args.sch, bak)
        print(f"\nBackup: {os.path.basename(bak)}")

        out = apply_replacements(sch_text, sch_updates)
        if sch_new_blocks:
            out = out.rstrip()
            tail = '\n' + '\n'.join(sch_new_blocks) + '\n)'
            out = (out[:-1] if out.endswith(')') else out) + tail

        with open(args.sch, 'w') as f:
            f.write(out)
        print(f"Wrote {args.sch}")

    # ── Write PCB ─────────────────────────────────────────────────────────────
    if run_pcb and (pcb_updates or pcb_new_blocks):
        bak = args.pcb + f".bak.{ts}"
        shutil.copy2(args.pcb, bak)
        print(f"Backup: {os.path.basename(bak)}")

        out = apply_replacements(pcb_text, pcb_updates)
        if pcb_new_blocks:
            out = out.rstrip()
            tail = '\n' + '\n'.join(pcb_new_blocks) + '\n)'
            out = (out[:-1] if out.endswith(')') else out) + tail

        with open(args.pcb, 'w') as f:
            f.write(out)
        print(f"Wrote {args.pcb}")

    print("\nDone.")


if __name__ == "__main__":
    main()
