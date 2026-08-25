#!/usr/bin/env python3
"""
TRIZ Su-Field -> 76 Standard Solutions class recommender.

Rule-based recommender that maps a Su-Field state (incomplete, insufficient,
harmful, measurement, excessive) to the matching standard-solution classes
with concrete candidate moves.  Also supports individual 76 Standard Solutions
lookup, search, and listing.

Usage:
    python triz_standard_solutions.py --state <state>
    python triz_standard_solutions.py --list
    python triz_standard_solutions.py --solution <id>   (e.g. "1.1.3")
    python triz_standard_solutions.py --search <query>
    python triz_standard_solutions.py --list-all
    python triz_standard_solutions.py                    # print usage

Standard library only -- Python 3.9+.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# -- Data directory helper ----------------------------------------------------


def _data_dir() -> Path:
    """Path to the bundled data directory, relative to this script."""
    return Path(__file__).resolve().parent / "data"


# -- State -> classes -> moves table ------------------------------------------
# Single readable table near the top -- extend it here.
# Each state key maps to a "synonyms" list (for input flexibility) and "classes"
# list.  Each class entry has "class" (int), "name" (str), and "moves" (list[str]).
# Consistent with references/substance-field-analysis.md.

_STATE_TABLE: dict[str, dict[str, Any]] = {
    "incomplete": {
        "synonyms": ["missing"],
        "classes": [
            {
                "class": 1,
                "name": "Class 1 -- Build or complete a Su-Field",
                "moves": [
                    "Add the missing field F between S1 and S2 to complete "
                    "the interaction",
                    "Add the missing substance S2 that the tool should act on",
                    "Introduce an external additive to supply the missing "
                    "component (substance or field)",
                    "Use the environment itself as the missing substance or field",
                ],
            },
        ],
        "note": (
            "See references/substance-field-analysis.md -- "
            "Class 1: complete an incomplete Su-Field (add the missing "
            "substance or field)."
        ),
    },
    "insufficient": {
        "synonyms": ["weak"],
        "classes": [
            {
                "class": 2,
                "name": "Class 2 -- Develop / enhance the Su-Field",
                "moves": [
                    "Chain Su-Fields -- add a second field and a third "
                    "substance S3 to boost the effect",
                    "Upgrade the field toward a more controllable form "
                    "(mechanical -> acoustic -> thermal -> chemical -> "
                    "electric -> magnetic -> electromagnetic)",
                    "Fragment substances to increase surface area and "
                    "interaction intensity (solid -> powder -> liquid -> "
                    "gas -> field)",
                    "Make the field dynamic -- pulse it, match the natural "
                    "frequency, or create a standing wave or gradient",
                ],
            },
        ],
        "note": (
            "See references/substance-field-analysis.md -- "
            "Class 2: strengthen a weak Su-Field (chain, upgrade field, "
            "fragment, make dynamic)."
        ),
    },
    "harmful": {
        "synonyms": [],
        "classes": [
            {
                "class": 1,
                "name": "Class 1 -- Eliminate or block the harmful interaction",
                "moves": [
                    "Block the harmful field -- insert a barrier substance "
                    "S3 between S1 and S2",
                    "Add a third substance S3 that absorbs or neutralizes "
                    "the harmful field",
                    "Redirect the harmful action onto a sacrificial element "
                    "that is cheap or easy to replace",
                    "Introduce a counter-field F2 that cancels or opposes "
                    "the harmful field F1",
                ],
            },
        ],
        "note": (
            "See references/substance-field-analysis.md -- "
            "Class 1: block, absorb, or redirect harmful interactions."
        ),
    },
    "measurement": {
        "synonyms": ["detection"],
        "classes": [
            {
                "class": 4,
                "name": "Class 4 -- Detection & measurement Su-Fields",
                "moves": [
                    "Generate a field that varies with the property to be "
                    "measured",
                    "Add an easily detectable additive (tag, tracer, marker) "
                    "to the substance",
                    "Use a resonant system -- match the natural frequency to "
                    "amplify the measurement signal",
                    "Transform the measurement problem into a simpler "
                    "detection problem (go/no-go instead of a continuous scale)",
                ],
            },
        ],
        "note": (
            "See references/substance-field-analysis.md -- "
            "Class 4: measurement and detection Su-Fields."
        ),
    },
    "excessive": {
        "synonyms": ["complex"],
        "classes": [
            {
                "class": 5,
                "name": "Class 5 -- Simplification & helpers",
                "moves": [
                    "Trim a component -- remove a substance or field and "
                    "transfer its function to another element already in "
                    "the system",
                    "Apply self-X (self-service, self-organization) -- let "
                    "the system regulate or act on itself",
                    "Use voids, bubbles, foams, or field-generated "
                    "structures instead of added solid matter",
                    "Break the excessive field into smaller, independently "
                    "controllable sub-fields",
                ],
            },
        ],
        "note": (
            "See references/substance-field-analysis.md -- "
            "Class 5 + Trimming: simplify, restructure, or use cheap/self-"
            "eliminating helpers."
        ),
    },
}

# Build a reverse index: synonym -> canonical state name
_SYNONYM_MAP: dict[str, str] = {}
for _canonical, _entry in _STATE_TABLE.items():
    _SYNONYM_MAP[_canonical] = _canonical
    for _syn in _entry.get("synonyms", []):
        _SYNONYM_MAP[_syn] = _canonical

_VALID_STATES = sorted(_STATE_TABLE.keys())


def recommend(state: str) -> dict[str, Any]:
    """Recommend standard-solution classes for a Su-Field state.

    Args:
        state: One of "incomplete" ("missing"), "insufficient" ("weak"),
               "harmful", "measurement" ("detection"), "excessive" ("complex").
               Case-insensitive.

    Returns:
        dict with keys:
        - "state": normalized canonical state name.
        - "classes": list of {"class": int, "name": str, "moves": [str, ...]}.
        - "note": str or None.

    Raises:
        ValueError: if the state is not recognised.
    """
    normalized = state.lower().strip()
    canonical = _SYNONYM_MAP.get(normalized)
    if canonical is None:
        raise ValueError(
            f"Unknown Su-Field state '{state}'. "
            f"Valid states: {', '.join(_VALID_STATES)}."
        )
    entry = _STATE_TABLE[canonical]
    return {
        "state": canonical,
        "classes": entry["classes"],
        "note": entry["note"],
    }


# -- 76 Standard Solutions DB -------------------------------------------------

# Module-level cache for the solutions database.
_solutions_db: dict[str, Any] | None = None


def load_solutions_db() -> dict[str, Any]:
    """Load the 76 Standard Solutions database from the bundled JSON file.

    Returns the full parsed JSON object (classes, meta, etc.).
    The result is cached so the file is only read once.
    """
    global _solutions_db
    if _solutions_db is not None:
        return _solutions_db
    path = _data_dir() / "standard_solutions_76.json"
    with open(path, "r", encoding="utf-8") as fh:
        _solutions_db = json.load(fh)
    return _solutions_db


def _iter_solutions(
    db: dict[str, Any],
) -> list[dict[str, Any]]:
    """Flatten all solutions (including variants) into a single list.

    Each returned dict has keys: id, name, description, subfield_state,
    mechanism, class_id, group_id, class_name, group_name, and optionally
    parent_id (for variants). Variants inherit the parent mechanism if
    their own is empty.
    """
    results: list[dict[str, Any]] = []
    classes = db.get("classes", {})
    for cls_id, cls_data in classes.items():
        groups = cls_data.get("groups", {})
        for grp_id, grp_data in groups.items():
            for sol in grp_data.get("solutions", []):
                results.append({
                    **sol,
                    "class_id": cls_id,
                    "group_id": grp_id,
                    "class_name": cls_data.get("name", ""),
                    "group_name": grp_data.get("name", ""),
                })
                # Recurse into variants if present.
                for variant in sol.get("variants", []):
                    entry = {
                        **variant,
                        "subfield_state": sol.get("subfield_state", ""),
                        "class_id": cls_id,
                        "group_id": grp_id,
                        "class_name": cls_data.get("name", ""),
                        "group_name": grp_data.get("name", ""),
                        "parent_id": sol["id"],
                    }
                    # R7.1: Inherit parent mechanism if variant has none
                    if not entry.get("mechanism", "").strip():
                        entry["mechanism"] = sol.get("mechanism", "")
                    results.append(entry)
    return results


def lookup_solution(solution_id: str) -> dict[str, Any]:
    """Look up a specific 76 Standard Solution by its ID.

    Args:
        solution_id: Dot-separated solution ID (e.g. "1.1.3" or "5.1.1.7").
            Case-sensitive.  Trailing/leading whitespace is stripped.

    Returns:
        dict with keys: id, name, description, subfield_state, mechanism,
        class_id, group_id, class_name, group_name, and optionally parent_id.

    Raises:
        ValueError: if the solution ID is not found.
    """
    sid = solution_id.strip()
    db = load_solutions_db()
    for sol in _iter_solutions(db):
        if sol["id"] == sid:
            return sol
    raise ValueError(f"Solution '{sid}' not found among the 76 Standard Solutions.")


def search_solutions(query: str) -> list[dict[str, Any]]:
    """Search the 76 Standard Solutions by name or description.

    Args:
        query: Case-insensitive search term.  Matches against solution name
            and description fields.

    Returns:
        List of solution dicts (same shape as lookup_solution), sorted by
        solution ID.  Empty list if no matches.
    """
    q = query.strip().lower()
    if not q:
        return []
    db = load_solutions_db()
    results: list[dict[str, Any]] = []
    for sol in _iter_solutions(db):
        name = sol.get("name", "").lower()
        desc = sol.get("description", "").lower()
        if q in name or q in desc:
            results.append(sol)
    results.sort(key=lambda s: _sort_key(s["id"]))
    return results


def _sort_key(solution_id: str) -> tuple[int, ...]:
    """Convert a dot-separated solution ID to a sortable tuple."""
    return tuple(int(part) for part in solution_id.split("."))


# -- CLI ----------------------------------------------------------------------


def _print_usage() -> None:
    """Print usage and the list of valid states."""
    print("Usage: python triz_standard_solutions.py --state <state>", file=sys.stderr)
    print("       python triz_standard_solutions.py --list", file=sys.stderr)
    print("       python triz_standard_solutions.py --solution <id>", file=sys.stderr)
    print("       python triz_standard_solutions.py --search <query>", file=sys.stderr)
    print("       python triz_standard_solutions.py --list-all", file=sys.stderr)
    print(file=sys.stderr)
    print("Valid states:", file=sys.stderr)
    for s in _VALID_STATES:
        entry = _STATE_TABLE[s]
        synonyms = entry.get("synonyms", [])
        if synonyms:
            syn_str = f"  (also: {', '.join(synonyms)})"
        else:
            syn_str = ""
        print(f"  {s}{syn_str}", file=sys.stderr)


def _print_list() -> None:
    """Print the 5 valid states with a one-line gloss."""
    glosses = {
        "incomplete": "A needed substance or field is missing -- the function cannot happen.",
        "insufficient": "The interaction exists but is too weak to deliver the required function.",
        "harmful": "An unwanted or damaging action accompanies the useful one.",
        "measurement": "You need to detect or measure a property but cannot do so reliably.",
        "excessive": "The system works but is too costly, complex, or over-engineered.",
    }
    for s in _VALID_STATES:
        print(f"  {s:<14} -- {glosses.get(s, '')}")


def _print_solution(sol: dict[str, Any]) -> None:
    """Pretty-print a single solution dict to stdout."""
    cid = sol.get("class_id", "?")
    cname = sol.get("class_name", "")
    gname = sol.get("group_name", "")
    parent = sol.get("parent_id")
    print(f"  ID:       {sol['id']}")
    print(f"  Name:     {sol.get('name', '')}")
    if parent:
        print(f"  Parent:   {parent}")
    print(f"  Class:    Class {cid} -- {cname}")
    print(f"  Group:    {gname}")
    print(f"  State:    {sol.get('subfield_state', '')}")
    print(f"  Mechanism: {sol.get('mechanism', '')}")
    print(f"  Description:")
    # Word-wrap the description for readability.
    desc = sol.get("description", "")
    for line in _wrap_text(desc, width=72):
        print(f"    {line}")
    print()


def _wrap_text(text: str, width: int = 72) -> list[str]:
    """Simple word-wrap: split text into lines no longer than *width* chars."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    current_len = 0
    for w in words:
        if current and current_len + 1 + len(w) > width:
            lines.append(" ".join(current))
            current = [w]
            current_len = len(w)
        else:
            if current:
                current_len += 1
            current.append(w)
            current_len += len(w)
    if current:
        lines.append(" ".join(current))
    return lines


