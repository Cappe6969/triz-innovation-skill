#!/usr/bin/env python3

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestDistribution(unittest.TestCase):
    def test_manifests_share_name_and_version(self):
        manifests = [
            json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")),
            json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")),
        ]
        self.assertEqual({item["name"] for item in manifests}, {"triz-coding-method"})
        self.assertEqual({item["version"] for item in manifests}, {"0.1.0"})

    def test_server_runs_from_path_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix="triz path with spaces ") as temporary:
            destination = Path(temporary) / "skill copy"
            shutil.copytree(ROOT / "skills" / "triz-coding-method", destination)
            completed = subprocess.run([sys.executable, str(destination / "scripts" / "triz_mcp_server.py"), "--self-test"], capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_release_archives_have_expected_layout(self):
        with tempfile.TemporaryDirectory() as temporary:
            completed = subprocess.run([sys.executable, str(ROOT / "scripts" / "package_release.py"), "--target", "all", "--output-dir", temporary], capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            archives = sorted(Path(temporary).glob("*.zip"))
            self.assertEqual(len(archives), 3)
            for archive_path in archives:
                with zipfile.ZipFile(archive_path) as archive:
                    names = archive.namelist()
                    self.assertFalse(any(name.startswith((".git/", "tests/", "benchmarks/")) for name in names))
                    self.assertTrue(any(name.endswith("/SKILL.md") for name in names))

    def test_case_cli_requires_explicit_output_directory(self):
        script = ROOT / "skills" / "triz-coding-method" / "engine" / "scripts" / "triz_case_template.py"
        completed = subprocess.run([sys.executable, str(script), "Example"], capture_output=True, text=True, check=False)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--output-dir", completed.stderr)

    def test_case_title_cannot_escape_output_directory(self):
        scripts = ROOT / "skills" / "triz-coding-method" / "engine" / "scripts"
        sys.path.insert(0, str(scripts))
        import triz_case_template
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "cases"
            created = triz_case_template.create_case("../../outside", cases_dir=output)
            created.resolve().relative_to(output.resolve())
            self.assertTrue(created.is_file())


if __name__ == "__main__":
    unittest.main()
