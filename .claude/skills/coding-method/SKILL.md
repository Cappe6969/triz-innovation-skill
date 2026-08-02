---
name: coding-method
description: Use this skill for any coding problem where the solution is not obvious, the first idea feels too complex, or a trade-off must be resolved. Triggers: "simplify/refactor/make this smaller", "I need X but that breaks Y", choosing between two approaches (library, algorithm, data structure, architecture), changing legacy code that must not break, reviewing code for complexity, debugging untested behavior, designing a module/API/algorithm, or any request wanting the minimal technical fix without over-engineering. Runs one 8-stage pipeline merging ponytail (minimum code, shortest diff), TRIZ (contradiction, Ideal Final Result, trimming), and the distilled method catalog.
---

# Coding Method — Lazy Ideality

A disciplined pipeline for coding problems. You are NOT typing the first thing
that comes to mind. You run a fixed method that reaches the **Ideal Final
Result of the code** — the behavior happening with the *least code that stays
least code next month* — by climbing ponytail's ladder first, then applying TRIZ
and the method catalog only when the ladder stalls. Default to method over
inspiration.

The three sources are one method at three depths:
- **Ponytail** is the lazy default: skip it → stdlib → native → existing dep →
  one line → minimum code. A one-liner is only possible because an existing or
  deep abstraction already hides the complexity.
- **TRIZ** is the stuck-state engine: contradiction, IFR, trimming, resources,
  separation — used when the catalog alone can't reach the one-liner.
- **The method catalog** is the field-branch catalog: deep modules, the design
  recipe, strategy catalogs, seams, red flags — the standard moves that converge
  on the target.

## When to use
Any coding task with a real decision in it: design, refactor, debugging,
architecture, choosing an approach, or modernizing legacy code. If it's a
trivial one-liner with a known pattern, run stages 1–3 (lite) and ship.

## Operating rules
1. **Run the pipeline in order** (stages 1–8 below). Skip a stage only when the
   escalation table says so; if a stage has no content, say so and move on.
2. **One question at a time, max 3 total.** Ask only when the answer changes the
   analysis. Otherwise state an assumption and proceed.
3. **Be concrete.** No generic advice ("improve design"). Every output names a
   module, a technique, a rule.
4. **Cite the method.** Tag every move with its source: `[YAGNI]`, `[IFR]`,
   `[Deep module]`, `[Design recipe]`, `[Seam]`, `[Characterization test]`,
   `[Red flag]`, `[Separation in time]`, `[IP-10 Prior action]`, `[Strategy:
   transform-and-conquer]`, …
5. **Load references on demand.** Read the matching file in `references/` only
   when a stage needs depth. Do not dump references into the answer.
6. **End with a test, always.** No change is complete without a test that proves
   the failure is gone and stays gone (stage 8).
7. **Shortest working diff.** Every candidate is judged against the naive
   alternative: same behavior, no larger a diff, with the why in ≤3 lines.

## Reference index (read on demand)
| Need | File |
|------|------|
| Which path/when, escalation, debugging | `references/method-map.md` |
| Design recipe (data-first) | `references/design-recipe.md` |
| Computation-model ladder, declarative default | `references/computation-models.md` |
| Algorithm strategy catalog + complexity | `references/algorithm-strategies.md` |
| Deep modules + complexity model | `references/deep-modules.md` |
| Review checklist (red flags + construction) | `references/red-flags.md` |
| Construction craft + debugging loop | `references/construction-checklist.md` |
| Safe change on legacy code | `references/legacy-change.md` |
| Architecture trade-offs, ADRs, katas | `references/architecture-tradeoffs.md` |
| Domain modeling | `references/domain-modeling.md` |
| Time/scale/tradeoffs engineering | `references/sustainable-engineering.md` |
| ETC/DRY/orthogonality mindset | `references/pragmatic-etiquette.md` |
| Rewrite ladder (plain → library → one line) | `references/rewrite-ladder.md` |
| Proof-pass / type-safety verification | `references/type-safety.md` |
| TRIZ ↔ code bridge | `references/triz-for-code.md` |
| Data-system decisions | `references/data-systems.md` |

## The pipeline

### 1. Frame the task (30 seconds)
- Restate the task in one neutral sentence (no solution baked in).
- Name the **primary function** the code must perform (Tool → Action → Object)
  and the **harmful / excessive effects** it must avoid (coupling, latency,
  boilerplate, over-generalization, hidden state).
- List the **real constraints** (time, scale, skill, platform).
- Classify: **wicked** (ill-defined, iterative) vs **tame** (well-defined,
  mechanical). Wicked → full recipe; tame → ladder and ship.

