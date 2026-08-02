# ARIZ — Algorithm for Inventive Problem Solving (simplified ARIZ-85C)

ARIZ is the heavy artillery of TRIZ: a **structured, sequential algorithm** for
problems that resist the quick tools (matrix, separation, trimming). You reach
for it only when (a) the problem is non-trivial, (b) the standard tools didn't
crack it, and (c) you don't yet understand the *real* contradiction. ARIZ's whole
purpose is to **reformulate a fuzzy problem until the core contradiction and the
solution become almost self-evident**.

> Rule of thumb: don't start with ARIZ. Start with framing + matrix + separation.
> Escalate to ARIZ when those stall. ARIZ is a worksheet, not a chat — fill every
> step in writing. Generate the worksheet with
> `python skills/triz-coding-method/engine/scripts/triz_ariz.py "problem title"`.

ARIZ-85C has 9 parts. This is a working subset — enough to run a real session.

## Part 1 — Analyze the problem (build the mini-problem)
1.1 State the **technical contradiction (TC)** in both directions:
- TC-1: if we do A, we gain X but lose Y.
- TC-2: if we do not-A (or the opposite), we keep Y but lose X.
1.2 Define the **conflict pair**: the two interacting elements (Tool & Object/
   Product) whose interaction is the conflict.
1.3 Pick the TC that **best preserves the main useful function**. State the
   *intensified* version (push the conflict to the extreme: "infinitely many",
   "zero", "instant") — extremes expose the real contradiction.

## Part 2 — Analyze the resources (the operating zone & time)
2.1 **Operating zone (OZ):** the exact space where the conflict happens.
2.2 **Operating time (OT):** the exact time window of the conflict (before /
   during / after — conflicts are often resolvable *before* they occur).
2.3 **Substance-Field resources (SFR):** list everything available *inside or
   around the OZ/OT* — substances, fields, space, time, the object itself, voids,
   by-products. (Cross-reference `references/resource-analysis.md`.)

## Part 3 — Define the Ideal Final Result & physical contradiction
3.1 **IFR-1:** "The **X-element** (some resource), by itself, eliminates the harm
   during OT within OZ, while keeping the useful function and adding nothing."
3.2 **Intensified IFR:** the X-element must use only resources already in the OZ.
3.3 **Physical contradiction (PC) at macro level:** the element in the OZ must be
   *P and not-P* (e.g. "hot and cold", "present and absent", "rigid and flexible")
   to satisfy both demands.
3.4 **PC at micro level:** particles/parts in the OZ must produce P and not-P
   (one region/state delivers P, another delivers not-P).

## Part 4 — Mobilize and apply resources
4.1 Apply the **separation principles** to the PC: separate the opposite demands
   in **time / space / condition / system level** (see `references/physical-
   contradictions.md`).
4.2 Apply the **76 standard solutions / Su-Field** model to the conflict
   (see `references/substance-field-analysis.md`).
4.3 Use **"smart little people"** modeling on the OZ if still stuck: imagine tiny
   agents that could satisfy P here and not-P there.

## Part 5 — Apply the knowledge base
5.1 Search **scientific/physical effects** that deliver the needed action with the
   available resources (see `references/scientific-effects.md`).
5.2 Reuse known **patterns/analogies** (function-oriented search): who else moves,
   heats, holds, separates, detects this cheaply elsewhere?

## Part 6 — Reformulate / change the problem
6.1 If no solution: was the **right problem** chosen? Switch to the other TC,
   widen the system (super-system) or narrow it (sub-system) and rerun.
6.2 Check whether the problem **disappears** if a constraint is removed or a
   different component is selected as the conflict pair.

## Part 7 — Analyze the solution
7.1 Does the concept introduce **new harms or costs**? Loop them back as new
   contradictions.
7.2 How many **resources** did it consume? Fewer = more ideal.

## Part 8 — Maximize the solution's use
8.1 Where else does this concept apply (other products, other parts of the
   system, the super-system)? Capture spin-off applications.

## Part 9 — Reflect on the process
9.1 What reformulation unlocked it? Save the case
   (`scripts/triz_case_template.py`) so the move is reusable.

## How ARIZ relates to the rest of the skill
- ARIZ **orchestrates** the other tools — it is the escalation path for stage 4/6
  of the main pipeline when contradictions are stubborn.
- The 3 engines it leans on hardest: **physical contradiction + separation**,
  **resource analysis (OZ/OT/SFR)**, and **Su-Field + standard solutions**.
- Output of an ARIZ run is always a **physical contradiction made resolvable** by
  a specific resource, then a concrete experiment (stage 10).
