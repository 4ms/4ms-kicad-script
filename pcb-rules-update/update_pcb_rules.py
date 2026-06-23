#!/usr/bin/env python3
"""
Apply 4ms standard PCB rules to a KiCad project directory.

Reads:  ~/kicad/pcb-rules/4ms-rules.toml  (single source of truth)

Updates:
  *.kicad_dru  — overwrites (or creates) with generated DRC constraints
  *.kicad_pro  — merges rules, track_widths, via_dimensions into board
                  design_settings (all other keys are preserved)

Usage:
  python3 update_pcb_rules.py <kicad-project-directory>

KiCad must be closed before running — it overwrites .kicad_pro on save.
"""

import sys
import json
import tomllib
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
RULES_TOML = SCRIPT_DIR.parent.parent / "pcb-rules" / "4ms-rules.toml"


def build_dru(cfg: dict) -> str:
    t = cfg["tracks"]
    v = cfg["vias"]
    lines = [
        "(version 1)",
        "",
        "# 4ms Company Standard PCB Design Rules",
        "# Generated from: ~/kicad/pcb-rules/4ms-rules.toml",
        "",
        f'(rule "4ms_min_track"',
        f'\t(constraint track_width (min {t["min"]}mm))',
        ")",
        "",
        f'(rule "4ms_min_clearance"',
        f'\t(constraint clearance (min {cfg["constraints"]["min_clearance"]}mm))',
        ")",
        "",
        f'(rule "4ms_min_via"',
        f'\t(constraint via_diameter (min {v["min_diameter"]}mm))',
        f'\t(constraint hole_size    (min {v["min_drill"]}mm))',
        ")",
    ]
    return "\n".join(lines) + "\n"


def build_board_settings(cfg: dict) -> dict:
    t = cfg["tracks"]
    v = cfg["vias"]
    c = cfg["constraints"]
    return {
        "rules": {
            "min_clearance":           c["min_clearance"],
            "min_track_width":         t["min"],
            "min_via_diameter":        v["min_diameter"],
            "min_through_hole_diameter": c["min_through_hole_dia"],
            "min_via_annular_width":   c["min_via_annular_width"],
            "min_copper_edge_clearance": c["min_copper_edge_clearance"],
            "min_hole_clearance":      c["min_hole_clearance"],
            "min_hole_to_hole":        c["min_hole_to_hole"],
        },
        "track_widths": [0.0] + t["presets"],
        "via_dimensions": [{"diameter": 0.0, "drill": 0.0}] + [
            {"diameter": d, "drill": dr} for d, dr in v["presets"]
        ],
    }


def update_dru(project_dir: Path, dru_content: str) -> Path:
    dru_files = sorted(project_dir.glob("*.kicad_dru"))
    if dru_files:
        target = dru_files[0]
    else:
        pro_files = sorted(project_dir.glob("*.kicad_pro"))
        stem = pro_files[0].stem if pro_files else project_dir.name
        target = project_dir / f"{stem}.kicad_dru"
    target.write_text(dru_content)
    return target


def update_pro(pro_file: Path, settings: dict) -> None:
    with open(pro_file) as f:
        pro = json.load(f)
    ds = pro.setdefault("board", {}).setdefault("design_settings", {})
    ds.setdefault("rules", {}).update(settings["rules"])
    ds["track_widths"] = settings["track_widths"]
    ds["via_dimensions"] = settings["via_dimensions"]
    with open(pro_file, "w") as f:
        json.dump(pro, f, indent=2)
        f.write("\n")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <kicad-project-directory>")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    if not project_dir.is_dir():
        print(f"Error: not a directory: {project_dir}")
        sys.exit(1)

    if not RULES_TOML.exists():
        print(f"Error: rules file not found: {RULES_TOML}")
        sys.exit(1)

    with open(RULES_TOML, "rb") as f:
        cfg = tomllib.load(f)

    dru_content = build_dru(cfg)
    settings = build_board_settings(cfg)

    dru_target = update_dru(project_dir, dru_content)
    print(f"DRU  → {dru_target}")

    pro_files = sorted(project_dir.glob("*.kicad_pro"))
    if not pro_files:
        print("Warning: no .kicad_pro found — skipping board settings update")
    for pro_file in pro_files:
        update_pro(pro_file, settings)
        print(f"PRO  → {pro_file}")


if __name__ == "__main__":
    main()
