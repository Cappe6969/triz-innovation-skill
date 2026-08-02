#!/usr/bin/env python3
"""
Tests for scripts/build_mirror.py — the .agents/ mirror generator.

Builds a tiny canonical .claude skill tree that includes an examples/ file,
runs build_mirror.build() against it, and asserts the examples file is copied
into the generated .agents mirror (with the .claude/ -> .agents/ prefix
rewrite applied). Guards the "examples in mirror" regression.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import build_mirror  # noqa: E402


class TestBuildMirrorExamples(unittest.TestCase):
    """build_mirror copies an existing examples/ directory into the mirror."""

    def _run_build(self, with_examples: bool):
        """Build into a temp mirror and yield a callback that asserts on it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / ".claude" / "skills" / "triz-innovation"
            (source / "references").mkdir(parents=True)
            (source / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
            (source / "references" / "ref.md").write_text(
                "ref content\n", encoding="utf-8"
            )
            if with_examples:
                (source / "examples").mkdir()
                (source / "examples" / "example-software-problem.md").write_text(
                    "Run `python .claude/skills/triz-innovation/scripts/triz.py`\n",
                    encoding="utf-8",
                )
            mirror = root / ".agents" / "skills" / "triz-innovation"

            old_source, old_mirror = build_mirror._SOURCE, build_mirror._MIRROR
            try:
                build_mirror._SOURCE = source
                build_mirror._MIRROR = mirror
                build_mirror.build()
                yield mirror
            finally:
                build_mirror._SOURCE = old_source
                build_mirror._MIRROR = old_mirror

    def test_examples_file_lands_in_mirror_with_prefix_rewrite(self):
        for mirror in self._run_build(with_examples=True):
            examples_file = mirror / "examples" / "example-software-problem.md"
            self.assertTrue(
                examples_file.is_file(),
                f"examples/ file not copied to mirror: {examples_file}",
            )
            content = examples_file.read_text(encoding="utf-8")
            self.assertIn(
                ".agents/skills/triz-innovation/scripts/triz.py", content
            )
            self.assertNotIn(".claude/skills/triz-innovation", content)
            # After a build the mirror is in sync.
            self.assertEqual(build_mirror.check(), [])

    def test_missing_examples_skipped_silently(self):
        """A source tree without examples/ builds cleanly and reports no drift."""
        for mirror in self._run_build(with_examples=False):
            self.assertFalse((mirror / "examples").exists())
            self.assertEqual(build_mirror.check(), [])


if __name__ == "__main__":
    unittest.main()
