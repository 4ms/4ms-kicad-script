# kicad2freecad

Scripts for exporting KiCad PCB files into formats suitable for FreeCAD enclosure modeling.
Designed for 4ms-style projects using KiCad 9 and FreeCAD 1.0.

## Workflow Overview

```
KiCad PCBs  →  export.sh  →  exports/  →  FreeCAD enclosure
```

1. Edit PCBs in KiCad as normal
2. Run `export.sh` from the project root to regenerate all exports
3. In FreeCAD, reload linked files — enclosure updates automatically

## Usage

Run from the project root:
```bash
bash ~/kicad/4ms-kicad-script/kicad2freecad/export.sh
```

Expects this folder structure in the project:
```
project-root/
  kicad/p1/
    front-pcb.kicad_pcb
    rear-pcb.kicad_pcb
  exports/              ← created automatically
```

Generates:
- `exports/front-panel.dxf` — front panel hole layout (Edge.Cuts circles only)
- `exports/front-pcb.step` — front PCB 3D model for FreeCAD placement
- `exports/rear-pcb.step` — rear PCB 3D model for FreeCAD placement

---

## Scripts

### `export.sh`
Master export script. Run this — it calls everything else.

### `make_faceplate_dxf.py`
Headless faceplate DXF generator. Reads a `.kicad_pcb` file, maps each panel
footprint to its correct hole diameter (using 4ms faceplate conventions), adds
Edge.Cuts circles at each position, and exports a DXF via `kicad-cli`.

No KiCad open required. No faceplate PCB file needed.

**Usage:**
```bash
python3 make_faceplate_dxf.py <input.kicad_pcb> <output.dxf>
```

**Hole size reference** (from `4ms_Faceplate.pretty`):

| Component | Footprint | Hole ⌀ |
|---|---|---|
| 16mm pot | `Pot_16mm_*_RV16AF-4A` | 7.112mm |
| 9mm pot (metal collar) | `Pot_9mm_DShaft`, `POT-9MM-ALPHA` | 7.1mm |
| 9mm pot (plastic) | `Pot_9mm_Knurl_*` | 6.604mm |
| Encoder (standard) | `ENC_SPST_12mm`, `ROTENC-12MM-BUT` | 7.366mm |
| Encoder (RGB) | `ENC_RGB_SPST_12mm` | 7.112mm |
| 3.5mm jack | `PJ301M-12`, `EighthInch_*_PJ*` | 6.604mm |
| 1/4" jack | `QuarterInch_Mono_*` | 10.0mm |
| LED 3mm | `LED_D3.0mm-3` | 3.048mm |
| PLCC4 / lightpipe | `LED_PLCC-4`, `PLCC4` | 2.921mm |
| Tactile button | `SW_TH_Tactile_Omron_B3F-100x` | 5.5mm |
| PB20 button | `Button_PB20B` | 9.5mm |
| Sub-mini toggle | `Switch_Toggle_SPDT_SubMini` | 4.953mm |
| Trimmer | `TRIM-T73YE` | 3.175mm |

### Rectangular cutouts (`RECT_SIZES`)

| Component | Footprint | Cutout |
|---|---|---|
| Cherry MX switch | `SW_Cherry_MX_PCB` | 14×14mm |
| Cherry MX w/ keycap | `SW_Cherry_MX_PCB_WithCap` | 14×14mm |
| Cherry MX w/ DSA cap | `SW_Cherry_MX_PCB_WithDSACap` | 14×14mm |

To add a new footprint type, add it to the `HOLE_SIZES` dict in `make_faceplate_dxf.py`.

### `edge_holes.py`
KiCad scripting console helper. Places Edge.Cuts circles at every PTH pad in
the currently open board, using the pad's drill diameter. Useful for one-off
checks or boards not covered by `make_faceplate_dxf.py`.

**Usage:** paste into KiCad scripting console, or run:
```python
exec(open('/Users/zach/kicad/4ms-kicad-script/kicad2freecad/edge_holes.py').read())
```

---

## Notes on Rear Panels with Right-Angle Hardware

Right-angle jacks (e.g. NRJ4HF) mount flat on the PCB but their bushings point
perpendicular — so panel hole positions cannot be derived from KiCad pad XY alone.
They depend on the PCB's depth position inside the enclosure.

**Rear panel workflow:**
1. Export `rear-pcb.step` via `export.sh`
2. Import into FreeCAD and position at correct Z depth inside enclosure
3. The STEP model shows exactly where jack bushings land on the rear face
4. Place holes in FreeCAD at those positions
5. No rear-panel DXF from KiCad needed

---

## Dependencies

- `kicad-cli` on PATH (installed with KiCad 9 at `/usr/local/bin/kicad-cli`)
- Python 3 (system)
- `~/kicad/4ms-kicad-lib/footprints/4ms_Faceplate.pretty` — used as reference for hole sizes (not loaded at runtime)
