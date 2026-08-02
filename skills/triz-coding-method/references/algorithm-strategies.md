# Algorithm Strategies

The strategy catalog: a computational problem is solved by **matching its
signature onto a small catalog of reusable attack plans**, not by inventing an
algorithm. The catalog spans brute force, decrease / divide / transform-and-
conquer, space-time tradeoffs, dynamic programming, greedy, and iterative
improvement, plus the process shapes (linear recursion, tree recursion,
iteration) and orders of growth that size them. Reach for it at stage 4
whenever a non-trivial computation shows up.

## When to use it
- Writing a loop you've seen before: pairwise scan, repeated lookup, recomputation, pathfinding.
- Choosing between two candidate implementations and you need a quantitative comparison, not a hunch.
- The naive solution is correct but slow — decide whether a smarter strategy is worth its complexity (the YAGNI cliff).
- Any code where input size is a variable that can grow: search, sort, aggregation, caching.
- Hand-debugging a function whose behavior you can't predict; you need a precise model of what it computes.
- Exposing a function in a module: you should know the shape and growth of the operations you are publishing.
- Tracing how far a clever trick pays for itself (is the win real at the actual input size?).

## Core method

### Step 0 — the problem-solving plan [Problem-solving plan]
Before any code, walk six steps (a classic problem-solving plan):
1. State the problem precisely — inputs, outputs, constraints, edge cases.
2. Decide the computational means — what memory and data structures are available.
3. Design the algorithm — match the catalog below.
4. Argue correctness — a *reason* the result is right, not a hope.
5. Classify efficiency — name the complexity class, worst and typical case.
6. Then code.

### The strategy decision table [Strategy catalog]
The load-bearing artifact: match the problem signature to a strategy.

| Problem signature | Strategy | Canonical move | Class | TRIZ read |
|---|---|---|---|---|
| No idea yet; need a correctness floor | [Brute force] | Check every candidate; pairwise O(n²) compare | O(n²)+ | The wasteful baseline TRIZ trims — write it first as a reference oracle |
| One step removes a guaranteed chunk; one call suffices | [Decrease-and-conquer] | Shrink by constant / constant-factor / variable each step — binary search, Euclid, insertion sort | O(log n)–O(n²) | Segmentation: reduce to a trivial remnant |
| Independent halves, cheap to combine | [Divide-and-conquer] | Split, recurse, combine — mergesort, quicksort, closest pair | O(n log n) | Segmentation + merging solutions |
| Repeated inner-loop scan; data can be preprocessed once | [Transform-and-conquer] [Presort] | Sort / heap / change representation once, then cheap lookup; Horner's rule | one sort, then cheap | Prior action (IP-10): pay up-front so the main work becomes cheap |
| Time is the bottleneck, memory is idle | [Space-time tradeoff] | Hash, B-tree, precomputed table | mem → time | Resource contradiction: spend the idle memory to resolve the time bottleneck |
| Naive recursion recomputes the same subproblems | [Dynamic programming] | Memoize or build a bottom-up table — Fibonacci, knapsack, Floyd | O(n²)–O(n³) | Distinguish *overlapping* subproblems (DP) from *non-overlapping* (divide-and-conquer) |
| A local choice can be proven globally optimal | [Greedy] | Irrevocable local optimum, never backtrack — Dijkstra, Prim, Huffman; must pass an exchange / optimal-substructure argument | O(n log n) | The classic TRIZ trap: local optimum ≠ ideal whole — verify before trusting |
| Provably hard, no fast exact algorithm | [Coping with limitations] | Backtracking, branch-and-bound, or approximation — switch the goal to near-optimal | exp / approx | Contradiction (exactness vs time): separate by accepting a near-optimal target |
| Start anywhere, improve by local tweak | [Iterative improvement] | Repeated hill-climb (simplex, max-flow); only when improvement is monotone | depends | The incremental path TRIZ rejects — try a new principle before settling |

### Process shapes [Process shape] [Order of growth]
Before coding, decide the shape of the computation; the shape sets the resource use.

