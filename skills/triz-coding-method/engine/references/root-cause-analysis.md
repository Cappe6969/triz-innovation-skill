# Root Cause Analysis (Cause-Effect Chain) -- RCA+ Methodology

Trace a symptom down to the **root cause(s)** so you fix the disease, not the
fever. This reference implements RCA+ (developed by Valeri Souchkov), which extends
classical Root Cause Analysis in two fundamental ways: (1) it identifies
**contradiction causes** -- causes that produce both a negative and a positive
effect, so they cannot be simply eliminated; (2) it targets contradictions
**closer to the problem** rather than drilling to the deepest root, which yields
more ideal solutions. In TRIZ this feeds straight into contradiction analysis:
the best place to break a chain is where a cause sits behind a contradiction.

**Canonical source:** `TRIZ-MASTER.md` section 4 (Root cause analysis).

Repositories:
- `technical_triz/root_cause_analysis/` -- classical RCA materials.
- `technical_triz/root_conflict_analysis/` -- RCA+ methodology (Souchkov
  approach), cause types (N, N+P, NC, P), contradiction formulation templates.

---

## Step 1 -- Anchor the symptom

State the observable problem as a measurable effect. No causes yet.

Classify the symptom into one of four RCA+ problem categories:

1. **Negative effect** -- something happens that we do not want at all (a
   failure, defect, damage, loss, complaint). Example: "The compressor
   overheats and shuts down."
2. **Insufficient effect** -- a desired result is not achieved with the required
   degree of performance, quality, or completeness. Example: "Daily active
   patients dropped 30% after week 2."
3. **Excessive effect** -- a desired result is achieved but wastes too much of a
   costly resource. Example: "The onboarding flow completes but requires 90
   minutes of staff hand-holding per user."
4. **Ineffective control** -- we have the means of control but the control
   process is too slow, inaccurate, or unreliable. Example: "The dashboard
   refreshes every 10 minutes but the situation can change in seconds."

---

## Step 2 -- Build the cause-effect chain

Repeatedly ask **"What causes this effect to occur?"** (not "Why?" -- RCA+
prefers a cause-formulation question over an open-ended why, which can produce
vague answers). Allow branching -- a cause can have several parents, and a
node can have multiple contributing causes.

Each cause must be stated as a complete sentence using one of four
formulations (never a single word):

- A **function**: subject + action + object. Example: "The knife scratches the
  table surface."
- A **relative parameter value**: property + relative value. Example:
  "Temperature is too high."
- A **change of a property**: direction + property + relative value. Example:
  "The decrease in temperature is too fast."
- A **radical state change**. Example: "Key employee leaves."

Mark each cause as **factual** (verified by data or observation) or
**assumptive** (hypothetical, requires verification).

```
Symptom
 └─ what causes this? → cause A   [factual / assumptive]
     └─ what causes this? → cause A1   (deeper)
     └─ what causes this? → cause A2
 └─ what causes this? → cause B   [factual / assumptive]
```

### AND / OR relationships between causes

After listing causes for a node, determine how they combine:

- **AND**: All causes are required together. Removing any single one eliminates
  the downstream effect. Draw with an arc or bracket across the incoming
  arrows.
- **OR**: Each cause contributes independently. Any one alone can produce the
  effect. Removing one reduces the likelihood but does not guarantee
  resolution; all must be addressed to fully prevent the effect.

For a specific problem in a known system, causes are usually AND-related. For
broad failure prevention across varied conditions, causes can be OR-related.

Document each AND/OR group explicitly:

```
Symptom
 ├─ AND ─ cause A
 ├─ AND ─ cause B       ← both A and B must be present; remove either → symptom gone
 └─ OR ─ cause C        ← C alone could also produce the symptom
```

### RCA+ stopping rules

Stop expanding a branch when you hit any of:

- a **contradiction cause (N+P)** -- the cause produces a positive effect
  alongside the negative one; this is exactly where TRIZ inventive resolution
  should be applied (the **"stop at first contradiction cause" rule** -- do NOT
  drill deeper below an N+P cause; instead, hand it to contradiction analysis),
