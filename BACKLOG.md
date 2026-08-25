# BACKLOG

Deferred Medium/Low findings from the ship builds. Reviewed with the user during
Phase 4 (2026-08-02). All seven remaining open items were closed in Phase 5
(2026-08-02) — this build is tests + BACKLOG/docs updates only.

## Open

The seven Phase 1–4 TRIZ items are closed (see Resolved below). The items below
are deferred from the **coding-method** skill build (Phase: Lazy Ideality,
branch `swarm/coding-method-skill`) and from the gauntlet improvement loop.
Reviewed with the user at the merge approval.

- [Low] **Two curriculum source materials not yet on disk** — the
  algorithm-strategy catalog (step 2) and safe refactoring (step 4) are marked
  `available: false` in `curriculum/README.md` with interim substitutes from the
  already-distilled cards. The data-system card is DONE (2026-08-02). Unblock:
  drop the source material into `CodingBooks-md/` and re-distill — the strategy
  source merges into `references/algorithm-strategies.md`, the refactoring
  source into `references/red-flags.md` + `references/construction-checklist.md`
  (see `curriculum/how-to-add-book.md`).
- [Low] **Contract-first verification source — OCR pending** — the source
  material still needs conversion before its content can be distilled into a
  reference file. No placeholder in the curriculum; candidate merge target is
  `references/design-recipe.md` (contract-first / weakest-precondition
  verification). Unblock: drop a converted (OCR'd / text) copy of the source
  into `CodingBooks-md/` and re-distill it the same way as the other coding-
  method sources (see `curriculum/how-to-add-book.md`) — the distilled content
  merges into `references/design-recipe.md`.
- [Low] **Four sub-tools lack the Windows-safe stdout guard** —
  `triz_ariz.py`, `triz_contradiction_network.py`, `triz_matrix.py`, and
  `triz_standard_solutions.py` (all under `.claude/skills/triz-innovation/scripts/`)
  never reconfigure stdout to UTF-8/errors=replace, unlike the other seven
  scripts. Latent only as of 2026-08-25: every string they print is
  cp1252-safe (verified by scanning all printed CSV/JSON data). Unblock:
  add a non-cp1252 character to any data file these tools print, or fold
  the standard reconfigure guard in opportunistically during a future build.

## Resolved

### 2026-08-02 — data-system card added to the coding-method skill (`references/data-systems.md`)

- [Low] **`references/data-systems.md` was a forward-reference** — `method-map.md`
  ("Data-heavy system decision" row) and the `data-heavy` signal in
  `scripts/method.py` pointed at a future file (from the data-system work). →
  Resolved: the data-system source distilled into `references/data-systems.md`
  (2026-08-02); the FUTURE markers were dropped from `method-map.md`, and the
  `data-heavy` signal now loads the real reference. Curriculum step-7 fork B
  flipped to ✅ available.

### Phase 5 — all 7 open items closed (commits `9056842` tests + `abc4b04` BACKLOG/SPEC)

- [Low] `.claude/skills/triz-innovation/scripts/triz_router.py:187` — engineering-contradiction label via `_short_label(text, 40)` truncated to the first 40 chars before the connector, producing partial fragments (e.g. "Ho un'app di fisioterapia che deve…"). → Resolved in Phase 5: the label heuristic already walks the last whole words before the connector (`_subject_words(before_raw, 3, from_end=True)`), so the label is now whole-word (e.g. `improve [per gli esercizi]`); locked in with whole-word regression tests (`test_router_physio_ec_label_whole_words`, `test_router_long_word_english_ec_label_whole_words`).
- [Low] `.claude/skills/triz-innovation/scripts/triz_router.py:25` — the keyword `"but "` (trailing space) would miss `"but,"`/`"but."`. → Resolved in Phase 5: connector keywords are bare whole words matched with `\b` word boundaries, so punctuation-adjacent connectors already match; covered by `test_router_punctuation_adjacent_connectors`.
- [Medium] `cases/2026-06-14-ariz-test-problem.md`, `cases/2026-06-14-smoke-test-case.md`, `reddit-post.md` — untracked working-tree files. → Resolved in Phase 5: the files no longer exist on disk and `git status` is clean.
- [Medium] `tests/test_triz.py:345` — dispatcher tests checked return codes only. → Resolved in Phase 5: subprocess output assertions added for `route` (markers `Engineering Contradiction` / `40 Inventive Principles`), `effects --keyword magnetic` and `network --demo` (non-empty stdout), plus the missing-subtool failure path (rc 1 + `Sub-tool not found` on stderr).
- [Medium] `tests/test_triz.py:572` — router label tests checked format/length but not whole words. → Resolved in Phase 5: whole-word / no-mid-word-split assertions added for the Italian physio label and a long-word English input, keeping the ASCII-ellipsis (`…`) constraint.
- [Medium] `tests/test_triz.py:693` — evaluator coverage omitted BOM handling, short-row validation, and clean-stderr assertions. → Resolved in Phase 5: UTF-8-BOM parse-and-score, short-row `missing value` (SystemExit 1), and `Error:`-with-no-Traceback + empty-stdout tests added.
- [Medium] `tests/test_triz.py:760` — matrix/catalog tests omitted exact values and coverage. → Resolved in Phase 5: exact (18,35) `[15, 1, 19]` ids/names, fixture-presence (fail loud), `matrix --list` output (39 lines + rows 18/35), `--list-all` totals, 11-variant count, complete 87-entry shape, and case-template `FileNotFoundError` tests added.

### Earlier phases (kept for provenance)

- [Medium] `Books/` copyrighted full-text books in the repo — resolved: removed from git (commit `f87685a`) and gitignored; on-disk copies are untracked.
- [Medium] `.agents/skills/triz-innovation/SKILL.md` references missing — resolved in Phase 2: mirror rebuilt self-contained via `scripts/build_mirror.py` (copies `references/`, `scripts/`, `branches/`, rewrites `.claude/` → `.agents/`).
- [Medium] TRIZ-MASTER §6 missing `**Procedure:**` — resolved in Phase 2 (R8 fix 2).
- [Low] TRIZ-MASTER TOC as extra H2 — resolved in Phase 2 (R8 fix 1, demoted to H3).
- [Medium] TRIZ-MASTER evaluation omits scoring direction — resolved in Phase 4: §9 now states "Cost/risk/complexity: 5 = cheap/safe/simple" and "sort by total".
- [Medium] TRIZ-MASTER §3/§10/§11 missing output contracts — resolved in Phase 2 (R8 fix 8).
- [Medium] TRIZ-MASTER §13 ARIZ TC-selection — resolved in Phase 2 (R8 fix 6).
- [Low] TRIZ-MASTER §17 SLP router keywords — resolved in Phase 2 (R8 fix 7).
- [Low] `commit-and-push.cmd` deletion — resolved: user chose to leave it deleted.
- [Low] `branches resolve --lang` not forwarded by dispatcher — resolved in Phase 2: `_FLAG_CONSUMERS` forwards `--lang` to `branches`; `triz_branches.py` accepts the flag at any position.
