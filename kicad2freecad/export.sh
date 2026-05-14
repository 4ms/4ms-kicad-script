#!/bin/bash
# export.sh
# Run from the root of a phase-mirror-style project.
# Generates all FreeCAD-ready exports from KiCad source files.
#
# Usage: ./scripts/export.sh
#   or:  bash /path/to/4ms-kicad-script/kicad2freecad/export.sh
#
# Output (relative to project root):
#   exports/front-panel.dxf   — front panel hole layout
#   exports/front-pcb.step    — front PCB 3D model
#   exports/rear-pcb.step     — rear PCB 3D model

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"
KICAD_DIR="$PROJECT_ROOT/kicad/p1"
EXPORTS_DIR="$PROJECT_ROOT/exports"

FRONT_PCB="$KICAD_DIR/front-pcb.kicad_pcb"
REAR_PCB="$KICAD_DIR/rear-pcb.kicad_pcb"

echo "=== Phase Mirror Export ==="
echo "Project: $PROJECT_ROOT"
echo "KiCad:   $KICAD_DIR"
echo "Exports: $EXPORTS_DIR"
echo ""

# Verify inputs exist
for f in "$FRONT_PCB" "$REAR_PCB"; do
    if [ ! -f "$f" ]; then
        echo "ERROR: Missing $f"
        exit 1
    fi
done

mkdir -p "$EXPORTS_DIR"

# --- Front panel DXF (hole layout) ---
echo "[1/3] Generating front panel DXF..."
python3 "$SCRIPT_DIR/make_faceplate_dxf.py" \
    "$FRONT_PCB" \
    "$EXPORTS_DIR/front-panel.dxf"

# --- Front PCB STEP (3D model) ---
echo ""
echo "[2/3] Generating front PCB STEP..."
kicad-cli pcb export step \
    --output "$EXPORTS_DIR/front-pcb.step" \
    --subst-models \
    --no-unspecified \
    "$FRONT_PCB"

# --- Rear PCB STEP (3D model) ---
echo ""
echo "[3/3] Generating rear PCB STEP..."
kicad-cli pcb export step \
    --output "$EXPORTS_DIR/rear-pcb.step" \
    --subst-models \
    --no-unspecified \
    "$REAR_PCB"

echo ""
echo "=== Done ==="
ls -lh "$EXPORTS_DIR"
