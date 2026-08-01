#!/usr/bin/env python3
"""
TRIZ Contradiction Network — multi-contradiction dependency analysis.

Analyses problems involving multiple engineering contradictions where resolving
one may affect others. Identifies shared parameters, conflict groups, and
suggests resolution order prioritising the most-connected contradictions.

It is a static one-shot ordering heuristic — it does not model propagation
after hypothetical resolution.

Usage:
    python triz_contradiction_network.py --add <id> <improving> <worsening> "<desc>"
    python triz_contradiction_network.py --analyze           # read JSON from stdin
    python triz_contradiction_network.py --demo              # built-in example

Standard library only — Python 3.8+.
"""

from __future__ import annotations

import sys
import json
import csv
import re as _re
from pathlib import Path
from typing import Any


# -- Parameter loading ---------------------------------------------------------

def _data_dir() -> Path:
    """Path to the bundled data directory, relative to this script."""
    return Path(__file__).resolve().parent / "data"


def _load_parameter_names() -> dict[int, str]:
    """Return {id: name} from parameters_39.csv."""
    params: dict[int, str] = {}
    path = _data_dir() / "parameters_39.csv"
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            params[int(row["id"])] = row["name"].strip()
    return params


def _sort_cid(cid: str) -> int:
    """Extract trailing integer from a contradiction ID like 'C2' or 'C10'."""
    m = _re.search(r'\d+$', cid)
    return int(m.group()) if m else 0


# -- Core functions ------------------------------------------------------------

def add_contradiction(
    network: dict[str, Any],
    cid: str,
    improving_param: int,
    worsening_param: int,
    description: str,
) -> dict[str, Any]:
    """Add a contradiction to the network, returning the updated network.

    Args:
        network: The contradiction network dict (mutated in place).
        cid: Contradiction identifier (e.g. "C1").
        improving_param: ID of the parameter being improved (1..39).
        worsening_param: ID of the parameter that worsens (1..39).
        description: Human-readable description of the contradiction.

    Returns:
        The same network dict with the new contradiction appended.

    Raises:
        ValueError: if cid already exists in the network, or parameter IDs are
                    not int or outside 1..39.
    """
    # R9.1: Reject non-int including bool (mirror R6.2)
    if not isinstance(improving_param, int) or isinstance(improving_param, bool) or not (1 <= improving_param <= 39):
        raise ValueError(
            f"improving_param must be an integer in 1..39, "
            f"got {improving_param!r} (type={type(improving_param).__name__})"
        )
    if not isinstance(worsening_param, int) or isinstance(worsening_param, bool) or not (1 <= worsening_param <= 39):
        raise ValueError(
            f"worsening_param must be an integer in 1..39, "
            f"got {worsening_param!r} (type={type(worsening_param).__name__})"
        )

    # Reject duplicate IDs
    for existing in network["contradictions"]:
        if existing["id"] == cid:
            raise ValueError(f"Contradiction id {cid!r} already exists in network")

    param_names = _load_parameter_names()

    entry: dict[str, Any] = {
        "id": cid,
        "improving": improving_param,
        "worsening": worsening_param,
        "improving_name": param_names[improving_param],
        "worsening_name": param_names[worsening_param],
        "description": description,
    }
    network["contradictions"].append(entry)
    return network


def find_shared_parameters(
    network: dict[str, Any],
) -> dict[int, list[str]]:
    """Find parameters that appear in more than one contradiction.

    Returns:
        Dict mapping parameter_id -> list of contradiction IDs that reference it
        (only parameters referenced by 2+ contradictions are included).
    """
    # param_id -> set of contradiction IDs
    param_uses: dict[int, set[str]] = {}

    for contra in network["contradictions"]:
        for key in ("improving", "worsening"):
            pid = contra[key]
            param_uses.setdefault(pid, set()).add(contra["id"])

    # Keep only parameters that appear in 2+ contradictions
    return {
        pid: sorted(uses)
        for pid, uses in param_uses.items()
        if len(uses) >= 2
    }


