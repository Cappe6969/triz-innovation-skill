# TRIZ Method Map

How to pick the right TRIZ tool fast. Read the problem signature, match the row,
run those methods. Most real problems need **2–4** methods, not one.

## Decision table (problem signature → methods)

| If the problem looks like… | Start with | Then |
|---|---|---|
| "Improving A makes B worse" (a trade-off) | Engineering Contradiction + 40 IP | Physical Contradiction if it reduces to one element |
| "It must be X and also not-X" (same thing, opposite needs) | Physical Contradiction + Separation | Resource Analysis |
| "Too many parts / too costly / too complex" | Trimming | Function Analysis first, then Ideality |
| "Why does this keep happening?" / recurring failure | Root Cause Analysis | Contradiction at the root cause |
| "What even is going on here?" / unclear system | Function Analysis | System Operator |
| "We lack budget / people / data" | Resource Analysis | Ideality |
| "Reinvent / leapfrog this whole thing" | Ideal Final Result | System Operator + Function-Oriented Search |
| "Someone, somewhere already solved this" | Function-Oriented Search | 76 Standard Solutions |
| "Two things interact badly" (weak/harmful/missing action) | Su-Field + 76 Standard Solutions | Standard-solution class for the state |
| "Where is this headed / how to leapfrog this whole class" | Evolution Trends + S-curve | System Operator (future column) |
| "I have the action but no mechanism" | Scientific Effects | Resource Analysis |
| "Tried the quick tools, still stuck on a hard contradiction" | ARIZ (escalation) | Physical Contradiction + Su-Field + Resources |
| "Stuck, need a perspective shift" | Smart Little People | System Operator |
| Business / org / pricing / market | Business TRIZ | Contradiction + Resource + Ideality |
| Software / architecture / performance | Software TRIZ | Contradiction + Trimming |
| Physio / rehab / clinic / adherence | Rehabilitation TRIZ | Physical Contradiction + Resource + Ideality |

## Method one-liners
- **Function Analysis** — model the system as Tool→Action→Object; find harmful/insufficient/redundant functions.
- **Root Cause Analysis** — chain symptom → root; find the leverage cause.
- **Engineering Contradiction (40 IP)** — two parameters fight; the contradiction matrix suggests principles.
- **Physical Contradiction (Separation)** — one element needs opposite states; separate in time/space/condition/scale.
- **Resource Analysis** — find what is already present and free before adding anything.
- **Ideality / IFR** — picture the function happening by itself; reduce cost+harm.
- **Trimming** — delete a component, reassign its useful function to what remains.
- **System Operator (9 Windows)** — look at sub/system/super × past/present/future.
- **Function-Oriented Search** — find another field that performs the same function well; transfer it.
- **Method-Oriented Search** — you have a capability; hunt for problems it can solve.
- **76 Standard Solutions** — pattern catalog for substance-field (component-interaction) problems.
- **Contradiction Matrix** — map a trade-off to 2 of 39 parameters; matrix returns the inventive principles that resolved it historically.
- **Su-Field Analysis** — model a function as S1—[field]→S2; fix incomplete/weak/harmful interactions via the 5 standard-solution classes.
- **Evolution Trends + S-curve** — place the system on its maturity curve and the 8 evolution laws; predict and force the next step.
- **Scientific Effects** — start from the needed function, pull proven physical/chemical/behavioral effects that deliver it.
- **ARIZ** — the master algorithm; reformulates a stubborn problem step-by-step until the core contradiction is resolvable. Escalation only.
- **Smart Little People** — imagine tiny agents doing the job; escapes psychological inertia.

## Router heuristics (used by triz_router.py)
Keyword/intent cues that suggest each method. These are signals, not rules — a
problem can hit several.

- **Engineering Contradiction:** "but", "trade-off", "at the cost of", "however", "increases ... decreases", "more X means less Y".
- **Physical Contradiction:** "must be both", "present and absent", "fast and slow", "big and small", "on and off", "hot and cold".
- **Trimming:** "too many", "too complex", "expensive", "remove", "simplify", "redundant", "overhead", "bloated".
- **Root Cause Analysis:** "keeps happening", "recurring", "again", "fails", "root", "why", "intermittent".
- **Resource Analysis:** "no budget", "limited", "can't afford", "without adding", "scarce", "few people".
- **Ideality / IFR:** "ideal", "leapfrog", "rethink", "from scratch", "best possible".
- **Function Analysis:** "unclear", "complex system", "many parts", "interactions", "how it works".
- **System Operator:** "future", "evolve", "long term", "context", "bigger picture".
- **Su-Field + 76 Standard Solutions:** "interaction", "interferes", "doesn't act on", "damages", "weak effect", "too strong", "harmful", "contact", "between", "connect", "interagisce", "danneggia".
- **Evolution Trends + S-curve:** "leapfrog", "next generation", "where is this going", "mature", "plateau", "diminishing returns", "reinvent the category", "obsolete".
- **Scientific Effects:** "how do I", "mechanism", "without a", "is there a way to", "what effect", "achieve X without".
- **ARIZ:** "still stuck", "tried everything", "hard problem", "nothing works", "very hard contradiction", "deep dive".
- **Smart Little People:** "stuck", "no idea", "creative block".
- **Business TRIZ:** "pricing", "customer", "market", "revenue", "team", "process", "org", "workflow".
- **Software TRIZ:** "app", "code", "latency", "API", "database", "deploy", "architecture", "bug", "notification".
- **Rehabilitation TRIZ:** "patient", "exercise", "therapy", "rehab", "adherence", "clinic", "physio".

## Default fallback
If signature is unclear, run: Function Analysis → Root Cause → Contradiction →
Resource → IFR. That sequence works on almost anything.