| Shape | Structure | Time | Space | Signal |
|---|---|---|---|---|
| Linear recursion | one recursive call feeding a deferred operation | O(n) | O(n) | answer accumulates along a chain |
| Tree recursion | multiple calls on overlapping branches | O(2^n) typical | O(n) | naturally exponential — the trigger for DP |
| Iteration | loop with fixed counters, no deferred work | O(n) | O(1) | convert tail recursion → loop for constant space |
| Pipeline | map / filter / reduce over a sequence | O(n) | depends | see [Conventional interfaces] |

Rule: **name the growth before you write it.** A recursion whose shape you never
checked is how an O(2^n) accident ships.

### Verification tools
- [Substitution model] — hand-trace a small case: replace each call with its body, each parameter with its argument, like evaluating an algebraic expression. Predicts what the code computes and exposes shape bugs (extra deferred op, missing base case) without running.
- Exchange / optimal-substructure argument — for greedy and DP, the one correctness argument worth writing: "any optimal solution can be swapped to include my choice with no loss."
- Recurrence solving — T(n) = 2T(n/2) + n → O(n log n). Count basic operations per level; sum the levels.
- [Asymptotic class] — state every candidate as Big-O/Theta/Omega, worst and typical, and compare on paper before coding.

### Abstraction layer — only when complexity is real
- [Wishful thinking] — write the consumer code against the interface you wish existed (constructors, selectors, the function you want), then implement the assumptions.
- [Black-box abstraction] — a function is its contract (inputs/outputs), not its body; anything with the same behavior is swappable.
- [Abstraction barrier] — separate *use* from *representation*; expose only constructor/selector functions and forbid clients from assuming internals. Gate: justified only when the representation may genuinely change — building it preemptively is over-engineering ([YAGNI]).
- [Higher-order abstraction] — parameterize a repeated shape over the one differing computation (sum → map → filter → accumulate).
- [Conventional interfaces] — pass sequences through standard operators so producers and consumers compose mix-and-match rather than being welded.
- [Closure property] — prefer a combining operation that accepts compound as well as primitive elements, so few primitives compose into arbitrarily deep structures.
- [Metalinguistic abstraction] — when the host language can't express the problem, build a small evaluator / DSL; an evaluator is just another program (the evaluate/apply cycle).
- [Structure on the model] — decompose to mirror the modeled thing: objects with local state for stateful systems, streams with delayed evaluation to decouple time.

## Worked example
*Does any pair of numbers in a list sum to target T?*

1. **Problem-solving plan** — input: list of n ints; output: bool.
2. **Brute force baseline** — nested loops, O(n²); correct, the reference oracle.
3. **Match the catalog** — the signature "repeated inner-loop scan" → [Transform-and-conquer] / [Presort], or "time-bound, memory idle" → [Space-time tradeoff].
4. **Decide** — presort, then binary search T-x per element: O(n log n). Or one pass with a hash set of seen values: O(n) time, O(n) memory.
5. **Process shape** — the hash-set pass is a single loop = iteration, O(1) space on top of the set.
6. **YAGNI cliff** — at n < 1,000 the O(n²) double loop is the correct lazy answer (simplest, correct). The hash version wins only when n or the call frequency makes the complexity claim real. State it: "O(n) via [Space-time tradeoff]" in the ≤3-line why.

## How it feeds the pipeline
Powers **stage 4 (Structure from data)** — the "strategy" slot in that stage's
output is this catalog. Feeds **stage 2** — the complexity class is what tells you
when YAGNI stops: the O(n²) double loop is the right lazy default until input
grows, then the ladder climbs to a catalog strategy. Feeds **stage 3** — the
efficiency class is the quantitative IFR metric (keep the function, minimize
operations and memory). Feeds **stage 5** — space-time tradeoff and greedy local-
vs-global are parameter contradictions resolvable via TRIZ separation and
[IP-10 Prior action]. Feeds **stage 8** — the ≤3-line why carries one asymptotic
claim; the ADR records the complexity class.

Cross-links: `design-recipe.md` (data definition before strategy), `computation-
models.md` (the declarative model as a candidate strategy), `deep-modules.md`
(the module boundary around the operation), `rewrite-ladder.md` (transform-and-
conquer as the stdlib-reduction read), `red-flags.md` (review: is the clever
strategy paying for itself at the real input size?). TRIZ depth:
`triz-for-code.md`, `triz-innovation/references/software-triz.md`,
`triz-innovation/branches/fields/software`.

## Source
Original operational synthesis from the classic algorithms literature.
