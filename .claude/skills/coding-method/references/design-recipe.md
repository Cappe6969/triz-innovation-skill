# design-recipe

The design recipe: a fixed sequence — data definition → signature/purpose/
stub → functional examples → template from the data → body → examples as tests —
that turns any problem statement into a correct program mechanically. Its one
idea: **the structure of the program follows the structure of its data.** Reach
for it whenever the structure is novel or unclear and you don't know what to
write first.

## When to use it
- The problem statement names information you must encode before you can write a
  function — start with a data definition, not a function.
- You're staring at a blank screen: the recipe gives you a guaranteed next step.
- A function's structure (recursion, conditionals) isn't obvious from the task.
- A structural function is slow because it re-traverses its input (O(n²)).
- A problem splits into several tasks, or a helper appears mid-design.
- Two function bodies look almost identical (abstraction is due).
- You're writing a genuinely new algorithm (sorting, search, backtracking).
- Route: method-map.md sends "novel structure, design unclear" here
  (stages 1 → 7, full recipe).

## Core method

### The six-step design recipe [Design recipe]
1. **Data definition first** [Data definitions first] — name the class of data
   with an interpretation comment. Program on information, not raw values.
2. **Contract before code** [Contract before code] — one line `Input -> Output`,
   one line of purpose ("what does it compute?"), then a **stub** body returning
   any piece of the output class.
3. **Functional examples** [Examples as tests] — work out concrete in/out pairs
   by hand *before* the body exists. These become the tests.
4. **Template from data** [Template from data] — translate the data definition
   into a `cond` skeleton mechanically: one clause per data clause, a
   recognizing question per clause, a selector per field. The template is the
   **inventory** — it lists exactly what you are allowed to compute with.
5. **Code the body** — fill each clause, combining values from the inventory.
6. **Examples become tests** — the hand-worked examples are the test suite; no
   separate test-authoring step.

### The data-shapes table (how the recipe extends)
| Data form | Example | Template shape | Selectors |
|---|---|---|---|
| Enumeration | red/green/blue | one `cond` clause per value | none |
| Interval | numbers in a range | numeric test + two clauses | none |
| Structure | (make-posn x y) | one clause, test the structure | field selector per field |
| Itemization | atomic or structure | one clause per alternative | per alternative |
| Self-referential list | empty or (cons x rest) | base clause + recursion clause | first, rest |
| Natural numbers | 0 or (add1 n) | zero? clause + recursion clause | sub1 |

Each new form of data extends the *same* recipe — there is one method, not one
per kind of program.

### Natural recursion / leap of faith [Natural recursion]
For self-referential data, recur on the self-referenced sub-piece (the arrow in
the data definition) and **assume the recursion already satisfies the purpose
statement**, then combine. The recursion is dictated by the data, never
invented — so a structural function cannot have the wrong shape.

### The table method — guessing the combinator [Table method]
Stuck on "combine the values" in step 5? Tabulate sample inputs, the
intermediate template-expression values, and the desired outputs side by side;
stare at the rows until the result column reveals the combining expression.

### Wish lists [Wish list]
Keep a running list of needed auxiliary functions (name + signature + purpose).
Pick a wish, design it, add new wishes discovered along the way, stop when the
list is empty. One single-purpose function per task (average = sum + count +
divide).

### Abstract from examples [Abstract from examples]
1. Diff two nearly-identical definitions.
2. Mark the differing values; add one parameter per differing line.
3. Validate: redefine the originals in terms of the abstraction.
4. Before keeping it, search the library for an existing abstraction (map,
   fold) — [Stdlib first]. Only generalize from real concrete examples; never
   pre-invent abstractions [YAGNI].

### Algorithm recipe + termination argument [Algorithm recipe]
For generative recursion (input is restructured, so data no longer dictates the
recursion), answer four questions — what's trivially solvable, how to solve the
trivial case, how to generate smaller new problems, how to combine solutions —
and add the seventh step: **an argument that every call shrinks the problem**,
or an illustration of an input on which it loops [Termination argument].

