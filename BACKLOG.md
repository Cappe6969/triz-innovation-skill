# BACKLOG

Deferred Medium/Low findings from the ship builds. Reviewed with the user during
Phase 4 (2026-08-02).

## Open

- [Low] `.claude/skills/triz-innovation/scripts/triz_router.py:187` — Engineering contradiction label via `_short_label(text, 40)` truncates to the first 40 characters before the contradiction connector, producing near-meaningless partial fragments (e.g. "Ho un'app di fisioterapia che deve…" instead of a meaningful subject like "app notifications"). (round 1) → Improve the label-extraction heuristic: walk backward from the connector to the nearest noun phrase, or use the last N words before the connector instead of the raw prefix.

- [Low] `.claude/skills/triz-innovation/scripts/triz_router.py:25` — The keyword `"but "` (with trailing space) won't match "but," or "but." — only "but " followed by another word. Contradiction detection is unaffected (it uses bare "but"). (round 1) → Add bare "but" / "ma" to the RULES keywords, or use a regex word-boundary match for connector keywords.

- [Medium] `cases/2026-06-14-ariz-test-problem.md`, `cases/2026-06-14-smoke-test-case.md`, `reddit-post.md` — untracked working-tree files. The round-1 finding flagged them as out of scope for a build; they were never added to any merged build. (round 1) → Decide their fate: commit deliberately, move to `docs/`, or delete. User has not yet chosen.

- [Medium] `tests/test_triz.py:345` — Dispatcher tests check return codes only; they omit required output assertions, non-empty effects/network output checks, and the missing-subtool failure path. (round 1) → Capture output and add marker, non-empty-output, and empty-script-directory assertions.

- [Medium] `tests/test_triz.py:572` — Router label tests check format and length but not that label halves contain whole words, leaving the key mid-word-split regression uncovered. (round 1) → Assert whole-word tokens for both Italian label halves and the ASCII-ellipsis constraint.

- [Medium] `tests/test_triz.py:693` — Evaluator coverage omits BOM handling, short-row validation, and clean stderr assertions for invalid/missing files. (round 1) → Add UTF-8-BOM, missing-field, and captured-stderr regression tests.

- [Medium] `tests/test_triz.py:760` — Matrix and catalog tests don't verify exact (18,35) principles, can silently skip the empty-cell case, and omit list-all output, variant-count, complete-entry, and missing-template checks. (round 1) → Assert exact expected values, fail when fixtures are absent, and add the missing catalog/template tests.

## Resolved (closed in later builds)

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
