# Function Analysis

Model the system as **functions**, not parts. A function is one component (the
**tool**) performing an **action** that changes or holds a **parameter** of
another component (the **object**). This exposes what to fix, what to remove, and
what to strengthen.

## Definition
> **Tool → Action → Object** ("broom *moves* dirt"; "display *informs* user";
> "reminder *prompts* patient").

**Magic-wand test:** if you delete the tool and the object changes, a function
exists. If nothing changes, it's not a real function (drop it).

## Step 1 — Component analysis (3 levels)
- **Super-system:** things outside you interact with (user, environment, other apps, the clinic).
- **System:** the thing you're improving.
- **Sub-system:** its internal parts.

## Step 2 — Build the function table
| Tool | Action | Object | U/H | N/I/E | Parameter changed/held |
|------|--------|--------|-----|-------|------------------------|

- **U/H** = Useful or Harmful.
- **N/I/E** (useful functions only) = Normal / Insufficient / Excessive.
  Harmful functions get `---`.
- **Main function** = the one that changes the target object in the super-system
  (the reason the system exists). Always identify it first.

## Step 3 — Read the table for opportunities
- **Harmful (H)** functions → eliminate, block, or convert to useful (Trimming / contradiction).
- **Insufficient (I)** → strengthen the tool or add a resource.
- **Excessive (E)** → throttle / make dynamic (often hides a contradiction).
- **Redundant** functions (two tools doing the same job) → trim one.
- **Trimming candidates:** any tool whose function could be done by the object
  itself or by another existing component → `trimming.md`.

## Non-engineering systems (business / clinic / workflow)
Functions still apply, just softer language:
- Tool = role / process / document / channel. Object = customer / staff / data / patient.
- Example: *Onboarding email (tool) informs (action) new patient (object)* — U,
  often **Insufficient**. *Reminder SMS prompts patient* — U but risks an
  **Excessive** harmful twin: *SMS annoys patient* (H).

Use the simplified business framing from
the upstream `prompts/business_triz/function_analysis/` material as a
template when the audience isn't technical.

## Output
A filled table + a 3-bullet summary: main function (and its N/I/E grade), the
worst harmful function, and the top trimming candidate.
