# red-flags

The review audit for the coding-method: one checklist that catches complexity
where it is introduced, not after it has compounded. It merges three catalogues —
the design red flags, the class- and routine-design filters, and the refactoring
triggers. Reach for it when you finish a change and before you ship it, and as
the training ground for reviews of others' code (it is far easier to spot
complexity in someone else's code than in your own).

Complexity is incremental — hundreds of small doses, never one big event — so a
single red flag is a stop-and-redesign signal, not a cosmetic nit. Every flag
below ultimately produces one of three symptoms: **change amplification** (one
idea touches many places), **high cognitive load** (a reader must hold too much
at once), or **unknown unknowns** (behavior no one can see coming).

## When to use it
- You just made a change and are about to commit / merge (the stage-6 → 8 gate).
- You're reviewing a pull request or a teammate's diff.
- A class, function, or API "feels wrong" but you can't say why — run the hunt.
- You wrote something that took multiple attempts or produced a "smell" while coding.
- A design decision was deferred ("we'll fix it later") — that's exactly when to flag it.
- Someone says "it works, just don't look too closely."

## Core method

### Run the audit (procedure)
1. **Read the diff top-down** as a caller, not an author — what does each new
   boundary hide, and what does the interface force the caller to know?
2. **Hunt the catalogue** (table 1). One hit = stop, look for an alternative
   design that eliminates the flag, don't add a comment and move on.
3. **Check the design filters** (table 2) at every class/routine boundary you
   touched or created.
4. **Run the refactor triggers** (table 3) over the changed code — these are the
   cheap, mechanical cleanups that should be done *before* the audit, not left
   for "a refactor later".
5. **Adopt zero tolerance:** complexity is incremental [Zero tolerance], so a
   modest flag ("it's only a bit unclear") is accepted at the same rate the
   project decays. Refuse it at the source.
6. Reviews are practice: review someone else's code to sharpen your eye, then
   re-read your own diff with that eye.

### Table 1 — the red-flag catalogue
| Flag | What it looks like | Fix |
|---|---|---|
| [Shallow module] | Interface costs as much as the implementation; the module hides almost nothing | Merge into the caller or redesign the boundary so it hides more than it exposes |
| [Information leakage] | The same design decision appears in two+ modules; a change ripples | Encapsulate the volatile decision in exactly one place |
| [Temporal decomposition] | Structure mirrors the runtime *order of operations* (a class per pipeline stage) instead of the knowledge each part hides | Re-decompose by the information concealed, not the timeline |
| [Overexposure] | The interface exposes far more than callers need (extra public methods, visible internals) | Shrink the interface to the essential operations |
| [Pass-through method] | A method does nothing but forward its arguments to another | Delete the middle; callers reach the real method |
| [Pass-through variable] | The same value threaded through many layers that never use it | Store it where it's finally needed, or bundle related params |
| [Repetition] | The same logic copied in several places | Extract to one deep place — prefer the abstraction that *eliminates* the code over a low-level helper that just relocates it |
| [Special-general mixture] | A module mixes one caller's special cases with general-purpose logic | Split; keep the general path clean, push special cases up to the callers |
| [Conjoined methods] | Two methods only make sense together; callers must remember to invoke both | Merge into one unit so the pairing is internal |
| [Comment repeats code] | The comment restates what the code literally shows | Delete it; fix the code to be self-evident |
| [Documentation describes implementation] | Interface docs explain *how* it's built instead of the caller's contract | Rewrite from the caller's view: what you pass, what you get, what it guarantees |
| [Vague name] | Name says nothing (data, value, handle, generic nouns) | Rename to something that creates a precise image |
| [Hard to pick name] | You can't find a name that fits — a signal the abstraction is muddled | Fix the design, not the name |
| [Hard to describe] | You can't write a concise complete interface comment | Redesign; a good interface is describable in 1-2 sentences |
| [Nonobvious code] | Behavior a reader can't safely guess from reading | Document the non-obvious decision, or restructure until it's obvious |

### Table 2 — design filters
Check every class and routine boundary:
- [Manage complexity] — a reader can hold this unit in one head; it works at the
  highest abstraction and speaks the problem's language, not the plumbing's.
