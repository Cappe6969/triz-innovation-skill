#!/usr/bin/env python3
"""Validate fixtures or execute one explicit Codex benchmark arm."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS = Path(__file__).resolve().parent
FIXTURES = BENCHMARKS / "fixtures"
SKILL = ROOT / "skills" / "triz-coding-method"
MODEL = "gpt-5.6-luna"


def load_fixture(fixture_id: str) -> dict[str, Any]:
    path = FIXTURES / (fixture_id + ".json")
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"id", "visibility", "prompt", "test_command", "expected", "files"}
    if data.get("id") != fixture_id or not required <= set(data):
        raise ValueError("invalid fixture schema: " + fixture_id)
    if data["visibility"] not in ("public", "anonymized-real"):
        raise ValueError("invalid fixture visibility: " + fixture_id)
    if data["visibility"] == "anonymized-real" and not re.fullmatch(r"[0-9a-f]{8}", data.get("derived_from", "")):
        raise ValueError("real fixture needs an eight-character commit id")
    if not isinstance(data["test_command"], list) or not data["test_command"]:
        raise ValueError("test_command must be a non-empty array")
    if not isinstance(data["files"], dict) or not data["files"]:
        raise ValueError("files must be a non-empty object")
    if data["expected"] != {"initial_tests": "fail", "target_tests": "pass"}:
        raise ValueError("fixture expected outcome must be fail -> pass")
    for name, content in data["files"].items():
        candidate = Path(name)
        if candidate.is_absolute() or ".." in candidate.parts or not isinstance(content, str):
            raise ValueError("unsafe fixture path: " + name)
    return data


def validate_all() -> None:
    manifest = json.loads((BENCHMARKS / "manifest.json").read_text(encoding="utf-8"))
    ids = manifest["fixtures"]
    if len(ids) != 10 or len(set(ids)) != 10:
        raise ValueError("manifest must contain ten unique fixtures")
    for fixture_id in ids:
        fixture = load_fixture(fixture_id)
        if "solution.py" not in fixture["files"] or "test_solution.py" not in fixture["files"]:
            raise ValueError("fixture must embed solution.py and test_solution.py")
        with tempfile.TemporaryDirectory(prefix="triz-fixture-check-") as temporary:
            workspace = Path(temporary)
            for relative, content in fixture["files"].items():
                target = workspace / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            initial = subprocess.run(fixture["test_command"], cwd=workspace, capture_output=True, text=True, check=False)
            if initial.returncode == 0:
                raise ValueError("starter tests must fail: " + fixture_id)
    print("BENCHMARK FIXTURES OK (10; no model calls)")


def materialize(fixture: dict[str, Any], destination: Path, treatment: bool) -> None:
    for relative, content in fixture["files"].items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    if treatment:
        shutil.copytree(SKILL, destination / ".agents" / "skills" / "triz-coding-method")
    subprocess.run(["git", "init", "-q"], cwd=destination, check=True)
    subprocess.run(["git", "add", "."], cwd=destination, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Benchmark", "-c", "user.email=benchmark@example.invalid", "commit", "-qm", "fixture"],
        cwd=destination,
        check=True,
    )


def _production_lines(patch: str) -> int:
    return sum(1 for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++") and not line.lstrip("+").lstrip().startswith(("#", "//")))


def execute(fixture_id: str, arm: str, results_dir: Path) -> Path:
    fixture = load_fixture(fixture_id)
    treatment = arm == "treatment"
    results_dir.mkdir(parents=True, exist_ok=True)
    run_dir = results_dir / (fixture_id + "-" + arm)
    if run_dir.exists():
        raise ValueError("result directory already exists: " + str(run_dir))
    run_dir.mkdir()
    with tempfile.TemporaryDirectory(prefix="triz-benchmark-") as temporary:
        workspace = Path(temporary) / "workspace"
        workspace.mkdir()
        materialize(fixture, workspace, treatment)
        prompt = fixture["prompt"]
        if treatment:
            prompt = "Use $triz-coding-method to find and implement the smallest safe solution.\n\n" + prompt
        command = [
            "codex", "exec", "--ignore-user-config", "--skip-git-repo-check",
            "--ephemeral", "--json", "--color", "never", "-s", "workspace-write",
            "-m", MODEL, "-c", 'model_reasoning_effort="low"', "-C", str(workspace), prompt,
        ]
        started = time.monotonic()
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        elapsed = time.monotonic() - started
        (run_dir / "events.jsonl").write_text(completed.stdout, encoding="utf-8")
        (run_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
        patch = subprocess.run(["git", "diff", "--no-ext-diff", "--binary"], cwd=workspace, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout
        (run_dir / "patch.diff").write_text(patch, encoding="utf-8")
        tests = subprocess.run(fixture["test_command"], cwd=workspace, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        (run_dir / "tests.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8")
        record = {
            "fixture": fixture_id,
            "arm": arm,
            "model": MODEL,
            "reasoning": "low",
            "codex_exit": completed.returncode,
            "tests_exit": tests.returncode,
            "production_lines_added": _production_lines(patch),
            "dependencies_added": bool(re.search(r"^\+.*(?:requirements|package\.json|pyproject)", patch, re.MULTILINE | re.IGNORECASE)),
            "elapsed_seconds": round(elapsed, 3),
        }
        (run_dir / "result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return run_dir


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--fixture")
    parser.add_argument("--arm", choices=("baseline", "treatment"))
    parser.add_argument("--results-dir", type=Path)
    args = parser.parse_args(argv)
    if args.dry_run:
        validate_all()
        return
    if not args.execute or not args.fixture or not args.arm or args.results_dir is None:
        parser.error("real runs require --execute, --fixture, --arm, and --results-dir")
    print(execute(args.fixture, args.arm, args.results_dir.resolve()))


if __name__ == "__main__":
    main()
