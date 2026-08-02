#!/usr/bin/env python3
"""
Coding-method (Lazy Ideality) test suite — runnable with plain Python (unittest)
or pytest.

Covers the three scripts (method dispatcher, ponytail ladder, red-flag scan),
the reference index (all 15 files present), the 8-stage pipeline shape, the
cross-invocation to triz-innovation, and the curriculum structure.

Usage:
    pytest tests/test_coding_method.py   # if pytest installed
    python tests/test_coding_method.py    # plain unittest runner
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

# ---- path setup: add the scripts directory so imports work ----
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SKILL_DIR = _REPO_ROOT / ".claude" / "skills" / "coding-method"
_SCRIPTS_DIR = _SKILL_DIR / "scripts"
_REFERENCES_DIR = _SKILL_DIR / "references"
sys.path.insert(0, str(_SCRIPTS_DIR))

import method  # noqa: E402
import ladder  # noqa: E402
import redflags  # noqa: E402

_REF_FILES = [
    "method-map.md",
    "design-recipe.md",
    "computation-models.md",
    "algorithm-strategies.md",
    "deep-modules.md",
    "red-flags.md",
    "construction-checklist.md",
    "legacy-change.md",
    "architecture-tradeoffs.md",
    "domain-modeling.md",
    "sustainable-engineering.md",
    "pragmatic-etiquette.md",
    "rewrite-ladder.md",
    "type-safety.md",
    "triz-for-code.md",
]


class TestStagePipeline(unittest.TestCase):
    """The 8-stage pipeline is complete, ordered, and names the right refs."""

    def test_stages_exactly_8(self):
        self.assertEqual(len(method.STAGES), 8)

    def test_stages_ordered_1_to_8(self):
        nums = [s["num"] for s in method.STAGES]
        self.assertEqual(nums, list(range(1, 9)))

    def test_each_stage_has_required_fields(self):
        for stage in method.STAGES:
            with self.subTest(stage=stage["num"]):
                self.assertIn("name", stage)
                self.assertIn("what", stage)
                self.assertIn("refs", stage)
                self.assertIn("tags", stage)
                self.assertGreater(len(stage["name"].strip()), 0)
                self.assertGreater(len(stage["what"].strip()), 0)
                self.assertIsInstance(stage["refs"], list)
                self.assertGreater(len(stage["refs"]), 0,
                                   f"Stage {stage['num']} has no reference files")

    def test_stage_refs_exist(self):
        for stage in method.STAGES:
            for ref in stage["refs"]:
                path = _REFERENCES_DIR / ref
                self.assertTrue(path.is_file(),
                                f"Stage {stage['num']} ref missing: {ref}")

    def test_plan_stage_valid(self):
        stage = method.plan_stage(5)
        self.assertEqual(stage["num"], 5)
        self.assertEqual(stage["name"], "Resolve contradictions")

    def test_plan_stage_invalid(self):
        self.assertIsNone(method.plan_stage(0))
        self.assertIsNone(method.plan_stage(9))
        self.assertIsNone(method.plan_stage("x"))


class TestRouteSignals(unittest.TestCase):
    """route() detects the six signal classes and code-side TRIZ hints."""

    def _signals(self, task: str) -> list[str]:
        return [hit["signal"] for hit in method.route(task)["signals"]]

    def test_default_shape(self):
        plan = method.route("anything at all")
        for key in ("task", "default", "signals", "triz_hints", "always_load"):
            self.assertIn(key, plan)
        self.assertEqual(plan["always_load"], ["method-map.md"])

    def test_contradiction_signal(self):
        signals = self._signals("more speed but less reliability")
        self.assertIn("contradiction", signals)

    def test_contradiction_tradeoff_language(self):
        signals = self._signals("there is a trade-off between cost and coverage")
        self.assertIn("contradiction", signals)

    def test_legacy_signal(self):
        signals = self._signals("the legacy module has no tests")
        self.assertIn("legacy", signals)

    def test_debugging_signal(self):
        signals = self._signals("this function returns the wrong result")
        self.assertIn("debugging", signals)

    def test_architecture_signal(self):
        signals = self._signals("the api design must scale to many services")
        self.assertIn("architecture", signals)

    def test_data_shape_signal(self):
        signals = self._signals("parse the tree of order data")
        self.assertIn("data-shape", signals)

    def test_data_heavy_signal(self):
        signals = self._signals("run a query against the database pipeline")
        self.assertIn("data-heavy", signals)

    def test_latency_hint(self):
        hints = method.route("the hot path is too slow")["triz_hints"]
        self.assertTrue(
            any("[IP-10 Prior action]" in h for h in hints),
            f"Expected an IP-10 Prior action hint, got {hints}",
        )

    def test_cache_consistency_hint(self):
        """Regression: the cache/staleness hint must fire (added after smoke
        test showed the contradiction signal fired but no TRIZ hint)."""
        hints = method.route(
            "the API must be fast, but caching makes it inconsistent"
        )["triz_hints"]
        self.assertTrue(
            any("cache" in h.lower() for h in hints),
            f"Expected a cache hint, got {hints}",
        )
        self.assertTrue(
            any("[IP-13 Other way round]" in h for h in hints),
            f"Expected eventual + reconcile hint, got {hints}",
        )

    def test_error_hint(self):
        hints = method.route("the parse throws an exception on bad input")["triz_hints"]
        self.assertTrue(
            any("[Define errors out of existence]" in h for h in hints),
            f"Expected 'define errors out of existence', got {hints}",
        )


class TestLadder(unittest.TestCase):
    """The ponytail ladder has 6 rungs in order and guesses correctly."""

    def test_ladder_6_rungs_in_order(self):
        rungs = [r[0] for r in ladder.LADDER]
        self.assertEqual(
            rungs,
            ["YAGNI", "stdlib", "native", "existing-dep", "one-line", "minimum-code"],
        )

    def test_suggest_rung_stdlib(self):
        result = ladder.suggest_rung("parse and sort the json list of dates")
        self.assertEqual(result["rung"], "stdlib")

    def test_suggest_rung_existing_dep(self):
        result = ladder.suggest_rung("reuse our existing module to wrap the api")
        self.assertEqual(result["rung"], "existing-dep")

    def test_suggest_rung_one_line(self):
        result = ladder.suggest_rung("rewrite the loop as a one-liner with map and filter")
        self.assertEqual(result["rung"], "one-line")

    def test_suggest_rung_minimum_code_default(self):
        result = ladder.suggest_rung("build a new framework from scratch")
        self.assertEqual(result["rung"], "minimum-code")

    def test_suggest_rung_shape(self):
        result = ladder.suggest_rung("any task")
        for key in ("task", "rung", "why", "ifr", "almost_ifr"):
            self.assertIn(key, result)
        self.assertIn("no new code", result["ifr"].lower())

    def test_method_re_exports_ladder(self):
        result = method.suggest_rung("parse the json")
        self.assertEqual(result["rung"], "stdlib")


class TestRedFlags(unittest.TestCase):
    """The checklist has 17 items; scan() finds mechanically-detectable smells."""

    def test_checklist_17_items(self):
        self.assertEqual(len(redflags.CHECKLIST), 17)

    def test_checklist_covers_key_flags(self):
        joined = " ".join(redflags.CHECKLIST).lower()
        for needle in ("shallow module", "information leakage",
                       "pass-through", "repetition", "vague", "nonobvious",
                       "leanness", "broken windows", "trimming",
                       "complexity relocated"):
            self.assertIn(needle, joined,
                          f"Checklist missing concept: {needle}")

    def test_scan_no_file_checklist_only(self):
        result = redflags.scan(None)
        self.assertEqual(len(result["checklist"]), 17)
        self.assertEqual(result["findings"], [])

    def test_scan_missing_file(self):
        result = redflags.scan("C:/nonexistent/path/nope.py")
        self.assertTrue(
            any("file not found" in f for f in result["findings"]),
            f"Expected 'file not found', got {result['findings']}",
        )

    def test_scan_detects_long_params(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad_sig.py"
            path.write_text(
                "def f(a, b, c, d, e, g, h):\n    return a\n",
                encoding="utf-8",
            )
            result = redflags.scan(str(path))
            self.assertTrue(
                any("6+ parameters" in f for f in result["findings"]),
                f"Expected long-params finding, got {result['findings']}",
            )

    def test_scan_detects_long_lines(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "long_line.py"
            path.write_text("x = " + "y" * 120 + "\n", encoding="utf-8")
            result = redflags.scan(str(path))
            self.assertTrue(
                any("longer than 100" in f for f in result["findings"]),
                f"Expected long-line finding, got {result['findings']}",
            )

    def test_scan_detects_markers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "todo.py"
            path.write_text("# TODO: finish this\n", encoding="utf-8")
            result = redflags.scan(str(path))
            self.assertTrue(
                any("TODO" in f for f in result["findings"]),
                f"Expected marker finding, got {result['findings']}",
            )

    def test_scan_detects_long_function(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "big.py"
            body = "def big():\n" + "    pass\n" * 70 + "\ndef other():\n    pass\n"
            path.write_text(body, encoding="utf-8")
            result = redflags.scan(str(path))
            self.assertTrue(
                any("long function" in f for f in result["findings"]),
                f"Expected long-function finding, got {result['findings']}",
            )

    def test_scan_clean_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "clean.py"
            path.write_text(
                "def clean(a, b):\n    return a + b\n",
                encoding="utf-8",
            )
            result = redflags.scan(str(path))
            self.assertTrue(
                any("no mechanically-detectable smells" in f
                    for f in result["findings"]),
                f"Expected clean-file message, got {result['findings']}",
            )

    def test_method_re_exports_scan(self):
        result = method.redflags(None)
        self.assertEqual(len(result["checklist"]), 17)


class TestReferenceIndex(unittest.TestCase):
    """All 15 reference files exist and the index lists exactly them."""

    def test_index_15_entries(self):
        files = [entry[1] for entry in method._REF_INDEX]
        self.assertEqual(len(files), 15)

    def test_index_matches_disk(self):
        files = [entry[1] for entry in method._REF_INDEX]
        self.assertEqual(sorted(files), sorted(_REF_FILES))

    def test_all_ref_files_exist(self):
        for name in _REF_FILES:
            path = _REFERENCES_DIR / name
            self.assertTrue(path.is_file(), f"Reference missing: {name}")
            content = path.read_text(encoding="utf-8")
            self.assertGreater(len(content.strip()), 0,
                               f"Reference empty: {name}")


class TestTrizCrossInvocation(unittest.TestCase):
    """The coding method cross-invokes triz-innovation — no duplication."""

    def test_triz_matrix_cross_invoke(self):
        result = method.triz_matrix("14", "2")
        self.assertEqual(result["exit"], 0, result["output"])
        self.assertIn("principles", result["output"].lower())

    def test_triz_matrix_invalid_id(self):
        result = method.triz_matrix("0", "2")
        self.assertNotEqual(result["exit"], 0)


class TestCurriculum(unittest.TestCase):
    """Curriculum README exists and describes the 7-step learning path."""

    def test_curriculum_readme_exists(self):
        path = _SKILL_DIR / "curriculum" / "README.md"
        self.assertTrue(path.is_file(), "curriculum/README.md missing")
        content = path.read_text(encoding="utf-8")
        self.assertGreater(len(content.strip()), 0)

    def test_curriculum_mentions_seven_steps(self):
        content = (_SKILL_DIR / "curriculum" / "README.md").read_text(encoding="utf-8")
        for step_num in ("1", "2", "3", "4", "5", "6", "7"):
            self.assertIn(f"Step {step_num}", content,
                          f"Curriculum missing 'Step {step_num}'")

    def test_cases_complete(self):
        """All 5 canned cases exist and close with the mandatory test section."""
        expected = [
            "2026-08-02-legacy-checkout-tax.md",
            "2026-08-02-datapipeline-loop-to-declarative.md",
            "2026-08-02-algorithm-closest-pair.md",
            "2026-08-02-apidesign-file-upload.md",
            "2026-08-02-architecture-cache-invalidation.md",
        ]
        cases_dir = _SKILL_DIR / "cases"
        for name in expected:
            path = cases_dir / name
            self.assertTrue(path.is_file(), f"Canned case missing: {name}")
            content = path.read_text(encoding="utf-8")
            self.assertIn("Stadio 8", content,
                          f"Case {name} missing the test section (Stadio 8)")
            self.assertIn("Criterio di successo", content,
                          f"Case {name} missing the numeric success criterion")


if __name__ == "__main__":
    unittest.main()