- a **non-changeable cause (NC)** -- beyond your control (laws of nature,
  supersystem constraints, policy outside your authority),
- a **requirement or demand** that cannot be changed.

The RCA+ principle is: closer to the top is better. Solving a contradiction
near the symptom produces more ideal solutions than drilling to the deepest
technically-possible root and solving there.

---

## Cause Classification: N / N+P / NC / P

Every cause in the chain is assigned one of four tags, per the RCA+ typology
(Souchkov). This classification is the core differentiator from classical RCA
and determines what you do with each cause.

### N -- Purely Negative

The cause is entirely negative. There is no positive effect it produces.
**Action:** eliminate or prevent it. These are the straightforward "just fix
it" causes.

- Example (factual): "The reminder fires at a random time" -- removing the
  randomness produces no downside.
- Example (assumptive): "The onboarding email is going to spam" -- must be
  verified before acting.

### N+P -- Negative + Positive (Contradiction Cause)

The same cause produces **both** a negative and a positive effect. You cannot
simply eliminate it because you would lose the positive effect. This is the
central discovery of RCA+ and the handoff point to contradiction analysis.

- Example: "Bristle surface is too hard" -- removes plaque (positive) but
  damages gums (negative). Eliminating hardness solves nothing; you must
  resolve the contradiction inventively.
- Example: "The notification is persistent" -- ensures the user sees it
  (positive) but feels annoying and drives churn (negative).

**The "stop at first contradiction cause" rule:** When you encounter an N+P
cause, do NOT expand its branch further. The deeper causes would only explain
why the positive effect exists, which is already understood. Instead, hand the
N+P cause directly to contradiction analysis (see `contradiction-analysis.md`).

### NC -- Non-Changeable

The cause contributes negatively but cannot be eliminated or modified because
it lies outside your sphere of influence (laws of nature, regulatory
requirements, supersystem constraints, or resources you cannot access).

- Example: "Surface of gums is too soft" -- you cannot change human anatomy.
- Example: "GDPR requires explicit consent" -- you cannot change the law.
- **Note:** Treat NC causes as boundary conditions. Do not expand them further.
  They constrain the solution space but do not block progress -- work around
  them by changing other causes in the AND group.

### P -- Positive Effect of an N+P Cause

A cause that is purely a positive effect resulting from an N+P contradiction
cause. Listed for completeness to document the full chain, but it is not a
target for change.

- Example: "All teeth are cleaned" -- this is the positive outcome of "Bristles
  move over the teeth (N+P)."

### Classification decision tree

For each cause, ask in order:

1. Does this cause also produce a useful/positive effect?
   - **Yes** → tag **N+P**. Stop expanding this branch. Document the positive
     effect. Hand to contradiction analysis.
   - **No** → continue to question 2.
2. Can we eliminate or change this cause?
   - **Yes** → tag **N**. Continue expanding this branch (deeper causes may
     reveal N+P or NC).
   - **No** (beyond our control) → tag **NC**. Stop expanding this branch.

---

## Step 3 -- Classify every cause

For each node in the chain, assign the full classification profile:

| Classification | Description |
|---|---|
| **N / N+P / NC / P** | RCA+ cause type (see Cause Classification section above). |
| **Surface vs deep** | How far down the chain from the symptom. |
| **Controllable vs not controllable** | Can you act on this cause? NC causes are not controllable by definition. |
| **Cause-behind-a-contradiction?** | An N+P tag automatically means YES -- hand to `contradiction-analysis.md`. An N-type cause may also sit upstream of or feed into a contradiction elsewhere in the chain; note this. |
| **Factual vs assumptive** | Is the cause verified by data/observation, or is it a hypothesis requiring investigation? Mark assumptive causes clearly. |
| **AND/OR relationship** | Is this cause part of an AND group (all required; removing one collapses the effect) or an OR group (each contributes independently)? |

Build a summary table as you go:

