# legacy-change

Safe change on code that has no tests. The problem is never "this code is ugly" —
it's "I can't change this safely" — so the method is: put a test net in place
first, then make the change in baby steps. Legacy code is simply code without
tests. Source: *Working Effectively with Legacy Code* — Michael C. Feathers.

## When to use it
- Any change to untested code: a new feature, a bug fix, a refactor.
- A method you must run under test calls a nasty dependency (global, I/O, third-party) that must be neutralized or swapped.
- New behavior must execute on every call to an existing method you can't get under test.
- You must change code whose intended behavior is unknown or untrusted.
- You must decide *which* tests to write for a change, instead of testing everything or nothing.
- Many changes land in one area and you want maximum coverage from minimum test code.
- First edits into code with no tests at all, where tests can't yet catch a break.

## Core method

### The master loop [Legacy Change Algorithm]
The 5-step meta-method that routes every legacy task:
1. **Identify change points** — where the behavior must differ.
2. **Find test points** — where a test can sense the change.
3. **Break dependencies** — use seams already latent in the code.
4. **Write tests** — cover the behavior you're about to touch.
5. **Make the change, then refactor** — baby steps, one behavior per edit.
Run this for ANY change to untested code. Every episode delivers value while
leaving a small island of tested code behind — the net effect is safe change now,
more test coverage later.

### The seam model [Seam]
A seam is an existing **substitution point**: a place in the code where you can
swap one implementation for another (a virtual method, an injected dependency, a
build-time binding) so a test sees different behavior without the edited code
changing at all. Before editing the risky line, look for a seam already in the
code and swap the dependency instead — you never touch the code under test.

| Software concept | TRIZ concept |
|---|---|
| Seam | Existing resource (`resource-analysis.md`) |
| Object seam (subclass + override) | Segmentation + superposition of a small difference |
| Test double / fake collaborator | Resource substitution — replace a harmful dependency with a controllable one |
| Break dependency | Trimming / relocating an obstructing dependency |

Seam types — name the type when you plan the change:
- **Object seam** — a virtual method you can override in a test subclass.
- **Preprocessing seam** — a build step substitutes a different implementation.
- **Link seam** — the linker / DI container binds a different implementation at assembly time.
- **Compile seam** — alternative code selected by a compile-time flag.

### Sensing and separation [Sensing] [Separation]
Two companion skills for getting hidden values out and bad dependencies out:
- **Sensing** — observing a value the method computes but never returns. Two levers: a *sensing variable* (a field the test subclass sets/reads) or a *fake collaborator* (a test double that records calls and values).
- **Separation** — getting the code into a test harness by breaking its dependencies (via a seam, an extraction, or parameter injection).

| Situation | Move |
|---|---|
| Method computes a value you can't see | Sensing variable in a test subclass |
| Method calls a collaborator that can't run under test | Fake collaborator records the call |
| Method hard-codes a global or a constructor | Extract the dependency, inject it |
| Class can't be constructed in a harness (construction blob) | Sprout Class, or extract the construction |

### Add code without touching old code [Sprout Method] [Sprout Class]
Prefer adding new tested code *beside* the old untested code over editing inline —
inline edits mix new and old and create untested temporaries.

| Move | What | Use when |
|---|---|---|
| [Sprout Method] | New behavior as a brand-new method: locals become parameters, result returned. Call it from the old method. Develop test-first. | The change is a distinct piece of work and you can't get the source method under test. |
| [Sprout Class] | Same, one level up: new behavior in a whole new class; constructor takes the needed locals; instantiate from the source class. Develop test-first in isolation. | Sprout Method is blocked — the class can't be constructed in a harness. |
| [Wrap Method] | Rename the old method; create a new method with the original name and signature that runs the new feature before/after the old logic. | New behavior must execute on every call to an existing method (temporal coupling). |
| [Wrap Class] | A wrapper object delegating to the wrapped one. | Same need at class level. |

Every one of these [Preserve Signatures] — callers are unaffected. That is the
Ideal Final Result applied to refactoring: new function achieved, original
function intact, no regression.

