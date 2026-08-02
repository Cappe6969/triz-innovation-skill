# TRIZ Cases

Saved TRIZ analyses. Each case = one real problem run through the full pipeline,
kept so it can be reused, audited, and learned from.

## How to create a case
Option A — script (recommended):
```
python skills/triz-coding-method/engine/scripts/triz_case_template.py "Reminder fatigue in physio app" --output-dir ./my-cases
```
This writes a date-stamped, slugified file like
`cases/2026-06-13-reminder-fatigue-in-physio-app.md` pre-filled from
`template-triz-case.md`.

Option B — manual: copy `template-triz-case.md`, rename it, fill it in.

## Naming convention
`YYYY-MM-DD-short-kebab-title.md` — the script does this automatically.

## What goes in a case
Fill every heading in the template as you run stages 1–10 of the skill. A good
case always ends with a concrete experiment (success/failure criterion as a
number) and, later, the **Risultati** and **Follow-up** sections updated after
you actually ran the test.

## Files here
- `template-triz-case.md` — the blank template (do not delete; the script reads it).
- `README.md` — this file.
- `YYYY-MM-DD-*.md` — your saved cases.
