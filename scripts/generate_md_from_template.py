"""
Generate a markdown skeleton from a Word template (.docx).
Walks the template body, maps paragraph styles to markdown syntax, and writes
a ready-to-edit .md file for use with build_docx_from_template.py.

The skeleton is derived from the template's actual structure and placeholder
text — re-run whenever the template changes to get an updated skeleton.

Usage:
    python3 scripts/generate_md_from_template.py [template.docx [output.md]]

Defaults:
    template : templates/Excella Resume Template 2026.docx
    output   : templates/resume-skeleton-from-template.md
"""
import sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn

TEMPLATE = sys.argv[1] if len(sys.argv) > 1 else "templates/Excella Resume Template 2026.docx"
OUTPUT   = sys.argv[2] if len(sys.argv) > 2 else "templates/resume-skeleton-from-template.md"

if not Path(TEMPLATE).exists():
    sys.exit(f"ERROR: file not found: {TEMPLATE}")

doc = Document(TEMPLATE)

# ── Style → markdown prefix (generic; longest match wins) ──────────────────
# Keys are lowercased substrings of the style name.
# Order matters: more specific first.
STYLE_MAP = [
    ("name",             "# "),
    ("section header",   "\n## "),
    ("heading 1",        "\n## "),
    ("section subhead",  "### "),
    ("heading 2",        "### "),
    ("company",          "### "),
    ("job position",     "**"),   # suffix added separately
    ("subtitle",         "**"),
    ("heading 3",        "#### "),
    ("bullet",           "- "),
    ("list paragraph",   "- "),
    ("skills",           "- "),
    ("certif",           "- "),
    ("title",            "# "),
]

BOLD_STYLES = {"job position", "subtitle"}
TXBX = qn("w:txbxContent")

# ── Noise filters ─────────────────────────────────────────────────────────────
# Substrings that identify Lorem ipsum filler or template instruction lines.
# Checked case-insensitively against the full paragraph text.
# Only filter actual Latin filler — keep all instructional/example text.
_LOREM = [
    "lorem ipsum",
    "dolor sit amet",
    "consectetur adipiscing",
    "pellentesque",
    "vestibulum",
    "curabitur",
    "maecenas",
    "phasellus",
    "viverra",
    "ullamcorper",
]

def is_lorem(text: str) -> bool:
    tl = text.lower()
    return any(pat in tl for pat in _LOREM)


def md_prefix(style_name):
    sl = style_name.lower()
    for key, prefix in STYLE_MAP:
        if key in sl:
            return prefix, key in BOLD_STYLES
    return "", False  # Normal → plain


def para_text(el):
    """Get visible text from a paragraph element, excluding textbox content."""
    texts = []
    for child in el:
        tag = child.tag.split("}")[-1]
        if tag in ("r", "ins"):
            for t in child.iter(qn("w:t")):
                texts.append(t.text or "")
    return "".join(texts).strip()


# ── Walk body elements ────────────────────────────────────────────────────────
lines = []
seen_h2  = set()         # deduplicates ## section headers (textboxes)
seen_h3  = {}            # h3 text -> occurrence count
skip_block = False       # True while inside a 3rd+ duplicate ### block

for el in doc.element.body:
    tag = el.tag.split("}")[-1]

    if tag == "sectPr":
        continue

    if tag == "tbl":
        skip_block = False
        col_headers = []
        for cell in el.iter(qn("w:tc")):
            cell_text = "".join(t.text or "" for t in cell.iter(qn("w:t"))).strip()
            if cell_text:
                col_headers.append(cell_text)
        if col_headers:
            lines.append("")
            lines.append("| " + " | ".join(col_headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(col_headers)) + " |")
            lines.append("| " + " | ".join([f"Your {h.title()} here" for h in col_headers]) + " |")
        continue

    if tag != "p":
        continue

    # Textbox paragraphs carry the sidebar section labels — emit as ## headers.
    txbx = el.find(".//" + TXBX)
    if txbx is not None:
        label = "".join(t.text or "" for t in txbx.iter(qn("w:t"))).strip()
        if label and label not in seen_h2:
            seen_h2.add(label)
            skip_block = False
            lines.append(f"\n## {label}")
        continue

    # Resolve style name
    ps = el.find(".//" + qn("w:pStyle"))
    style_name = ps.get(qn("w:val")) if ps is not None else "Normal"
    try:
        style_name = doc.styles.get_by_id(style_name, 1).name
    except Exception:
        pass

    text = para_text(el)
    if not text or is_lorem(text):
        continue

    prefix, is_bold = md_prefix(style_name)
    is_h3 = prefix.strip() == "###"
    is_heading = prefix.strip().startswith("#")

    if is_h3:
        # Allow up to 2 occurrences of each ### heading:
        # occurrence 1 = multi-role format example
        # occurrence 2 = single-role format example
        # 3rd+ = true duplicates, skip with their content
        count = seen_h3.get(text, 0)
        seen_h3[text] = count + 1
        if count >= 2:
            skip_block = True
            continue
        skip_block = False
    elif is_heading:
        skip_block = False

    if skip_block:
        continue

    if is_bold:
        lines.append(f"**{text}**")
    else:
        lines.append(f"{prefix}{text}")

skeleton = "\n".join(lines) + "\n"

Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
Path(OUTPUT).write_text(skeleton, encoding="utf-8")
print(f"Skeleton written to: {OUTPUT}")


