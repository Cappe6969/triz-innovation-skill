# rewrite-ladder

The method from *Learning Underscore.js* (Alex Pop): a climbable ladder that
compresses code expression — plain imperative → a library-assisted call → a
single idiomatic declaration of intent — with a test-first net keeping every
rung behavior-preserving. Reach for it whenever you catch yourself writing a
loop, hand-rolling a data transformation, or choosing between a library call and
a native one.

## When to use it
- You catch yourself writing a loop that a higher-order function expresses in one line.
- A data transformation reads like traversal bookkeeping (`i`, `len`, `acc`) instead of intent (`map`, `filter`, `countBy`).
- You are about to hand-roll something the stdlib or an existing dependency already does.
- Code works but is needlessly long — climb the ladder to shrink it, tests proving each step.
- A loop logically "stops when found" but still re-scans the full list (non-breakable iteration).
- Migrating an OOP module toward functional style.
- Choosing between a library call and a native/standard call.

## Core method

### The rewrite ladder
[Rewrite ladder] — solve the same problem in three shapes, each rung shrinking
expression while the tests stay green:

| Rung | Shape | Example |
|---|---|---|
| 0 | Plain imperative ES5: nested loops, state variables | `for` loop + counter object |
| 1 | Library-assisted: one improving call at a time | `_.find` replaces the search loop |
| 2 | One idiomatic declaration of intent | `_.countBy(bicycles, "bicycleType")` |

Each rung keeps tests green; the final rung is the target you migrate toward.
TRIZ read: the ladder **is** trimming toward the Ideal Final Result — each rung
deletes elements (state variables, intermediate arrays, loop control) until the
function vanishes into a one-line declaration. The IFR: no loop, no state, no
intermediate variables — just the data and the transformation name.

### Test-first safety net
- [Test-first with Jasmine] — write `describe`/`it`/`expect` specs BEFORE
  implementing any behavior; run them; implement until green. Apply to any
  non-trivial function, especially one about to be refactored through the ladder.
- [Make the SUT testable] — before either tests or code, the system under test
  must allow dependency swapping, run in isolation, and avoid shared/global
  state. This forces dependency injection and decoupled design before the first
  spec is written.
- The book's ceremony (SpecRunner page, Jasmine boilerplate) is optional. The
  load-bearing part is the tiny spec before each rung, so every shrink is
  provably behavior-preserving. Ponytail keeps the ladder and drops the ceremony.

### Replace non-breakable iteration
[Replace non-breakable iteration] — `forEach` cannot break, so any "stop when
found" logic in a loop re-scans the full list. Use early-exit primitives:

| Search intent | Primitive |
|---|---|
| First match | `find` |
| Any match | `some` |
| All match | `every` |
| The matching values | `filter` |

TRIZ read: this is a contradiction resolved by separation (IP-1 Segmentation,
IP-3 Local Quality) — split the "iterate-all" feature from the
"stop-when-found" feature. The wasteful resource is redundant full-array
traversal; the early-exit primitive consumes it and the waste disappears.

### Declarative over imperative
[Declarative over imperative] — use higher-order functions so code says WHAT the
transformation is, not HOW the loop runs:
- Pipelines: `map`, `filter`, `reduce`
- Tallying: `countBy`, `groupBy`
- Ordering: `sortBy`
- Projection: `where`, `pluck`, `first`, `rest`

### Compose small pure functions
[Compose pure functions] — functions with no side effects, no argument
mutation, and deterministic output; join them with `partial`/`bind`/`wrap`/
`compose`/`memoize` instead of stateful classes. TRIZ read: IP-25 Self-service /
IP-35 Parameter change (a pure function returns its own transformed result;
`memoize` caches), and IP-13 Inversion (control flow inverted — higher-order
functions replace loop control).

### Fluent pipelines
[Fluent chains] — chain a value through a sequence of transformations and end
with `.value()`; use `.tap()` to inspect intermediate results. TRIZ read:
IP-24 Intermediary — the wrapped chain object is a stage between value and value.

### Standards first, library second
[Standards first] — know which functions the language spec now provides
(`Array#map`/`filter`/`reduce`/`find`) and prefer them over the library; the
library fills gaps, not replaces thought. When the platform catches up, the
abstraction dissolves entirely — ponytail's "existing dependency" rung collapses
to the "native/stdlib" rung. Use when choosing between a library call and a
native one, or when upgrading a codebase as the platform matures.

### Extract reusable modules
[Extract modules] — move behavior out of classes into standalone units of
closely related functions, reusable and composable without instantiating a
class. TRIZ read: IP-2 Taking out — extract validation and modules out of the class.

