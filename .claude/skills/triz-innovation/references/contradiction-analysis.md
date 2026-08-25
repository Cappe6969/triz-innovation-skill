# Engineering Contradictions & the 40 Inventive Principles

An **engineering (technical) contradiction** = two parameters in conflict:
improving one degrades the other. TRIZ resolves it without compromise by applying
inventive principles that broke the same conflict in other fields.

## Step 1 — State it in canonical form
> **IF** we [change/improve X], **THEN** [Y improves], **BUT** [Z worsens].

Example: *IF we add more reminder notifications, THEN exercise adherence improves,
BUT user annoyance and uninstall risk increase.*

## Step 2 — Map to the 39 parameters (abstract the conflict)
Translate "what improves" and "what worsens" into generic engineering
parameters. Common, broadly useful ones:

| Theme | Generic parameters |
|---|---|
| Quantity/intensity | Amount of substance, Quantity, Force, Power, Energy use |
| Time | Speed, Duration of action, Loss of time |
| Reliability | Reliability, Stability, Ease of repair |
| Effort/complexity | Device complexity, Ease of operation, Ease of manufacture |
| Adaptability | Adaptability/versatility, Convenience of use |
| Harm/loss | Harmful side effects, Loss of substance, Loss of information |
| Comfort/UX (soft) | "Annoyance/friction", "Cognitive load" (business/UX mapping) |

For non-engineering domains, map by analogy: e.g. "annoyance" ≈ *harmful side
effects*; "engagement" ≈ *useful function / amount of action*; "manual work" ≈
*device complexity / ease of operation*.

## Step 3 — Look up the contradiction matrix
The matrix cross-references improving × worsening parameter → a shortlist of
inventive principles. In this repo the matrix ships as data — look cells up
with:
`python .claude/skills/triz-innovation/scripts/triz_matrix.py <improving_id> <worsening_id>`
(data: `scripts/data/contradiction_matrix.csv`). Use the script instead of
reading cells by hand.

If you have no matrix handy, the **most universally productive principles** are:
**1 Segmentation, 2 Taking out, 3 Local quality, 10 Prior action, 13 The other
way round, 15 Dynamics, 25 Self-service, 35 Parameter change.** Try these first.

## Step 4 — Apply each principle concretely
For each suggested principle, write a *specific* idea for THIS problem, not the
generic definition. Tag it `[IP-NN name]`. Full list: `inventive-principles.md`.

## Worked mini-example (physio notifications)
- Conflict: *useful action (engagement)* ↑ vs *harmful side effect (annoyance)* ↑.
- IP-15 **Dynamics** → notification frequency adapts to recent adherence (back off when the user is already compliant).
- IP-25 **Self-service** → the app earns the right to notify only after the user sets their own goal.
- IP-10 **Prior action** → schedule reminders to fire at the user's historically active time, so they feel timely not intrusive.
- IP-2 **Taking out** → move the nudge out of push notifications into a passive home-screen widget the user checks voluntarily.
- IP-3 **Local quality** → different reminder style per exercise type / patient phase.

If the conflict reduces to "the notification must exist and not exist," escalate
to a **physical contradiction** → `physical-contradictions.md`.
