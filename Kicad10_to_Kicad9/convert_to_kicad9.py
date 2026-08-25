#!/usr/bin/env python3
"""
Convert KiCad 10 schematic files to KiCad 9 format.

Usage:
    python3 convert_to_kicad9.py <project_dir>

Creates a copy of <project_dir> named <project_dir>-kicad9/ and converts
all .kicad_sch files inside it. The original directory is never touched.

Example:
    python3 convert_to_kicad9.py ~/kicad/pcb-phase-mirror/kicad/p1
    # Creates: ~/kicad/pcb-phase-mirror/kicad/p1-kicad9/
"""

import re
import shutil
import sys
from pathlib import Path

K10_VERSION = "20260306"
K9_VERSION  = "20250114"

# Lines consisting solely of these KiCad 10-only properties are removed
STRIP_PATTERNS = [
    re.compile(r"^\s+\(do_not_autoplace\s+(yes|no)\)\s*$"),
    re.compile(r"^\s+\(in_pos_files\s+(yes|no)\)\s*$"),
    re.compile(r"^\s+\(exclude_from_sim\s+(yes|no)\)\s*$"),
    re.compile(r"^\s+\(duplicate_pin_numbers_are_jumpers\s+(yes|no)\)\s*$"),
]

def convert(path: Path) -> tuple[int, int]:
    """Convert a single .kicad_sch file in-place. Returns (replaced, stripped)."""
    text = path.read_text(encoding="utf-8")

    if f"(version {K10_VERSION})" not in text:
        print(f"  SKIP {path.name} (not KiCad 10 format)")
        return 0, 0

    lines = text.splitlines(keepends=True)
    out = []
    replaced = 0
    stripped = 0

    for line in lines:
        # Version markers
        line = line.replace(f"(version {K10_VERSION})", f"(version {K9_VERSION})")
        line = line.replace('(generator_version "10.0")', '(generator_version "9.0")')

        # (power global) → (power)
        if "(power global)" in line:
            line = line.replace("(power global)", "(power)")
            replaced += 1

        # (body_style N) → (convert N)
        if "(body_style " in line:
            line = re.sub(r"\(body_style (\d+)\)", r"(convert \1)", line)
            replaced += 1

        # Strip KiCad 10-only property lines entirely
        if any(p.match(line) for p in STRIP_PATTERNS):
            stripped += 1
            continue

        out.append(line)

    path.write_text("".join(out), encoding="utf-8")
    print(f"  CONVERTED {path.name}: {replaced} replacements, {stripped} lines stripped")
    return replaced, stripped


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    src = Path(sys.argv[1]).expanduser().resolve()
    if not src.is_dir():
        print(f"Error: {src} is not a directory")
        sys.exit(1)

    dst = src.parent / (src.name + "-kicad9")
    if dst.exists():
        print(f"Removing existing {dst}")
        shutil.rmtree(dst)

    print(f"Copying {src} → {dst}")
    shutil.copytree(src, dst)

    sch_files = sorted(dst.rglob("*.kicad_sch"))
    print(f"Found {len(sch_files)} .kicad_sch files\n")

    total_replaced = 0
    total_stripped = 0
    for f in sch_files:
        r, s = convert(f)
        total_replaced += r
        total_stripped += s

    print(f"\nDone. Output: {dst}")
    print(f"Total replacements: {total_replaced}, lines stripped: {total_stripped}")


if __name__ == "__main__":
    main()
