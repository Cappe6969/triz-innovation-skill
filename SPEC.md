# Harden the TRIZ algorithm: word-boundary routing, evaluator contract, regression suite

## Context

An independent audit (8 specialist auditors, every claim verified by running the
code) found real bugs in the `triz-innovation` skill's scripts and data. This
build fixes **all verified algorithm defects** and adds the **regression tests**
that would have caught them. It is the foundation phase: later builds add the
branch architecture and new-domain/use-case content on top of this hardened core.

Every fix below is **verified present-and-broken in the current code**; every
acceptance criterion is objectively checkable by running the code.

## Files to modify

1. `.claude/skills/triz-innovation/scripts/triz_router.py`
2. `.claude/skills/triz-innovation/scripts/triz_evaluator.py`
3. `.claude/skills/triz-innovation/scripts/triz_matrix.py`
4. `.claude/skills/triz-innovation/scripts/data/contradiction_matrix.csv`
5. `.claude/skills/triz-innovation/scripts/triz_standard_solutions.py`
6. `.claude/skills/triz-innovation/scripts/triz_evolution.py`
7. `.claude/skills/triz-innovation/scripts/triz_contradiction_network.py`
8. `.claude/skills/triz-innovation/scripts/triz.py`
9. `.claude/skills/triz-innovation/scripts/triz_case_template.py`
10. `tests/test_triz.py`

## Requirements

### R1. Router — word-boundary keyword matching (kills the substring false-positive class)

The router matches keywords with raw substring containment, so a 2–3-letter
keyword fires inside unrelated words. Verified examples:

- `"ma"` matches inside `sistema`, `macchina`, `programma` → benign Italian
  sentences fabricate an Engineering Contradiction (10/10 benign sentences tested).
- `"but"` matches inside `button`, `debut`, `rebuttal`.
- `"ui"` matches inside `circuit` → misroutes hardware problems to Software TRIZ.
- `"on"`/`"off"` (physical pair) match inside `only`/`office`.

**Requirement:** Rewrite keyword matching so every keyword is matched with
`\b` word boundaries: `re.search(rf"\b{re.escape(kw)}\b", lower_text)`.

- Canonicalize the keyword tables so each keyword is a bare whole word or whole
  phrase. **Drop** the redundant space/punctuation variants (e.g. `"but "`,
  `" but "`, `"but,"`, `"but."` → just `"but"`; `"ma "`, `" ma "`, `"ma,"`,
  `"ma."` → just `"ma"`). Word-boundary matching already handles punctuation
  adjacency, so the variants are unnecessary.
- Apply word-boundary matching uniformly to: the `RULES` table keywords,
  `_CONTRADICTION_CONNECTORS`, and the `_PHYSICAL_TOPICS` pairs.
- Keep the existing scoring model (per-rule weight accumulates per matched
  keyword, capped at 10 per method). De-duplicating the keyword tables makes the
  double-count disappear naturally.
- Multi-word phrases (e.g. `"at the cost of"`, `"must be both"`, `"diminishing
  returns"`) work correctly with the same `\b...\b` pattern because `\b` is the
  word/non-word boundary at the phrase edges.

### R2. Router — fix engineering-contradiction label extraction

`_short_label(text, 40)` takes a raw 40-char prefix, producing meaningless
fragments. Verified:

- `"Il sistema non risponde."` → `improve [Il siste] / worsens [non risponde.]`
- The physio example → `improve [Ho un'app di fisioterapia che deve…] / worsens [le notifiche li infastidiscono e…]`

The connector loop also finds the FIRST substring occurrence with no
word-boundary check, so a real connector like `però` can be hijacked by an
earlier `ma` substring inside a word.

**Requirement:** Rewrite `_detect_engineering_contradiction` to:

1. Find connectors with the word-boundary matcher (never inside a word).
2. For the chosen connector, extract the **nearest noun-phrase subject**: the
   last 2–3 words before the connector and the first 2–3 words after it (whole
   words only, never split mid-word).
3. Build the label as `improve [before-subject] / worsens [after-subject]`.
4. If there is no valid pre-connector subject (connector at start of text, or
   nothing useful before it), return a plain `trade-off near: <short whole-word
   text>` fallback — **do NOT** emit the misleading `improve [...] / worsens
   [...]` framing.
5. Replace the `U+2026 …` ellipsis with ASCII `...`.

The label halves must be short (each ≤ 40 characters), consist of whole words,
and never contain a mid-word split or a `…` character.

### R3. Router — physical-contradiction detection

Two verified defects:

- The `"must be" / "deve essere" / "dovrebbe"` fallback is gated on `has_but`,
  so connector-less physical contradictions are never labeled.
