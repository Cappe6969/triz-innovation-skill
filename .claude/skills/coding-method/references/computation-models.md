# computation-models

Computation-model literacy: underneath the variety of languages sits a small set
of computation models, each built from a tiny kernel language by adding ONE
concept at a time; default to the declarative model ("what, not how") where
referential transparency makes correctness reasoning nearly free. Reach for this
when choosing an abstraction level, a data structure, a concurrency style, or
component boundaries.

## When to use it
- Deciding which abstraction level / computation model fits the problem — climb the ladder only as far as needed.
- Adding machinery to a language, framework, or codebase — apply the [Creative extension] YAGNI test at the concept level.
- Any correctness check, refactoring, or reuse decision — make the common case trivially provable via [Referential transparency].
- Replacing recursion with a constant-stack loop, or building output incrementally.
- Concurrency needed without lock complexity — reach for [Dataflow] before threads+locks.
- Structuring teams/components so implementation can change behind a stable interface ([Model independence]).
- Analyzing whether adding state or timing will break reasoning about a program ([Monotonicity]).
- Growing a system "in the large" — [Incremental development] over big-design-up-front.

## Core method

### The ladder of computation models
Each rung adds exactly one concept; climb only to the lowest rung that solves the problem.
| Rung | Concept added | Resolves |
|---|---|---|
| strict functional | — (kernel) | — |
| declarative | single assignment, statelessness | determinism of computation |
| declarative concurrency | dataflow variables / streams | concurrency vs determinism |
| message passing | ports, explicit send/receive | decoupled, asynchronous flow |
| explicit state | state cells (single assign + mutable) | updating a persistent value |
| object-oriented | state bundled with procedures | encapsulation of changing state |
| shared state | concurrency + explicit state | — (costliest rung; last resort) |
| relational / constraint | choice, search, constraints | solving, not computing |

### Rules
- **[Creative extension]** — Add a concept to a model only when programs get
  complicated for technical reasons unrelated to the problem. Prefer a local
  translation (a function, a library) over a kernel change; the overall scheme
  must stay minimal. Test: *does this feature earn its complexity?*
- **[Referential transparency]** — Treat components as pure functions depending
  only on their arguments, so "equals replace equals." The ideal component is
  stateless, deterministic, self-contained. Test: *can I substitute an equal
  value anywhere and still get equal results?* If yes, reasoning is nearly free.
- **[Accumulator]** — Thread input/output state through a tail-recursive
  procedure with a pair of accumulator arguments (S1/Sn) so the stack stays
  bounded and the computation runs in one pass. Use when replacing recursion
  with a constant-stack loop, or building output incrementally.
- **[Difference list]** — Represent a list as a (list, tail-variable) pair so
  appending is O(1) instead of O(n). Use when a loop's repeated append would
  otherwise be quadratic.
- **[Higher-order]** — Functions as arguments and results are the basis of
  control and data abstractions; they compensate for a model's limited
  expressiveness. Use to factor repeated structure and to encode limited
  concurrency/state inside a declarative model.
- **[Data abstraction]** — Hide representation behind an interface; use names
  (unforgeable keys) and read-only views to enforce invariants the interface
  alone can't guarantee. Use when internals may change, or when capabilities and
  rights must not leak.
- **[Dataflow]** — Concurrent producers/consumers communicate through
  single-assignment streams; results stay deterministic and incremental
  (Unix-pipe style). Use for concurrency without locks, or for reacting to event
  streams.
- **[Model independence]** — A component's interface depends only on its
  externally visible functionality, never on the computation model it's
  implemented in; internals (e.g. memoization) can be swapped without touching
  callers.
- **[Incremental development]** — Build a running system from a small subset of
  requirements, grow it by user feedback, refactor to keep good component
  organization, and never optimize early — profile only if problems exist.
- **[Monotonicity]** — Classify a mechanism by its strength of state (none /
  single assignment / single + boundness test / multiple assignment) and check
  that execution stays monotonic; monotonicity is what keeps a program
  declarative and enables deterministic concurrency. Test: *does adding this
  state or timing feature break the "equals replace equals" reading?*

### TRIZ translation table
| Software concept | TRIZ concept |
|---|---|
| Kernel language (minimal primitive set) | Resource analysis — strip a phenomenon to the primitives that encode everything else |
| Creative extension | Trimming + IFR — remove any element a local translation can encode; the ideal scheme is "as simple as possible while complete" |
| Referential transparency | IFR for a component — it performs its function "by itself," statelessly; provability as a free immaterial resource |
| Ladder of computation models | Laws of system evolution / increasing ideality — minimal stepwise additions, each resolving one contradiction |
| Single-assignment dataflow | Resolves the *concurrency vs determinism* contradiction |
| Lazy execution | Resolves the *efficiency vs total computation* contradiction |
| Model independence | Segmentation (IP-1) — the interface is the trimming surface where the implementation model is freely substitutable |
| Accumulator / single-pass traversal | Prior action / economy of effort — do the work in one traversal |
| Boundary-stressing test examples | Testing a solution against all constraints before committing |

### Design methodology — in the small
1. Write a spec.
2. Stress it with boundary examples.
3. Explore (probe the space the spec doesn't pin down).
4. Structure into single-purpose operations.
5. Code.
6. Test AND reason — the steps are not obligatory, but never skip the test loop.

### Design methodology — in the large
- Grow incrementally as a hierarchical component graph ([Incremental development]).
- Interfaces are independent of implementation ([Model independence]).
- Do not optimize during development; do not add complexity just to increase performance.

## Worked example
Rebuilding a list with an O(n) append per element is quadratic; pick the
right rung's technique instead:

```
-- trap: O(n²), n appends × O(n) each
build []     = []
build (x:xs) = build xs ++ [x]

-- [Accumulator]: one pass, bounded stack
build xs = go [] xs
go acc []     = reverse acc     -- reverse once at the end
go acc (x:xs) = go (x:acc) xs

-- [Difference list]: append is O(1), no reverse needed
dl []     = (id, [])                -- (function, tail)
dl (x:xs) = let (f, t) = dl xs in ((f .) (x:), t)
```

The accumulator version is [Referential transparency]-friendly: a pure function
of its arguments, tail-recursive (bounded stack), one pass over the input. The
naive `build` is exactly the case [Accumulator] / [Difference list] exist to
fix — picked by asking *which rung and which representation keep the common case
provable and single-pass.*

## How it feeds the pipeline
- **Stage 2 — Climb the ponytail ladder:** the ladder of computation models IS
  ponytail's ladder ("climb only to the lowest rung that works"); [Creative
  extension] is YAGNI applied at the concept level.
- **Stage 3 — Sketch the IFR:** [Referential transparency] is the IFR for a
  component — stateless, deterministic, self-contained, reasoning free.
- **Stage 4 — Structure from data (primary):** choose the computation model,
  abstraction level, and data structure via [Ladder of models], [Accumulator],
  [Difference list], [Data abstraction].
- **Stage 5 — Resolve contradictions:** each ladder rung resolves a named
  contradiction (concurrency vs determinism, efficiency vs total computation);
  [Monotonicity] predicts when a state addition breaks reasoning.
- **Stage 7 — Review with red flags:** audit questions — is this the simplest
  model that works? Is execution still monotonic? Is the loop single-pass?

Cross-links (same folder): `design-recipe.md`, `deep-modules.md`,
`algorithm-strategies.md`, `red-flags.md`, `method-map.md`. triz-innovation:
`references/software-triz.md`, `references/trimming.md`,
`references/ideal-final-result.md`, `branches/fields/software`.

## Source
Original operational synthesis from the computation-models literature.
