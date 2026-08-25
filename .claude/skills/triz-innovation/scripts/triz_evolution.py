#!/usr/bin/env python3
"""
TRIZ Evolution Trends & S-curve classifier.

Rule-based classifier that maps textual signals to an S-curve stage
(Infancy / Growth / Maturity / Decline / Unknown), then provides the
8 evolution trend prompts as a structured checklist.

Usage:
    python triz_evolution.py --signals "..."
    python triz_evolution.py                    # prints stage Unknown + 8 trends

Standard library only — Python 3.9+.
"""

from __future__ import annotations

import sys
import re
from typing import Any

# ── S-curve stage cue table ────────────────────────────────────────────────────
# Ordered from latest to earliest so higher-numbered stages get precedence
# when tie-breaking among mixed signals.
# Each entry: (stage int, stage name, tuple of lowercase cue substrings).
# No match → stage 0 / Unknown.
# Cues are matched with \\b word boundaries (R8.1).

_STAGE_CUES: list[tuple[int, str, tuple[str, ...]]] = [
    (
        4,
        "Decline",
        (
            "obsolete", "replaced by", "being replaced", "outdated",
            "declining", "dying", "being phased out", "end of life",
            "discontinued", "no longer used",
        ),
    ),
    (
        3,
        "Maturity",
        (
            "diminishing returns", "plateau", "plateaued", "minor tweaks",
            "cost rising", "cost of improvement", "gains shrinking",
            "gains are shrinking", "mature", "saturated", "incremental",
            "polishing", "commoditized", "commodity",
        ),
    ),
    (
        2,
        "Growth",
        (
            "rapid", "scaling", "scaling fast", "investment", "growing fast",
            "growing quickly", "expanding", "adoption", "taking off",
            "accelerating", "exponential", "viral",
        ),
    ),
    (
        1,
        "Infancy",
        (
            "prototype", "unreliable", "early", "experimental",
            "nascent", "emerging", "r&d", "uncertain", "lab stage",
            "proof of concept", "poc", "first of its kind",
        ),
    ),
]

# ── 8 Evolution Trends (consistent with references/evolution-trends.md) ────────

_TRENDS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Increasing ideality",
        "prompt": (
            "Where is your system on the ideality trend?  More useful "
            "function per unit cost/harm — what functions could be "
            "delivered with fewer or no added components?  What is the "
            "next step toward the Ideal Final Result?"
        ),
    },
    {
        "id": 2,
        "name": "Non-uniform development of parts",
        "prompt": (
            "Which sub-system is evolving most slowly and is now the "
            "bottleneck?  That uneven part is your next contradiction — "
            "find it and resolve it to unlock the whole system."
        ),
    },
    {
        "id": 3,
        "name": "Increasing dynamism & controllability",
        "prompt": (
            "Where is your system on the rigid -> flexible -> fluid/field "
            "continuum?  Manual -> automatic -> adaptive?  What could "
            "become tunable in real time that is currently fixed?"
        ),
    },
    {
        "id": 4,
        "name": "Increasing complexity then simplification (mono->bi->poly->trim)",
        "prompt": (
            "Is your system in the 'adding' phase (mono->bi->poly) or the "
            "'trimming' phase?  If still adding, what would trimming look "
            "like — fewer parts carrying more functions?  If already "
            "complex, which component can be removed?"
        ),
    },
    {
        "id": 5,
        "name": "Matching & mismatching of parts",
        "prompt": (
            "Are your parts unmatched -> matched -> dynamically matched?  "
            "Could deliberately mismatching a property (e.g. different "
            "thermal expansion, different stiffness) create a useful "
            "effect?  What is the next step on this trend?"
        ),
    },
    {
        "id": 6,
        "name": "Transition to the super-system & micro-level",
        "prompt": (
            "Could your system merge into a larger system (super-system "
            "integration) or drop to act at the micro/field level?  "
            "What capability would move up or down a level?"
        ),
    },
    {
        "id": 7,
        "name": "Decreasing human involvement",
        "prompt": (
            "Which steps still require a human?  Map the path: human -> "
            "tool-assisted -> semi-automatic -> fully automatic -> self-"
            "service/self-healing.  What is the next manual step to "
            "automate or eliminate?"
        ),
    },
    {
        "id": 8,
        "name": "Uneven flow / increasing field controllability",
        "prompt": (
            "How does energy, substance, or information flow through your "
            "system?  Can the field be upgraded to a more controllable "
            "form (mechanical -> electromagnetic)?  Can flows be made "
            "smoother, more conductive, or lossless?"
        ),
    },
]


