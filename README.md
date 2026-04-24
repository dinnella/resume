# Resume

Source-controlled resume in Markdown. A GitHub Actions pipeline renders it to
PDF and DOCX on every push to `main`. Local scripts are provided for offline builds.

## Files

| File | Purpose |
|---|---|
| `resume.md` | Master resume content — edit this |
| `requirements.txt` | Pinned pip dependencies (`weasyprint`, `python-docx`) |
| `templates/resume.css` | PDF stylesheet |
| `scripts/makepdf.sh` | Local + CI PDF build script |
| `scripts/makedocx.sh` | Local + CI DOCX build script (auto-generates `templates/reference.docx`) |
| `scripts/build_docx_from_template.py` | Generate Template-aligned DOCX from Word template |
| `scripts/generate_md_from_template.py` | Generate a markdown skeleton from a Word template (run when template changes) |
| `scripts/style_reference_docx.py` | Called by `makedocx.sh` — styles the pandoc reference doc |
| `scripts/postprocess_docx.py` | Called by `makedocx.sh` — centers header block in DOCX output |
| `scripts/remove-ids.lua` | Called by `makedocx.sh` — strips heading bookmark IDs (prevents `[` artifacts) |
| `.github/workflows/build-resume.yml` | CI pipeline |

## Quickstart

### Local build

**1. Install dependencies**

**macOS (Homebrew)**
```bash
brew install pandoc
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Ubuntu / Debian**
```bash
sudo apt-get install pandoc libpango-1.0-0 libpangocairo-1.0-0
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Windows**
Download the pandoc installer from https://pandoc.org/installing.html, then:
```powershell
python3 -m venv .venv; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> The build scripts auto-activate `.venv` if present.

**2. Build the PDF**
```bash
# defaults: resume.md → resume.pdf
bash scripts/makepdf.sh

# custom: [input] [output] [css] [title]
bash scripts/makepdf.sh resume.md MyResume.pdf templates/resume.css "Jane Doe – Resume"
```

**3. Build the standard DOCX**
```bash
# defaults: resume.md → resume.docx
bash scripts/makedocx.sh

# custom: [input] [output] [reference.docx]
bash scripts/makedocx.sh resume.md MyResume.docx templates/reference.docx
```

**4. Build the DOCX** (requires a docx template, e.g. `templates/Excella Resume Template 2026.docx`)
```bash
source .venv/bin/activate

# defaults: resume.md → resume_from_template.docx
python3 scripts/build_docx_from_template.py

# custom: [template] [source] [output]
python3 scripts/build_docx_from_template.py "templates/Excella Resume Template 2026.docx" resume.md MyResume_Excella.docx
```

### CI build (GitHub Actions)

Push any change to `resume.md`, `scripts/`, or `templates/` on `main`. The workflow runs
automatically and uploads `resume.pdf` and `resume.docx` as workflow artifacts
(retained for 400 days). Download them from the **Actions** tab → latest run →
**Artifacts**.

Trigger a build manually anytime from **Actions → Build Resume → Run workflow**.

## Dependencies

| Dependency | Version | Purpose | macOS | Ubuntu / Debian | Windows |
|---|---|---|---|---|---|
| [pandoc](https://pandoc.org) | ≥ 3.0 | Markdown → PDF/DOCX | `brew install pandoc` | `sudo apt install pandoc` | [installer](https://pandoc.org/installing.html) |
| [WeasyPrint](https://weasyprint.org) | ≥ 61.0 | HTML → PDF engine | `pip install -r requirements.txt` | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| [python-docx](https://python-docx.readthedocs.io) | ≥ 1.0 | DOCX generation | (via `requirements.txt`) | (via `requirements.txt`) | (via `requirements.txt`) |
| libpango / libcairo | — | WeasyPrint system libs | via Homebrew (auto) | `sudo apt install libpango-1.0-0 libpangocairo-1.0-0` | bundled |
| [actions/checkout](https://github.com/actions/checkout) | v4 | CI: checkout repo | — | — | — |
| [actions/upload-artifact](https://github.com/actions/upload-artifact) | v4 | CI: upload artifacts | — | — | — |

> Pip packages are installed via `pip install -r requirements.txt` inside the `.venv` (see Quickstart step 1).
