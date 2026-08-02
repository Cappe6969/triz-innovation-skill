# Phase 5: Close all 7 OPEN BACKLOG items — regression-test coverage + router/evaluator/catalog hardening

## Goal

Close every open item in `BACKLOG.md` by (a) confirming the three already-fixed
code items (router label heuristic, `"but "` word-boundary keyword, untracked
files cleanup) and locking them in with regression tests, and (b) filling the
four test-coverage gaps (dispatcher output assertions, router whole-word label
assertions, evaluator BOM/short-row/stderr assertions, matrix + standard-
solutions catalog exact-value assertions). No behavioral change to any script's
public functions is required — this build is tests + BACKLOG/docs updates only.

## Context (verified facts, current master `1af5bde`)

- Router EC-label extraction already uses the last 3 whole words before the
  connector (`_subject_words(before_raw, 3, from_end=True)` in
  `.claude/skills/triz-innovation/scripts/triz_router.py`) and never emits a
  mid-word split (the 40-char truncation drops the partial token via
  `rsplit(" ", 1)[0]`). Live output for the physio example:
  `improve [per gli esercizi] / worsens [le notifiche li]`.
- Router contradiction-connector keywords are bare whole words (`"but"`, `"ma"`,
  …) matched with `\b` word boundaries, so `but,`/`but.` already match.
- The three untracked files (`cases/2026-06-14-ariz-test-problem.md`,
  `cases/2026-06-14-smoke-test-case.md`, `reddit-post.md`) no longer exist on
  disk; `git status` is clean.
- Exact values for the new assertions (live-verified):
  - `triz_matrix.lookup(18, 35)` → principle ids exactly `[15, 1, 19]` in order,
    names Dynamization, Segmentation, Periodic Action.
  - `triz_matrix.lookup(27, 25)` → `[10, 30, 4]` (already asserted in
    `test_master_matrix_27_25`).
  - Parameters CSV: `18 → "Illumination intensity"`, `35 → "Adaptability or versatility"`.
  - `triz_standard_solutions.load_solutions_db()`: 76 base solutions, **11
    variants**, 87 total; every entry has non-empty `name` and `mechanism`.
  - `triz_standard_solutions._print_list_all()` prints
    `Total: 76 standard solutions` and `       + 11 variant(s)`.
  - `triz_evaluator._parse_csv` opens with `encoding="utf-8-sig"` (BOM-tolerant)
    and, for a short row, prints `Error: row N: missing value for column(s): …`
    to stderr then `sys.exit(1)`.
  - Dispatcher tests live in `tests/test_triz.py`; the CLI-output assertion
    pattern is `subprocess.run([sys.executable, <script>, …], capture_output=True)`
    (e.g. `test_dispatcher_lang_it_route`), because `triz.dispatch` forwards to
    subprocesses that write to the real stdout fd.

## Requirements

### R1 — Router whole-word label regression tests (closes BACKLOG items A + E)

In `tests/test_triz.py`, extend router EC-label coverage. For the existing
Italian physio input AND a new long-word English input:

- Both label halves are ≤ 40 chars and contain **no mid-word split**: every
  whitespace-separated token in each half must be a complete word (reconstructable
  from the source sentence's words — a truncated fragment is never a whole word).
- The physio label must NOT start with a raw 40-char prefix like
  `improve [Ho un'app di` (the old regression). Assert it uses the last words
  before the connector, e.g. the label contains `per gli esercizi`.
- Long-word English input (subject words exceed 40 chars combined), e.g.
  `"the supercalifragilisticexpialidocious gearbox must transmit more torque but
  the housing cannot grow heavier"` → neither half contains a token that is a
  mid-word slice of a source word.
- Keep asserting the ASCII-ellipsis constraint: the EC label contains no `…`
  (the existing `self.assertNotIn("…", ec)` pattern).

Concrete assertion helper (allowed): parse the two halves out of
`improve [X] / worsens [Y]`, split each into tokens, and for each token assert
it is a substring of some whole word in the (tokenized) source sentence — this
fails on both a mid-word slice and on `…`.

### R2 — Dispatcher output assertions + missing-subtool path (closes item D)

Add subprocess-based tests (capture_output pattern) asserting non-empty,
marker-bearing output, not just exit codes:

- `triz.py route "more speed but less reliability"` → rc 0, stdout contains
  `Engineering Contradiction` and `40 Inventive Principles`.
- `triz.py effects --keyword magnetic` → rc 0, stdout non-empty.
- `triz.py network --demo` → rc 0, stdout non-empty.
- Missing-subtool failure path (unit level): with
  `unittest.mock.patch("triz._SCRIPT_DIR", <temp dir with no scripts>)`,
  `triz.dispatch(["matrix", "1", "2"])` returns `1` and writes `Sub-tool not
  found` to stderr (capture with `contextlib.redirect_stderr`).

### R3 — Evaluator BOM / short-row / clean-stderr tests (closes item F)

- **UTF-8 BOM**: write a solutions CSV with a `﻿` BOM prefix before the
  header row; `triz_evaluator._parse_csv` must parse it and `score` must total
  correctly (proves `utf-8-sig` handling).
- **Short-row validation**: a CSV whose second data row has fewer columns than
  the header → `_parse_csv` raises `SystemExit(1)`; captured stderr contains
  `missing value` and no `Traceback`.
- **Clean stderr for invalid/missing files**: for a missing file and for a
  wrong-header CSV, captured stderr contains `Error:` and no `Traceback`, and
  nothing is written to stdout.

### R4 — Matrix + catalog exact-value and coverage tests (closes item G)

- **Exact (18,35)**: `lookup(18, 35)` returns principle ids exactly
  `[15, 1, 19]` in order with names Dynamization, Segmentation, Periodic Action.
- **Fixtures present**: assert the three data CSVs exist under
  `.claude/skills/triz-innovation/scripts/data/` (`contradiction_matrix.csv`,
  `parameters_39.csv`, `inventive_principles.csv`) — fail loudly if absent.
- **`matrix --list` output**: subprocess `triz.py matrix --list` → rc 0, stdout
  has 39 parameter lines and contains `18  Illumination intensity` and
  `35  Adaptability or versatility`.
- **Standard-solutions `--list-all`**: subprocess
  `triz_standard_solutions.py --list-all` → rc 0, stdout contains
  `Total: 76 standard solutions` and `+ 11 variant(s)`.
- **Variant-count**: `_iter_solutions(load_solutions_db())` → exactly 11 entries
  with `parent_id`, 76 without, 87 total.
- **Complete-entry**: every one of the 87 entries has non-empty `id`, `name`,
  `description`, `mechanism`, `subfield_state`, `class_id`, `group_id`; each
  variant's `parent_id` resolves to an existing base id.
- **Missing-template**: `triz_case_template.create_case` raises
  `FileNotFoundError` when the template is absent — implement by patching
  `triz_case_template._template_path` (via `unittest.mock.patch`) to return a
  nonexistent path, then assert `FileNotFoundError`.

### R5 — BACKLOG.md closure

Rewrite `BACKLOG.md`: move all 7 items (router label truncation, `"but "`
keyword, untracked files, dispatcher tests, router label tests, evaluator tests,
matrix/catalog tests) into **Resolved**, each with this build's commit reference
and a one-line note of what closed it (code already fixed + regression test, or
test added). The **Open** section states explicitly that no open items remain.

### R6 — Docs + mirror sync

- `docs/usage-guide.md` / `docs/source-map.md`: update only if the build changed
  documented behavior (expected: no change needed).
- Rebuild the `.agents` mirror via `scripts/build_mirror.py` so
  `build_mirror.py --check` exits 0.
- Full suite via `python -m unittest discover -s tests -p "test_triz.py"` must
  report `OK` with the previous 114 tests plus the new ones.

## Acceptance criteria

- **AC1**: Full suite passes (`Ran N tests … OK`), N = 114 + number added.
- **AC2**: The R1 tests genuinely guard the fix — if the physio label were the
  raw prefix `improve [Ho un'app di fisioterapia]` or contained a mid-word
  token, at least one new test fails.
- **AC3**: R2 tests assert non-empty marker output for `route`, `effects`,
  `network`, and rc=1 + `Sub-tool not found` for the missing-subtool path.
- **AC4**: R3 tests pass with BOM, short-row, and invalid/missing-file inputs,
  asserting clean stderr (no `Traceback`).
- **AC5**: R4 tests assert exact (18,35) ids/names, fixture presence, `matrix
  --list` (39 lines + the two named rows), `--list-all` totals, 11-variant
  count, complete 87-entry shape, and the case-template `FileNotFoundError`.
- **AC6**: `python scripts/build_mirror.py --check` exits 0 (mirror in sync).
- **AC7**: `BACKLOG.md` has all 7 items in Resolved with this build's commit
  reference and an empty Open section.
- **AC8**: No behavioral change to any script's public functions; the only
  source edits are additions to `tests/test_triz.py`, `BACKLOG.md`, and the two
  doc files if needed.

## Out of scope

- Any change to `Books/`, `triz-prompt-engineering-main/`, `TRIZ-MASTER.md`,
  the branch JSONs, `references/*.md` (use-cases included), SKILL.md.
- Merging — handled after this build passes and the user approves the diff.
