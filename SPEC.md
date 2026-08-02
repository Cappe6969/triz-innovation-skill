# Branch Architecture + Language Axis + TRIZ-MASTER Compliance (ship build 2)

Build on top of master (`6e8883e`, Phase 1 merged). Two workstreams in one build:

- **A — Branch architecture (Carpenter-built).** A thin, pure-data branch layer over the
  canonical core: `branches/fields/<id>/branch.json` (domain vocabulary) ×
  `branches/langs/<lang>/branch.json` (localized labels), a registry script
  (`triz_branches.py`), `--branch`/`--lang` flags threaded through the dispatcher,
  `detect_language()` auto-detection, and `build_mirror.py` to regenerate the
  `.agents` mirror. This makes the skill a *mix of branches* that solve
  field-specific tasks, with English as the default language and Italian as the
  first additional branch (user-locked: bilingual en+it).
- **B — TRIZ-MASTER.md compliance fixes (Architect-authored).** Content
  synthesis only; per ADR-0011 the Architect authors these directly. The
  Carpenter MUST NOT modify `TRIZ-MASTER.md` in this build.

## Requirements

### R1 — Branch data model

Create the `branches/` tree with pure-data JSON only (no code in branches/):

- `branches/fields/general/branch.json` — the default identity branch.
- `branches/fields/business/branch.json`
- `branches/fields/software/branch.json`
- `branches/fields/rehab/branch.json`
- `branches/langs/en/branch.json` — identity overlay (empty `labels`).
- `branches/langs/it/branch.json` — Italian overlay.

Schema for `branches/fields/<id>/branch.json` (all required keys present in every
field file):

```json
{
  "id": "software",
  "name": "Software TRIZ",
  "name_it": "TRIZ software",
  "description": "Same TRIZ machinery with software vocabulary.",
  "keywords": ["app", "code", "api", "latency", "deploy", "bug", "server", "frontend", "backend", "database"],
  "parameter_map": {
    "Weight of moving object": "payload / request size",
    "Speed": "latency / throughput"
  },
  "principle_soft": {
    "1": "microservices",
    "2": "move a feature out of the core"
  },
  "examples": [
    "A login page must be secure and fast."
  ]
}
```

