#!/usr/bin/env python3
"""Route a software decision through the TRIZ Coding Method.

The module is dependency-free and safe to import. Its heuristics select which
parts of the method deserve attention; they are a first guess, not a verdict.

Usage:
    python method.py route [--mode auto|lite|focused|ultra] "<task>"
    python method.py stages
    python method.py stage <n>
    python method.py ladder "<task>"
    python method.py redflags [<file>]
    python method.py references
    python method.py triz <improving_id> <worsening_id>
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
_TRIZ_MATRIX = _SKILL_DIR / "engine" / "scripts" / "triz_matrix.py"

MODES = ("auto", "lite", "focused", "ultra")

STAGES = [
    {"num": 1, "name": "Frame the task", "what": "Restate required behavior, harmful effects, constraints, and proof of success.", "refs": ["method-map.md"], "tags": ["frame"]},
    {"num": 2, "name": "Climb the Lazy Ideality ladder", "what": "Delete, use stdlib/native, configure or compose, adapt existing code, then add minimum code.", "refs": ["rewrite-ladder.md", "method-map.md"], "tags": ["lazy-ideality", "yagni"]},
    {"num": 3, "name": "Sketch the Ideal Final Result", "what": "State the no-new-mechanism IFR and the smallest feasible almost-IFR.", "refs": ["deep-modules.md"], "tags": ["ifr", "almost-ifr"]},
    {"num": 4, "name": "Structure from data", "what": "Use data definitions, the weakest computation model, and an appropriate algorithm strategy.", "refs": ["design-recipe.md", "algorithm-strategies.md", "computation-models.md"], "tags": ["data", "algorithm"]},
    {"num": 5, "name": "Resolve contradictions", "what": "Escalate only when two required qualities remain incompatible; eliminate the contradiction before compromising.", "refs": ["triz-for-code.md", "architecture-tradeoffs.md"], "tags": ["triz", "contradiction"]},
    {"num": 6, "name": "Make the minimal safe change", "what": "Use a contract for new code; characterize and create seams for legacy or broken code.", "refs": ["legacy-change.md", "construction-checklist.md"], "tags": ["safe-change"]},
    {"num": 7, "name": "Review nontrivial changes", "what": "Check coupling, leakage, repetition, shallow abstractions, and relocated complexity.", "refs": ["red-flags.md"], "tags": ["review"]},
    {"num": 8, "name": "Verify", "what": "Prove the outcome with tests or reproducible evidence; record assumptions and residual risk.", "refs": ["type-safety.md", "architecture-tradeoffs.md"], "tags": ["verification"]},
]

_TRIZ_HINTS = [
    (r"latency|slow|expensive (call|query)|hot path", "[IP-10 Prior action] precompute/cache; [IP-2 Taking out] move work off the hot path."),
    (r"flexib|config|option|extend", "[IP-1 Segmentation] plugins; [IP-6 Universality] one extension point; [IP-25 Self-service] config over code."),
    (r"coupl|reuse|duplicate|shared", "[IP-24 Intermediary] interface/queue/broker; [IP-7 Nesting] bounded contexts; [IP-5 Merging] consolidate the shared core."),
    (r"cover|test.*time|deadline", "[IP-16 Partial action] test the risky 20%; [IP-10 Prior action] fixtures prepared once."),
    (r"concurr|race|deadlock|thread|parallel", "[Computation model] declarative streams; [IP-13 Other way round] eventual + reconcile; separate in time."),
    (r"cach|consisten|stale", "[IP-10 Prior action] cache prepared in advance; [IP-13 Other way round] eventual + reconcile; [Separation in time] per-read freshness."),
    (r"error|exception|fail|edge case", "[Define errors out of existence] change the contract so the error case disappears; mask or aggregate the rest."),
]

_SIGNALS = [
    ("contradiction", r"\b(but|yet|however|breaks|trade-?off|conflict|too (slow|big|complex|large)|cannot|cant)\b|\bvs\b", "Stage 5", ["triz-for-code.md", "architecture-tradeoffs.md"], "Name the two required qualities and eliminate the contradiction before accepting a compromise."),
    ("legacy", r"\blegacy\b|\buntested\b|no tests|spaghetti|brownfield|moderni[sz]e|old code|already in production", "Stage 6", ["legacy-change.md"], "Characterize behavior, find a seam, and change it in small verified steps."),
    ("debugging", r"\bbug\b|\bbroken\b|crash|\bfails?\b|wrong result|not working|\berror\b", "Stage 6", ["construction-checklist.md", "pragmatic-etiquette.md", "legacy-change.md"], "Reproduce, minimize, isolate the cause, fix it, and add a regression test."),
    ("architecture", r"\barchitectur\w*|\bservice\b|\bmodule boundary\b|\bapi design\b|\bscalab\w*|\bsystem-level\b", "Stages 3 + 7", ["architecture-tradeoffs.md", "deep-modules.md"], "Compare at least two small interfaces and record the load-bearing trade-off."),
    ("data-shape", r"\blist\b|\barray\b|\btree\b|\bparse\b|\brepresentation\b|\bdata\b|\bstructure\b", "Stage 4", ["design-recipe.md", "algorithm-strategies.md"], "Define the data and complexity target before selecting an algorithm."),
    ("data-heavy", r"\bdatabase\b|\bpipeline\b|\banalytics\b|\bdata model\b|\btable\b|\bquery\b", "Stage 4", ["data-systems.md", "computation-models.md"], "Identify the source of truth and the consistency/isolation actually required."),
]

_REF_INDEX = [
    ("Router/escalation", "method-map.md"), ("Design recipe", "design-recipe.md"),
    ("Computation-model ladder", "computation-models.md"), ("Algorithm strategy catalog", "algorithm-strategies.md"),
    ("Deep modules + complexity", "deep-modules.md"), ("Review checklist", "red-flags.md"),
    ("Construction craft + debugging", "construction-checklist.md"), ("Safe change on legacy", "legacy-change.md"),
    ("Architecture trade-offs", "architecture-tradeoffs.md"), ("Domain modeling", "domain-modeling.md"),
    ("Time/scale engineering", "sustainable-engineering.md"), ("ETC/DRY mindset", "pragmatic-etiquette.md"),
    ("Rewrite ladder", "rewrite-ladder.md"), ("Proof-pass verification", "type-safety.md"),
    ("TRIZ <-> code bridge", "triz-for-code.md"), ("Data-system decisions", "data-systems.md"),
]


def _select_mode(task: str, requested: str) -> str:
    if requested not in MODES:
        raise ValueError("mode must be one of: " + ", ".join(MODES))
    if requested != "auto":
        return requested
    if re.search(r"\b(security|auth|permission|migration|production data|irreversible|cross-system|safety-critical)\b", task, re.I):
        return "ultra"
    if re.search(r"\b(rename|format|typo|comment|one[- ]line|mechanical)\b", task, re.I):
        return "lite"
    return "focused"


def _relative_refs(names: list[str]) -> list[str]:
    return ["references/" + name for name in names]


def route(task: str, mode: str = "auto") -> dict:
    """Return a structured, JSON-serializable method route."""
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task must be a non-empty string")
    selected_mode = _select_mode(task, mode)
    lower = task.lower()
    hits = []
    for name, pattern, stages, refs, advice in _SIGNALS:
        if re.search(pattern, lower):
            hits.append({"signal": name, "stages": stages, "refs": refs, "advice": advice})

    signal_names = {hit["signal"] for hit in hits}
    contradiction = "contradiction" in signal_names
    if selected_mode == "ultra":
        applied = list(range(1, 9))
    elif selected_mode == "lite":
        applied = [1, 2, 3, 8]
    else:
        applied = [1, 2, 3]
        if signal_names & {"data-shape", "data-heavy"}:
            applied.append(4)
        if contradiction:
            applied.append(5)
        if signal_names & {"legacy", "debugging"}:
            applied.append(6)
        if signal_names & {"architecture", "contradiction", "legacy", "data-heavy"}:
            applied.append(7)
        applied.append(8)
    applied = sorted(set(applied))

    from ladder import LADDER, suggest_rung
    rung = suggest_rung(task)
    ladder_findings = [
        {"rung": name, "question": question, "selected": name == rung["rung"]}
        for name, question in LADDER
    ]
    references = {"references/method-map.md"}
    for hit in hits:
        references.update(_relative_refs(hit["refs"]))
    triz_hints = [hint for pattern, hint in _TRIZ_HINTS if re.search(pattern, lower)]

    return {
        "task": task,
        "requested_mode": mode,
        "mode": selected_mode,
        "stages": applied,
        "applied_stages": [dict(STAGES[n - 1]) for n in applied],
        "ladder": ladder_findings,
        "selected_rung": rung["rung"],
        "ifr": rung["ifr"],
        "almost_ifr": rung["almost_ifr"],
        "remaining_contradiction": (
            "The task states incompatible required qualities; clarify the improving and worsening parameters."
            if contradiction else None
        ),
        "triz_escalated": contradiction,
        "references": sorted(references),
        # Compatibility fields retained for existing callers.
        "default": "Run the mandatory core and only the conditional stages selected by the task.",
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
    from ladder import suggest_rung as suggest
    return suggest(task)


def redflags(file_path: Optional[str] = None) -> dict:
    from redflags import scan
    return scan(file_path)


def triz_matrix(improving: str, worsening: str) -> dict:
    """Invoke the internal matrix without passing input through a shell."""
    if not _TRIZ_MATRIX.is_file():
        return {"note": "triz_matrix.py not found"}
    proc = subprocess.run(
        [sys.executable, str(_TRIZ_MATRIX), str(improving), str(worsening)],
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": f"triz_matrix.py {improving} {worsening}",
        "exit": proc.returncode,
        "output": proc.stdout.strip() or proc.stderr.strip(),
    }


def _print_usage(stream=sys.stderr) -> None:
    print(__doc__.strip(), file=stream)


def _route_args(argv: list[str]) -> tuple[str, str]:
    mode = "auto"
    words = argv[:]
    if "--mode" in words:
        index = words.index("--mode")
        if index + 1 >= len(words):
            raise ValueError("--mode requires a value")
        mode = words[index + 1]
        del words[index:index + 2]
    if not words:
        raise ValueError("route requires a task")
    return " ".join(words), mode


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    argv = sys.argv[1:]
    if not argv:
        _print_usage()
        raise SystemExit(1)
    command = argv[0]
    if command == "stages":
        for stage in STAGES:
            print(f"[{stage['num']}] {stage['name']}: {stage['what']}")
        raise SystemExit(0)
    if command == "stage":
        if len(argv) < 2 or not argv[1].isdigit():
            print("Usage: python method.py stage <n>", file=sys.stderr)
            raise SystemExit(1)
        stage = plan_stage(int(argv[1]))
        if stage is None:
            print(f"Error: no stage {argv[1]} (1-8).", file=sys.stderr)
            raise SystemExit(1)
        print(f"[{stage['num']}] {stage['name']}")
        print(stage["what"])
        print("tags: " + ", ".join(stage["tags"]))
        print("load: " + ", ".join(stage["refs"]))
        raise SystemExit(0)
    if command == "route":
        try:
            task, mode = _route_args(argv[1:])
            plan = route(task, mode)
        except ValueError as exc:
            print(f"Usage: python method.py route [--mode {'|'.join(MODES)}] \"<task>\"", file=sys.stderr)
            print(f"Error: {exc}", file=sys.stderr)
            raise SystemExit(1)
        print(f"Task: {plan['task']}")
        print(f"Mode: {plan['mode']}")
        print("Stages: " + ", ".join(str(n) for n in plan["stages"]))
        if plan["signals"]:
            print("\nSignals detected:")
            for hit in plan["signals"]:
                print(f"  [{hit['signal']}] {hit['stages']} — {hit['advice']}")
        if plan["triz_escalated"]:
            print("\nTRIZ escalation: " + plan["remaining_contradiction"])
        print("\nIFR: " + plan["ifr"])
        print("Almost-IFR: " + plan["almost_ifr"])
        print("Verify with a reproducible test or measurement.")
        raise SystemExit(0)
    if command == "ladder":
        if len(argv) < 2:
            print("Usage: python method.py ladder \"<task>\"", file=sys.stderr)
            raise SystemExit(1)
        result = suggest_rung(" ".join(argv[1:]))
        print(f"Task: {result['task']}")
        print(f"Rung: [{result['rung']}] — {result['why']}")
        print(f"IFR: {result['ifr']}")
        print(f"Almost-IFR: {result['almost_ifr']}")
        raise SystemExit(0)
    if command == "redflags":
        result = redflags(argv[1] if len(argv) > 1 else None)
        print(result["summary"])
        for line in result["checklist"]:
            print(f"  [ ] {line}")
        print("\nDetectable smells:")
        for finding in result["findings"]:
            print(f"  {finding}")
        raise SystemExit(0)
    if command == "references":
        for what, file_name in _REF_INDEX:
            print(f"{file_name:28} {what}")
        raise SystemExit(0)
    if command == "triz":
        if len(argv) < 3:
            print("Usage: python method.py triz <improving_id> <worsening_id>", file=sys.stderr)
            raise SystemExit(1)
        result = triz_matrix(argv[1], argv[2])
        print(f"Command: {result.get('command', '')}")
        print(result.get("output", result.get("note", "")))
        raise SystemExit(0)
    _print_usage()
    raise SystemExit(1)


if __name__ == "__main__":
    main()
