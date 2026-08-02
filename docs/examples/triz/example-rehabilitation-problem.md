# Example — Rehabilitation problem (worked)

**Problem (raw):** "Ho un'app di fisioterapia che deve aiutare i pazienti ad
aderire agli esercizi, ma se aggiungo troppe notifiche diventa fastidiosa."

This is the canonical example the router is tuned on.

## 1. Problem framing
- **Restated:** Increase home-exercise adherence without the prompting mechanism
  becoming a source of friction that drives annoyance/uninstalls.
- **System:** the physio app's reminder/adherence loop.
- **Sub-system:** notification scheduler, exercise log, goal settings.
- **Super-system:** patient's day, phone OS, clinician, family.
- **Stakeholders:** patient (wants to recover with low burden), clinician (wants
  carryover), app team (wants retention).
- **Main useful function:** *App prompts patient → patient performs exercises.*
- **Harmful function:** *Notifications annoy patient* (H, currently Excessive).
- **Constraints:** no wearable assumed; can't see the patient at home; must work on a phone.
- **Symptoms / causes / goals:** symptom = drop-off after week 2; cause = generic
  fixed-time pushes ignore context; goal = sustained adherence.

## 2. Function analysis
| Tool | Action | Object | U/H | N/I/E | Parameter |
|---|---|---|---|---|---|
| Notification | prompts | patient | U | Excessive | likelihood to act |
| Notification | interrupts | patient | H | --- | attention/comfort |
| Exercise log | records | sessions | U | Insufficient | adherence data |
Trimming candidate: the dedicated push channel (could the OS calendar/habit do it?).

## 3. Root cause analysis
Drop-off → reminders feel irrelevant → fire at fixed times unrelated to the
patient's day → **root cause: the app doesn't know the patient's real active
window** (controllable) and **doesn't back off when adherence is fine**
(controllable). Leverage point: make prompting context-aware.

## 4. Contradiction analysis
- **Engineering:** IF we send more reminders THEN adherence improves BUT annoyance/uninstall risk rises.
- **Physical:** the notification must be **present** (drive adherence) and **absent** (avoid annoyance).
- Breakable via **separation in time** and **separation on condition**.

## 5. Resource analysis
Informational: in-app timestamps reveal when the patient actually opens/exercises.
Temporal: the post-routine moment (after breakfast). Human: the patient's own
stated goal. Digital: OS calendar, local notifications, on-device patterns.

## 6. Ideal Final Result
The patient does the right exercise at the right time **on their own**, because
it's tied to an existing habit and goal — the app prompts rarely and only when
genuinely needed.

## 7. Methods selected (matches router output)
1. **Physical Contradiction + Separation in time/condition**
2. **Resource Analysis**
3. **Ideality / IFR**
4. **Trimming**
5. **System Operator**

## 8. Solutions (tagged)
Conservative: (a) let patient pick reminder time [Resource]; (b) cap to 1/day
[IP-16]; (c) snooze button [IP-23 Feedback].
Creative-realistic: (d) adaptive frequency that backs off when weekly adherence ≥
target [Separation on condition / IP-15]; (e) habit-anchored reminder ("after you
brush your teeth") [IP-10 Prior action]; (f) passive home-screen widget instead
of push [Separation in space / IP-2].
Non-obvious TRIZ: (g) patient sets a weekly self-commitment; app only nudges on a
miss [Trimming Rule B / IP-25 self-service]; (h) clinician's existing check-in
becomes the reminder channel [Trimming Rule C]; (i) detect exercise via phone
motion and turn reminders into confirmations [IP-25 + Resource].
High-risk/high-upside: (j) drop push entirely, rely on habit-anchoring + weekly
clinician touchpoint [Trim Rule A direction]; (k) peer/family accountability
loop [IP-24 Intermediary].
Minimal test this week: ship adaptive frequency + active-window inference behind a flag.

## 9. Evaluation (excerpt, 1–5; cost/risk/complexity: 5 = cheap/safe/simple)
| Solution | Impact | Feasibility | Cost | Speed | Risk | Reversibility | Complexity | Ideality | Total |
|---|---|---|---|---|---|---|---|---|---|
| (d) Adaptive frequency | 4 | 4 | 4 | 4 | 4 | 5 | 3 | 4 | 32 |
| (e) Habit-anchored | 4 | 5 | 5 | 5 | 4 | 5 | 4 | 5 | 37 |
| (g) Self-commitment + miss-nudge | 5 | 4 | 4 | 3 | 3 | 4 | 3 | 5 | 31 |

## 10. Experiment plan
- **Best candidate:** (e) habit-anchored reminders + (d) adaptive frequency.
- **Experiment:** A/B for 3 weeks — control (fixed daily) vs variant (habit-anchor + back-off).
- **Data:** weekly adherence %, notifications/day, opt-out rate, uninstalls.
- **Success:** variant adherence ≥ +10pp AND opt-out ≤ control.
- **If works:** add active-window inference (solution i). **If fails:** test
  self-commitment model (g) before touching frequency further.