def _print_list_all() -> None:
    """Print all 76 Standard Solutions grouped by class, group, and solution."""
    db = load_solutions_db()
    classes = db.get("classes", {})
    base_count = 0
    variant_count = 0
    for cls_id in sorted(classes, key=int):
        cls_data = classes[cls_id]
        print(f"{'=' * 70}")
        print(f"Class {cls_id}: {cls_data['name']}")
        print(f"  {cls_data.get('tagline', '')}")
        print(f"{'=' * 70}")
        groups = cls_data.get("groups", {})
        for grp_id in sorted(groups, key=_sort_key):
            grp_data = groups[grp_id]
            print(f"\n  Group {grp_id}: {grp_data['name']}")
            print(f"    {grp_data.get('description', '')}")
            for sol in sorted(grp_data.get("solutions", []),
                              key=lambda s: _sort_key(s["id"])):
                base_count += 1
                print(f"\n    [{sol['id']}] {sol['name']}")
                print(f"        {sol.get('mechanism', '')}")
                # Variants
                for variant in sorted(sol.get("variants", []),
                                      key=lambda v: _sort_key(v["id"])):
                    variant_count += 1
                    print(f"\n    [{variant['id']}] {variant['name']}  (variant)")
                    print(f"        {variant.get('description', '')}")
            print()
    print(f"Total: {base_count} standard solutions")
    if variant_count:
        print(f"       + {variant_count} variant(s)")


