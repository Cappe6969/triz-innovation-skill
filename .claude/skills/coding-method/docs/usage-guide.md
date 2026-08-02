# Usage Guide — `coding-method`

How to use the coding-method skill in Claude Code, invoke it manually, add
references, save cases, and run the scripts.

## 1. Using the skill in Claude Code
The skill auto-triggers when you describe a coding problem with a real decision:
a non-obvious solution, a trade-off ("I need X but that breaks Y"), a choice
between approaches, legacy code that must not break, a complexity review, or a
minimal-fix request (see the `description` in
`.claude/skills/coding-method/SKILL.md`).

Just describe the problem naturally, e.g.:
> "Use the coding method: my sync worker polls the DB every 5 seconds, but that
> wastes queries and the data is stale anyway."

Claude will run the 8-stage pipeline and end with a test that proves the change.

### Invoking it manually / forcing it
- Be explicit: start your message with **"Run the coding-method skill on: …"**
- Or follow `.claude/skills/coding-method/SKILL.md` for this problem.
- To go deep on one technique, ask Claude to read the specific reference, e.g.
  *"Read `references/legacy-change.md` and apply it here."*

## 2. The pipeline (what you'll get)
1. Frame the task → 2. Climb the ponytail ladder → 3. Sketch the IFR →
4. Structure from data → 5. Resolve contradictions → 6. Make the minimal safe
change → 7. Review with red flags → 8. Verify, record, ship (mandatory test
close). Intensity levels: `lite` (1–3), `full` (all 8), `ultra` (+ proof pass).

## 3. Adding new references
1. Create `references/<topic>.md` under `.claude/skills/coding-method/`.
2. Keep it **operational**: checklists, tables, procedures — not essays.
3. Add a row to the **Reference index** table in `SKILL.md`.
4. If it changes routing, add keyword cues to `references/method-map.md` (and
   the router script).
5. New source material? Follow `curriculum/how-to-add-book.md`.

## 4. Saving coding-method cases
Mirror the triz-innovation case flow: keep a filled template in `cases/`, fill
each stage as you work, and after running the experiment update the result and
follow-up. See the canned cases in `cases/` as worked examples.

## 5. Using the Python scripts
All scripts are plain-stdlib MVPs (no install needed; Python 3.8+).

**Dispatcher — one entrypoint:**
```
python .claude/skills/coding-method/scripts/method.py route "the API must be fast, but caching makes it inconsistent"
```
`method.py` returns a stage plan: which stages to emphasize, which references to
load, code-side TRIZ hints, and the cross-invoked matrix command. Other
commands: `stages`, `stage <n>`, `ladder "<task>"`, `redflags [<file>]`,
`references`, `triz <improving> <worsening>` (cross-invokes
`triz-innovation/scripts/triz_matrix.py`). Run with no args for the full list.

**Ponytail ladder + IFR:**
```
python .claude/skills/coding-method/scripts/ladder.py "parse the json and sort the dates"
```
Prints the cheapest rung that likely works (stdlib/existing-dep/…) and the IFR
statement to aim at.

**Red-flag review:**
```
python .claude/skills/coding-method/scripts/redflags.py            # checklist
python .claude/skills/coding-method/scripts/redflags.py <file>     # checklist + scan
```
Scans for mechanically-detectable smells (6+ params, long lines, TODO markers,
long functions, deep nesting).

### Cross-invoking the TRIZ engine
The contradiction stage is the real triz-innovation engine, never a copy:
`python .claude/skills/coding-method/scripts/method.py triz <imp> <wor>`
forwards to `triz-innovation/scripts/triz_matrix.py`. The same applies to
`triz_router.py` (first-guess methods) and `triz_standard_solutions.py` /
`triz_evolution.py` for the escalation path.

## 6. Curriculum
`curriculum/README.md` is the 7-step learning path in the recommended order
(data-first discipline → algorithm strategy → design judgment → safe refactoring
→ legacy-change safety → reasoning engine → final fork). The data-systems card
is now available (distilled into `references/data-systems.md`, the data-heavy
fork). Two steps remain marked ❌ **da aggiungere**; each has an interim
substitute. `how-to-add-book.md` documents the convert → distill → render →
test flow.

## 7. Relationship to triz-innovation
Both skills live in `.claude/skills/`. `triz-innovation` solves *any* problem
(software included) with pure TRIZ; `coding-method` is the *coding-specific*
merge of TRIZ + ponytail + the method catalog. Point any agent at
`.claude/skills/coding-method/` — no mirror exists; `triz-for-code.md` is the
one-way bridge to the TRIZ engine.