def find_conflicts(network: dict[str, Any]) -> list[dict[str, Any]]:
    """Find groups of contradictions that share parameters.

    Returns:
        List of conflict-group dicts, each with:
        - "parameter_id": int
        - "parameter_name": str
        - "role": "improving" or "worsening" (all members share this role on the param)
        - "contradiction_ids": list of contradiction IDs in the group

        Groups where two contradictions share a parameter but with different roles
        are listed separately for each role.
    """
    param_names = _load_parameter_names()

    # R9.1: Validate all parameter IDs before any lookup
    for contra in network["contradictions"]:
        for key in ("improving", "worsening"):
            pid = contra[key]
            if not isinstance(pid, int) or isinstance(pid, bool) or not (1 <= pid <= 39):
                raise ValueError(
                    f"Invalid parameter {pid!r} in contradiction {contra.get('id', '?')} "
                    f"(must be int in 1..39)"
                )

    conflicts: list[dict[str, Any]] = []

    # Build index: (param_id, role) -> set of contradiction IDs
    role_index: dict[tuple[int, str], set[str]] = {}

    for contra in network["contradictions"]:
        for role in ("improving", "worsening"):
            pid = contra[role]
            key = (pid, role)
            if key not in role_index:
                role_index[key] = set()
            role_index[key].add(contra["id"])

    # Now also check cross-role sharing (param as improving in one, worsening in another)
    cross_index: dict[int, set[str]] = {}

    for contra in network["contradictions"]:
        for role in ("improving", "worsening"):
            pid = contra[role]
            if pid not in cross_index:
                cross_index[pid] = set()
            cross_index[pid].add(contra["id"])

    seen_groups: set[tuple] = set()

    # Same-role conflicts
    for (pid, role), cids in role_index.items():
        if len(cids) >= 2:
            sorted_cids = sorted(cids)
            group_key = (pid, role, tuple(sorted_cids))
            if group_key not in seen_groups:
                seen_groups.add(group_key)
                conflicts.append({
                    "parameter_id": pid,
                    "parameter_name": param_names[pid],
                    "role": role,
                    "contradiction_ids": sorted_cids,
                })

    # Cross-role conflicts: same param, different roles across contradictions
    for pid, cids in cross_index.items():
        if len(cids) >= 2:
            roles_seen: set[str] = set()
            for contra in network["contradictions"]:
                if contra["id"] in cids:
                    if contra["improving"] == pid:
                        roles_seen.add("improving")
                    if contra["worsening"] == pid:
                        roles_seen.add("worsening")
            if roles_seen == {"improving", "worsening"}:
                sorted_cids = sorted(cids)
                group_key = ("cross", pid, tuple(sorted_cids))
                if group_key not in seen_groups:
                    seen_groups.add(group_key)
                    conflicts.append({
                        "parameter_id": pid,
                        "parameter_name": param_names[pid],
                        "role": "mixed",
                        "contradiction_ids": sorted_cids,
                    })

    return conflicts


def suggest_resolution_order(network: dict[str, Any]) -> list[dict[str, Any]]:
    """Suggest resolution order prioritising most-connected contradictions.

    Contradictions that share parameters with the most other contradictions
    are ranked first — resolving them may simplify or eliminate the others.

    Returns:
        List of dicts, each with:
        - "id": contradiction ID
        - "connected_count": how many distinct other contradictions share a parameter
        - "shared_params": list of parameter_ids shared with other contradictions
        - "description": contradiction description
        Ordered by connected_count descending, ties broken numerically (C2 before C10).
    """
    shared = find_shared_parameters(network)

    # R9.2: Count distinct neighboring contradiction IDs, not shared params
    neighbor_map: dict[str, set[str]] = {}  # cid -> set of neighbor contradiction IDs
    param_map: dict[str, set[int]] = {}     # cid -> set of shared parameter IDs
    for pid, cids in shared.items():
        for cid in cids:
            param_map.setdefault(cid, set()).add(pid)
            neighbor_map.setdefault(cid, set()).update(c for c in cids if c != cid)

    result: list[dict[str, Any]] = []
    for contra in network["contradictions"]:
        cid = contra["id"]
        shared_params = sorted(param_map.get(cid, set()))
        neighbor_count = len(neighbor_map.get(cid, set()))
        result.append({
            "id": cid,
            "connected_count": neighbor_count,
            "shared_params": shared_params,
            "description": contra["description"],
        })

    # R9.3: Sort ties numerically by trailing integer
    result.sort(key=lambda x: (-x["connected_count"], _sort_cid(x["id"])))
    return result