### Characterization tests [Characterization test]
Tests that document **actual behavior, not spec** — a net to detect future
divergence, not a verdict on correctness:
1. Write an assertion you know will fail.
2. Run it; let the failure tell you what the code does.
3. Lock that expectation in as the baseline to preserve.
You are not bug-hunting. You are defining success as "no harm" before adding good.

### Effect analysis and pinch points [Effect analysis] [Pinch point]
Decide which tests to write by tracing consequences forward from the change:
1. **Effect sketch** — one bubble per mutable variable; an arrow to every method whose value can change at runtime.
2. Reason forward from the change point: which methods can be damaged by this change? Those are the ones a test must sense.
3. Find the **pinch point** — the one or few places where a small set of tests senses a wide set of downstream effects. Test there.
If many changes land in one area, a few tests at the pinch point cover them all.

### Safe first incisions [Safe first incisions]
The discipline for the first break-dependency edits in code with no tests at all —
tests can't yet tell you if you broke something, so the editing itself must be hypercareful:
- **Hyperaware editing** — know exactly what each keystroke does.
- **Single-goal editing** — one behavioral change per edit.
- **Preserve signatures** — never break a caller.
- **Lean on the compiler** — let it catch what tests can't.
- Small, compile-checked, reversible steps; never a big-bang edit.

### TRIZ mapping
- The central contradiction — to change safely you need tests, but to write tests you must change the code — is resolved not by force but by using **seams already latent in the system** (TRIZ resource analysis): the free resources are the object/preprocessing/link seams already present; you substitute a controllable test double for the harmful dependency (trimming + resource substitution).
- Sprout/Wrap are **Segmentation** + **Prior Action**: don't modify the original function — keep it intact and add new behavior beside/around it.
- Characterization tests are **reverse IFR**: pin actual current behavior as the baseline to preserve before adding good.
- Effect sketches are **cause-effect analysis**; pinch points are the leverage point where a small test force controls a large effect region (**Local Quality** / the key x-resource).
- Sensing + characterization tests implement **Feedback** — a measuring mechanism that reports divergence; fake collaborators act as **Intermediary**.
- The dependency-breaking catalog is a **trimming table**: many ways to remove or relocate an obstructing dependency.

## Worked example
A legacy `checkout(cart)` charges via a hard-coded `PaymentGateway` field that
hits the network; there are no tests. You must add tax before the charge.

1. **Seam** — the gateway is a private field. Add a virtual getter `getGateway()` (one signature-preserving edit); a test subclass overrides it with a fake that records `lastAmount`. The seam was already latent in the field.
2. **Characterization test** — assert `checkout(basketOf(2)).total == 0`; the failure prints the real total; pin that as the baseline.
3. **[Sprout Method]** — write `computeTotal(items)` test-first (pure: params in, result out, no gateway), then call it from `checkout`.
4. **Effect analysis** — `total` is a mutable variable read only by `charge()`; that read is the pinch point, so one assertion on the fake's `lastAmount` senses the whole change.
5. Ship: one getter extraction + new method + one characterization test + one behavioral test. Old logic untouched.

## How it feeds the pipeline
Powers **stage 6 (Make the minimal safe change)** — the full Feathers path
(change points → test points → seams → tests → change). Also feeds **stage 1
(Frame the task)** (what is safe to change), **stage 7 (Review with red flags)**
(did the diff preserve every useful function; was a dependency trimmed, not the
behavior), and **stage 8 (Verify, record, ship)** (the characterization test IS
the proof).

- Siblings in this folder: `method-map.md` (the router sends "legacy/untested code that must not break" here), `rewrite-ladder.md` (ponytail ladder — sprout/wrap are its legacy expression), `red-flags.md` (audit the diff), `construction-checklist.md` (debugging loop — characterize before touching), `type-safety.md` (verification pass).
- TRIZ files: `triz-innovation/references/software-triz.md` and `triz-innovation/branches/fields/software` (seam = resource, dependency-break = trimming, feedback/intermediary principles).

## Source
*Working Effectively with Legacy Code* — Michael C. Feathers.
