"""Tests for gui_charts helpers and chart data logic.

All tests are display-free: no QApplication, no paint events, no rendering.
"""
from __future__ import annotations

import importlib
import unittest

from gdlex_inspector.models import CategorySummary, DirectoryEntry, ScanResult
from gdlex_inspector.report import calculate_percentages, category_color, _fmt_size


# ---------------------------------------------------------------------------
# Pure-logic helpers (no PySide6 needed)
# ---------------------------------------------------------------------------

class TestChartDataFromResult(unittest.TestCase):
    """Tests for gui_charts.chart_data_from_result (pure function, no display)."""

    def _call(self, result):
        from gdlex_inspector.gui_charts import chart_data_from_result
        return chart_data_from_result(result)

    def test_none_returns_empty_lists(self):
        cats, dirs, pcts = self._call(None)
        self.assertEqual(cats, [])
        self.assertEqual(dirs, [])
        self.assertEqual(pcts, [])

    def test_empty_scan_result_returns_empty_lists(self):
        result = ScanResult(root_path="/tmp/empty")
        cats, dirs, pcts = self._call(result)
        self.assertEqual(cats, [])
        self.assertEqual(dirs, [])
        self.assertEqual(pcts, [])

    def test_categories_and_dirs_are_extracted(self):
        result = ScanResult(root_path="/tmp/test")
        result.categories = [
            CategorySummary(category="pst", total_size=800, file_count=1),
            CategorySummary(category="other", total_size=200, file_count=5),
        ]
        result.top_dirs = [
            DirectoryEntry(path="/tmp/test/mail", size=800, file_count=1),
        ]
        cats, dirs, pcts = self._call(result)
        self.assertEqual(len(cats), 2)
        self.assertEqual(len(dirs), 1)
        self.assertEqual(len(pcts), 2)

    def test_percentages_sum_to_100(self):
        result = ScanResult(root_path="/tmp/test")
        result.categories = [
            CategorySummary(category="a", total_size=300, file_count=1),
            CategorySummary(category="b", total_size=700, file_count=2),
        ]
        _, _, pcts = self._call(result)
        self.assertAlmostEqual(sum(pcts), 100.0)
        self.assertAlmostEqual(pcts[0], 30.0)
        self.assertAlmostEqual(pcts[1], 70.0)

    def test_all_zero_sizes_returns_zero_percentages(self):
        result = ScanResult(root_path="/tmp/test")
        result.categories = [
            CategorySummary(category="a", total_size=0, file_count=0),
            CategorySummary(category="b", total_size=0, file_count=0),
        ]
        _, _, pcts = self._call(result)
        self.assertEqual(pcts, [0.0, 0.0])

    def test_single_category_gets_100_percent(self):
        result = ScanResult(root_path="/tmp/test")
        result.categories = [
            CategorySummary(category="pst", total_size=1024, file_count=1),
        ]
        _, _, pcts = self._call(result)
        self.assertAlmostEqual(pcts[0], 100.0)

    def test_result_lists_are_copied(self):
        """Modifying the returned lists should not affect the original result."""
        result = ScanResult(root_path="/tmp/test")
        result.categories = [CategorySummary(category="a", total_size=100, file_count=1)]
        cats, dirs, _ = self._call(result)
        cats.clear()
        self.assertEqual(len(result.categories), 1)


# ---------------------------------------------------------------------------
# Palette stability
# ---------------------------------------------------------------------------

class TestCategoryColorStability(unittest.TestCase):
    """category_color must be deterministic and consistent with theme colours."""

    def test_known_categories_have_stable_colors(self):
        known = ("pst", "ost", "downloads", "browser_cache", "temp",
                 "node_modules", "venv", "docker", "snap_flatpak", "onedrive", "other")
        for cat in known:
            c1 = category_color(cat)
            c2 = category_color(cat)
            self.assertEqual(c1, c2, f"Color not stable for category '{cat}'")

    def test_unknown_category_is_deterministic(self):
        self.assertEqual(category_color("custom_xyz"), category_color("custom_xyz"))

    def test_colors_start_with_hash(self):
        for cat in ("pst", "other", "venv", "totally_new_category"):
            color = category_color(cat)
            self.assertTrue(color.startswith("#"), f"Bad color format: {color!r}")
            self.assertEqual(len(color), 7, f"Color not 7 chars: {color!r}")


# ---------------------------------------------------------------------------
# gui_charts module import
# ---------------------------------------------------------------------------

class TestGuiChartsImport(unittest.TestCase):
    """The gui_charts module must import without errors regardless of PySide6."""

    def test_module_importable(self):
        mod = importlib.import_module("gdlex_inspector.gui_charts")
        self.assertIsNotNone(mod)

    def test_chart_data_from_result_is_callable(self):
        from gdlex_inspector.gui_charts import chart_data_from_result
        self.assertTrue(callable(chart_data_from_result))

    def test_pyside6_flag_present(self):
        from gdlex_inspector.gui_charts import _PYSIDE6_AVAILABLE
        self.assertIsInstance(_PYSIDE6_AVAILABLE, bool)

    def test_charts_tab_class_exists_when_pyside6_available(self):
        from gdlex_inspector.gui_charts import _PYSIDE6_AVAILABLE
        if not _PYSIDE6_AVAILABLE:
            self.skipTest("PySide6 not available")
        from gdlex_inspector.gui_charts import ChartsTab
        self.assertTrue(callable(ChartsTab))


# ---------------------------------------------------------------------------
# fmt_size helper sanity (shared with report, used by charts)
# ---------------------------------------------------------------------------

class TestFmtSizeForCharts(unittest.TestCase):

    def test_bytes(self):
        self.assertEqual(_fmt_size(512), "512.0 B")

    def test_kilobytes(self):
        self.assertEqual(_fmt_size(2048), "2.0 K")

    def test_megabytes(self):
        self.assertEqual(_fmt_size(1024 * 1024), "1.0 M")


if __name__ == "__main__":
    unittest.main()