def analyze_network(contradictions: list[dict[str, Any]]) -> dict[str, Any]:
    """Run a full analysis on a list of contradiction dicts.

    Args:
        contradictions: List of contradiction dicts, each with keys:
            id, improving, worsening, improving_name, worsening_name, description.

    Returns:
        Dict with keys:
        - "contradictions": the input list (echoed)
        - "shared_parameters": from find_shared_parameters()
        - "conflicts": from find_conflicts()
        - "resolution_order": from suggest_resolution_order()
        - "summary": human-readable summary string
    """
    network: dict[str, Any] = {"contradictions": contradictions}

    shared_params = find_shared_parameters(network)
    conflicts = find_conflicts(network)
    resolution_order = suggest_resolution_order(network)

    # Build a human-readable summary
    lines: list[str] = []
    lines.append(f"Network: {len(contradictions)} contradictions")
    lines.append(f"Shared parameters across contradictions: {len(shared_params)}")
    lines.append(f"Conflict groups: {len(conflicts)}")

    if resolution_order:
        top = resolution_order[0]
        lines.append(
            f"Suggested first to resolve: {top['id']} "
            f"(connected to {top['connected_count']} other contradiction(s))"
        )

    return {
        "contradictions": contradictions,
        "shared_parameters": shared_params,
        "conflicts": conflicts,
        "resolution_order": resolution_order,
        "summary": "\n".join(lines),
    }


# -- Demo ----------------------------------------------------------------------

def _demo_contradictions() -> list[dict[str, Any]]:
    """Return a built-in set of interconnected contradictions.

    Scenario: designing a portable bridge (think military/emergency).
    """
    network: dict[str, Any] = {"contradictions": []}

    # C1: Improving strength (14) increases weight (1)
    add_contradiction(
        network, "C1", 14, 1,
        "Improving structural strength increases weight",
    )
    # C2: Reducing weight (1) worsens shape stability (12)
    add_contradiction(
        network, "C2", 1, 12,
        "Reducing weight compromises shape stability under load",
    )
    # C3: Improving shape stability (12) reduces ease of manufacture (32)
    add_contradiction(
        network, "C3", 12, 32,
        "Complex shapes for stability are harder to manufacture",
    )
    # C4: Improving ease of manufacture (32) reduces strength (14)
    add_contradiction(
        network, "C4", 32, 14,
        "Simpler manufacturing processes result in lower strength",
    )

    return network["contradictions"]


