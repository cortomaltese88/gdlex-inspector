"""Smoke tests for the CLI via subprocess."""

import json
import os
import subprocess
import sys
import tempfile
import unittest


def _run(*args):
    """Run gdlex_inspector as a module and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "gdlex_inspector"] + list(args),
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


class TestSmokeCLI(unittest.TestCase):

    def test_version_command(self):
        rc, out, err = _run("version")
        self.assertEqual(rc, 0)
        self.assertIn("0.1.0", out)

    def test_help_flag(self):
        rc, out, err = _run("--help")
        self.assertEqual(rc, 0)
        self.assertIn("scan", out)

    def test_scan_temp_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            for i in range(5):
                with open(os.path.join(tmpdir, f"file_{i}.txt"), "w") as f:
                    f.write("x" * (1024 * (i + 1)))
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)
            with open(os.path.join(subdir, "nested.dat"), "wb") as f:
                f.write(b"\x00" * 2048)

            rc, out, err = _run("scan", tmpdir, "--top", "5")
            self.assertEqual(rc, 0, msg=f"stderr: {err}")
            self.assertIn("Total", out)
            self.assertIn("Files", out)

    def test_scan_nonexistent_path(self):
        rc, out, err = _run("scan", "/nonexistent/path/xyz_gdlex")
        self.assertNotEqual(rc, 0)

    def test_export_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.txt"), "w") as f:
                f.write("hello world")
            json_out = os.path.join(tmpdir, "report.json")
            rc, out, err = _run("scan", tmpdir, "--json", json_out)
            self.assertEqual(rc, 0, msg=f"stderr: {err}")
            self.assertTrue(os.path.exists(json_out))
            self.assertGreater(os.path.getsize(json_out), 0)
            with open(json_out) as f:
                data = json.load(f)
            self.assertIn("total_files", data)
            self.assertIn("top_files", data)

    def test_export_html(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.txt"), "w") as f:
                f.write("hello world")
            html_out = os.path.join(tmpdir, "report.html")
            rc, out, err = _run("scan", tmpdir, "--html", html_out)
            self.assertEqual(rc, 0, msg=f"stderr: {err}")
            self.assertTrue(os.path.exists(html_out))
            self.assertGreater(os.path.getsize(html_out), 0)
            with open(html_out) as f:
                content = f.read()
            self.assertIn("GD LEX Inspector", content)
            self.assertIn("DOCTYPE html", content)


if __name__ == "__main__":
    unittest.main()
