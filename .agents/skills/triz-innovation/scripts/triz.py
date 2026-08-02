#!/usr/bin/env python3
"""
TRIZ master tool — one entrypoint for every TRIZ helper.

A single dispatcher that Claude Code or Codex can call when a TRIZ capability is
needed, instead of remembering each individual script. It forwards to the right
sub-tool using the same Python interpreter and absolute paths, so it works from
any working directory.

Usage:
    python triz.py <command> [args...]
    python triz.py [--branch <id>] [--lang <lang>] <command> [args...]
    python triz.py                       # list commands
    python triz.py help                  # list commands

Global flags (position-independent; stripped before forwarding):
    --branch <id>    field branch: any registered field branch (default general)
    --lang <lang>    language overlay: en|it|auto (default en)
    These are forwarded to `route` (both) and to `case`/`branches` (--lang
    only); every other command ignores them. Unknown --branch values (ids not
    registered as a field branch) and unknown --lang values are rejected here
    with a clear error (exit 1) rather than forwarded.

Commands:
    route "<problem text>"               -> suggest TRIZ methods + contradictions
    matrix <improving_id> <worsening_id> -> contradiction-matrix lookup
    matrix --list                        -> list the 39 parameters
    sufield --state <state>              -> Su-Field / 76-standard-solutions classes
    sufield --list                       -> list the 5 Su-Field states
    ariz "<title>"                       -> generate an ARIZ-85C worksheet
    evolution [--signals "..."]          -> S-curve stage + 8 evolution trends
    case "<title>"                       -> create a blank TRIZ case file
    evaluate [solutions.csv]             -> score & rank solutions from a CSV
    effects --function <query>           -> search scientific effects by function
    effects --keyword <query>            -> search scientific effects by keyword
    network --demo                       -> contradiction network demo
    network --analyze                    -> analyze network from stdin JSON
    branches list|check|info|resolve|detect -> manage field + language branches
    master                               -> show the TRIZ-MASTER.md knowledge base

Aliases: router->route, standard-solutions/standard_solutions/su-field->sufield,
         evaluator->evaluate, kb/knowledge-base->master.

Standard library only — Python 3.8+.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

from triz_branches import list_branches

# command -> sub-script filename (lives beside this file)
_COMMANDS = {
    "route": "triz_router.py",
    "matrix": "triz_matrix.py",
    "sufield": "triz_standard_solutions.py",
    "ariz": "triz_ariz.py",
    "evolution": "triz_evolution.py",
    "case": "triz_case_template.py",
    "evaluate": "triz_evaluator.py",
    "effects": "triz_effects.py",
    "network": "triz_contradiction_network.py",
    "branches": "triz_branches.py",
}

# friendly aliases -> canonical command
_ALIASES = {
    "router": "route",
    "standard-solutions": "sufield",
    "standard_solutions": "sufield",
    "su-field": "sufield",
    "evaluator": "evaluate",
    "kb": "master",
    "knowledge-base": "master",
}

_SCRIPT_DIR = Path(__file__).resolve().parent

_VALID_LANGS = ("en", "it", "auto")


def _valid_branches() -> tuple[str, ...]:
    """Registered field branch ids, derived from the branch registry."""
    return tuple(list_branches()["fields"])

# Sub-tools that accept the global flags. route takes --branch + --lang;
# case and branches take --lang only (branches resolve requires it).
_FLAG_CONSUMERS = {
    "route": ("branch", "lang"),
    "case": ("lang",),
    "branches": ("lang",),
}


def _find_master() -> Optional[Path]:
    """Walk up from the script dir to find TRIZ-MASTER.md at the repo root."""
    for parent in [_SCRIPT_DIR, *_SCRIPT_DIR.parents]:
        candidate = parent / "TRIZ-MASTER.md"
        if candidate.is_file():
            return candidate
    return None


def _print_usage(stream=sys.stdout) -> None:
    print(__doc__.strip(), file=stream)


def _run_master() -> int:
    """Show where the master knowledge base lives and its section headings."""
    master = _find_master()
    if master is None:
        print(
            "TRIZ-MASTER.md not found. Expected at the repository root.",
            file=sys.stderr,
        )
        return 1
    print(f"TRIZ master knowledge base: {master}")
    print()
    print("Sections:")
    for line in master.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            print(f"  {line[3:].strip()}")
    return 0


def _parse_global_flags(argv: list) -> tuple[dict, list, int]:
    """Extract --branch/--lang from argv; return (flags, remaining, exit_code).

    Flags may appear anywhere (before or after the command). `--flag value`
    and `--flag=value` forms are both accepted. Unknown values produce a
    non-zero exit code here so the user sees a clear error immediately.
    """
    flags: dict = {}
    rest: list = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--branch" or arg.startswith("--branch="):
            if "=" in arg:
                value = arg.split("=", 1)[1]
            else:
                if i + 1 >= len(argv):
                    print("Error: --branch requires a value.", file=sys.stderr)
                    return flags, rest, 1
                value = argv[i + 1]
                i += 1
            if value not in _valid_branches():
                print(
                    f"Error: unknown --branch value {value!r} "
                    f"(expected {', '.join(_valid_branches())}).",
                    file=sys.stderr,
                )
                return flags, rest, 1
            flags["branch"] = value
        elif arg == "--lang" or arg.startswith("--lang="):
            if "=" in arg:
                value = arg.split("=", 1)[1]
            else:
                if i + 1 >= len(argv):
                    print("Error: --lang requires a value.", file=sys.stderr)
                    return flags, rest, 1
                value = argv[i + 1]
                i += 1
            if value not in _VALID_LANGS:
                print(
                    f"Error: unknown --lang value {value!r} "
                    f"(expected {', '.join(_VALID_LANGS)}).",
                    file=sys.stderr,
                )
                return flags, rest, 1
            flags["lang"] = value
        else:
            rest.append(arg)
        i += 1
    return flags, rest, 0


def dispatch(argv: list) -> int:
    """Dispatch a master-tool invocation. Returns a process exit code.

    Args:
        argv: arguments after the program name (e.g. ["matrix", "14", "1"]).

    Returns:
        The exit code of the invoked sub-tool (0 on success).
    """
    flags, rest, flag_err = _parse_global_flags(argv)
    if flag_err:
        return flag_err

    if not rest or rest[0] in ("help", "--help", "-h", "list", "--list"):
        _print_usage()
        return 0

    command = rest[0].lower()
    command = _ALIASES.get(command, command)

    if command == "master":
        return _run_master()

    script = _COMMANDS.get(command)
    if script is None:
        print(f"Unknown command: {rest[0]!r}", file=sys.stderr)
        print(file=sys.stderr)
        _print_usage(sys.stderr)
        return 2

    script_path = _SCRIPT_DIR / script
    if not script_path.is_file():
        print(f"Sub-tool not found: {script_path}", file=sys.stderr)
        return 1

    # Forward the supplied global flags as leading flags, but only to sub-tools
    # that support them. Other sub-tools ignore the flags entirely.
    forward: list = []
    supported = _FLAG_CONSUMERS.get(command, ())
    if "branch" in flags and "branch" in supported:
        forward += ["--branch", flags["branch"]]
    if "lang" in flags and "lang" in supported:
        forward += ["--lang", flags["lang"]]

    completed = subprocess.run(
        [sys.executable, str(script_path), *forward, *rest[1:]]
    )
    return completed.returncode


def main() -> None:
    # Windows-safe stdout
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    sys.exit(dispatch(sys.argv[1:]))


if __name__ == "__main__":
    main()
