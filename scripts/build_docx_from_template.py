"""
Generate Resume from template (e.g. Excella Resume Template 2026.docx) and markdown source (resume.md).
Run from the repo root: python scripts/build_docx_from_template.py [template] [source] [output]
  e.g.  python scripts/build_docx_from_template.py "templates/Excella Resume Template 2026.docx" excella-resume.md resume_from_template.docx

Markdown → Word style mapping
------------------------------
  # Heading              → Name
  **bold** (header)      → Job Position or Title
  plain   (header)       → Normal
  ## SECTION             → Section Header
  **BOLD** (experience)  → Company          (resets paragraph counter)
  *italic*               → Normal italic    (resets paragraph counter)
  1st paragraph after role   → Normal
  2nd+ paragraphs after role → Bullet Points
  **partial bold** line  → Section Subheader  (EDUCATION only)
  plain (EDUCATION)      → Company
  plain (CERTIFICATIONS) → Certifications
  plain (SKILL SETS)     → Skills
  plain (SUMMARY/CLEARANCE) → Normal

Template compatibility
----------------------
This script binds to paragraph style names in the template
(e.g. 'Name', 'Company', 'Bullet Points', 'Section Header'). It will survive
visual template updates as long as style names stay the same. If Excella
renames or removes a style, update the matching style= argument here.

To inspect current style names in any template revision:
    python3 -c "from docx import Document; d = Document('Excella Resume Template 2026.docx'); print({p.style.name for p in d.paragraphs})"
"""
import re
import sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from copy import deepcopy

TEMPLATE = sys.argv[1] if len(sys.argv) > 1 else "templates/Excella Resume Template 2026.docx"
SOURCE   = sys.argv[2] if len(sys.argv) > 2 else "resume.md"
OUTPUT   = sys.argv[3] if len(sys.argv) > 3 else "resume_from_template.docx"

for f in [TEMPLATE, SOURCE]:
    if not Path(f).exists():
        sys.exit(f"ERROR: file not found: {f}")

tmpl = Document(TEMPLATE)
sect_pr = deepcopy(tmpl.element.body.find(qn("w:sectPr")))

doc = Document(TEMPLATE)
body = doc.element.body
for child in list(body):
    body.remove(child)


def ap(text, style, italic=False):
    para = doc.add_paragraph(style=style)
    if text:
        run = para.add_run(text)
        if italic:
            run.italic = True
    return para


def strip_bold(text):
    return re.sub(r"\*\*([^*]*)\*\*", r"\1", text)


lines = Path(SOURCE).read_text(encoding="utf-8").splitlines()

in_header = True        # True until the first ## section is encountered
current_section = None
para_count = 0          # paragraphs since last Company or italic-role line

for line in lines:
    s = line.strip()

    if not s or s == "---":
        continue

    # H1 → Name
    if s.startswith("# "):
        ap(s[2:], "Name")
        continue

    # H2 → Section Header
    if s.startswith("## "):
        current_section = s[3:]
        ap(current_section, "Section Header")
        in_header = False
        para_count = 0
        continue

    # Fully bold line: **text**
    if s.startswith("**") and s.endswith("**"):
        text = strip_bold(s)
        if in_header:
            ap(text, "Job Position or Title")
        elif current_section == "EDUCATION":
            ap(text, "Section Subheader")
        else:
            ap(text, "Company")
            para_count = 0
        continue

    # Partially bold line: **Foo** — rest of line  (e.g. Widener University)
    if s.startswith("**") and "**" in s[2:]:
        text = strip_bold(s)
        ap(text, "Section Subheader" if current_section == "EDUCATION" else "Normal")
        continue

    # Italic line: *role title*  — resets paragraph counter
    if re.match(r"^\*[^*]", s) and s.endswith("*"):
        ap(s[1:-1], "Normal", italic=True)
        para_count = 0
        continue

    # Regular paragraph
    if current_section == "EXPERIENCE":
        ap(s, "Normal" if para_count == 0 else "Bullet Points")
        para_count += 1
    elif current_section == "EDUCATION":
        ap(s, "Company")
    elif current_section == "CERTIFICATIONS":
        ap(s, "Certifications")
    elif current_section == "SKILL SETS":
        ap(s, "Skills")
    else:
        ap(s, "Normal")

body.append(sect_pr)

doc.save(OUTPUT)
print(f"Built: {OUTPUT}")
