#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$SCRIPT_DIR")"
[[ -f "$REPO/.venv/bin/activate" ]] && source "$REPO/.venv/bin/activate"
cd "$REPO"

INPUT="${1:-resume.md}"
OUTPUT="${2:-resume.docx}"
REFERENCE="${3:-templates/reference.docx}"

command -v pandoc >/dev/null 2>&1 || { echo "ERROR: pandoc not found. See README.md."; exit 1; }

# Build the styled reference doc if it doesn't exist
if [[ ! -f "$REFERENCE" ]]; then
    echo "Generating $REFERENCE..."
    mkdir -p "$(dirname "$REFERENCE")"
    pandoc --print-default-data-file reference.docx > "$REFERENCE"
    python3 scripts/style_reference_docx.py
fi

pandoc "$INPUT" \
  --reference-doc="$REFERENCE" \
  --lua-filter=scripts/remove-ids.lua \
  -o "$OUTPUT"

OUTPUT="$OUTPUT" python3 scripts/postprocess_docx.py

echo "Built: $OUTPUT"
