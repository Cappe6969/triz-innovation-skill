# type-safety

The formal type-safety method: define a structure with total precision
(inductive definition + inference rules), then **prove its safety properties
before trusting it**. Reach for it when adding a capability to
an existing system that must not break, when an error class must be eliminated at
compile time rather than caught at runtime, or as the proof-pass verification at
the end of the pipeline.

## When to use it
- Adding a new construct/feature to an existing, proven system — introduce it as
  a **minimal verified delta**, never a rewrite.
- You must *guarantee* a behavior ("this can't crash", "this terminates") rather
  than hope, and the guarantee matters.
- Designing an interface or API where a static contract (types, preconditions)
  can be checked mechanically and compositionally.
- The debugger is the wrong tool for the error class — compile time is the right
  time to kill it.
- Ultra verification pass over a diff (stage 8): a proof-style argument the
  change cannot introduce undefined behavior.

## Core method

### 1. Define the universe precisely — smallest-set closure
- Define every structure (syntax, AST, data type) as the **smallest set closed
  under a few constructor rules**; nothing is in the set unless the rules force
  it. [Smallest-set closure]
- Write the grammar (BNF + inductive definition) **before** any code or proof —
  the definition *is* the spec; it trims all ambiguity.
- Characterize the same set **three ways** — inductive closure, inference rules,
  and a staged generation (S₀, S₁, …) — and prove they coincide. You get both an
  abstract and an executable view, cross-checked. [Three views]

### 2. Reason by shape — structural induction
- To prove a property of every term, induct on the **shape** of the term, using
  the induction hypothesis on each subterm — not on natural numbers. [Structural induction]
- For rule-based systems, extend to **induction on the derivation** (proof tree):
  one case per rule.

### 3. Make execution observable — small-step operational semantics
- Model evaluation as single-step transitions `t → t′` written as inference
  rules, ending at a value. [Operational semantics]
- Define a **stuck** state explicitly: can step no further but is not a value.
  The stuck states *are* the definition of "goes wrong" — enumerate them.

### 4. Compose contracts statically — typing as inference rules
- Assign types **compositionally** — the type of a term depends only on the types
  of its subterms — via the three-place relation `Γ ⊢ t : T` (context ⊢ term :
  type). [Compositional contract]
- Judge well-typedness by building a **derivation tree**; the tree is the
  machine-checkable artifact, like modular design made static.

### 5. Prove safety in two halves — progress + preservation
- **Type safety = progress + preservation.** [Progress + preservation]
  - *Preservation*: if a well-typed term steps, the result is well-typed with the
    same type.
  - *Progress*: a well-typed non-value can always step.
  - Together: a well-typed program **never gets stuck**.
- Split the "safe vs capable" contradiction into two separable proofs rather than
  one monolithic argument. [Contradiction]

### 6. Grow the system one minimal verified delta at a time
- Every new feature runs the same pipeline: motivating examples → formal
  definitions → safety proofs → metatheory → typechecking algorithm (sound,
  complete, terminating) → concrete implementation. [Minimal verified delta]
- Isolate each new feature in the **smallest language that exhibits it**
  (numbers + booleans, then the lambda) — feature isolation as resource analysis.

### 7. Let the checker infer — type reconstruction / unification
- Replace unspecified annotations with type variables, derive equations from the
  typing rules, solve by **unification**, and compute the **principal type** (the
  most general type all instances share). [Principal type]
- Generalize by leaving unknowns to the solver; require annotations only where
  inference genuinely can't decide.

### 8. Tune the abstraction deliberately — conservativity vs expressiveness
- A static analysis is a conservative, compositional approximation of runtime
  behavior: it can prove **absence** of bad behavior, not presence, so it rejects
  some programs that behave fine. [Conservative abstraction]
- Treat precision as a budget: refine the analysis only where you actually need
  more programs to type.

### TRIZ moves baked in
- [IP-10 Prior action] — move the check before runtime: the checker runs before
  the program does.