- `_PHYSICAL_TOPICS` is a closed ~19-pair set. Verified misses:
  `"The window must be both transparent and opaque."` and
  `"Il pezzo deve essere rigido e flessibile."` return
  `physical_contradiction=None` even though the method scores high — an
  internal inconsistency.

**Requirement:**

1. **Drop the `has_but` gate** on the must-be fallback.
2. **Expand `_PHYSICAL_TOPICS`** with at least: `rigid/flexible`
   (`rigido/flessibile`), `transparent/opaque` (`trasparente/opaco`),
   `thick/thin` (`spesso/sottile`), `dense/sparse` (`denso/rado`),
   `precise/imprecise` (`preciso/impreciso`), `cheap/expensive`
   (`economico/costoso`), plus the existing pairs.
3. Match every pair word with `\b` boundaries.
4. Keep the annoyance/notification heuristic (`must be present (useful) and
   absent (avoids annoyance)`).

### R4. Router — Italian keyword coverage, Python-version claim, ASCII ellipsis

**Italian domain keywords missing** (verified: these natural sentences fire only
the 5 default fallbacks at score 0):

- Business: `vendita`, `costo`, `margine`, `utenti`, `fidelizzazione`
- Software: `sito`, `web`, `pagina`, `login`, `accesso`, `caricamento`, `dati`,
  `errore`, `connessione`
- Rehab: `dolore`, `movimento`, `muscolo`, `ginocchio`, `schiena`,
  `allenamento`, `protocollo`
- Workflow/task: `attività`, `task`, `compito`, `passaggio`, `ritardo`, `attesa`

Add these to the matching domain rules in `RULES` (word-boundary matched).

**Python-version claim:** module and test docstrings say `Standard library only —
Python 3.8+`, but the code uses PEP 604 `X | None` (3.10) and PEP 585 builtin
generics (3.9) with no `from __future__ import annotations`, so it raises
`TypeError` on 3.8/3.9. Add `from __future__ import annotations` as the first
import in **every** `.py` under `scripts/` and in `tests/test_triz.py` so the
3.8+ claim is true. (This also fixes module-level annotations like
`RULES: list[tuple[...]]`.)

**ASCII ellipsis:** replace all `U+2026 …` occurrences in `triz_router.py`
with ASCII `...`.

### R5. Evaluator — canonical criteria contract + validation + clean errors + UTF-8 stdout

**Header contract bug (THE most-blocking, reported by 3 of 8 auditors):**
`triz_evaluator.py` `CRITERIA` is
`[impact, feasibility, affordability, speed, safety, reversibility, simplicity,
ideality]`, but **every** other source — `SKILL.md` stage 9, `TRIZ-MASTER.md`
§21, `docs/usage-guide.md`, the Italian case template, and all 4 worked examples
— documents `cost/risk/complexity`. A CSV built from the documented headers
exits 1 with `Error: unexpected CSV header`. The documented workflow is broken.

**Requirement (decision: rename + accept aliases):**

1. Rename canonical `CRITERIA` to
   `["impact", "feasibility", "cost", "speed", "risk", "reversibility",
   "complexity", "ideality"]`.
2. Accept the old names as **aliases** in `_parse_csv`:
   `affordability → cost`, `safety → risk`, `simplicity → complexity`
   (case-insensitive). A CSV using either header convention parses and scores
   identically.
3. Update `_SAMPLE_DATA`, `format_table` headers, `_print_help`, and the module
   docstring to the canonical names.
4. `_parse_csv`: open with `encoding="utf-8-sig"` so an Excel-exported UTF-8 BOM
   header parses; normalize header names through the alias map before the
   exact-match check; on mismatch print a clean error to stderr and `sys.exit(1)`.
5. Missing/invalid CSV file → clean error message, `sys.exit(1)`, **no raw
   traceback**.
6. Rows with fewer fields than the header → per-row clear error
   (`row N: missing value for column X`), `sys.exit(1)`; no `AttributeError`.
7. `score()` must validate: raise `ValueError` when a criterion is missing or
   not an int in 1..5 (matching `_parse_csv`), so the exported API and CSV path
   agree. Share one validation helper between both paths.
8. Make CLI stdout UTF-8-safe (see R12).

### R6. Matrix — data fix + type validation

1. **Data bug:** `data/contradiction_matrix.csv` line 558 is
   `18,35,15;1;1;19` — principle id 1 (Segmentation) appears twice.
   `triz_matrix.lookup(18, 35)` returns two identical Segmentation entries. The
   canonical Altshuller matrix lists (18,35) as `[1, 15, 19]`. Fix the cell to
   `18,35,15;1;19`. This is the only mismatching cell of 1248.
