# Substance-Field (Su-Field) Analysis & the 76 Standard Solutions

Su-Field analysis models *interactions* as the smallest working unit of a system:
**two substances (S1, S2) interacting through a field (F)**. A useful function
needs all three. When one is missing, weak, harmful, or excessive, the model tells
you *which kind of fix* applies — and the **76 Standard Solutions** are the catalog
of those fixes, grouped into 5 classes.

> Use this when the problem is about an **interaction** ("the brush doesn't clean
> enough", "vibration damages the bearing", "the reminder annoys the user") rather
> than a parameter trade-off. It pairs with the contradiction matrix, not replaces
> it.

## The model

- **S1** = the object/product (acted upon). **S2** = the tool/substance acting on it.
- **F** = the field carrying the action: Mechanical, Acoustic, Thermal, Chemical,
  Electric, Magnetic, Electromagnetic, Gravitational, **and in non-engineering
  domains: Informational, Social/Behavioral, Economic** (the field is whatever
  *carries the influence* — money, attention, a notification, a rule).
- Draw it: `S1 —[F]→ S2`. Mark the link:
  - **solid arrow** = adequate useful action
  - **dashed/thin arrow** = insufficient action
  - **wavy arrow** = harmful action

## The 5 diagnoses → which solution class

| Su-Field state | What you see | Go to class |
|---|---|---|
| **Incomplete** (S1 + S2 but no F, or a substance missing) | function doesn't happen at all | **Class 1** — complete the field |
| **Insufficient** | function happens but too weakly | **Class 1/2** — add/upgrade field |
| **Harmful** | an unwanted action accompanies the useful one | **Class 1** — block, neutralize, or add S3 |
| **Measurement/detection** problem | you can't sense or measure the state | **Class 4** — measurement standards |
| **Excessive / needs simplification** | works but too costly/complex | **Class 5 + Trimming** |

## The 5 classes of standard solutions (summary)

**Class 1 — Build or destroy a Su-Field (13 solutions).**
Complete an incomplete model; if a field is harmful, either *block* it, introduce a
third substance S3 that absorbs the harm, or *redirect* the harmful field onto a
sacrificial element. Core moves: add the missing substance/field; introduce S3
(often a modified version of S1 or S2, a void, a foam, an additive); switch to an
externally-added or environmentally-available field.

**Class 2 — Develop / enhance the Su-Field (23 solutions).**
Make a working model stronger or more controllable: chain Su-Fields (add another
S–F stage), move to a **double or complex Su-Field**, increase **controllability**
by upgrading the field (mechanical → electric → magnetic → electromagnetic, i.e.
toward more easily controlled fields), **fragment** substances (solid → powder →
liquid → gas → field), introduce **capillary/porous** structures, make the field
or substance **dynamic/rhythmic** (pulse instead of constant), and match field
frequency to the natural frequency of the object.

**Class 3 — Transition to super-system or micro-level (6 solutions).**
Combine the system with others into a **bi-/poly-system**, or drop to the
**micro-level** (act on molecules/fields rather than the whole part). "Solve it one
level up or one level down."

**Class 4 — Detection & measurement (17 solutions).**
If you must measure, first ask if you can **avoid measuring** (change the system so
the measurement isn't needed). Else: measure a **copy**, measure two states and
their **difference**, add an easily-detected **marker/additive**, exploit
**resonance** or a field the object naturally emits, measure **derivatives** of a
quantity instead of the quantity.

**Class 5 — Simplification & helpers / "how to apply 1–4" (17 solutions).**
Introduce substances/fields the *cheap* way: use **voids, foams, inflatable or
field-generated substances** instead of added matter; use **self-eliminating**
substances (ice, evaporating, dissolving) that vanish after acting; obtain a field
from the **environment** or from **phase transitions**; let the system **act on
itself** (self-service). This class is where ideality lives.

## Procedure (run it in order)
1. Identify the function as an interaction → draw `S1 —[F]→ S2`.
2. Classify the link: complete / insufficient / harmful / measurement / excessive.
3. Jump to the class above; pick 1–3 candidate moves.
4. Translate each into a concrete change to *your* system. Tag `[SS Class 2: field
   upgrade]` etc. The recommender does steps 2–3:
   `python .agents/skills/triz-innovation/scripts/triz_standard_solutions.py --state harmful`.
5. Hand the candidates to stage 8 (solution generation) and stage 9 (evaluation).

## Cross-domain field examples
- **Software:** S1 = user data, S2 = validator, F = a rule/check. Insufficient
  validation → Class 2 (chain checks; make the field dynamic = run on change).
- **Rehab/adherence:** S1 = patient, S2 = exercise plan, F = a reminder
  (informational field). *Harmful* (annoying) → Class 1: add S3 (context) so the
  field only fires when useful, or Class 5: self-service (the patient's own routine
  triggers it). See `references/rehabilitation-triz.md`.
- **Business:** S1 = customer, S2 = offer, F = price/attention. Insufficient pull →
  Class 2: upgrade the field (from static price to dynamic/segmented).
