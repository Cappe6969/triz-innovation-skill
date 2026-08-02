# TRIZ for Code

The bridge that maps TRIZ onto software so the coding-method can run the TRIZ
engine on code problems. Everything here is original synthesis; the canonical
TRIZ definitions live in `triz-innovation/` — **never duplicate them**. Load
`triz-innovation/references/software-triz.md` and the `software` field branch
when you need the full software adaptation.

```
triz-innovation/SKILL.md  →  the TRIZ pipeline (stages 4-6: contradiction, resources, IFR)
triz-innovation/references/software-triz.md  →  software adaptation of the core concepts
triz-innovation/branches/fields/software/branch.json  →  software vocabulary, soft principle readings
```

## Translate the core concepts (code)
| TRIZ | Code |
|---|---|
| Component / system | Module, class, function, service, data store, endpoint, layer |
| Useful function | The behavior the caller needs |
| Harmful function | Coupling, latency, boilerplate, over-generalization, tech debt, hidden state |
| Insufficient | Slow, under-tested, incomplete, non-obvious |
| Excessive | Over-fetching, over-abstraction, dead generality, over-engineering |
| Resource | Existing code, stdlib, the platform/OS, cache, logs, tests, the data itself |
| Contradiction | "If I improve X, Y gets better but Z gets worse" |
| Ideal Final Result | The function happens with zero new code, zero new complexity |

## Contradiction → inventive principles (code)
Run the real matrix instead of guessing:
`python .claude/skills/triz-innovation/scripts/triz_matrix.py <improving_id> <worsening_id>`
then translate the principle into code terms. Recurring software contradictions
(from `software-triz.md`, given code shape here):

- **Latency vs cost** → [IP-10 Prior action] precompute/cache; [IP-19 Periodic] batch; [IP-2 Taking out] move work off the hot path.
- **Flexibility vs simplicity** → [IP-1 Segmentation] plugins; [IP-6 Universality] one extension point; [IP-25 Self-service] config over code.
- **Coupling vs performance/reuse** → [IP-24 Intermediary] queue, interface, broker; [IP-7 Nesting] bounded contexts.
- **Coverage vs delivery speed** → [IP-16 Partial action] test the risky 20%; [IP-10] fixtures prepared once.
- **Concurrency vs determinism** → the declarative model resolves it without locks (`computation-models.md`); [IP-13 Other way round] eventual + reconcile.

## Separation in time / space / condition / part (code)
When an element must be A and not-A, separate instead of compromising:
- **Time** — do X eagerly at startup, lazily on demand, or on a schedule (config at build vs at runtime).
- **Space** — move the conflict to different layers: presentation vs domain vs infrastructure.
- **Condition** — feature flags, per-tenant behavior, context-dependent behavior.
- **Part** — split the varying part from the stable core (extract the parameter, the strategy, the boundary).

## IFR for code
> The **[behavior]** happens **by itself** — no new module, no new dependency,
> no added complexity — because an existing or deep abstraction already performs
> it. The ideal module has **no interface** (Ousterhout's garbage collector:
> the function the user had to invoke is gone).

State the IFR, then the **almost-IFR**: the smallest thing that must still be
written. Work backwards from there. If a one-liner already exists in stdlib or
an existing dependency, that IS the IFR reached — stop (`ladder.py`).

## Trimming rules (code)
Remove a component while keeping its function:
- **Rule A — the need disappears:** make the source of truth singular so a sync
  step dies; change the contract so an error case disappears (define errors out
  of existence).
- **Rule B — another component does it:** the client, the DB, the platform, the
  compiler, an existing dependency.
- **Rule C — the component does it itself (self-service):** self-healing,
  self-validating schemas, self-timing.
Each trim must keep every useful function intact — the audit is `red-flags.md`.

## Resource inventory (code)
Before adding anything, list what already exists: stdlib functions, platform
APIs, cache, idle compute, logs/telemetry, existing fields, the tests, the data
itself, the type system, the compiler. TRIZ asks *"how do we get the result
without adding a new element?"* — in code, the cheapest resource is almost
always an existing abstraction.

## Standard solutions for code (escalation)
For interaction problems (missing / weak / harmful link between two parts), the
76 standard solutions apply: `python .../triz_standard_solutions.py --state <state>`.
Read them as *known-good structural moves* (intermediary, self-service,
decomposition) alongside the refactoring catalog.

## Evolution for code (leapfrog)
For "where is this headed / how do we leapfrog" questions:
`python .../triz_evolution.py --signals "..."`. Place the subsystem on the
S-curve; the dynamization trend maps to `--branch software` field readings.

## How it feeds the pipeline
Powers **stage 5 (Resolve contradictions)** — the default when the ladder and
the book catalogs stall. Also feeds stage 3 (IFR) and stage 7 (trimming). Load
the triz-innovation files only when a stage needs depth.
