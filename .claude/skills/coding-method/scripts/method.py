#!/usr/bin/env python3
"""
Coding-method dispatcher — Lazy Ideality stage planner.

Turns a coding task into a concrete, technique-named plan across the 8-stage
pipeline. Heuristic MVP (keyword/intent rules), like triz-innovation's router:
it is a first guess, not a verdict — the skill still reasons.

Usage:
    python method.py route "<task>"       # print the stage plan for a task
    python method.py stages               # list the 8 stages
    python method.py stage <n>            # detail for one stage
    python method.py ladder "<task>"      # ponytail rung + IFR suggestion
    python method.py redflags [<file>]    # run the review checklist
    python method.py references           # list the reference index
    python method.py triz <imp> <wor>     # cross-invoke triz_matrix.py

Standard library only — Python 3.8+.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
_SKILL_DIR = _SCRIPT_DIR.parent
_REFS_DIR = _SKILL_DIR / "references"
_TRIZ_MATRIX = (
    _SKILL_DIR.parents[1] / "skills" / "triz-innovation" / "scripts" / "triz_matrix.py"
)

STAGES = [
    {
        "num": 1,
        "name": "Frame the task",
        "what": "Neutral restatement; primary function (Tool -> Action -> Object); harmful/excessive effects to avoid; real constraints; wicked vs tame triage.",
        "refs": ["method-map.md"],
        "tags": ["[Function analysis]", "[Wicked vs tame]"],
    },
    {
        "num": 2,
        "name": "Climb the ponytail ladder",
        "what": "YAGNI -> stdlib -> native -> existing dep -> one line -> minimum code. Default answer to 'should I build this?' is no.",
        "refs": ["rewrite-ladder.md", "method-map.md"],
        "tags": ["[YAGNI]", "[Leanness]", "[Creative extension]"],
    },
    {
        "num": 3,
        "name": "Sketch the Ideal Final Result",
        "what": "IFR: the behavior happens by itself, no new code/module/complexity. Almost-IFR: the smallest thing that must still be written. Design the module DEEP; design it twice.",
        "refs": ["deep-modules.md"],
        "tags": ["[IFR]", "[Deep module]", "[Design it twice]"],
    },
    {
        "num": 4,
        "name": "Structure from data",
        "what": "Data definition + interpretation comment first, then signature + one-line purpose; template follows the data; pick the computation-model rung and the algorithm strategy; state the complexity class before coding.",
        "refs": ["design-recipe.md", "algorithm-strategies.md", "computation-models.md"],
        "tags": ["[Design recipe]", "[Computation model]", "[Strategy catalog]"],
    },
    {
        "num": 5,
        "name": "Resolve contradictions",
        "what": "Name the engineering ('if I improve X, Y gets better but Z worse') or physical (must be A and not-A) contradiction. Apply matrix IPs or separation in time/space/condition/part, or reframe (define errors out of existence, find the Box). Only then verify the residual with a weighted +/- trade-off matrix.",
        "refs": ["triz-for-code.md", "architecture-tradeoffs.md"],
        "tags": ["[Contradiction]", "[Separation in condition]", "[Trade-off matrix]"],
    },
    {
        "num": 6,
        "name": "Make the minimal safe change",
        "what": "Greenfield: contract first, then body. Legacy/untested: Legacy Code Change Algorithm, seams, characterization tests, Sprout/Wrap, baby steps. Broken code: debugging path.",
        "refs": ["legacy-change.md", "construction-checklist.md"],
        "tags": ["[Legacy Change]", "[Seam]", "[Characterization test]"],
    },
    {
        "num": 7,
        "name": "Review with the red flags",
        "what": "Red-flag catalogue + construction checklist (coupling/cohesion, hide secrets, leanness, DRY, orthogonality). Confirm the complexity didn't relocate. Fix broken windows now.",
        "refs": ["red-flags.md"],
        "tags": ["[Red flag]", "[Trimming]", "[DRY]"],
    },
    {
        "num": 8,
        "name": "Verify, record, ship",
        "what": "Tests as proof + numeric success/failure criterion. ADR-lite when architecturally significant. <=3-line explanation stating the load-bearing why.",
        "refs": ["type-safety.md", "architecture-tradeoffs.md"],
        "tags": ["[Test as proof]", "[ADR]", "[<=3 lines]"],
    },
]

# Code-side TRIZ hints (original synthesis; the full matrix lives in triz-innovation).
_TRIZ_HINTS = [
    ("latency|slow|expensive (call|query)|hot path", "[IP-10 Prior action] precompute/cache; [IP-2 Taking out] move work off the hot path."),
    ("flexib|config|option|extend", "[IP-1 Segmentation] plugins; [IP-6 Universality] one extension point; [IP-25 Self-service] config over code."),
    ("coupl|reuse|duplicate|shared", "[IP-24 Intermediary] interface/queue/broker; [IP-7 Nesting] bounded contexts; [IP-5 Merging] consolidate the shared core."),
    ("cover|test.*time|deadline", "[IP-16 Partial action] test the risky 20%; [IP-10 Prior action] fixtures prepared once."),
    ("concurr|race|deadlock|thread|parallel", "[Computation model] declarative streams; [IP-13 Other way round] eventual + reconcile; separate in time."),
    ("cach|consisten|stale", "[IP-10 Prior action] cache prepared in advance; [IP-13 Other way round] eventual + reconcile; [Separation in time] per-read freshness."),
    ("error|exception|fail|edge case", "[Define errors out of existence] change the contract so the error case disappears; mask or aggregate the rest."),
]

_SIGNALS = [
    ("contradiction",
     r"\b(but|yet|however|breaks|trade-?off|conflict|too (slow|big|complex|large)|cannot|cant)\b|\bvs\b",
     "Stages 5 + 8", ["triz-for-code.md", "architecture-tradeoffs.md"],
     "Name the engineering contradiction, apply matrix IPs or separation, then verify with a weighted +/- matrix. Run: method.py triz <improving_id> <worsening_id>"),
    ("legacy",
     r"\blegacy\b|\buntested\b|no tests|spaghetti|brownfield|moderni[sz]e|old code|already in production",
     "Stage 6", ["legacy-change.md"],
     "Run the Legacy Code Change Algorithm: change points -> test points -> seams -> characterization tests -> baby steps."),
    ("debugging",
     r"\bbug\b|\bbroken\b|crash|\bfails?\b|wrong result|not working|\berror\b",
     "Debugging path + Stage 8", ["construction-checklist.md", "pragmatic-etiquette.md", "legacy-change.md"],
     "Characterize first (test the failing behavior), 5-step loop, fix the root cause, regression test."),
    ("architecture",
     r"\barchitectur\w*|\bservice\b|\bmodule boundary\b|\bapi design\b|\bscalab\w*|\bsystem-level\b",
     "Stages 3 + 5 + 8", ["architecture-tradeoffs.md", "deep-modules.md"],
     "Extract a small prioritized set of characteristics, design it twice, and record an ADR-lite when significant."),
    ("data-shape",
     r"\blist\b|\barray\b|\btree\b|\bparse\b|\brepresentation\b|\bdata\b|\bstructure\b",
     "Stage 4", ["design-recipe.md", "algorithm-strategies.md"],
     "Define the data first (named data definition + interpretation), template follows the data, pick the strategy."),
    ("data-heavy",
     r"\bdatabase\b|\bpipeline\b|\banalytics\b|\bdata model\b|\btable\b|\bquery\b",
     "Stages 4 + 5", ["data-systems.md", "computation-models.md"],
     "Data-heavy system: consult references/data-systems.md — frame as a composite data system, derive caches/indexes from the source-of-truth log, pick the isolation level you actually need."),
]

_REF_INDEX = [
    ("Router/escalation", "method-map.md"),
    ("Design recipe", "design-recipe.md"),
    ("Computation-model ladder", "computation-models.md"),
    ("Algorithm strategy catalog", "algorithm-strategies.md"),
    ("Deep modules + complexity", "deep-modules.md"),
    ("Review checklist", "red-flags.md"),
    ("Construction craft + debugging", "construction-checklist.md"),
    ("Safe change on legacy", "legacy-change.md"),
    ("Architecture trade-offs", "architecture-tradeoffs.md"),
    ("Domain modeling", "domain-modeling.md"),
    ("Time/scale engineering", "sustainable-engineering.md"),
    ("ETC/DRY mindset", "pragmatic-etiquette.md"),
    ("Rewrite ladder", "rewrite-ladder.md"),
    ("Proof-pass verification", "type-safety.md"),
    ("TRIZ <-> code bridge", "triz-for-code.md"),
    ("Data-system decisions", "data-systems.md"),
]


def route(task: str) -> list[dict]:
    """Return the stage plan for a task: which stages to emphasize, why, and
    which references to load. Heuristic, not a verdict."""
    lower = task.lower()
    hits = []
    for name, pattern, stages, refs, advice in _SIGNALS:
        if re.search(pattern, lower):
            hits.append({"signal": name, "stages": stages, "refs": refs, "advice": advice})
    triz_hints = [hint for pattern, hint in _TRIZ_HINTS if re.search(pattern, lower)]
    return {
        "task": task,
        "default": "Run stages 1-8 in order; skip to lite (1-3) if the pattern is known and trivial.",
        "signals": hits,
        "triz_hints": triz_hints,
        "always_load": ["method-map.md"],
    }


def plan_stage(num: int) -> Optional[dict]:
    for stage in STAGES:
        if stage["num"] == num:
            return stage
    return None


def suggest_rung(task: str) -> dict:
    """Ponytail ladder rung guess for a task (see ladder.py for the full logic)."""
    from ladder import suggest_rung  # noqa: F401  (re-export)
    return suggest_rung(task)


def redflags(file_path: Optional[str] = None) -> dict:
    from redflags import scan
    return scan(file_path)


def triz_matrix(improving: str, worsening: str) -> dict:
    """Cross-invoke triz-innovation's triz_matrix.py. No duplication: the matrix
    data and logic stay in triz-innovation."""
    if not _TRIZ_MATRIX.is_file():
        return {"note": "triz_matrix.py not found at " + str(_TRIZ_MATRIX)}
    proc = subprocess.run(
        [sys.executable, str(_TRIZ_MATRIX), improving, worsening],
        capture_output=True, text=True,
    )
    return {
        "command": f"triz_matrix.py {improving} {worsening}",
        "exit": proc.returncode,
        "output": proc.stdout.strip() or proc.stderr.strip(),
    }


def _print_usage(stream=sys.stderr) -> None:
    print(__doc__.strip(), file=stream)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    argv = sys.argv[1:]
    if not argv:
        _print_usage()
        sys.exit(1)

    command = argv[0]
    if command == "stages":
        for stage in STAGES:
            print(f"[{stage['num']}] {stage['name']}: {stage['what']}")
        sys.exit(0)

    if command == "stage":
        if len(argv) < 2 or not argv[1].isdigit():
            print("Usage: python method.py stage <n>", file=sys.stderr)
            sys.exit(1)
        stage = plan_stage(int(argv[1]))
        if stage is None:
            print(f"Error: no stage {argv[1]} (1-8).", file=sys.stderr)
            sys.exit(1)
        print(f"[{stage['num']}] {stage['name']}")
        print(stage["what"])
        print("tags: " + ", ".join(stage["tags"]))
        print("load: " + ", ".join(stage["refs"]))
        sys.exit(0)

    if command == "route":
        if len(argv) < 2:
            print("Usage: python method.py route \"<task>\"", file=sys.stderr)
            sys.exit(1)
        plan = route(" ".join(argv[1:]))
        print(f"Task: {plan['task']}")
        print(plan["default"])
        if plan["signals"]:
            print("\nSignals detected:")
            for hit in plan["signals"]:
                print(f"  [{hit['signal']}] stages {hit['stages']} — {hit['advice']}")
                print(f"      load: {', '.join(hit['refs'])}")
        if plan["triz_hints"]:
            print("\nCode-side TRIZ hints:")
            for hint in plan["triz_hints"]:
                print(f"  {hint}")
        print("\nClose: end with a test (stage 8) + a numeric success criterion.")
        sys.exit(0)

    if command == "ladder":
        if len(argv) < 2:
            print("Usage: python method.py ladder \"<task>\"", file=sys.stderr)
            sys.exit(1)
        rung = suggest_rung(" ".join(argv[1:]))
        print(f"Task: {rung['task']}")
        print(f"Rung: [{rung['rung']}] — {rung['why']}")
        print(f"IFR: {rung['ifr']}")
        sys.exit(0)

    if command == "redflags":
        result = redflags(argv[1] if len(argv) > 1 else None)
        print(result["summary"])
        for line in result["checklist"]:
            print(f"  [ ] {line}")
        if result["findings"]:
            print("\nDetectable smells:")
            for finding in result["findings"]:
                print(f"  {finding}")
        sys.exit(0)

    if command == "references":
        for what, file in _REF_INDEX:
            print(f"{file:28} {what}")
        sys.exit(0)

    if command == "triz":
        if len(argv) < 3:
            print("Usage: python method.py triz <improving_id> <worsening_id>", file=sys.stderr)
            sys.exit(1)
        result = triz_matrix(argv[1], argv[2])
        print(f"Command: {result.get('command', '')}")
        print(result.get("output", result.get("note", "")))
        sys.exit(0)

    _print_usage()
    sys.exit(1)


if __name__ == "__main__":
    main()
