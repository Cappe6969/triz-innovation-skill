#!/usr/bin/env python3
"""
TRIZ Scientific Effects Database — function-oriented search of physical,
chemical, geometric, and behavioral effects.

Searches the bundled scientific_effects.json by function family or keyword.
Each effect describes a mechanism, required resources, output, and real-world
examples — useful during the TRIZ "How" step (after the contradiction matrix
suggests *what* to change, effects suggest *how* to implement it).

Usage:
    python triz_effects.py --function "detect"          # search by function family
    python triz_effects.py --keyword "magnetic"          # keyword search
    python triz_effects.py --list                        # list all function families
    python triz_effects.py --family "detect_measure"     # list effects in a family

Standard library only — Python 3.9+.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


# ── Data ─────────────────────────────────────────────────────────────────────────


def _data_dir() -> Path:
    """Path to the bundled data directory, relative to this script."""
    return Path(__file__).resolve().parent / "data"


def load_effects() -> list[dict[str, Any]]:
    """Return all effects from scientific_effects.json as a list of dicts."""
    path = _data_dir() / "scientific_effects.json"
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ── Search / lookup ─────────────────────────────────────────────────────────────


def search_by_function(query: str) -> list[dict[str, Any]]:
    """Return effects whose function_family matches *query* (case-insensitive).

    The query is split into words; a family matches if it contains **any**
    query word as a substring. This lets natural-language queries like
    "move liquid" hit `move_transport`, which a whole-phrase substring search
    would miss. Single-word queries behave exactly like a plain substring
    search.

    Args:
        query: One or more words to match against function family names.

    Returns:
        List of matching effect dicts (empty list if none match).
    """
    q = query.strip().lower()
    if not q:
        return []
    tokens = [t for t in q.split() if t]
    return [
        effect for effect in load_effects()
        if any(t in effect["function_family"].lower() for t in tokens)
    ]


def search_by_keyword(query: str) -> list[dict[str, Any]]:
    """Return effects whose name, mechanism, or function family contains *query*.

    Searches across effect_name, mechanism, function_family, and output fields.

    Args:
        query: Keyword or substring to search for (case-insensitive).

    Returns:
        List of matching effect dicts (empty list if none match).
    """
    q = query.strip().lower()
    if not q:
        return []
    results: list[dict[str, Any]] = []
    for effect in load_effects():
        searchable = " ".join(
            [
                effect.get("effect_name", ""),
                effect.get("mechanism", ""),
                effect.get("function_family", ""),
                effect.get("output", ""),
            ]
        ).lower()
        if q in searchable:
            results.append(effect)
    return results


def get_function_families() -> list[str]:
    """Return the sorted list of unique function family names."""
    families: set[str] = set()
    for effect in load_effects():
        families.add(effect["function_family"])
    return sorted(families)


def list_effects(family: str = None) -> list[dict[str, Any]]:
    """Return effects, optionally filtered by function family.

    Args:
        family: Function family name to filter by (case-insensitive).
                If None, returns all effects.

    Returns:
        List of effect dicts.
    """
    effects = load_effects()
    if family is None:
        return effects
    f = family.strip().lower()
    if not f:
        return effects
    return [
        effect for effect in effects if effect["function_family"].lower() == f
    ]


# ── Formatting ──────────────────────────────────────────────────────────────────


def format_effect(effect: dict[str, Any], index: int = None) -> str:
    """Format a single effect as a readable text block.

    Args:
        effect: Effect dict from the database.
        index: Optional 1-based index for numbered output.

    Returns:
        Formatted multi-line string.
    """
    prefix = f"[{index}] " if index is not None else ""
    lines = [
        f"{prefix}{effect['effect_name']}  (domain: {effect.get('domain', '-')})",
        f"  Family:     {effect['function_family']}",
        f"  Mechanism:  {effect['mechanism']}",
        f"  Output:     {effect['output']}",
        f"  Resources:  {', '.join(effect.get('resources_needed', []))}",
        f"  Examples:   {', '.join(effect.get('examples', []))}",
    ]
    return "\n".join(lines)


def format_effects(effects: list[dict[str, Any]], title: str = None) -> str:
    """Format a list of effects with optional title and numbered entries.

    Args:
        effects: List of effect dicts.
        title: Optional header line printed before the results.

    Returns:
        Formatted multi-line string.
    """
    parts: list[str] = []
    if title:
        parts.append(title)
        parts.append("-" * len(title))
    if not effects:
        parts.append("(no effects found)")
    else:
        for i, effect in enumerate(effects, start=1):
            if i > 1:
                parts.append("")  # blank line between entries
            parts.append(format_effect(effect, index=i))
    return "\n".join(parts)


# ── CLI ─────────────────────────────────────────────────────────────────────────


def _safe_print(*args: Any, file: object = None, **kwargs: Any) -> None:
    """Print with encoding-tolerant fallback for Windows console codecs.

    Replaces any character that cannot be encoded by the target stream
    rather than raising UnicodeEncodeError.
    """
    target = file if file is not None else sys.stdout
    try:
        print(*args, file=target, **kwargs)
    except UnicodeEncodeError:
        # Some characters (e.g. right-arrow) can't encode in cp1252.
        # Fall back to 'replace' strategy.
        encoded_args = []
        for arg in args:
            encoded_args.append(
                str(arg)
                .encode(target.encoding or "utf-8", errors="replace")
                .decode(target.encoding or "utf-8", errors="replace")
            )
        print(*encoded_args, file=target, **kwargs)


def _print_families() -> None:
    """Print all function family names with effect counts."""
    effects = load_effects()
    families: dict[str, int] = {}
    for effect in effects:
        f = effect["function_family"]
        families[f] = families.get(f, 0) + 1

    print(f"{len(families)} function families:")
    for name in sorted(families):
        print(f"  {name}  ({families[name]} effects)")


def _print_usage() -> None:
    """Print usage to stderr and exit."""
    print(
        "Usage: python triz_effects.py --function <query>",
        file=sys.stderr,
    )
    print(
        "       python triz_effects.py --keyword <query>",
        file=sys.stderr,
    )
    print(
        "       python triz_effects.py --list",
        file=sys.stderr,
    )
    print(
        "       python triz_effects.py --family <family_name>",
        file=sys.stderr,
    )
    print(
        "\nHint: run 'python triz_effects.py --list' to see function families.",
        file=sys.stderr,
    )


def main() -> None:
    if len(sys.argv) < 2:
        _print_usage()
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--list":
        _print_families()
        return

    if arg == "--function":
        if len(sys.argv) < 3:
            print(
                "Error: --function requires a query string.",
                file=sys.stderr,
            )
            sys.exit(1)
        query = sys.argv[2]
        results = search_by_function(query)
        _safe_print(format_effects(results, title=f'Effects matching function "{query}":'))
        return

    if arg == "--keyword":
        if len(sys.argv) < 3:
            print(
                "Error: --keyword requires a query string.",
                file=sys.stderr,
            )
            sys.exit(1)
        query = sys.argv[2]
        results = search_by_keyword(query)
        _safe_print(format_effects(results, title=f'Effects matching keyword "{query}":'))
        return

    if arg == "--family":
        if len(sys.argv) < 3:
            print(
                "Error: --family requires a family name.",
                file=sys.stderr,
            )
            sys.exit(1)
        family = sys.argv[2]
        all_families = get_function_families()
        if family.lower() not in (f.lower() for f in all_families):
            print(
                f'Error: unknown family "{family}". '
                f"Run --list to see available families.",
                file=sys.stderr,
            )
            sys.exit(1)
        results = list_effects(family=family)
        _safe_print(format_effects(results, title=f'Effects in family "{family}":'))
        return

    print(f'Error: unknown flag "{arg}".', file=sys.stderr)
    _print_usage()
    sys.exit(1)


if __name__ == "__main__":
    main()