| ID | Cause | Type | AND/OR | Positive Effect | Negative Effect | Factual? |
|----|-------|------|--------|----------------|-----------------|----------|
| 1  | ...   | N    | AND    | --              | ...             | yes      |
| 2  | ...   | N+P  | AND    | ...             | ...             | assumptive |

---

## Step 4 -- Find leverage points

A **leverage point** is a controllable cause that, if removed, collapses the
most downstream effects. Prefer leverage points that are:

1. upstream (kill many effects at once),
2. controllable, and
3. cheap to act on.

**RCA+ selection guidelines:**

- **AND causes (contradiction type):** Solving any single contradiction cause
  in the AND group eliminates the entire negative effect. This is the highest
  leverage -- pick the N+P cause closest to the symptom.
- **OR causes:** All must be solved to fully prevent the negative effect.
  Prioritize by controllability and cost.
- **Closer to the top** is generally preferred -- more ideal solutions with
  fewer unintended consequences.
- **System-level** causes are preferred over supersystem causes (easier to
  change -- your own system vs. someone else's).
- **Fewer components** involved makes resolution easier.
- **N-type causes without contradictions** can be directly eliminated without
  inventive effort.

Rank causes by *(reach x controllability / cost)* and pick the top 1-2.

---

## Step 5 -- Convert to a problem to solve

Restate each leverage cause as a solvable problem. The formulation depends on
the cause type.

### For N-type causes (purely negative)

> "How to eliminate / prevent [cause]?"

Example:
> "Reminders fire at random times" -> *root cause* "we don't know the patient's
> active hours" (N, factual) -> **solvable:** how do we learn or infer the
> active window without asking?

### For N+P-type causes (contradiction causes)

Formulate both a **technical contradiction (TC)** and a **physical
contradiction (PC)**:

**TC:** "How to ensure [N+P-cause] to enable [positive effect] but avoid
[negative effect]?"

**PC:** "[N+P-cause] should be present/high/strong to [positive effect] AND
should be absent/low/weak to avoid [negative effect]."

Example:
> "Bristle hardness is too high" (N+P, factual) ->
> **TC:** "How to ensure bristles are hard enough to remove plaque but not
> hard enough to damage gums?"
> **PC:** "Bristle hardness should be high to remove plaque AND should be low
> to avoid damaging gums."

Both formulations are handed to stages 4-8 of the TRIZ pipeline
(`contradiction-analysis.md` for the 39 parameters and contradiction matrix,
then inventive principles).

### For NC-type causes (non-changeable)

Do not formulate a direct solution. Instead, treat the NC cause as a boundary
condition and reframe the problem around an upstream or sibling cause in the
same AND group.

---

## Pitfalls

- **Stopping at a blame-the-user cause** ("patients are lazy") -- push deeper
  to a system cause you can change. RCA+ specifically bans person-blaming as a
  terminal node.
- **Single-line chains** -- real failures usually have 2-3 contributing
  branches. If you have only one linear chain, you have probably missed AND
  relationships. Re-examine each node for co-requisite causes.
- **Confusing correlation with cause** -- apply the magic-wand test: remove the
  candidate cause mentally; does the symptom vanish? If not, it is correlated,
  not causal.
- **Expanding below an N+P cause** -- RCA+ explicitly forbids this. Once you
  identify a contradiction cause, stop that branch. Deeper causes explain why
  the positive effect exists, which is already known and does not help you
  resolve the contradiction.
- **Accepting NC too early** -- before tagging a cause as non-changeable,
  verify that it truly cannot be influenced. "Too expensive" is not the same as
  "non-changeable"; reclassify as N with high cost. "We don't have the talent"
  is not NC; it is N (hire or train).
- **Skipping the positive-effect check** (classification step) -- the most
  common RCA+ failure mode. Every cause must be checked: "Does this cause also
  produce a positive effect?" Failing to find N+P causes means you are doing
  plain RCA, not RCA+, and will miss the inventive resolution path.
- **One-word causes** -- "pressure", "temperature", "cost" are not causes. They
  are parameter names. RCA+ requires every cause to be a complete sentence
  (function, parameter value, change of property, or state change).