### Accumulator style + invariant [Accumulator style]
When a structural function re-traverses the result of its natural recursion
(typically O(n²)), add an extra parameter that accumulates knowledge, write an
**invariant** relating the accumulator to the original argument, initialize it,
and use it in the base case. Turns O(n²) re-traversal into one pass.

### TRIZ mapping
| Software concept | TRIZ concept |
|---|---|
| Structure of data dictates structure of program | [IFR] — the solution is derived from the problem's own structure, not imposed |
| Template from data | [Trimming Rule] — drop selectors the function doesn't use (e.g. how-many ignores `first`) |
| Inventory of what's given | [Resource analysis] — compute only from parameters, constants, selectors, library functions |
| Accumulator parameter | [Separation] — resolves "traverse once (fast)" vs "need whole input (re-traversal)" by separating the conflict in space (a parameter) |
| Termination argument | [IFR] — the check that every valid input yields a result |
| Abstract from examples | [IP-1 Segmentation] / parameterization of the differing parts, with a validation loop that re-proves the originals |
| Wish list | [IP-1 Segmentation] — split the program into single-purpose sub-functions |
| Natural recursion / leap of faith | Solve the sub-problem within the system: trust the recursive sub-solution and combine |

### Ponytail reconciliation [Ponytail off]
The recipe mandates design artifacts *before* code; ponytail is code first, then
≤3 lines of explanation. For a trivial, known pattern the full recipe is heavy
ceremony — drop to the ladder one-liner. The two methods agree where it counts:
no abstraction until two concrete examples exist (YAGNI), stdlib before own
code, stub-then-fill is a minimal working skeleton, examples double as tests.
The one real conflict: the recipe's purpose statement is a load-bearing artifact
written before code, while ponytail defers explanation. Resolution: **always
write the one-line purpose; treat the rest of the ceremony as optional for
known patterns** [Design recipe].

## Worked example
Summing a list, recipe-walked:

```
; A List-of-Numbers is empty or (cons Number List-of-Numbers)
;   interpretation: the whole sequence                    <- data definition
; sum : List-of-Numbers -> Number                          <- signature
;   purpose: total of all the numbers                      <- purpose
; stub: (define (sum l) 0)                                 <- stub
; examples: (sum empty) = 0
;           (sum (cons 2 (cons 5 empty))) = 7              <- examples
; template from data (one clause per data clause):         <- inventory
;   (define (sum l)
;     (cond [(empty? l) ...]
;           [else (... (first l) ... (sum (rest l))) ]))
; body — leap of faith: (sum (rest l)) is already the      <- step 5
;   total of the rest, so combine with +:
;   (define (sum l)
;     (cond [(empty? l) 0]
;           [else (+ (first l) (sum (rest l))) ]))
; tests: (check-expect (sum empty) 0)                      <- examples as tests
;         (check-expect (sum (cons 2 (cons 5 empty))) 7)
```

Each line was forced by the previous line — that's the point of the recipe: no
blank-screen invention, every choice is mechanical.

## How it feeds the pipeline
- **Stage 4 — Structure from data**: this file is the home stage. Data
  definition + signature + strategy before any code.
- **Stage 1 — Frame the task**: the data definition is the neutral restatement —
  encode the information the problem names before touching behavior.
- **Stage 6 — Make the minimal safe change**: stub-then-fill is the minimal
  skeleton; examples-as-tests protect the change.
- **Stage 7 — Review with red flags**: bodies that don't follow their template,
  unused selectors (trim them), and duplicated bodies (abstract) are red flags.
- **Stage 8 — Verify, record, ship**: the examples *are* the verification — no
  separate test-authoring step.

Siblings: `method-map.md` (router), `deep-modules.md` (complexity of the
module), `rewrite-ladder.md` (drop to one-liner for known patterns),
`algorithm-strategies.md` (complexity + strategy catalog),
`computation-models.md`, `red-flags.md`, `type-safety.md` (a stronger
verification pass). TRIZ side: `software-triz.md`, `trimming.md`,
`resource-analysis.md`, `ideal-final-result.md`, `contradiction-analysis.md`,
`branches/fields/software`.

## Source
Original operational synthesis from the design-recipe literature.
