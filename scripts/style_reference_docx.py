"""
Apply PDF-matching styles to reference.docx for pandoc DOCX output.
Called automatically by makedocx.sh when reference.docx needs to be (re)generated.
Run manually after any style change: python3 style_reference_docx.py
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

REFERENCE = "templates/reference.docx"
FONT      = "Calibri"   # universally available in Word Online + LibreOffice

doc = Document(REFERENCE)


def get_style(name):
    """Subscript lookup is broken on pandoc reference docs; iterate instead."""
    return next(s for s in doc.styles if s.name == name)


def set_font(style, size_pt, bold=False, italic=False, hex_color=None):
    f = style.font
    f.name = FONT
    f.size = Pt(size_pt)
    f.bold = bold
    f.italic = italic
    if hex_color:
        r, g, b = bytes.fromhex(hex_color)
        f.color.rgb = RGBColor(r, g, b)


def set_spacing(style, before_pt=0, after_pt=0, line=1.5):
    pf = style.paragraph_format
    pf.space_before = Pt(before_pt)
    pf.space_after = Pt(after_pt)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line


def add_bottom_border(style, hex_color="8ca9c8", sz=6):
    """Add a single bottom border to a paragraph style (sz in 1/8 pt)."""
    pPr = style.element.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(sz))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), hex_color)
    pBdr.append(bottom)
    pPr.append(pBdr)


# Normal / body text
normal = get_style("Normal")
set_font(normal, 11, hex_color="2d2d2d")
set_spacing(normal, before_pt=0, after_pt=8, line=1.5)

# Heading 1 → Name
h1 = get_style("Heading 1")
set_font(h1, 19, bold=True, hex_color="1a1a1a")
h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_spacing(h1, before_pt=0, after_pt=3, line=1.0)

# Heading 2 → Section headers (EXPERIENCE, EDUCATION, …)
h2 = get_style("Heading 2")
set_font(h2, 10, bold=True, hex_color="2e4a6b")
set_spacing(h2, before_pt=20, after_pt=8, line=1.0)
add_bottom_border(h2)

# Heading 3 → Company / employer line
h3 = get_style("Heading 3")
set_font(h3, 11, bold=True, hex_color="2d2d2d")
set_spacing(h3, before_pt=12, after_pt=2, line=1.0)

# Heading 4 → Sub-role / date range
h4 = get_style("Heading 4")
set_font(h4, 10.5, bold=False, italic=True, hex_color="2d2d2d")
set_spacing(h4, before_pt=8, after_pt=2, line=1.0)

# Page margins  (match CSS: 0.75in top/bottom, 1in left/right)
for section in doc.sections:
    section.top_margin    = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin   = Inches(1.0)
    section.right_margin  = Inches(1.0)

doc.save(REFERENCE)
print(f"Styled: {REFERENCE}")
