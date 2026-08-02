# Implementation Notes — coding-method

Design decisions and architecture for the `coding-method` skill. Read this
before extending it.

## Goals
- One coding problem-solving method from three sources: **ponytail** (the lazy
  default), **TRIZ** (the stuck-state engine), and the **distilled methods of
  classic programming books** (the standard-moves catalog).
- Reaches the **Ideal Final Result of the code** — the behavior with the least
  code that stays least code next month.
- **No duplication of triz-innovation**: the TRIZ engine is cross-invoked, not
  copied.
- Original operational synthesis from the source books — **no book text copied**,
  books are gitignored (`CodingBooks/`, `CodingBooks-md/`).

## Architecture
```
.claude/skills/coding-method/
  SKILL.md            # core: triggers + operating rules + 8-stage pipeline + reference index
  references/*.md     # 15 method notes (progressive disclosure)
  scripts/*.py        # stdlib MVP helpers (method.py, ladder.py, redflags.py)
  curriculum/         # 7-step reading path + how-to-add-book
  cases/              # canned pipeline runs
  docs/               # this file + usage-guide
```

## Key decisions
1. **Progressive disclosure.** `SKILL.md` stays short and always loaded; deep
   method content lives in `references/` and is read only when a stage needs it.
2. **Lazy Ideality is one method, not a mashup.** Ponytail decides *what to
   build* (skip everything unneeded); the books decide *how the thing hides its
   complexity* (deep modules, seams, strategy catalogs); TRIZ dissolves the
   *contradiction* when the catalog can't reach the one-liner. IFR is the
   generation north-star; trade-off analysis is the evaluation instrument.
3. **No TRIZ duplication.** `triz-for-code.md` maps TRIZ→code; the actual engine
   (`triz_matrix.py`, `triz_router.py`, `triz_standard_solutions.py`,
   `triz_evolution.py`, `software-triz.md`, `branches/fields/software`) lives in
   `.claude/skills/triz-innovation/` and is cross-invoked by path.
4. **Cards → references.** The 15 reference files were rendered from 13
   distilled book cards (produced by a design workflow over the converted books
   in `CodingBooks-md`). Merges: `algorithm-strategies.md` (Levitin + SICP),
   `red-flags.md` (Ousterhout + Code Complete + Dooley),
   `construction-checklist.md` (Code Complete + Dooley). The two cross-cutting
   files (`method-map.md`, `triz-for-code.md`) were authored directly.
5. **Scripts are heuristic MVPs.** `method.py route` is keyword/intent-based
   (first guess, not verdict); `ladder.py` maps keywords to ladder rungs;
   `redflags.py` scans for mechanically-detectable smells. No external deps,
   Python 3.8+.

## Script contracts (so MCP wrapping is trivial later)
- `method.route(task: str) -> dict` — stage plan with signals + TRIZ hints
- `ladder.suggest_rung(task: str) -> dict` — {rung, why, ifr, almost_ifr}
- `redflags.scan(file_path: str|None) -> dict` — {summary, checklist, findings}

## Extension points
- New book → `how-to-add-book.md`: convert → distill → render → update index +
  curriculum. Planned: Algorithm Design Manual → `algorithm-strategies.md`;
  Refactoring → `red-flags.md`/`construction-checklist.md`; DDIA →
  `data-systems.md`.
- New reference → `references/<topic>.md` + a row in SKILL.md's reference index.
- New script → importable core + `__main__` guard.

## Known limitations
- Router is keyword-based; it can misroute paraphrased tasks — it's a first
  guess, the skill still reasons. Improve with more cues, not a model.
- `redflags.py` detects only the mechanically-visible smells; the deep ones
  (shallow module, information leakage) still need human judgment.
- The 3 missing books are marked in the curriculum with interim substitutes;
  DDIA blocks only the data-heavy fork.
- Books in `CodingBooks-md` are copyrighted — never commit them.