- [Consistent abstraction] — the class models one coherent concept behind a
  complete, minimal, non-leaky interface.
- [Hide secrets] — the design decisions most likely to change are concealed
  behind a stable interface; [Isolate likely changes] confines each likely change
  to a single spot.
- [Loose coupling] — few, small, clear connections to the outside; low-to-medium
  fan-out; utility layers earn high fan-in.
- [High cohesion] — the internals are strongly related to one purpose.
- [Standard techniques] — prefer named, standard solutions over exotic custom
  designs; familiarity is a feature for the next reader.
- [Leanness] — nothing more can be taken away; before adding anything ask *"what
  will we hurt by putting it in?"* — it costs development, review, testing, and
  compatibility forever.
- [Defer decisions] — don't force closure on the last 20% you lack information
  for; if stuck, switch mediums (English → sketch → prototype → brute force).
- Routine checks: [Short routine] (single purpose, roughly one screen),
  [Parameter discipline] (few params, consistent order, self-documenting names,
  no output-only surprises).

### Table 3 — refactoring triggers
Run these over any code you touch; each has a mechanical move:
| Trigger | Move |
|---|---|
| [Duplicate code] | Extract the method / DRY |
| [Long method] | Split by responsibility until each part is one screen |
| [Weak cohesion] | One method doing several jobs → split |
| [Too many parameters] | Bundle into a request/parameter object |
| [Magic number] | Named constant |
| Comments explaining hard code | Rewrite the code to read clearly |
| [Public instance variable] | Encapsulate behind accessors/methods |
| [Middleman] | Delete the middleman; call the real object |
| Code that knows the answer but keeps going | [Early return] — return as soon as the answer is known |
| [Root cause] | Never special-case a symptom; fix the harm at its source |

### When the flags are the symptom, debug the cause
If a change ships with several flags, don't patch each one — that's patching
symptoms. The underlying defect is a design boundary drawn in the wrong place.
Re-run the [Systematic debugging loop] at design level: characterize the failure
(multiple flags = one root), isolate the wrong boundary, redraw it once, and
verify with the audit again.

## Worked example
Reviewing a change that added `processOrder`:

```
processOrder(customer, items, discount, address, shipping, payment)   // 6 params
  ...
  submit(order)                        // [Pass-through method]
    authorize(payment)                 // just calls gateway.authorize(payment)
  for item in items:                   // [Duplicate code] — cart.applyDiscount exists
    item.price -= item.price * discount
```

Audit hits: [Too many parameters] → bundle into `CheckoutRequest`; the
`authorize`/`submit` chain is a [Pass-through method] → delete `submit`, give
`Payment` a deep interface; the discount loop is [Duplicate code] → reuse
`cart.applyDiscount`. One pass, three flags, each with a mechanical fix — the
redesigned boundary is a deep `Checkout` module and the diff shrinks.

## How it feeds the pipeline
Powers **stage 7 (Review with red flags)** — the audit that closes a change.
Also feeds **stage 3 (Sketch the IFR)** — [Hard to describe] and [Shallow module]
are design-time flags that say *redesign, not more comments*; and **stage 6
(Make the minimal safe change)** — the audit is the gate that proves the minimal
solution didn't just relocate complexity.

Cross-links: this file is the review half of `references/method-map.md`;
`references/deep-modules.md` is the design half (deep modules are the fix for
most of table 1); `references/construction-checklist.md` holds the routine-craft
and debugging loop; `references/legacy-change.md` gives the characterization
tests that make a red-flag fix safe on old code; `references/design-recipe.md`
feeds stage-4 structure so flags don't appear at birth. TRIZ side: flags are
symptoms of TRIZ harm — see `triz-innovation/references/software-triz.md`
(harmful function = coupling, over-generalization, non-obviousness) and
`triz-innovation/references/trimming.md` (table 3 moves are trimming: keep the
function, remove the element); the software branch is
`triz-innovation/branches/fields/software/branch.json`.

## Source
Original operational synthesis from the design-review literature.
