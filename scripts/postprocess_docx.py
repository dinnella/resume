"""
Post-process Michael_Dinnella_Resume.docx to center the header block
(name + all Normal paragraphs before the first Heading 2).
Run automatically by makedocx.sh after pandoc.
"""
import os
import sys
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUTPUT = os.environ.get("OUTPUT", "resume.docx")

if not Path(OUTPUT).exists():
    sys.exit(f"ERROR: {OUTPUT} not found")

doc = Document(OUTPUT)
past_h1 = False

for para in doc.paragraphs:
    if para.style.name == "Heading 1":
        past_h1 = True
        para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        continue
    if not past_h1:
        continue
    if para.style.name.startswith("Heading"):
        break  # stop at first H2+
    # Center Normal paragraphs in the header block
    para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.save(OUTPUT)
print(f"Post-processed: {OUTPUT}")