def analyze(signals: str = "") -> dict[str, Any]:
    """Classify S-curve stage from textual signals and return the 8 trend prompts.

    Args:
        signals: Free-text description of system state, market signals,
                 or technology indicators.  Case-insensitive.

    Returns:
        dict with keys:
        - "s_curve_stage": {"stage": int, "name": str, "why": str}
            stage 1..4 (Infancy/Growth/Maturity/Decline) or 0 / "Unknown".
        - "trends": list of {"id": int, "name": str, "prompt": str} (always 8).
        - "note": str or None.
    """
    lower = signals.lower().strip()

    # S-curve stage classification
    stage = 0
    name = "Unknown"
    why = "No signals provided or no cues matched."

    if lower:
        # Collect all matching cues, grouped by stage (R8.1: word-boundary match)
        matches_by_stage: dict[int, dict[str, Any]] = {}
        for stage_val, stage_name, cues in _STAGE_CUES:
            matched = [cue for cue in cues if re.search(rf"\b{re.escape(cue)}\b", lower)]
            if matched:
                matches_by_stage.setdefault(stage_val, {
                    "name": stage_name,
                    "cues": [],
                })["cues"].extend(matched)

        if matches_by_stage:
            # Pick stage with most matches; tie → later stage (higher number)
            best_count = max(len(v["cues"]) for v in matches_by_stage.values())
            best_stage = max(
                (s for s, v in matches_by_stage.items() if len(v["cues"]) == best_count),
                key=lambda s: s,
            )
            tie_broken = sum(
                1 for s, v in matches_by_stage.items() if len(v["cues"]) == best_count
            ) > 1
            stage = best_stage
            name = matches_by_stage[best_stage]["name"]

            # Build "why" listing all cues, grouped by stage (sorted earliest→latest)
            def _stage_label(sv: int) -> str:
                return f"{matches_by_stage[sv]['name']} (stage {sv})"

            groups = [
                f"{_stage_label(sv)}: {', '.join(matches_by_stage[sv]['cues'])}"
                for sv in sorted(matches_by_stage)
            ]
            why = "Matched cues — " + "; ".join(groups)
            if tie_broken:
                why += " (tie broken toward the later stage)"
        else:
            why = "No recognised S-curve cues matched the provided signals."

    note: str | None = None
    if not lower:
        note = (
            "No signals provided — S-curve stage is Unknown.  Run with "
            "--signals to classify the stage; the 8 trend prompts are "
            "still useful as a checklist."
        )

    return {
        "s_curve_stage": {"stage": stage, "name": name, "why": why},
        "trends": _TRENDS,
        "note": note,
    }


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    # R12: Windows-safe stdout
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    signals = ""

    if len(sys.argv) >= 2:
        if sys.argv[1] == "--signals":
            if len(sys.argv) >= 3:
                signals = " ".join(sys.argv[2:])
            # else: no signals arg → signals stays "", stage Unknown
        else:
            # Assume bare signals (backward-compatible)
            signals = " ".join(sys.argv[1:])

    result = analyze(signals)

    # S-curve stage
    stage_info = result["s_curve_stage"]
    print(f"S-curve stage: {stage_info['name']} (stage {stage_info['stage']})")
    print(f"  Why: {stage_info['why']}")
    print()

    # 8 trends
    print("Evolution Trends checklist:")
    print("-" * 60)
    for t in result["trends"]:
        print(f"  {t['id']}. {t['name']}")
        # Word-wrap the prompt for readability
        prompt = t["prompt"]
        print(f"     {prompt}")
        print()

    if result["note"]:
        print(f"Note: {result['note']}")


if __name__ == "__main__":
    main()
