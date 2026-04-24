#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$SCRIPT_DIR")"
[[ -f "$REPO/.venv/bin/activate" ]] && source "$REPO/.venv/bin/activate"
cd "$REPO"

INPUT="${1:-resume.md}"
OUTPUT="${2:-resume.pdf}"
CSS="${3:-templates/resume.css}"
TITLE="${4:-Resume}"

command -v pandoc  >/dev/null 2>&1 || { echo "ERROR: pandoc not found. See README.md."; exit 1; }
command -v weasyprint >/dev/null 2>&1 || { echo "ERROR: weasyprint not found. See README.md."; exit 1; }

pandoc "$INPUT" \
  --pdf-engine=weasyprint \
  --css="$CSS" \
  --metadata pagetitle="$TITLE" \
  -o "$OUTPUT"

echo "Built: $OUTPUT"
