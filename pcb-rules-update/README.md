# pcb-rules-update

Applies 4ms standard PCB rules to a KiCad project.

## What it does

Updates two files in the target project directory:

- `*.kicad_dru` — DRC minimum constraints (track width, clearance, via size)
- `*.kicad_pro` — Board Setup presets (track width and via size dropdowns in the routing toolbar)

Everything else in the project is left alone.

## Usage

```bash
python3 update_pcb_rules.py <kicad-project-directory>
```

Example:

```bash
python3 update_pcb_rules.py ~/kicad/pcb-listen-closely/v1.0/
```

**KiCad must be closed before running.** If KiCad is open it will overwrite the changes on next save.

## Editing the rules

All rules live in one file:

```
~/kicad/pcb-rules/4ms-rules.toml
```

Edit the values there, then re-run the script on any project you want to update. The TOML file contains the full 4ms layout reference as comments alongside the active values.
