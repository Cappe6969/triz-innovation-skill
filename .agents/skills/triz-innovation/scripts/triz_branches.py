#!/usr/bin/env python3
"""
TRIZ branch registry — field + language branches for the triz-innovation skill.

The skill is a mix of branches: `branches/fields/<id>/branch.json` carries
domain vocabulary (keywords, parameter translations, soft principle readings,
examples) and `branches/langs/<lang>/branch.json` carries localized labels plus
stopwords for language auto-detection. This registry lists, reads, validates and
searches those pure-data files.

Usage:
    python triz_branches.py list                 # list field + lang branch ids
    python triz_branches.py info <field_id>      # print a field branch JSON
    python triz_branches.py resolve --lang it    # print resolved label dict
    python triz_branches.py check                # validate all branch files
    python triz_branches.py detect "<text>"      # print 'it' or 'en'

Standard library only — Python 3.8+.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
_BRANCHES_DIR = _SCRIPT_DIR.parent / "branches"
_FIELDS_DIR = _BRANCHES_DIR / "fields"
_LANGS_DIR = _BRANCHES_DIR / "langs"

_FIELD_REQUIRED = {"id", "name", "name_it", "description", "keywords", "examples"}
_LANG_REQUIRED = {"lang", "name", "labels", "contradiction_labels", "stopwords"}

# Canonical ordering for the shipped branches; unknown ids are appended
# alphabetically so the registry auto-extends when a new branch is added.
_FIELD_IDS = ["general", "business", "software", "rehab",
              "mechanical", "datascience", "marketing", "supplychain"]
_LANG_IDS = ["en", "it"]

# Small English cue list used by the language heuristic. It is deliberately a
# cue list, not a language detector: distinctive Italian stopwords are scored
# against these English cues and the higher count wins.
_ENGLISH_CUES = [
    "the", "an", "of", "to", "is", "are", "this", "that",
    "for", "how", "what", "when", "why", "not", "can", "with", "and",
]


def _word_hits(words: list[str], text: str) -> int:
    return sum(1 for w in words if re.search(rf"\b{re.escape(w)}\b", text))


def list_branches() -> dict[str, list[str]]:
    """Return the branch inventory as {"fields": [...], "langs": [...]} in
    deterministic order (canonical shipped order first, extras appended
    alphabetically)."""
    fields = [f for f in _FIELD_IDS if (_FIELDS_DIR / f).is_dir()]
    fields += sorted(
        p.name for p in _FIELDS_DIR.iterdir() if p.is_dir() and p.name not in _FIELD_IDS
    )
    langs = [lang for lang in _LANG_IDS if (_LANGS_DIR / lang).is_dir()]
    langs += sorted(
        p.name for p in _LANGS_DIR.iterdir() if p.is_dir() and p.name not in _LANG_IDS
    )
    return {"fields": fields, "langs": langs}


def get_field_branch(field_id: str) -> dict[str, Any]:
    """Return the parsed field branch JSON, or raise KeyError for unknown id."""
    path = _FIELDS_DIR / field_id / "branch.json"
    if not path.is_file():
        raise KeyError(f"Unknown field branch: {field_id!r}")
    return json.loads(path.read_text(encoding="utf-8"))


def get_lang_branch(lang: str) -> dict[str, Any]:
    """Return the parsed language branch JSON, or raise KeyError for unknown lang."""
    path = _LANGS_DIR / lang / "branch.json"
    if not path.is_file():
        raise KeyError(f"Unknown language branch: {lang!r}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_labels(lang: str) -> dict[str, str]:
    """Return the merged label dict for a language (field-independent).

    English is the identity overlay (empty labels); Italian returns its label
    dict. Unknown lang raises KeyError.
    """
    if lang == "en":
        return {}
    return get_lang_branch(lang).get("labels", {})


def detect_language(text: str) -> str:
    """Heuristic language guess for a problem text: 'it' or 'en'.

    Scores the Italian stopwords from branches/langs/it/branch.json against a
    small English cue list. Returns "it" when Italian hits >= 1 AND Italian
    hits >= English hits, else "en". This is a heuristic, not a language
    detector — short or cue-free text falls back to "en".
    """
    it_stopwords = get_lang_branch("it").get("stopwords", [])
    lower = text.lower()
    it_hits = _word_hits(it_stopwords, lower)
    en_hits = _word_hits(_ENGLISH_CUES, lower)
    if it_hits >= 1 and it_hits >= en_hits:
        return "it"
    return "en"


def validate() -> list[str]:
    """Walk every branch file and return a list of error strings (empty when
    valid). Does NOT raise; callers decide what to do with the errors."""
    errors: list[str] = []

    for field in list_branches()["fields"]:
        path = _FIELDS_DIR / field / "branch.json"
        if not path.is_file():
            errors.append(f"missing file: {path}")
            continue
        data = _load_json(path, errors)
        if data is None:
            continue
        for key in sorted(_FIELD_REQUIRED):
            if key not in data:
                errors.append(f"{path}: missing required key {key!r}")
        if data.get("id") != field:
            errors.append(f"{path}: id {data.get('id')!r} != directory name {field!r}")
        for key in ("keywords", "examples"):
            if key in data and not isinstance(data[key], list):
                errors.append(f"{path}: {key!r} must be a list")
        for key in ("parameter_map", "principle_soft"):
            if key in data and not isinstance(data[key], dict):
                errors.append(f"{path}: {key!r} must be a dict")

    for lang in list_branches()["langs"]:
        path = _LANGS_DIR / lang / "branch.json"
        if not path.is_file():
            errors.append(f"missing file: {path}")
            continue
        data = _load_json(path, errors)
        if data is None:
            continue
        for key in sorted(_LANG_REQUIRED):
            if key not in data:
                errors.append(f"{path}: missing required key {key!r}")
        if data.get("lang") != lang:
            errors.append(f"{path}: lang {data.get('lang')!r} != directory name {lang!r}")
        for key in ("labels", "contradiction_labels"):
            if key in data and not isinstance(data[key], dict):
                errors.append(f"{path}: {key!r} must be a dict")
        if "stopwords" in data and not isinstance(data["stopwords"], list):
            errors.append(f"{path}: 'stopwords' must be a list")

    return errors


def _load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return None


def _strip_lang(argv: list) -> tuple[list, str | None]:
    """Pull `--lang <v>`/`--lang=<v>` out of argv at any position.

    Mirrors the dispatcher's position-independent global flags so
    `triz.py branches resolve --lang it` (forwarded as leading flags) and
    direct `triz_branches.py resolve --lang it` both work.
    """
    rest: list = []
    value: str | None = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--lang" or arg.startswith("--lang="):
            if "=" in arg:
                value = arg.split("=", 1)[1]
            else:
                if i + 1 >= len(argv):
                    raise ValueError("--lang requires a value")
                value = argv[i + 1]
                i += 1
        else:
            rest.append(arg)
        i += 1
    return rest, value


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

    try:
        argv, lang = _strip_lang(argv)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    if lang is not None and lang not in _LANG_IDS:
        print(
            f"Error: unknown --lang value {lang!r} "
            f"(expected {', '.join(_LANG_IDS)}).",
            file=sys.stderr,
        )
        sys.exit(1)

    command = argv[0]
    if command == "list":
        inv = list_branches()
        print("fields: " + ", ".join(inv["fields"]))
        print("langs: " + ", ".join(inv["langs"]))
        sys.exit(0)

    if command == "info":
        if len(argv) < 2:
            print("Usage: python triz_branches.py info <field_id>", file=sys.stderr)
            sys.exit(1)
        try:
            data = get_field_branch(argv[1])
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        sys.exit(0)

    if command == "resolve":
        if lang is None:
            print("Usage: python triz_branches.py resolve --lang <lang>", file=sys.stderr)
            sys.exit(1)
        try:
            labels = resolve_labels(lang)
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(labels, ensure_ascii=False, indent=2))
        sys.exit(0)

    if command == "check":
        errors = validate()
        if errors:
            for error in errors:
                print(error)
            sys.exit(1)
        inv = list_branches()
        print(f"OK — {len(inv['fields'])} field branch(es), {len(inv['langs'])} language overlay(s)")
        sys.exit(0)

    if command == "detect":
        text = " ".join(argv[1:])
        print(detect_language(text))
        sys.exit(0)

    _print_usage()
    sys.exit(1)


if __name__ == "__main__":
    main()
