# deep-modules

Complexity is the enemy, and modular design is how you fight it. Reach for this
whenever you draw a module/class/function boundary, choose an API, or a design
feels tangled but you can't say why.

## When to use it
- Drawing any module, class, function, or API boundary.
- A first-draft decomposition feels wrong but the reason is unclear.
- An API needs an exception or config option for every caller.
- A feature threatens to ripple across many files.
- Refactoring a call chain that forwards the same parameters through 3+ functions.
- Code review / self-review of a design for complexity (hardest to see in your own code).
- Splitting, merging, or extracting classes after a first decomposition pass.

## Core method

### The complexity model
- Complexity = **dependencies** (a change forces other changes) + **obscurity**
  (you can't tell what's going on). [Complexity]
- It accrues incrementally — hundreds of small doses, not one event. Refuse each
  one at the source with **zero tolerance**; small kludges compound into
  macro-complexity. [Zero tolerance]
- The three symptoms: change amplification, high cognitive load, and — worst —
  **unknown unknowns** (you don't know what you don't know).
- Goal: the developer faces only a small fraction of the total complexity at a time.

### The deep module
A module is **deep** when its interface is much simpler than its implementation:
a lot of hidden functionality behind a small, simple interface. [Deep module]
- A module's **benefit is its functionality**; its **cost to the system is its interface**.
- Depth = the fraction of complexity that is invisible to the module's users.
- The ideal module approaches **zero interface** — the garbage-collector ideal:
  the `free()` the user used to call is simply gone. In TRIZ terms that is
  trimming the function away, not hiding it.
