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

COMBINED_PCB="$KICAD_DIR/phase-mirror.kicad_pcb"
PCB_OUT_DIR="$KICAD_DIR/_pcbs_for_export"
FRONT_PCB="$PCB_OUT_DIR/phase-mirror_FRONT.kicad_pcb"
REAR_PCB="$PCB_OUT_DIR/phase-mirror_REAR.kicad_pcb"

# KiCad's bundled Python (has pcbnew; system python3 does not)
KICAD_PYTHON="/Applications/KiCad9/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
SPLIT_SCRIPT="$HOME/DIIRT-LOG/4MS/scripts/split_pcb.py"

# 3D model search paths for kicad-cli (not inherited from KiCad GUI environment)
export KICAD_4MS_LIBS="/Users/zach/kicad/4ms-kicad-lib"
export ALT3DMOD="/Users/zach/kicad/4ms-kicad-lib/packages3d"
export KICAD6_3DMODEL_DIR="/Applications/KiCad9/KiCad.app/Contents/SharedSupport/3dmodels"

echo "=== Phase Mirror Export ==="
echo "Project: $PROJECT_ROOT"
echo "KiCad:   $KICAD_DIR"
echo "Exports: $EXPORTS_DIR"
echo ""

# Verify combined source exists
if [ ! -f "$COMBINED_PCB" ]; then
    echo "ERROR: Missing $COMBINED_PCB"
    exit 1
fi

mkdir -p "$EXPORTS_DIR"
mkdir -p "$PCB_OUT_DIR"

# --- Split combined PCB into FRONT / REAR ---
echo "[0/3] Splitting combined PCB into FRONT/REAR..."
"$KICAD_PYTHON" "$SPLIT_SCRIPT" "$COMBINED_PCB" "$PCB_OUT_DIR/"
echo ""

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
