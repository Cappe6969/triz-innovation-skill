---
name: triz-coding-method
description: "Use for a coding or software-design decision with a real trade-off, contradiction, or request for the smallest safe solution: simplifying an overbuilt change, choosing an algorithm/API/module boundary, changing risky legacy code, or resolving 'improve X without worsening Y.' Do not use for routine mechanical edits or general non-software innovation."
---

# TRIZ Coding Method

Find the smallest safe solution. Lazy Ideality is the default: remove work and
reuse existing capability before designing anything new. TRIZ is an escalation
engine, not a ceremony to run on every task.

## Choose a mode

- `lite`: a familiar, low-risk local change. Frame, ladder, IFR, verify.
- `focused`: default for `auto`. Add only the conditional analysis the task
  signals require.
- `ultra`: high-risk, cross-system, irreversible, or unusually ambiguous work.
  Compare alternatives and run the full review.

If the user supplies a mode, honor it. Otherwise use `focused`; choose `lite`
only when the change is clearly routine, and `ultra` only when concrete risk or
complexity justifies it.

## Method

1. Frame the decision in one neutral sentence. Name required behavior, harmful
   effects, constraints, and the evidence that will prove success.
2. Walk the ladder in order and stop at the first sufficient rung:
   1. delete the requirement or code;
   2. use the standard library or a native platform feature;
   3. configure or compose existing behavior;
   4. adapt code already present;
   5. add the smallest new code.
3. State the Ideal Final Result: the behavior happens with no new mechanism.
   Then state the almost-IFR: the least mechanism that can actually deliver it.
4. Load conditional guidance only when signaled:
   - data shapes or algorithmic scale: `references/design-recipe.md`,
     `references/algorithm-strategies.md`, and
     `references/computation-models.md`;
   - data-system consistency or storage: `references/data-systems.md`;
   - legacy or untested code: `references/legacy-change.md`;
   - a defect: characterize the failure, isolate the cause, then regression-test
     the fix using `references/construction-checklist.md`;
   - a significant architecture decision: `references/architecture-tradeoffs.md`.
5. Ask whether a contradiction still remains. A contradiction has two required
   qualities that cannot both be obtained with the current design. If none
   remains, do not invoke TRIZ. If one remains, use
   `references/triz-for-code.md` and the internal `engine/` to eliminate it by
   separation, trimming, resources, or inventive principles before accepting a
   compromise.
6. Make the smallest safe change. For nontrivial changes, review with
   `references/red-flags.md`; skip the full catalogue for a tiny local edit.
7. Verify with tests or other reproducible evidence. Report assumptions and
   residual risk; do not invent measurements.

The router at `scripts/method.py` can produce the structured stage selection.
The general TRIZ CLI at `engine/scripts/triz.py` remains available for
non-coding analysis, but it is not a second public skill.

## Output

Lead with the selected solution, then the reason it is the smallest safe one,
verification, and any remaining trade-off. Keep method names and stage tags in
structured notes unless the user asks for the analysis; normal output should be
concise.