2. **Type validation:** `lookup(True, 2)` succeeds (bool is an `int`) and
   `lookup(14.5, 2)` is accepted by the range check then crashes with an
   uncaught `KeyError`. Reject any non-`int` (including `bool`) argument with a
   `ValueError` before the range check: require
   `isinstance(x, int) and not isinstance(x, bool)` and `1 <= x <= 39`.

### R7. Standard-solutions — variant mechanism + count consistency

1. **Variant mechanism:** `lookup_solution("5.1.1.7")` (a variant of `5.1.1`)
   returns `mechanism=None`; `--solution 5.1.1.7` prints an empty
   `Mechanism:` line. Fix: when a variant has no own `mechanism`, inherit the
   parent's mechanism, or omit the line entirely when empty. Prefer inheritance
   (keeps output informative).
2. **Count consistency:** `--list-all` prints `Total: 87 solutions listed.`
   (76 base + 11 variants) but the DB meta, docstrings, and skill all say 76.
   Fix: print `Total: 76 standard solutions` with a separate
   `+ 11 variant(s)` line.

### R8. Evolution — word-boundary cue matching + tie-break note

1. **Substring cue bugs (verified):**
   - `"premature aging"` → Maturity (cue `mature` inside `premature`)
   - `"pocket tool"` → Infancy (cue `poc` inside `pocket`)
   - `"nearly done"` → Infancy (cue `early` inside `nearly`)
   Match cues with `\b` word boundaries (whole-token match), not substring.
2. **Tie-break note:** when the chosen stage wins only on the
   `(count, stage)` tie-break (not on count alone), append to the `why` string
   something like `(tie broken toward the later stage)`.

### R9. Network — input validation + ordering semantics

1. **Uncaught KeyError (verified):** `find_conflicts()` looks up
   `param_names[pid]` on any parameter in a conflict group; an invalid id
   (e.g. 99) shared by two contradictions crashes with
   `KeyError: KeyError(99)`. Validate that every `improving`/`worsening` value
   in `analyze_network`/`_run_analyze`/`add_contradiction` is an `int` (not
   `bool`) in 1..39, raising `ValueError` with a clear message before any
   parameter-name lookup. Mirror the matrix validation (R6.2).
2. **`connected_count` semantics:** `suggest_resolution_order()` counts shared
   parameters, but its docstring and the summary say "how many other
   contradictions" — two contradictions sharing params 1 and 2 report 2.
   Fix the semantics to count **distinct neighboring contradiction IDs** (or
   rename to `shared_param_count`). Prefer counting distinct neighbors so the
   output matches the documentation.
3. **Tie-break sort:** `result.sort(key=lambda x: (-count, x["id"]))` sorts ties
   by string id, so `C10` sorts before `C2`. Sort ties numerically by the
   trailing integer in the id (`C2` before `C10`), or preserve insertion order.
4. **Document** the tool as a static one-shot ordering heuristic (update the
   module docstring: it does not model propagation after hypothetical
   resolution).

### R10. Dispatcher — register `effects` and `network` + fix alias doc

1. `triz.py` `_COMMANDS` maps only `route/matrix/sufield/ariz/evolution/case/
   evaluate`. `python triz.py effects --keyword magnetic` and
   `python triz.py network --demo` exit 2 `Unknown command`, yet the modules are
   shipped/importable and `SKILL.md` promises "one entrypoint". Register:
   - `effects` → `triz_effects.py`
   - `network` → `triz_contradiction_network.py`
2. Fix the docstring alias list to include the three working-but-undocumented
   aliases: `standard_solutions`, `su-field`, `knowledge-base`.

### R11. Case-template — fix stale comment

The `_repo_root` comment says "Repo root is 4 parent directories up" and "5
levels to root" while the code uses five `.parent` calls (correct). Fix the
comment to be consistent (5 levels up).

### R12. Windows-safe stdout across CLIs

Em-dashes emit `cp1252` byte 0x97 when piped on Windows, corrupting output for
UTF-8 consumers and crashing on cp437 consoles. `triz_effects.py` already solves
this with `_safe_print`. Adopt one consistent fix in the `main()` of
`triz.py`, `triz_evolution.py`, `triz_evaluator.py` (and any other CLI whose
output contains non-ASCII):

```python
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:  # Python < 3.7
    pass
```

This makes piped output valid UTF-8 regardless of console codec.

### R13. Regression + coverage test suite

Extend `tests/test_triz.py` with the new tests below. The existing 18 tests must
keep passing. All new tests must pass after the fixes above (write red → green
against R1–R12).