- **Anti-classitis rule:** deep classes beat many small shallow ones. Do not
  split a method just because it is "long" or "does too much" — split it only
  when the parts are independently useful. Refuse structure that does not earn
  its keep (the same instinct as ponytail's minimum code). [Classitis]

### Translation table
| Software concept | TRIZ concept |
|---|---|
| Deep module | Trimming + Ideal Final Result — interface shrinks toward zero |
| Dependencies + obscurity | The harmful function of software |
| Information hiding | Local quality — complexity lives where it costs least |
| Pull complexity down | Resource analysis — the module with resources absorbs the work |
| Define errors out of existence | Prior action (IP-10) + ARIZ re-framing — restate the problem so the error dissolves |
| Design it twice | Generate multiple strong alternatives before converging |
| Incremental complexity | Micro-contradictions compounding (uneven system development) |
| Pass-through method | Low-ideality solution that duplicates the harmful function |

### Information hiding
- Encapsulate the design decisions **most likely to change**. [Information hiding]
- A design decision must NOT appear in multiple modules — if it does, that is
  **information leakage**. [Information leakage]

### Different layer, different abstraction
- Each layer must provide a different abstraction from the layer below. [Different layer]
- **Pass-through methods** that merely forward args (and pass-through variables
  threaded across layers) duplicate the lower layer's interface and add
  complexity. Collapse them. [Pass-through method]

### Pull complexity downwards
- Push complexity into the module where it will be seen least. [Pull complexity down]
- Make the common case the default; extra mechanism is opt-in so most users
  never see it.

### Define errors out of existence
- Redefine the operation's contract so the exceptional case becomes normal
  behavior — e.g. "ensure this no longer exists" instead of "delete and error if
  missing". [Define errors out of existence]
- Fewer exception-handling sites; mask or aggregate what cannot be eliminated.
- TRIZ read: restate the problem so the contradiction dissolves (ARIZ-style),
  rather than patching the symptom.

### Strategic programming
- Reject tactical programming (get it working ASAP, kludge now, fix later).
  [Strategic programming]
- Keep zero tolerance toward small complexity additions; invest ~10-20% of effort
  on design even during feature work.

### Design it twice
- For any non-trivial design decision, implement two alternatives and pick the
  better one. [Design it twice]
- Cheapest on small isolated modules. Never ship the first idea just because it came first.

### Write the comments first
- Write the interface comments BEFORE the implementation — comments are a design
  tool. [Write comments first]
- If you cannot describe a method or class concisely and completely in advance,
  the design is probably wrong — redesign, do not add more comments.
- Ponytail read: the interface comment IS the ≤3-line explanation, written first
  so it constrains the diff.

### General-purpose core, special-purpose shell
- General-purpose modules tend to be deeper; keep them clean of one-off
  application logic. [General-purpose]
- Push specialization upwards: the special-purpose glue lives close to the caller.

### Obviousness and precise names
- Code should be obvious — a quick guess the developer is confident is correct.
  [Obviousness]
- Precise names that create an image, consistency, and no special cases. [Precise names]
- Comments document what is NOT obvious from the code — never repeat the code.

### The red-flag catalogue (audit any design)
[Red flag] — when one appears, stop and search for an alternative design that
eliminates it:
| Red flag | Fix |
|---|---|
| Shallow module | Merge it or deepen it [Shallow module] |
| Information leakage | Move the shared decision into one module |
| Temporal decomposition | Reorganize by design decision, not time order [Temporal decomposition] |
| Overexposure | Narrow the interface [Overexposure] |
| Pass-through method | Collapse the layers [Pass-through method] |
| Repetition | Extract once, then generalize [Repetition] |
| Special-general mixture | Split special glue from the general core |
| Conjoined methods | Merge them or insert an interface [Conjoined methods] |
| Comment repeats code | Delete it or upgrade it to the "why" [Comment repeats code] |
| Vague name | Rename to something that creates an image [Vague name] |
| Hard to pick a name | The design is muddled — redesign [Hard to pick name] |
| Nonobvious code | Add a comment or simplify the code [Nonobvious code] |

## Worked example

A file helper raises `FileNotFoundError` when asked to delete a path that is
already gone. Eight call sites each wrap it in try/except — scattered exception
handling you cannot distinguish from real failures.

1. **Frame:** 8 handlers across callers = obscurity + change amplification. [Complexity]
2. **Restate the contract:** `ensure_absent(path)` — "make sure no file exists at
   path". Missing file → nothing to do, success. The error case is designed out
   of existence. [Define errors out of existence]
3. **Result:** zero try/except anywhere; the function is deeper (stronger
   guarantee, smaller interface).
4. **Comment first:** "Ensures no file exists at path. True if anything was
   removed, True if nothing was there." If this sentence had been awkward to
   write, the contract would have been wrong. [Write comments first]
5. **Audit:** no pass-through, no leakage, one precise name — pass. [Red flag]

## How it feeds the pipeline
- **Stage 2 (Climb the ponytail ladder)** — deep modules are why a "one line"
  fix stays one line next month; interfaces should make the common case simple
  (YAGNI on API surface); anti-classitis refuses structure that does not earn its
  keep. [Deep module] [Classitis]
- **Stage 3 (Sketch the IFR)** — the ideal module has no interface (the garbage
  collector); a deep module is the almost-IFR; design it twice supplies the two
  candidates to compare. [Deep module] [Design it twice]
- **Stage 6 (Make the minimal safe change)** — pull complexity downwards and
  define errors out of existence are the change-time moves that keep a diff
  minimal and provably local. [Pull complexity down] [Define errors out of existence]
- **Stage 7 (Review with red flags)** — this file's red-flag catalogue is the
  audit; the full review checklist lives in `red-flags.md`. [Red flag]

Cross-links: siblings in this folder — `design-recipe.md` (data-first structure),
`architecture-tradeoffs.md` (system-level boundaries), `red-flags.md` (the audit),
`method-map.md` (stage router). TRIZ files —
`triz-innovation/references/software-triz.md`,
`triz-innovation/references/ideal-final-result.md`,
`triz-innovation/references/trimming.md`,
`triz-innovation/branches/fields/software`.

## Source
Original operational synthesis from the modular-design literature.
