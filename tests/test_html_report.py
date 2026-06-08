"""Unit tests for static HTML report charts."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from gdlex_inspector.models import CategorySummary, DirectoryEntry, ScanResult
from gdlex_inspector.report import (
    calculate_percentages,
    category_color,
    category_donut_svg,
    to_html,
    top_directories_bar_svg,
)


def _make_result() -> ScanResult:
    result = ScanResult(root_path="/tmp/test_scan")
    result.total_size = 1000
    result.total_files = 4
    result.total_dirs = 2
    result.categories = [
        CategorySummary(category="pst", total_size=750, file_count=1),
        CategorySummary(category="other", total_size=250, file_count=3),
    ]
    result.top_dirs = [
        DirectoryEntry(path="/tmp/test_scan/mail", size=750, file_count=1, category="pst"),
        DirectoryEntry(path="/tmp/test_scan/docs", size=250, file_count=3, category="other"),
    ]
    return result


class TestHtmlReportCharts(unittest.TestCase):

    def test_category_chart_present_in_html(self):
        html = to_html(_make_result())
        self.assertIn('id="category-chart"', html)
        self.assertIn("Distribuzione per categoria", html)
        self.assertIn("75.0%", html)

    def test_top_directories_chart_present_in_html(self):
        html = to_html(_make_result())
        self.assertIn('id="top-directories-chart"', html)
        self.assertIn("Grafico statico a barre orizzontali", html)
        self.assertIn("/tmp/test_scan/mail", html)

    def test_empty_categories_are_valid(self):
        result = ScanResult(root_path="/tmp/empty")
        html = to_html(result)
        self.assertIn('id="category-chart"', html)
        self.assertIn("Nessuna categoria disponibile", html)
        self.assertIn("Nessun dato", category_donut_svg([]))

    def test_percentages_are_coherent(self):
        percentages = calculate_percentages([750, 250, 0])
        self.assertEqual(percentages, [75.0, 25.0, 0.0])
        self.assertAlmostEqual(sum(percentages), 100.0)
        self.assertEqual(calculate_percentages([]), [])
        self.assertEqual(calculate_percentages([0, 0]), [0.0, 0.0])

    def test_palette_is_stable(self):
        self.assertEqual(category_color("pst"), category_color("pst"))
        self.assertNotEqual(category_color("pst"), category_color("other"))
        self.assertEqual(category_color("custom"), category_color("custom"))

    def test_svg_helpers_return_expected_sections(self):
        result = _make_result()
        self.assertIn("<svg", category_donut_svg(result.categories))
        self.assertIn("<circle", category_donut_svg(result.categories))
        self.assertIn("<svg", top_directories_bar_svg(result.top_dirs))
        self.assertIn("<rect", top_directories_bar_svg(result.top_dirs))

    def test_html_contains_expected_document_sections(self):
        html = to_html(_make_result())
        for section in (
            "<!DOCTYPE html>",
            "Riepilogo scansione",
            "Grafici statici",
            "Top file per dimensione",
            "Top cartelle per dimensione",
            "Riepilogo per categoria",
            "</html>",
        ):
            self.assertIn(section, html)

    def test_missing_scan_timestamp_uses_timezone_aware_utc(self):
        html = to_html(_make_result())
        timestamp = html.split("<b>Data scansione:</b> ", 1)[1].split("<br>", 1)[0]
        parsed = datetime.fromisoformat(timestamp)
        self.assertEqual(parsed.utcoffset(), timezone.utc.utcoffset(parsed))


if __name__ == "__main__":
    unittest.main()