1. **`test_scripts_importable`** — import all ten scripts (`triz`, `triz_router`,
   `triz_matrix`, `triz_evaluator`, `triz_standard_solutions`, `triz_evolution`,
   `triz_effects`, `triz_ariz`, `triz_case_template`,
   `triz_contradiction_network`). Guards against silent breakage of the three
   previously-unimported modules.
2. **Dispatcher tests** (`triz.py`, currently 0% covered):
   - `dispatch([])` and `dispatch(["help"])` → returncode 0, usage printed.
   - aliases `router`, `su-field`, `evaluator`, `kb` → returncode 0.
   - unknown command (`frobnicate`) → returncode 2.
   - `dispatch(["master"])` → returncode 0, output contains "TRIZ master
     knowledge base".
   - sub-tool missing (point `triz._SCRIPT_DIR` at an empty temp dir) →
     returncode 1.
   - `dispatch(["effects", "--keyword", "magnetic"])` → 0, non-empty output.
   - `dispatch(["network", "--demo"])` → 0, non-empty output.
3. **Network tests** (module currently untested):
   - `add_contradiction` basic + out-of-range (0, 40, 99, float, bool) →
     `ValueError`; duplicate id → `ValueError`.
   - `find_shared_parameters` on the demo network → exact dict.
   - `find_conflicts` with an invalid shared param → `ValueError` (not KeyError).
   - `suggest_resolution_order` → sorted by connected_count desc, ties sorted
     numerically (`C2` before `C10`).
   - `analyze_network` → all keys present; summary contains counts.
4. **Effects-module tests** (suite currently only opens the JSON):
   - `search_by_function("detect")` → non-empty; empty/whitespace query → `[]`.
   - `search_by_keyword("magnetic")` → non-empty.
   - `get_function_families()` → sorted, unique, non-empty.
   - `list_effects()` → all; `list_effects(family)` filters.
   - `format_effects([])` → contains "(no effects found)".
5. **Router regression tests** (red until R1–R4):
   - Benign Italian `"Il sistema non risponde."` → `engineering_contradiction`
     is `None`.
   - Benign `"La macchina funziona bene ogni giorno."` → EC `None`.
   - Benign `"Il programma si avvia correttamente."` → EC `None`.
   - `"This button works fine."` → EC `None` (no "but" from "button").
   - `"We have no budget and only a few people, and the office workflow keeps
     failing"` → `physical_contradiction` is `None` (no on/off from
     only/office).
   - `"a circuit board overheats"` → Software TRIZ must NOT be boosted by
     "circuit" (assert Software TRIZ score is 0 or absent from methods).
   - Real Italian physio example → EC label matches
     `^improve \[[^\]]+\] / worsens \[[^\]]+\]$`, halves are whole words, no
     `…`, each ≤ 40 chars.
   - `"La vendita è calata questo mese ma i margini crescono."` → EC label both
     halves non-empty and whole-word.
   - `"simple, but it works"` and `"fast but."` → still boost scoring (the
     old BACKLOG item; punctuation-adjacent connectors must match).
   - Repeated cues → per-method score capped at 10.
   - `"The window must be both transparent and opaque."` →
     `physical_contradiction` not `None`.
   - `"Il pezzo deve essere rigido e flessibile."` →
     `physical_contradiction` not `None`.
   - Italian domain sentences route to the right branch:
     `"La vendita è calata questo mese."` → Business TRIZ present;
     `"Il sito web è lento a caricare."` → Software TRIZ present;
     `"Il paziente sente dolore durante il movimento."` → Rehabilitation TRIZ
     present.
6. **Evaluator tests**:
   - CSV with `cost/risk/complexity` headers parses and totals correctly.
   - CSV with `affordability/safety/simplicity` headers parses and produces the
     **same** totals.
   - Wrong/unknown header → `SystemExit(1)`, clean stderr message.
   - Missing file → clean error (no traceback), exit 1.
   - `score()` with a missing criterion or value 6 → `ValueError`.
   - Ties preserve stable order; highest total sorts first.
   - `format_table` on empty list → header only.
7. **Matrix tests**:
   - `lookup(18, 35)` → exactly 3 principles: Dynamization, Segmentation,
     Periodic Action (no duplicate Segmentation).
   - No cell in the matrix contains duplicate principle ids (would have caught
     the (18,35) bug).
   - `lookup(True, 2)`, `lookup(14.5, 2)`, `lookup("14", 2)`, `lookup(14, None)`
     → `ValueError`.
   - Boundary valid ids `lookup(1, 39)`, `lookup(39, 1)` → no error.
   - A known-empty off-diagonal cell → `[]` principles + note mentioning
     "Resource Analysis".
