"""Unit tests for CSV report generation."""

from __future__ import annotations

import csv
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

from gdlex_inspector.models import (
    CategorySummary,
    DirectoryEntry,
    ExtensionSummary,
    FileEntry,
    ScanIssue,
    ScanResult,
)
from gdlex_inspector.report import to_csv, to_json


def _make_result() -> ScanResult:
    result = ScanResult(root_path="/tmp/test_scan")
    result.total_size = 1048576
    result.total_files = 3
    result.total_dirs = 1
    result.top_files = [
        FileEntry(path="/tmp/test_scan/big.bin", size=1024000, category="other", risk_level="low"),
        FileEntry(path="/tmp/test_scan/données/résumé.txt", size=48576, category="documents", risk_level="none"),
    ]
    result.top_dirs = [
        DirectoryEntry(path="/tmp/test_scan/données", size=48576, file_count=1, category="documents", risk_level="none"),
    ]
    result.extensions = [
        ExtensionSummary(extension=".bin", total_size=1024000, file_count=1),
        ExtensionSummary(extension=".txt", total_size=48576, file_count=1),
    ]
    result.categories = [
        CategorySummary(category="other", total_size=1024000, file_count=1, risk_level="low"),
        CategorySummary(category="documents", total_size=48576, file_count=1, risk_level="none"),
    ]
    result.issues = [
        ScanIssue(path="/tmp/test_scan/forbidden", error="Permission denied"),
    ]
    return result


def _run(*args):
    res = subprocess.run(
        [sys.executable, "-m", "gdlex_inspector"] + list(args),
        capture_output=True,
        text=True,
    )
    return res.returncode, res.stdout, res.stderr


class TestToCsvGeneration(unittest.TestCase):

    def setUp(self):
        self.result = _make_result()
        self.csv_text = to_csv(self.result)

    def test_returns_non_empty_string(self):
        self.assertIsInstance(self.csv_text, str)
        self.assertGreater(len(self.csv_text), 0)

    def test_section_top_files_present(self):
        self.assertIn("top_files", self.csv_text)

    def test_section_top_dirs_present(self):
        self.assertIn("top_dirs", self.csv_text)

    def test_section_extensions_present(self):
        self.assertIn("extensions", self.csv_text)

    def test_section_categories_present(self):
        self.assertIn("categories", self.csv_text)

    def test_section_issues_present(self):
        self.assertIn("issues", self.csv_text)

    def test_all_five_section_headers(self):
        sections = []
        reader = csv.reader(io.StringIO(self.csv_text))
        for row in reader:
            if row and row[0] == "SECTION":
                sections.append(row[1])
        self.assertEqual(sections, ["top_files", "top_dirs", "extensions", "categories", "issues"])

    def test_top_files_data_row(self):
        self.assertIn("big.bin", self.csv_text)
        self.assertIn("1024000", self.csv_text)

    def test_unicode_path_preserved(self):
        self.assertIn("données", self.csv_text)
        self.assertIn("résumé.txt", self.csv_text)

    def test_issue_row_present(self):
        self.assertIn("forbidden", self.csv_text)
        self.assertIn("Permission denied", self.csv_text)

    def test_parseable_by_csv_reader(self):
        rows = list(csv.reader(io.StringIO(self.csv_text)))
        self.assertGreater(len(rows), 5)

    def test_top_files_column_headers(self):
        lines = self.csv_text.splitlines()
        found = False
        for i, line in enumerate(lines):
            if "SECTION" in line and "top_files" in line:
                header = lines[i + 1]
                self.assertIn("path", header)
                self.assertIn("size_bytes", header)
                self.assertIn("risk_level", header)
                found = True
                break
        self.assertTrue(found, "top_files section header not found")

    def test_categories_column_headers(self):
        lines = self.csv_text.splitlines()
        found = False
        for i, line in enumerate(lines):
            if "SECTION" in line and "categories" in line:
                header = lines[i + 1]
                self.assertIn("category", header)
                self.assertIn("total_size_bytes", header)
                self.assertIn("file_count", header)
                found = True
                break
        self.assertTrue(found, "categories section header not found")

    def test_csv_uses_readable_sensitivity_and_keeps_technical_risk(self):
        self.result.top_files = [
            FileEntry(
                path="/etc/ssh/moduli",
                size=620032,
                category="other",
                risk_level="critical",
            )
        ]
        rows = list(csv.reader(io.StringIO(to_csv(self.result))))
        header_index = rows.index(["SECTION", "top_files"]) + 1
        header = rows[header_index]
        data = rows[header_index + 1]
        self.assertEqual(data[header.index("sensitivity")], "Sistema")
        self.assertEqual(data[header.index("risk_level")], "critical")
        self.assertEqual(data[header.index("size_human")], "605.5 KiB")

    def test_json_keeps_numeric_sizes_and_technical_risk(self):
        self.result.top_files = [
            FileEntry(
                path="/etc/ssh/moduli",
                size=620032,
                category="other",
                risk_level="critical",
            )
        ]
        data = json.loads(to_json(self.result))
        self.assertIsInstance(data["total_size"], int)
        self.assertIsInstance(data["top_files"][0]["size"], int)
        self.assertEqual(data["top_files"][0]["risk_level"], "critical")
        self.assertNotIn("sensitivity", data["top_files"][0])


class TestCsvCLI(unittest.TestCase):

    def test_export_csv_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "sample.txt"), "w") as f:
                f.write("hello csv")
            csv_out = os.path.join(tmpdir, "report.csv")
            rc, out, err = _run("scan", tmpdir, "--csv", csv_out)
            self.assertEqual(rc, 0, msg=f"stderr: {err}")
            self.assertTrue(os.path.exists(csv_out), "CSV file was not created")

    def test_export_csv_not_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "sample.txt"), "w") as f:
                f.write("hello csv")
            csv_out = os.path.join(tmpdir, "report.csv")
            _run("scan", tmpdir, "--csv", csv_out)
            self.assertGreater(os.path.getsize(csv_out), 0)

    def test_export_csv_contains_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "sample.txt"), "w") as f:
                f.write("hello csv")
            csv_out = os.path.join(tmpdir, "report.csv")
            _run("scan", tmpdir, "--csv", csv_out)
            with open(csv_out, encoding="utf-8") as f:
                content = f.read()
            for section in ("top_files", "top_dirs", "extensions", "categories", "issues"):
                self.assertIn(section, content, f"section '{section}' missing from CSV")

    def test_export_csv_message_in_stdout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "sample.txt"), "w") as f:
                f.write("hello")
            csv_out = os.path.join(tmpdir, "report.csv")
            rc, out, _ = _run("scan", tmpdir, "--csv", csv_out)
            self.assertIn("CSV report saved", out)

    def test_export_csv_unicode_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            udir = os.path.join(tmpdir, "données_légales")
            os.makedirs(udir)
            with open(os.path.join(udir, "résumé.txt"), "w", encoding="utf-8") as f:
                f.write("contenu unicode")
            csv_out = os.path.join(tmpdir, "report.csv")
            rc, out, err = _run("scan", tmpdir, "--csv", csv_out)
            self.assertEqual(rc, 0, msg=f"stderr: {err}")
            with open(csv_out, encoding="utf-8") as f:
                content = f.read()
            self.assertGreater(len(content), 0)


if __name__ == "__main__":
    unittest.main()
