# Example — Product design problem (worked, condensed)

**Problem:** "Our reusable water bottle keeps the drink cold for hours, but the
double wall makes it heavy and bulky — users say it's too big for a bag."

## 1. Framing
System: insulated bottle. Sub: inner wall, outer wall, vacuum gap, lid. Super:
the user's bag, hand, daily carry. Main function: *bottle keeps liquid cold.*
Harmful: *bottle is heavy/bulky* (excessive). Constraint: must still insulate;
food-safe; manufacturable at current price. Goal: cold drink + compact/light.

## 2. Function analysis (excerpt)
| Tool | Action | Object | U/H | N/I/E |
|---|---|---|---|---|
| Vacuum wall | insulates | liquid | U | Normal |
| Double wall | adds | weight/volume | H | Excessive |
Trimming candidate: permanent double wall (needed only while carrying a cold drink).

## 3. Root cause
Bulky → insulation is **always-on and full-size** even when the bottle is empty or
the user wants compactness → **root cause: insulation can't be reduced when not
needed** (controllable via design).

## 4. Contradiction
- **Engineering:** IF insulation ↑ (thicker wall) THEN cold-retention ↑ BUT size/weight ↑.
- **Physical:** the bottle wall must be **thick** (insulate) and **thin** (compact).
- Break via separation in **time/condition** and **parts/whole**.

## 5. Resources
Existing: the air gap itself, the lid, the user's hand/bag, ambient temperature.
Underused: the bottle is often carried **empty** (collapsible opportunity); the
cold liquid's own thermal mass.

## 6. IFR
The bottle keeps the drink cold **only when full**, and takes **near-zero space**
when empty — insulation appears on demand, not permanently.

## 7. Methods: Physical Contradiction (separation) + Trimming + Resource + Ideality.

## 8. Solutions (tagged)
- Conservative: thinner aerogel insulation, same shape [IP-35 Parameter change]; lighter alloy [IP-40 Composite].
- Creative-realistic: **collapsible silicone body** — full when in use, flat when empty [Separation in time / IP-29 Pneumatics-flexible]; insulate only the lower 2/3 where liquid sits [Separation in space / IP-3 Local quality].
- Non-obvious TRIZ: a **sleeve** that the user adds only when they need cold (insulation moves to the super-system) [Trimming Rule C / Separation on condition]; phase-change gel insert that does the cold-keeping so walls can be thin [IP-36 Phase transition / Resource].
- High-risk/high-upside: ditch passive insulation for a thin active mini-cooler [IP-28 Mechanics substitution].
- Minimal test: prototype the collapsible body + lower-section-only insulation.

## 9. Evaluation (excerpt)
| Solution | Impact | Feas | Cost | Speed | Risk | Rev | Cplx | Ideal | Total |
|---|---|---|---|---|---|---|---|---|---|
| Collapsible body | 5 | 3 | 3 | 2 | 3 | 3 | 2 | 5 | 26 |
| Lower-section insulation | 3 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 32 |
| Aerogel thinner wall | 4 | 4 | 3 | 4 | 4 | 4 | 4 | 4 | 31 |

## 10. Experiment plan
- **Best candidate:** lower-section-only insulation (quick, cheap, low risk) as v-next; collapsible body as a parallel R&D bet.
- **Experiment:** build 5 lower-section prototypes; measure cold-retention vs current and weigh/measure them; user-test bag fit with 10 people.
- **Data:** °C after 4h, grams, packed volume, "fits my bag" yes/no.
- **Success:** ≤2°C worse retention at −25% weight AND ≥8/10 "fits my bag".
- **If works:** tool the lower-section design; continue collapsible R&D. **If fails (retention loss too high):** switch to aerogel thin-wall route.