### Deliberate paradigm choice
[Deliberate paradigm] — keep style consistent within a module: FP for
algorithms and data transformations, OOP for persistence and UI objects; do not
mix principles inside one class. The OOP→FP migration keeps classes as data
structures and extracts the modules.

### Translation table (Software ↔ TRIZ)
| Software concept | TRIZ concept |
|---|---|
| Ladder rungs | Trimming toward the IFR — delete elements until the function vanishes |
| One-line declaration of intent | IFR: no loop, no state, no intermediate variables |
| Early-exit primitives | Contradiction resolved by separation (IP-1 Segmentation, IP-3 Local Quality) |
| Redundant full-array scan | Wasteful resource; `find`/`some`/`every` consume it (resource analysis) |
| Fluent chain | IP-24 Intermediary — wrapper between value and value |
| Pure functions return their own result; memoize | IP-25 Self-service / IP-35 Parameter change |
| Higher-order functions replace loop control | IP-13 Inversion |
| Extract modules out of a class | IP-2 Taking out |
| Combining steps via chaining | IP-5 Merging |

### Efficiency red flags (the ladder's review pass)
When a rung looks good enough, run the efficiency audit — the wasteful-
iteration red flag: a nested `forEach` that re-scans the list is exactly what the
lazy senior dev catches. The full review checklist lives in `red-flags.md`,
which merges three sources: card 1's red-flag catalogue (Ousterhout — shallow
module, pass-through, repetition, vague name, …), card 2's chapter-end
checklist items (Code Complete — Key Points and construction checklists), and
card 9's refactor triggers (Dooley — duplicate code, a method longer than ~1
screen, weak cohesion, too many parameters, magic numbers, a middleman object,
code that doesn't return as soon as it knows the answer). [Red flag]
[Refactor triggers]

## Worked example
`bicycles` is an array of `{ bicycleType }` objects; count per type.

1. **Spec first:** `expect(countPerType(bicycles)).toEqual({ "Road": 2, "Mountain": 1 })`. [Test-first with Jasmine]
2. **Rung 0 — imperative:** nested loop, counter object, full scans. Tests green.
3. **Rung 1 — library:** `_.find` replaces the search loop. Tests green.
4. **Rung 2 — one call:** `return _.countBy(bicycles, "bicycleType")` — the whole
   hand-rolled `getBicyclesCountPerType()` function dissolves into one line. [Rewrite ladder]
5. **Standards pass:** today the call is `reduce` into an object — the library
   tier collapses to native. [Standards first]
6. **Audit:** no non-breakable loop, one pure deterministic one-liner, no
   side effects. [Declarative over imperative] [Compose pure functions]

## How it feeds the pipeline
- **Stage 2 (Climb the ponytail ladder)** — the rewrite ladder IS the
  expression-level ladder: plain → stdlib/native → existing dep → one line;
  [Standards first] collapses the dep tier to native when the platform catches
  up. [Rewrite ladder] [Standards first]
- **Stage 3 (Sketch the IFR)** — the one-line declaration of intent is the IFR;
  every rung trims toward it. [Rewrite ladder]
- **Stage 5 (Resolve contradictions)** — "iterate all" vs "stop when found" is
  separated via `find`/`some`/`every`. Cross-ref `triz-for-code.md`.
  [Replace non-breakable iteration]
- **Stage 6 (Make the minimal safe change)** — the test-first net makes each
  shrink provably behavior-preserving. [Test-first with Jasmine]
  [Make the SUT testable]
- **Stage 7 (Review with red flags)** — the efficiency audit (wasteful scans,
  non-breakable loops) plus the shared catalogue in `red-flags.md` (card 1's
  red flags, card 2's chapter-end checklists, card 9's refactor triggers).
  [Red flag] [Refactor triggers]
- **Stage 8 (Verify, record, ship)** — tests stay green at every rung; the
  rung's spec is its regression test. [Test-first with Jasmine]

Cross-links: siblings in this folder — `method-map.md` (stage router),
`construction-checklist.md` (TDD, refactor triggers, the [Leanness] gate),
`deep-modules.md` (the module depth that keeps the one-liner one line next
month), `red-flags.md` (the audit), `computation-models.md` (declarative
default), `pragmatic-etiquette.md` (ETC/DRY). TRIZ files —
`triz-for-code.md`, `triz-innovation/references/software-triz.md`,
`triz-innovation/references/ideal-final-result.md`,
`triz-innovation/references/trimming.md`,
`triz-innovation/branches/fields/software`.

## Source
*Learning Underscore.js* — Alex Pop (Packt, 2015).
