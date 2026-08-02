# Resource Analysis

Before adding anything new, find what is **already present and underused**. The
ideal solution uses resources you already have for free. This is the cheapest
path to higher ideality.

## The resource checklist
Walk every category. For each, ask: *what's here, and how could it do work for me?*

| Type | Look for | Examples |
|------|----------|----------|
| **Internal (substance)** | parts, materials, data already in the system | logs, existing DB fields, sensors, unused screen space |
| **External (super-system)** | things in the environment | the phone's calendar, GPS, weather, the clinic's existing intake form |
| **Free / underused** | capacity that's idle or wasted | idle CPU, dead time in a workflow, a staff member's slack hours, waste heat |
| **Informational** | signals and data you could read | usage patterns, timestamps, error rates, patient self-reports |
| **Temporal** | moments and idle periods | time before/after an action, breaks, off-peak windows, the gap between sessions |
| **Spatial** | surfaces, volumes, positions, directions | margins of a UI, the back of a form, the lock screen, room layout |
| **Human** | attention, motivation, social ties | the patient's own goals, family, peer groups, the user's habit triggers |
| **Digital / software** | APIs, automations, existing tools | webhooks, cron, a spreadsheet, an LLM, push APIs, existing integrations |

## Resource fields (TRIZ "MATCHEMIB")
Physical/engineering resources also come as **fields**: **M**echanical,
**A**coustic, **T**hermal, **CHEM**ical, **E**lectromagnetic, **I**ntermolecular,
**B**iological. Useful for hardware/physical problems.

## Derived resources
You can transform a resource into a more useful one:
- Combine two weak resources (idle time + existing data → predicted active window).
- Change state (waste heat → energy; raw logs → a signal).
- Use a resource against itself (the annoyance signal becomes the throttle input).

## Procedure
1. Fill the checklist — at least one concrete item per row, or write "none".
2. Star the 3–5 resources most relevant to the problem.
3. For each starred resource, write one sentence: how it could replace a new
   component or strengthen an insufficient function.
4. Feed these into IFR (`ideal-final-result.md`) and solution generation.

## Why this matters
Most "we need budget / people / a new tool" problems dissolve once the existing
resource inventory is honest. A solution built from present resources is cheaper,
faster, and more reversible — it scores high on ideality.