def _print_search_results(results: list[dict[str, Any]]) -> None:
    """Print a list of search results compactly, then a prompt for details."""
    if not results:
        print("No matching solutions found.")
        return
    print(f"Found {len(results)} matching solution(s):\n")
    for sol in results:
        parent = f" (variant of {sol['parent_id']})" if sol.get("parent_id") else ""
        print(f"  [{sol['id']}] {sol['name']}{parent}")
    print(f"\n  Run with --solution <id> to see full details for any entry.")


def main() -> None:
    if len(sys.argv) < 2:
        _print_usage()
        sys.exit(1)

    if sys.argv[1] == "--list":
        _print_list()
        return

    if sys.argv[1] == "--list-all":
        _print_list_all()
        return

    if sys.argv[1] == "--solution":
        if len(sys.argv) < 3:
            print("Error: --solution requires a solution ID (e.g. '1.1.3').",
                  file=sys.stderr)
            sys.exit(1)
        sid = sys.argv[2]
        try:
            sol = lookup_solution(sid)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        _print_solution(sol)
        return

    if sys.argv[1] == "--search":
        if len(sys.argv) < 3:
            print("Error: --search requires a query string.",
                  file=sys.stderr)
            sys.exit(1)
        query = sys.argv[2]
        results = search_solutions(query)
        _print_search_results(results)
        return

    if sys.argv[1] != "--state":
        _print_usage()
        sys.exit(1)

    if len(sys.argv) < 3:
        _print_usage()
        sys.exit(1)

    state = sys.argv[2]

    try:
        result = recommend(state)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Su-Field state: {result['state']}")
    print()
    for cls in result["classes"]:
        print(f"  {cls['name']}")
        for i, move in enumerate(cls["moves"], 1):
            print(f"    {i}. {move}")
        print()

    if result["note"]:
        print(f"Note: {result['note']}")


if __name__ == "__main__":
    main()
