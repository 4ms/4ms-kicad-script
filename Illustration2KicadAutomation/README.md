# Illustration2KicadAutomation

> **EXPERIMENTAL** — This toolset is in active development and was first tested on the Phase Mirror P2 project. Results should be verified in KiCad before committing or fabricating. Always review the dry-run output before running for real.

---

## Quick start

```bash
# Install dependency (one-time)
pip3 install openpyxl

# Run — backups are written automatically
python3 kicad_sync_from_coordinates.py \
    ~/path/to/coordinates.xlsx \
    ~/path/to/project.kicad_pro
```

The `.kicad_sch` and `.kicad_pcb` files are found automatically from the
`.kicad_pro` path — they must be in the same folder with the same base name
(standard KiCad project layout).

Running bare with no arguments defaults to Phase Mirror P2 (for development).

---

## What it does

A two-script workflow that bridges a visual component placement spreadsheet (the "illustration" or layout document) into a live KiCad 10 project:

```
Component Placement .xlsx
        │
        ▼
kicad_sync_from_coordinates.py
        │
        ├─► .kicad_sch  — updates Display labels, adds new symbols to staging area
        └─► .kicad_pcb  — moves footprints to spreadsheet X/Y, adds new footprints
```

## Files

| File | Purpose |
|------|---------|
| `make_placement_template.py` | Generates a blank `Component Placement Template.xlsx` for a new project |
| `Component Placement Template.xlsx` | Blank template — copy into your project's `artwork/` folder |
| `kicad_sync_from_coordinates.py` | Reads a filled-in spreadsheet and syncs it into `.kicad_sch` + `.kicad_pcb` |

---

## Workflow

### 1. Generate (or copy) a blank template

```bash
python3 make_placement_template.py
# Output: Component Placement Template.xlsx (in the same folder)
```

Copy this into your project's `artwork/` folder and rename it
(e.g. `my-module-coordinates.xlsx`).

### 2. Fill in the spreadsheet

| Column | Fill in | Notes |
|--------|---------|-------|
| A — Ref | Leave blank for new parts; put existing schematic ref for parts already placed | Auto-assigned on first sync |
| B — Display Name | Functional name shown on schematic (e.g. `LFO_Freq`, `Mix`) | |
| C — X | Panel X coordinate in mm, panel-center origin | |
| D — Y | Panel Y coordinate in mm, panel-center origin, +Y = down | |
| E — Component Type | Pick from dropdown: Pot / Jack / LED / Button / Switch / Standoff / Connector | |
| F — Subtype | Dependent dropdown — narrows by Component Type | |
| G — KiCad Symbol | Auto-fills via VLOOKUP — do not edit | Blank OK; subtype lookup used as fallback |
| H — Notes | `IGNORE` skips the row; anything else is informational | |

Rows with **Subtype = "Silkscreen Label"** or **Notes = "IGNORE"** are skipped entirely.

### 3. Run it

```bash
python3 kicad_sync_from_coordinates.py \
    artwork/my-module-coordinates.xlsx \
    kicad/p2/my-module.kicad_pro
```

Every UPDATE / ADD / MOVE / SKIP prints as it runs. Backups are written automatically.

Timestamped backups are written automatically:
```
my-module.kicad_sch.bak.20261008_114000
my-module.kicad_pcb.bak.20261008_114000
```

### 5. Open in KiCad and review

- New schematic symbols land in a **staging area** off the right edge of the sheet (~x=600). Wire them up and move them into place.
- New PCB footprints are placed at the correct panel X/Y with no rotation — add rotation as needed for back-copper or angled components.
- Run **ERC** and **DRC** to catch any issues before committing.

---

## CLI reference

```
python3 kicad_sync_from_coordinates.py  SPREADSHEET.xlsx  PROJECT.kicad_pro  [flags]

Positional arguments:
  SPREADSHEET.xlsx    Component placement coordinates spreadsheet
  PROJECT.kicad_pro   KiCad project file — .kicad_sch and .kicad_pcb are
                      resolved automatically from the same folder + base name

Optional flags:
  --lib-sym PATH    Symbol library root    (default: ~/kicad/4ms-kicad-lib/symbols)
  --lib-fp  PATH    Footprint library root (default: ~/kicad/4ms-kicad-lib/footprints)
  --sch-only        Only update the schematic
  --pcb-only        Only update the PCB
```

Running with no arguments defaults to **Phase Mirror P2** (development/testing).

---

## Dependencies

```bash
pip3 install openpyxl
```

Python 3.9+, KiCad 10.x file format.

---

## Known limitations / TODO

- New schematic symbols are added as **minimal stubs** — they have the correct lib_id, ref, footprint, and Display label, but their graphical body (pins, lines) is not drawn on the schematic canvas until KiCad re-renders them. They will show as question marks or empty boxes until KiCad resolves them from the library.
- **Lib_id mismatch** (e.g. a pot changed from 16mm to 9mm) is not handled — the sync updates position and Display only. Change the lib_id manually in KiCad.
- **Net connections** are not created — wiring must be done by hand in eeschema after new symbols are placed.
- **PCB rotation** is not preserved for newly added footprints (placed at 0°). Adjust in PCB editor.
- **Back-copper footprints** are placed on F.Cu by default. Flip manually if needed.
- Tested on **KiCad 10.0** s-expression format only. KiCad 7/8 may work but is untested.