- [IP-2 Taking out] — once a property is proven, extract the now-unnecessary
  dynamic check from the runtime path.
- [IP-5 Merging] — compositional typing assembles a term's type from its parts'
  types.
- [IP-24 Intermediary] — the typechecker is the intermediate verifier between
  code and execution.

## Translation table
| Type-theory concept | Software concept |
|---|---|
| Typing context Γ | Resource inventory / list of assumptions in scope |
| Inductive definition | Precise data definition (define the data first) |
| Derivation tree | Machine-checkable contract artifact |
| Stuck state | Undefined behavior, crash, silent wrong result |
| Progress + preservation | "Can't get stuck" = no runtime error class |
| Minimal verified delta | Minimal safe change, tested at every rung |
| Conservative abstraction | Static-analysis precision budget |
| Normalization | "Every well-typed program terminates" |

## Worked example
Adding `div` to a small typed expression language.
- Terms by smallest-set closure: `t ::= n | t1 + t2 | t1 / t2` — nothing else is
  a term. [Smallest-set closure]
- Small-step rules: `n1 + n2 → n`, `n1 / n2 → n3` when `n2 ≠ 0`. The term
  `t1 / 0` is **stuck**: it can't step and isn't a value. The stuck state names
  the error class "divide by zero." [Operational semantics]
- Typing: `Γ ⊢ t1 : Nat   Γ ⊢ t2 : Nat  ⇒  Γ ⊢ t1 / t2 : Nat`. [Compositional contract]
- Preservation: stepping `n1 / n2 → n3` stays `: Nat`. Progress: a well-typed
  `t1 / t2` with `t2` a non-zero value always steps. [Progress + preservation]
- The delta is one constructor, two step rules, one typing rule — every existing
  rule untouched. [Minimal verified delta]
- IFR: the checker, not the runtime, eliminates the entire "divide by zero"
  error class at compile time. [IFR]

## How it feeds the pipeline
- **Stage 2 — Climb the ponytail ladder:** the language's built-in type system is
  the existing-dep rung — reach for a typed language/checker instead of
  hand-building the proof apparatus. Ponytail's YAGNI = smallest-set definitions
  and minimal deltas; the contrast: don't write the proof if the compiler already
  checks it. [YAGNI], [Existing dep]
- **Stage 3 — Sketch the IFR:** a checker that eliminates an entire error class
  at compile time *is* the IFR for that class; normalization pushes to "every
  well-typed program terminates." [IFR]
- **Stage 4 — Structure from data:** smallest-set closure and "define the data
  first" are the same move; the derivation tree is the contract artifact.
  [Smallest-set closure]
- **Stage 5 — Resolve contradictions:** expressiveness-vs-conservativity is a
  technical contradiction resolved by refining precision, never by weakening
  safety; progress/preservation splits "safe vs capable" into two separable
  proofs. [Contradiction], [Separation]
- **Stage 6 — Make the minimal safe change:** the uniform per-feature pipeline is
  the minimal verified delta — every new construct lands as a provably local,
  tested diff. [Minimal verified delta]
- **Stage 8 — Verify, record, ship:** the proof-pass — a progress/preservation-
  style argument or a substitution-model trace over the diff — as the ultra-level
  verification; the derivation tree is the test-as-proof artifact. [Test as proof]

Cross-links: `method-map.md` (escalation — type-safety is the ultra verification
pass), `deep-modules.md` (static contract behind a simple interface),
`design-recipe.md` (data-first discipline), `algorithm-strategies.md`
(unification as an algorithm), `red-flags.md` (types as the static audit).
TRIZ engine: `references/software-triz.md`,
`references/ideal-final-result.md`, `references/trimming.md` (Rule A — the check
vanishes once proven unnecessary), `references/contradiction-analysis.md`,
`branches/fields/software`.

## Source
Original operational synthesis from the type-safety literature.