Constraints:
- `id` must equal the directory name; `name_it` present in every field file
  (it is the Italian branch's name even when the overlay is not loaded).
- The four field ids are exactly `general`, `business`, `software`, `rehab`.
  `general` has an empty `keywords` list and no `parameter_map`/`principle_soft`
  (it IS the canonical core).
- `branches/langs/en/branch.json` and `branches/langs/it/branch.json` follow:

```json
{
  "lang": "it",
  "name": "Italiano",
  "labels": {
    "Engineering Contradiction + 40 Inventive Principles": "Contraddizione tecnica + 40 principi inventivi",
    "Physical Contradiction + Separation": "Contraddizione fisica + principi di separazione",
    "Trimming": "Riduzione (Trimming)",
    "Root Cause Analysis": "Analisi delle cause",
    "Resource Analysis": "Analisi delle risorse",
    "Ideality / IFR": "Idealità / RIF",
    "Function Analysis": "Analisi funzionale",
    "System Operator (9 Windows)": "Operatore di sistema (9 finestre)",
    "Smart Little People": "Ominetti intelligenti",
    "Function-Oriented Search (FOS)": "Ricerca orientata alla funzione (FOS)",
    "Method-Oriented Search (MOS)": "Ricerca orientata al metodo (MOS)",
    "Business TRIZ": "TRIZ aziendale",
    "Software TRIZ": "TRIZ software",
    "Rehabilitation TRIZ": "TRIZ riabilitativo",
    "Su-Field + 76 Standard Solutions": "Su-Field + 76 soluzioni standard",
    "Evolution Trends + S-curve": "Tendenze evolutive + curva a S",
    "Scientific Effects": "Effetti scientifici",
    "ARIZ (escalation)": "ARIZ (escalation)"
  },
  "contradiction_labels": {
    "engineering": "Contraddizione tecnica:",
    "physical": "Contraddizione fisica:"
  },
  "stopwords": ["però", "perché", "più", "meno", "anche", "quindi", "questo", "questa", "questi", "queste", "essere", "avere", "già", "ancora", "tutto", "tutta", "tutti", "tutte", "loro", "cosa", "quale", "quando", "dove", "molto", "sempre", "mai", "dopo", "prima", "della", "delle", "degli", "nelle", "nella"]
}
```

- `en/branch.json` is `{"lang": "en", "name": "English", "labels": {}, "contradiction_labels": {}, "stopwords": []}` — the identity overlay.

### R2 — `scripts/triz_branches.py` registry

New stdlib-only script at `.claude/skills/triz-innovation/scripts/triz_branches.py`.

Public API:
- `list_branches()` → dict `{"fields": ["general","business","software","rehab"], "langs": ["en","it"]}` (deterministic order).
- `get_field_branch(field_id)` → parsed dict or raises `KeyError` for unknown id.
- `get_lang_branch(lang)` → parsed dict or raises `KeyError` for unknown lang.
- `resolve_labels(lang)` → merged label dict (field-independent; English = empty
  overlay, Italian = the it labels). Unknown lang → `KeyError`.
- `detect_language(text)` → `"it"` or `"en"` (see R4 for the algorithm).
- `validate()` → walks `branches/fields/*` and `branches/langs/*`, checks every
  file is valid JSON and has all required keys (the R1 schema), returns a list of
  error strings (empty when valid). Does NOT raise; callers decide.

CLI:
- `python triz_branches.py list` → prints fields + langs lines.
- `python triz_branches.py info <field_id>` → prints the parsed JSON of that
  field branch; non-zero exit + stderr message for unknown id.
- `python triz_branches.py resolve --lang it` → prints the resolved label dict
  for the language; non-zero exit for unknown lang.
- `python triz_branches.py check` → runs `validate()`; prints
  `OK — N field branch(es), M language overlay(s)` on success, one error per
  line + non-zero exit on any error.
- `python triz_branches.py detect "<text>"` → prints `it` or `en`.
- No args → usage, exit 1.

The registry resolves all paths relative to its own file location (works from any
working directory), exactly like the other scripts.

### R3 — `triz.py` global `--branch` / `--lang` flags + `branches` command

In `.claude/skills/triz-innovation/scripts/triz.py`:

- Add `"branches": "triz_branches.py"` to `_COMMANDS`.
- Accept two global flags anywhere in `argv` (before or after the command):
  `--branch <id>` (default `general`) and `--lang <lang>` (default `en`).
  Strip them from the argument list before forwarding.
- When `--branch`/`--lang` were supplied, forward them to the sub-tool as
  leading flags ONLY when that sub-tool supports them. Supported consumers:
  `route` (→ `triz_router.py`) and `case` (→ `triz_case_template.py`).
  Other sub-tools ignore the flags (do NOT forward to matrix/sufield/ariz/
  evolution/evaluate/effects/network).
- Update the module docstring usage block to document `--branch`/`--lang` and
  the new `branches` command.
- `python triz.py --lang it route "problema"` must produce Italian labels;
  `python triz.py route "problema" --lang it` must behave identically
  (flag position-independent).
- Unknown `--branch`/`--lang` values → forward anyway and let the consumer
  error, OR validate: either is acceptable, but the exit code must be non-zero
  and the user must see a clear error. Choose ONE behavior and document it.

### R4 — `triz_router.py` `--lang` + `--branch` domain filtering

In `.claude/skills/triz-innovation/scripts/triz_router.py`:

- `detect_language(text)`: score distinctive Italian stopwords from
  `branches/langs/it/branch.json` `stopwords` against a small English cue list
  (the/an/of/to/is/are/this/that/for/how/what/when/why/not/can/with/and).
  Return `"it"` when Italian hits ≥ 1 AND Italian hits ≥ English hits,
  else `"en"`. This is a heuristic, not a language detector — document that in
  the docstring.
- New CLI flags:
  - `--lang <en|it|auto>` (default `en` — MUST NOT change the current default
    output; existing tests assert English labels for Italian input).
    - `en` → English labels (current behavior).
    - `it` → Italian labels for the two contradiction lines and every method
      name, looked up from the it overlay (`resolve_labels("it")`).
    - `auto` → run `detect_language` on the problem text, then use the matching
      overlay.
  - `--branch <general|business|software|rehab>` (default `general`). When set
    to a domain id, SKIP the domain rules for the other domains:
    - `software` → only the `Software TRIZ` domain rule runs; `Business TRIZ`
      and `Rehabilitation TRIZ` rules are skipped.
    - `business` → only `Business TRIZ`.
    - `rehab` → only `Rehabilitation TRIZ`.
    - `general` (or omitted) → all domain rules run (current behavior).
    This requires tagging each domain rule in the RULES table with its domain.
    Add a module-level mapping `_DOMAIN_RULES = {"business": {"Business TRIZ"}, "software": {"Software TRIZ"}, "rehab": {"Rehabilitation TRIZ"}}`.
  - `--list` → print available `--branch` ids and `--lang` values, exit 0.
- Italian labels apply to the CLI print-out only; `suggest_methods()` keeps
  returning English method keys (tests and callers depend on the keys).

### R5 — `triz_case_template.py` `--lang en|it`

In `.claude/skills/triz-innovation/scripts/triz_case_template.py`:

- New file `cases/template-triz-case-en.md` — the existing
  `cases/template-triz-case.md` translated to English section headers
  (same section set, English): Problema originale → Original problem,
  Problema riformulato → Restated problem, Sistema → System,
  Sottosistemi → Sub-systems, Sovrasistema → Super-system,
  Stakeholder → Stakeholders, Funzione utile principale → Primary useful
  function, Funzioni dannose → Harmful functions, Vincoli → Constraints,
  Cause principali → Root causes, Contraddizione tecnica → Technical
  contradiction, Contraddizione fisica → Physical contradiction,
  Risorse disponibili → Available resources, Ideal Final Result → Ideal Final
  Result, Metodi TRIZ selezionati → Selected TRIZ methods,
  Soluzioni generate → Generated solutions, Valutazione soluzioni → Solution
  evaluation, Migliore esperimento → Best experiment, plus the English
  evaluation-table header row and the six experiment bullets.
  Keep `cases/template-triz-case.md` byte-identical (backward compatible —
  it is Italian by default).
- `create_case(title, cases_dir=None, lang=None)`: `lang=None` or `"it"` →
  `template-triz-case.md`; `"en"` → `template-triz-case-en.md`; unknown lang →
  `ValueError`.
- CLI: `--lang en|it` before or after the title; `--lang it` == no flag.
- Update the module docstring usage.

### R6 — `scripts/build_mirror.py` (regenerate `.agents`)

New stdlib-only script at repo root `scripts/build_mirror.py` (repo-level dev
tool; a new `scripts/` directory at the repo root — separate from the skill's
`scripts/`).

Purpose: the `.agents/skills/triz-innovation/` mirror is currently broken — it
has `SKILL.md` + `references/` but no `scripts/`, and its `SKILL.md` points at
`.claude/skills/triz-innovation/scripts/...` paths that do not exist inside
`.agents`. Regenerate it as a **self-contained copy** so Codex (and any other
agent that reads `.agents/`) can run every script from inside the mirror.

Behavior:
- Source: `.claude/skills/triz-innovation/` (SKILL.md, references/**, scripts/**
  including `scripts/data/**`).
- Target: `.agents/skills/triz-innovation/` — wipe and re-copy
  `references/`, `scripts/`, and `branches/`, plus `SKILL.md`.
- In every copied text file (`.md`, `.py`, `.json`, `.csv`), rewrite the literal
  prefix `.claude/skills/triz-innovation` → `.agents/skills/triz-innovation`.
- Prepend a `GENERATED` banner to the mirror's `SKILL.md`:
  `<!-- GENERATED by scripts/build_mirror.py — do not edit; edit the source under .claude/skills/triz-innovation/ -->`
  (plus a `> GENERATED` line for non-comment readers).
- The mirror's `SKILL.md` gets a `## Branches` note that the branch tree is
  copied verbatim from source.
- CLI:
  - no args → rebuild the mirror.
  - `--check` → compare the current mirror against what a rebuild would produce
    (banner-aware); print `Mirror is in sync` and exit 0, or print the list of
    drifted/missing files and exit 1. Do NOT modify anything in `--check` mode.
- The builder must compute the repo root from its own location (repo-root
  `scripts/build_mirror.py` → one parent up), so it works from any directory.

### R7 — SKILL.md branches documentation

In `.claude/skills/triz-innovation/SKILL.md`:

- Add a `## Branches` section (placed right before `## Master tool`) that
  documents:
  - The branch model: `branches/fields/<id>/branch.json` (domain vocabulary:
    keywords, parameter translations, soft principle readings, examples) ×
    `branches/langs/<lang>/branch.json` (localized labels + stopwords).
  - The orthogonal axes: FIELD (general, business, software, rehab) ×
    LANGUAGE (en default, it).
  - The flags: `python .../triz.py --branch <id> --lang <lang> route "..."`,
    and `--lang auto` for auto-detection.
  - The registry: `python .../triz.py branches list|check`.
  - How to add a field branch (drop a `branch.json` in `branches/fields/<id>/`)
    and a language (drop a `branch.json` in `branches/langs/<lang>/` + add
    labels + stopwords). One short paragraph each; no code dumps.
- Update the `## Master tool` command list to add `branches` and note
  `--branch/--lang` global flags.

### R8 — TRIZ-MASTER.md compliance fixes (Architect-authored; Carpenter must NOT touch this file)

The following are **content-synthesis fixes** authored by the Architect per
ADR-0011. They are REQUIRED acceptance criteria but are NOT Carpenter work — the
Carpenter must leave `TRIZ-MASTER.md` untouched (the Reviewer verifies the
changes exist and match these bullets; the Architect produces them).

1. **TOC is the 25th H2.** Demote `## Table of Contents` to
   `### Table of Contents` so the document has exactly 24 `## ` sections.
2. **§6 missing `**Procedure:**`.** Section 6 (The 40 inventive principles) is
   the only method section lacking a Procedure label. Add a `**Procedure:**`
   block between `**Core idea:**` and the complete list:
   1. Frame the contradiction (engineering §5 or physical §7).
   2. Get candidate principles from the matrix (step 3 of §5) or from §7's
      separation principles for physical contradictions.
   3. Read each candidate and force a concrete translation: "How would this
      pattern manifest in my system?" — push every principle through the *soft*
      readings until it names a real change.
   4. If the shortlist feels weak, walk the "most universally useful" list
      (1, 2, 3, 10, 13, 15, 25, 35) or re-map the parameters.
   5. Tag every proposed change `[IP-NN Name]`.
3. **§6 IP-2 name.** `2. **Separation** — extract…` → `2. **Taking out** —
   extract…` (matches `inventive_principles.csv` row 2 = `Taking Out` and
   `references/inventive-principles.md`). Update the §6 example tag
   `[IP-2 Separation]` → `[IP-2 Taking out]` and the `[IP-2 Separation]` text.
4. **§5 example hedge.** The §5 example claims the matrix returns
   "10, 30, 4, 34 (Discarding)" for improving=27 / worsening=25, but
   `python triz_matrix.py 27 25` returns exactly `10, 30, 4` (no 34). Rewrite
   the sentence to list exactly `10, 30, 4` and add a hedge that the live tool
   is authoritative (e.g. "— run `python triz_matrix.py 27 25` for the live
   answer").
5. **§5 parameter names 30/31.** In the 39-parameters table, rows 30 and 31 use
   singular "Object-affected harmful factor" / "Object-generated harmful
   factor"; `data/parameters_39.csv` uses plural "Object-affected harmful
   factors" / "Object-generated harmful factors". Align the master table to the
   CSV (plural).
6. **§13 ARIZ Part 1 TC-selection.** Part 1 of ARIZ-85C must include the
   TC-selection step from `references/ariz.md` Part 1.3: after stating the TC in
   both directions, add "Pick the TC that best preserves the main useful
   function." as an explicit step.
7. **§17 router-keyword mislabel.** §17 (Smart Little People) line "Key router
   keywords (used by triz_router.py): FOS — …; MOS — …" is wrong — those are
   FOS/MOS keywords, not SLP keywords. Replace with the actual SLP router
   keywords from `triz_router.py`: `"stuck"`, `"no idea"`, `"creative block"`
   (+ Italian `"bloccato"`, `"nessuna idea"`, `"blocco creativo"`).
8. **§3/§10/§11 output contracts.** Add a `**Output:**` line to each section
   matching its reference file:
   - §3: "A filled function table + a 3-bullet summary: main function (and its
     N/I/E grade), the worst harmful function, the top trimming candidate."
   - §10: "For each trim: what's removed, which rule, who inherits the function,
     net effect on cost/complexity/harm, and any new contradiction created. Tag
     `[Trimming Rule A/B/C]`."
   - §11: "The filled 9-window grid + 2–3 candidate intervention points it
     revealed."
9. **§4 RCA inversion.** `references/root-cause-analysis.md` declares master §4
   its "Canonical source" but contains roughly 17× the master's content — the
   consolidation dropped the RCA+ machinery. Enrich §4 (compact, keep the
   section's existing when-to-use/core-idea/procedure/example shape) with:
   - the four RCA+ problem categories in the anchor step (negative,
     insufficient, excessive, ineffective control),
   - cause-formulation requirements (function + relative parameter value, change
     of property, radical state change),
   - factual vs assumptive cause tagging,
   - AND/OR rules for building the cause tree,
   - the stop rule: **stop a branch at the first contradiction cause (N+P)** —
     do not drill deeper below an N+P cause,
   - the classification decision tree and the pitfalls pointer, summarized in
     ≤ 3 lines, with `**Derives →** references/root-cause-analysis.md` retained.
10. **§21 Tooling table.** Add rows for `triz.py` (master dispatcher),
    `triz_contradiction_network.py`, `triz_effects.py`, and
    `triz_branches.py`, each with a one-line description and usage example
    consistent with the existing rows.
11. **§23 provenance.** Add a `### Books used (conceptual reference only)`
    subsection under Primary sources crediting the books by title, mirroring
    `docs/source-map.md`: **Simplified TRIZ, 3rd ed.**; **Deep Dive into TRIZ —
    Engineering Problem Solving Algorithm**; **TRIZ Engineering Problem-Solving
    Algorithm** (tips & tricks); **World Conference of AI-Powered Innovation and
    TRIZ Methodology** (2nd IFIP WG 5.2); **TRIZ-Anwendertag 2020** (Oliver
    Mayer). One line each, noting "used as conceptual cross-checks only; no text
    copied."

### R9 — Regression tests

Extend `tests/test_triz.py` (unittest style, matching the existing suite) with
new tests:

- **Branches registry** (`triz_branches` import):
  - `list_branches()` returns exactly the four field ids + two langs.
  - `validate()` returns an empty error list for the shipped data.
  - `get_field_branch("software")["id"] == "software"` and `parameter_map`
    is a non-empty dict for the domain branches, empty/absent for `general`.
  - unknown id/lang → `KeyError`.
- **detect_language**:
  - Italian string → `"it"`; English string → `"en"`.
  - mixed with ≥ 1 Italian hit → `"it"`.
- **Router `--lang`/`--branch`** (import `suggest_methods`, or CLI):
  - `suggest_methods` keys stay English even for Italian input (default output
    unchanged).
  - `--lang it` CLI output contains an Italian label (e.g. "Contraddizione")
    and not the English method header.
  - `--branch software` with a business-only keyword string: the returned
    methods do NOT include "Business TRIZ".
  - `--branch general` (default) with the same string DOES include the business
    rule.
- **Case template `--lang en`**:
  - `create_case("x", cases_dir=tmp, lang="en")` file contains "Restated
    problem" and "Technical contradiction".
  - `create_case(..., lang="it")` == default Italian template file (contains
    "Problema riformulato").
  - unknown lang → `ValueError`.
- **Dispatcher**:
  - `triz.py --lang it route "problema ma migliora"` exits 0 and prints an
    Italian label.
  - `triz.py branches list` exits 0 and prints `software`.
  - `triz.py branches check` exits 0.
- **Mirror**:
  - `scripts/build_mirror.py --check` exits 0 when the mirror is in sync and
    non-zero when a file is added to the source but not the mirror (run a real
    drift test against a temp tree, not the real `.agents`).
  - A mirrored script file has the `.claude/` prefix rewritten to `.agents/`.
- **Master structure regression** (guards the R8 content fixes):
  - Exactly 24 `## ` sections in `TRIZ-MASTER.md`.
  - Every method section 3–20 contains `**Procedure:**` (or is explicitly not a
    method section).
  - `inventive_principles.csv` row 2 is `Taking Out`.
  - `triz_matrix.py 27 25` returns exactly `[10, 30, 4]`.

All new scripts and the modified scripts keep the `from __future__ import
annotations` first-import and Windows-safe UTF-8 stdout
(`sys.stdout.reconfigure(encoding="utf-8", errors="replace")`) conventions from
Phase 1.

## Acceptance criteria

| # | Criterion | Verified by |
|---|-----------|-------------|
| AC1 | `branches/` tree exists with exactly the 4 field + 2 lang JSON files, all schema-valid | `python .claude/skills/triz-innovation/scripts/triz_branches.py check` → `OK` |
| AC2 | `triz_branches.py list` shows the 4 fields and 2 langs; `info`, `resolve --lang`, `detect` all work; unknown ids fail non-zero | manual + tests |
| AC3 | `triz.py --lang it route "..."` and `triz.py route "..." --lang it` print Italian labels; `triz.py branches list|check` work; flags are position-independent | tests + manual |
| AC4 | Router default output is unchanged (English labels for Italian input); `--lang it` localizes; `--branch <domain>` filters the other domains' rules; `--lang auto` detects | tests |
| AC5 | `triz_case_template.py --lang en "title"` produces an English-template case; no flag / `--lang it` reproduces the existing Italian default; existing `template-triz-case.md` is byte-identical | tests |
| AC6 | `.agents/skills/triz-innovation/` mirror is self-contained (scripts/ + references/ + branches/ present, `.claude/` paths rewritten, GENERATED banner) and `build_mirror.py --check` passes | tests + manual |
| AC7 | `SKILL.md` has a `## Branches` section and documents `--branch/--lang` in the master-tool block | reviewer |
| AC8 | All 11 TRIZ-MASTER.md compliance fixes present (TOC is H3; §6 Procedure + IP-2 Taking out; §5 hedge + plural params; §13 TC-selection; §17 SLP keywords; §3/§10/§11 Output; §4 RCA enrichment; §21 rows; §23 books) | reviewer + structural tests |
| AC9 | Full test suite passes (existing 75 + new) via `python tests/test_triz.py` | command |
| AC10 | No file outside the listed scope is created or modified (no stray files; `cases/`, `docs/`, `.gitignore` untouched unless named above) | reviewer diff |

## Out of scope (ship build 3)

- New domain branches (mechanical/hardware, data science/ML/AI, marketing/growth,
  supply chain/logistics) — user-selected for Phase 3.
- `.agents` for any agent besides the generic mirror.
- Any change to `Books/`, `triz-prompt-engineering-main/`, `reddit-post.md`.