### 2. Climb the ponytail ladder first → `references/rewrite-ladder.md`
The default answer to "should I build this?" is **no**. In order:
1. **YAGNI** — is this needed at all? (Trim it. Code is a liability.)
2. **stdlib / native** — does the language or platform already do it?
3. **existing dep** — does a dependency already do it?
4. **one line** — can it collapse to one idiomatic call?
5. **minimum code** — only then write the smallest thing that works.
If an existing or deep abstraction already does the work, stop — that IS the
IFR reached. Inventory resources (existing code, cache, tests, data) before
adding anything.

### 3. Sketch the Ideal Final Result → `references/deep-modules.md`
- State the **IFR**: the behavior happens by itself — no new code, no new
  module, no added complexity.
- State the **almost-IFR**: the smallest thing that must still be written.
- Design the module to be **DEEP**: lots of hidden functionality behind a simple
  interface. Push complexity downwards so most users never see it.
- For any non-trivial decision, **design it twice** — two alternatives, pick the
  better — and use **wishful thinking**: postulate the ideal interface, build
  toward it.

### 4. Structure from data → `references/design-recipe.md` + `references/algorithm-strategies.md`
- **Define the data first**: a named data definition with an interpretation
  comment, then the signature and a one-line purpose (the contract). The
  template follows the data; the recursion follows the data.
- Pick the **computation-model rung**: declarative → explicit state →
  concurrency → constraints. Climb only as far as the problem demands.
- Pick the **algorithm strategy**: start from the brute-force baseline, then
  decrease / divide / transform-and-conquer / DP / greedy as the problem
  dictates. State the **complexity class before coding**.

### 5. Resolve contradictions → `references/triz-for-code.md`
When the design forces a genuine trade-off, name the **engineering
contradiction** ("if I improve X, Y gets better but Z gets worse") or the
**physical contradiction** (element must be A and not-A), then apply TRIZ:
- Map to the 39×39 matrix for inventive principles:
  `python .claude/skills/triz-innovation/scripts/triz_matrix.py <improving> <worsening>`.
- Or separate in **time / space / condition / part**.
- Or reframe so the contradiction dissolves (define errors out of existence;
  find the Box).
Only after elimination attempts, verify the residual compromise with a weighted
+/− trade-off matrix — never accept the first "least worst".

### 6. Make the minimal safe change → `references/legacy-change.md`
- **Greenfield:** write the one-line purpose/interface contract FIRST, then the
  body — the contract is the ≤3-line explanation, written before it constrains
  the diff. Novel patterns: test-first, keeping tests green at every rung of the
  rewrite ladder toward the one-line target.
- **Legacy / untested:** run the **Legacy Code Change Algorithm** — identify
  change points, find test points, break dependencies via **seams** already
  latent in the code, write **characterization tests**, then change and refactor
  in baby steps. Use Sprout/Wrap to avoid touching the original untestable code.
- **Broken code:** run the debugging path (`method-map.md`) — characterize, then
  the 5-step loop, then the root-cause fix.

### 7. Review with the red flags → `references/red-flags.md`
Audit before shipping: shallow module, information leakage, pass-through method,
repetition, vague names, conjoined methods, special-general mixture, comment
repeats code, nonobvious code, coupling/cohesion, hide secrets, leanness, DRY,
orthogonality, abstraction barriers. Confirm the complexity didn't just
**relocate** — every module deep, every piece of knowledge single-sourced. Fix
each broken window now.

### 8. Verify, record, ship (mandatory close)
- **Prove with tests** — add a regression or characterization test so the fix
  stays fixed. The machine reports truth; no analysis is complete without a
  numeric **success / failure criterion**.
- If the decision is architecturally significant, record an **ADR-lite** (why
  beats how).
- **Ship** with the ≤3-line explanation stating the load-bearing WHY, not the
  how.

## Intensity levels (ponytail-compatible)
- **lite** — stages 1–3 only: routine task, ladder + IFR + one-liner.
- **full** — all 8 stages: default for anything with a design decision.
- **ultra** — full + forced TRIZ contradiction escalation + a **verification
  pass** (`type-safety.md`: inductive definition / progress-preservation-style
  reasoning or a substitution-model trace) + the trade-off matrix scored twice.

## Cross-links to triz-innovation
The TRIZ engine is **not duplicated** — it lives in
`.claude/skills/triz-innovation/` and is cross-invoked:
- Contradiction matrix: `triz_matrix.py`
- Method first-guess: `triz_router.py`
- Standard solutions (interaction problems): `triz_standard_solutions.py`
- Evolution trends (leapfrog): `triz_evolution.py`
- Software adaptation: `references/software-triz.md` + `branches/fields/software`

## Saving a case
Persist the analysis as a reusable case file in `cases/`. Mirror the
triz-innovation case template: fill each stage as you work; after running the
experiment, update the result and the follow-up.

## Scripts
`python .claude/skills/coding-method/scripts/method.py route "<task>"` returns a
concrete, technique-named stage plan. `ladder.py` suggests the ponytail rung +
the IFR. `redflags.py` runs the review checklist. Run `method.py` with no args
for the full command list.
