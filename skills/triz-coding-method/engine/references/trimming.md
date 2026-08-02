# Trimming

Trimming = **delete a component but keep its useful function**, by handing that
function to something that remains. It's the most direct way to raise ideality:
fewer parts, same value. Always do `function-analysis.md` first — you trim
functions, not random parts.

## When to trim
- The function table shows redundant, costly, or harmful-side-effect components.
- A part exists only to support another part (auxiliary, not main function).
- You're told "it's too complex / too expensive / too many steps."

## The trimming question (key problem)
> IF we remove **[component]**, THEN [benefit: less cost/complexity/harm], BUT
> [its useful function is lost]. **How do we keep [function] without [component]?**

## The three trimming rules
- **Rule A — the object disappears.** Trim the tool if the object of its useful
  function is itself removed/no longer needs the action.
  *(No dirty dishes → no dishwasher. No manual data entry → no validation step.)*
- **Rule B — the object does it itself.** Trim the tool if the **object performs
  the function on itself** (self-service).
  *(Self-cleaning surface; a form that validates as the user types; an exercise
  that auto-logs because the motion sensor already sees it.)*
- **Rule C — another component does it.** Trim the tool if **another existing
  component** can perform the function. Guidelines:
  1. another component does the **same function on the same object**,
  2. on a **different object**,
  3. a **different function on the same object**, or
  4. another component has the **resources** to take it on.
  *(The phone's calendar already nudges — trim the app's separate reminder engine.)*

## Procedure
1. From the function table, pick the component to trim (favor costly/harmful/redundant).
2. Write the trimming key problem.
3. Try Rule A, then B, then C in order (A is the biggest win — the need vanishes).
4. For Rule C, scan the resource inventory (`resource-analysis.md`) for a
   component that already has what's needed.
5. Verify the main function survives and no new harmful function appears.

## Trimming + contradiction
Trimming often surfaces a contradiction ("if we remove it we lose X"). That's
good — hand the residual "how do we keep X without it" to
`contradiction-analysis.md` / `physical-contradictions.md`.

## Output
For each trim: what's removed, which rule, who inherits the function, net effect
on cost/complexity/harm, and any new contradiction created. Tag `[Trimming Rule
A/B/C]`.