8. **Standard-solutions tests**:
   - All 5 states map to their class: incomplete→1, insufficient→2, harmful→1,
     measurement→4, excessive→5 (harmful is already covered; add the rest).
   - Synonyms resolve: missing/weak/detection/complex.
   - `lookup_solution("5.1.1.7")` → non-empty mechanism (inherited).
   - `--list-all` output: contains "76 standard solutions" and a variants line.
   - DB integrity: exactly 76 base solutions + 11 variants, all ids unique,
     every entry has name/mechanism.
9. **Evolution tests**:
   - `"premature aging"` → stage 0 (Unknown), not Maturity.
   - `"pocket tool"` → Unknown, not Infancy.
   - `"nearly done"` → Unknown, not Infancy.
   - `"prototype is unreliable and experimental"` → Infancy (stage 1).
   - `"obsolete and being replaced by the new version"` → Decline (stage 4).
   - `""` and gibberish → stage 0 with note present.
   - `"diminishing returns scaling"` → Maturity (later-stage tie-break), and
     the `why` contains the tie-break note.
10. **ARIZ + case-template tests**:
    - Creating the same title twice → `-2` suffix on the second.
    - `"App * !! Refactor!!"` → slug `app-refactor`; empty title → `untitled`.
    - Missing template path → `FileNotFoundError`.
    - Template headings preserved verbatim in the generated file.

## Acceptance criteria

1. All 13 requirements implemented in the listed files; no other files modified.
2. `python tests/test_triz.py` passes: the existing 18 tests **and** all new
   R13 tests (full suite green).
3. Every script in `scripts/` and `tests/test_triz.py` starts with
   `from __future__ import annotations` as its first import (after the shebang
   and module docstring), making the `Python 3.8+` claim true.
4. Router sanity spot-checks via `python`:
   - `suggest_methods("Il sistema non risponde.")["engineering_contradiction"]`
     is `None`.
   - `suggest_methods("This button works fine.")["engineering_contradiction"]`
     is `None`.
   - `suggest_methods("We have no budget and only a few people, and the office
     workflow keeps failing")["physical_contradiction"]` is `None`.
   - `suggest_methods("Il paziente sente dolore durante il movimento.")` includes
     Rehabilitation TRIZ.
5. Evaluator: a CSV with headers
   `solution,impact,feasibility,cost,speed,risk,reversibility,complexity,ideality`
   parses; an equivalent CSV with `affordability/safety/simplicity` parses and
   produces identical totals.
6. Matrix: `lookup(18, 35)` returns exactly 3 distinct principles
   (Dynamization, Segmentation, Periodic Action); `lookup(True, 2)` raises
   `ValueError`.
7. Standard-solutions: `lookup_solution("5.1.1.7")["mechanism"]` is non-empty;
   `python triz_standard_solutions.py --list-all` reports 76 standard solutions
   and lists variants separately.
8. Evolution: `analyze("premature aging")`, `analyze("pocket tool")`,
   `analyze("nearly done")` all return stage 0/Unknown.
9. Network: `find_conflicts` with an invalid shared param raises `ValueError`
   (never `KeyError`); `analyze_network` output is stable and well-ordered.
10. Dispatcher: `python triz.py effects --keyword magnetic` and
    `python triz.py network --demo` both exit 0 with non-empty output;
    `python triz.py frobnicate` exits 2.
11. Windows-safe stdout: running `python triz.py`, `python triz_evolution.py`,
    and `python triz_evaluator.py` and piping output to a UTF-8 decoder does not
    raise `UnicodeDecodeError`; the `sys.stdout.reconfigure(...)` guard is
    present in each `main()`.
12. The only data file changed is `contradiction_matrix.csv` (the single
    (18,35) cell). No other `data/` file, no `references/`, `SKILL.md`,
    `examples/`, `cases/`, `docs/`, or `TRIZ-MASTER.md` content is modified by
    this build.
13. `python -m py_compile` succeeds on every modified `.py` file.

## Out of scope (do NOT build)

- Branch architecture (`branches/`, `triz_branches.py`, `--branch/--lang`
  flags, `build_mirror.py`, `.agents` regeneration) — next build.
- TRIZ-MASTER.md content compliance fixes — next build.
- New domain references (mechanical, data-science, marketing, supply-chain) —
  later build.
- Use-case/case-template content authoring — later build.
- Rewriting SKILL.md stage 9 / docs — not needed: they already document
  `cost/risk/complexity`, which this build makes the script match.
- Removing or redesigning the contradiction-network tool; it is wired in and
  documented here.
- Any MCP server, web UI, GUI, or front-end.
