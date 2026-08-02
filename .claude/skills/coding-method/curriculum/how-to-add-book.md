# How to add a book to the curriculum

When you add one of the **3 missing books** (The Algorithm Design Manual,
Refactoring, Designing Data-Intensive Applications) — or any future book — this
is the path from PDF/EPUB to a distilled method card to a reference file.

## ⚠️ Copyright
The books are copyrighted source material. `CodingBooks/` and `CodingBooks-md/`
are **gitignored** and must NEVER be committed or published. The distilled
method cards and reference files in this skill are original synthesis — never
copy passages from a book into committed files.

## 1. Convert the book → `.md`
Drop the source file into `C:\Dev\TRIZskill.md\CodingBooks\`, then run the
converter with the system Python (the one with pymupdf/markdownify — not the
`python` on PATH, which is a bare venv):

```
"C:\Users\matte\AppData\Local\Programs\Python\Python313\python.exe" CodingBooks-md\convert.py
```

- **Born-digital PDFs** are extracted heading-aware (font-size-based `#`/`##`
  detection, code blocks fenced, running headers removed).
- **EPUBs** are converted via markdownify (spine order, styles stripped).
- **Scanned PDFs** can't be extracted — run `ocr_dijkstra.py` (pymupdf 300 DPI
  render + tesseract per page). Requires tesseract first:
  `! winget install --id UB-Mannheim.TesseractOCR -e` (confirm the UAC prompt),
  then `"C:\...\Python313\python.exe" CodingBooks-md\ocr_dijkstra.py`.

## 2. Distill the method card
The workflow that built this skill distills each book into a card: essence,
techniques (name/what/when), TRIZ mapping, ponytail mapping, capability,
prerequisites, readingNotes. For a new book, ask Claude to "distill
`CodingBooks-md/<book>.md` into a method card" — or re-run the distillation
workflow with the new file added.

## 3. Render the reference file
Add (or merge) the card into a `references/*.md` file in the triz reference
style (operational tables, bracket-tagged rules, worked example, how-it-feeds-
the-pipeline). Merge targets:
- **DDIA** → DONE (2026-08-02): new `references/data-systems.md`, unblocked the
  curriculum's data-heavy fork (step 7 fork B).
- **Algorithm Design Manual** → merge into `references/algorithm-strategies.md`
- **Refactoring** → merge the catalog into `references/red-flags.md` +
  `references/construction-checklist.md`

Update the reference index in `SKILL.md` and the curriculum table when you do.

## 4. Update the curriculum
Flip the step's status from ❌ to ✅ in `curriculum/README.md` and fill in the
real reading path from the card's `readingNotes`.

## 5. Test
`python -m unittest discover -s tests -p "test_*.py"` must stay green (the
curriculum test asserts every step is either startable today or marked missing
with an unblock path).