def _run_demo() -> None:
    """Run a demonstration with built-in examples and print full analysis."""
    contradictions = _demo_contradictions()
    result = analyze_network(contradictions)

    print("=" * 62)
    print("  TRIZ Contradiction Network — Demo")
    print("=" * 62)
    print()
    print("Scenario: portable emergency bridge design")
    print()

    # List contradictions
    print("--- Contradictions ---")
    for c in result["contradictions"]:
        print(
            f"  {c['id']}: improve {c['improving_name']} (id={c['improving']}) "
            f"/ worsens {c['worsening_name']} (id={c['worsening']})"
        )
        print(f"      \"{c['description']}\"")
    print()

    # Shared parameters
    print("--- Shared Parameters ---")
    shared: dict[int, list[str]] = result["shared_parameters"]
    if shared:
        param_names = _load_parameter_names()
        for pid, cids in sorted(shared.items()):
            print(f"  {param_names[pid]} (id={pid}) shared by: {', '.join(cids)}")
    else:
        print("  (no shared parameters)")
    print()

    # Conflicts
    print("- Conflict Groups -")
    for grp in result["conflicts"]:
        print(
            f"  Parameter {grp['parameter_name']} (id={grp['parameter_id']}) "
            f"as {grp['role']}: {', '.join(grp['contradiction_ids'])}"
        )
    print()

    # Resolution order
    print("- Suggested Resolution Order -")
    for item in result["resolution_order"]:
        marker = " <-- resolve first" if item["connected_count"] == max(
            r["connected_count"] for r in result["resolution_order"]
        ) else ""
        print(
            f"  {item['id']}: connected={item['connected_count']} "
            f"params={item['shared_params']}{marker}"
        )
        print(f"      \"{item['description']}\"")
    print()

    # Summary
    print("- Summary -")
    print(result["summary"])


# -- CLI ------------------------------------------------------------------------

def _run_add(argv: list[str]) -> None:
    """Handle --add <id> <improving> <worsening> <description>."""
    if len(argv) < 4:
        print(
            "Usage: python triz_contradiction_network.py --add <id> <improving> <worsening> \"<desc>\"",
            file=sys.stderr,
        )
        sys.exit(1)

    cid = argv[0]
    try:
        improving = int(argv[1])
        worsening = int(argv[2])
    except ValueError:
        print("Error: improving and worsening must be integers in 1..39", file=sys.stderr)
        sys.exit(1)

    description = " ".join(argv[3:])
    network: dict[str, Any] = {"contradictions": []}

    try:
        add_contradiction(network, cid, improving, worsening, description)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(network["contradictions"], indent=2))


def _run_analyze() -> None:
    """Handle --analyze: read JSON array from stdin, print analysis."""
    raw = sys.stdin.read().strip()
    if not raw:
        print("Error: no input on stdin. Pipe a JSON array of contradiction dicts.", file=sys.stderr)
        sys.exit(1)

    try:
        contradictions = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(contradictions, list):
        print("Error: expected a JSON array of contradiction objects", file=sys.stderr)
        sys.exit(1)

    # Validate each contradiction has required fields
    required = {"id", "improving", "worsening", "improving_name", "worsening_name", "description"}
    for i, c in enumerate(contradictions):
        if not isinstance(c, dict):
            print(f"Error: item {i} is not an object", file=sys.stderr)
            sys.exit(1)
        missing = required - set(c.keys())
        if missing:
            print(
                f"Error: contradiction at index {i} missing fields: {', '.join(sorted(missing))}",
                file=sys.stderr,
            )
            sys.exit(1)
        # R9.1: Validate improving/worsening are valid ints
        for key in ("improving", "worsening"):
            val = c[key]
            if not isinstance(val, int) or isinstance(val, bool) or not (1 <= val <= 39):
                print(
                    f"Error: contradiction at index {i}: '{key}' must be an integer 1..39, "
                    f"got {val!r}",
                    file=sys.stderr,
                )
                sys.exit(1)

    result = analyze_network(contradictions)
    print(json.dumps(result, indent=2))


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python triz_contradiction_network.py --add <id> <improving> <worsening> \"<desc>\"",
            file=sys.stderr,
        )
        print(
            "       python triz_contradiction_network.py --analyze",
            file=sys.stderr,
        )
        print(
            "       python triz_contradiction_network.py --demo",
            file=sys.stderr,
        )
        sys.exit(1)

    command = sys.argv[1]

    if command == "--demo":
        _run_demo()
    elif command == "--add":
        _run_add(sys.argv[2:])
    elif command == "--analyze":
        _run_analyze()
    else:
        print(f"Unknown option: {command}", file=sys.stderr)
        print("Expected: --add, --analyze, or --demo", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
