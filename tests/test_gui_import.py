"""Tests for GUI module import safety and CLI gui command."""

import importlib
import subprocess
import sys
import unittest


class TestGuiImport(unittest.TestCase):

    def test_gui_module_importable_without_pyside6(self):
        """gdlex_inspector.gui must import successfully regardless of PySide6 presence."""
        mod = importlib.import_module("gdlex_inspector.gui")
        self.assertIsNotNone(mod)

    def test_pyside6_available_flag_is_bool(self):
        from gdlex_inspector.gui import _PYSIDE6_AVAILABLE
        self.assertIsInstance(_PYSIDE6_AVAILABLE, bool)

    def test_launch_gui_is_callable(self):
        from gdlex_inspector.gui import launch_gui
        self.assertTrue(callable(launch_gui))

    def test_gui_theme_importable(self):
        import gdlex_inspector.gui_theme as theme
        self.assertIsNotNone(theme.STYLESHEET)
        self.assertIsInstance(theme.STYLESHEET, str)
        self.assertIn("background-color", theme.STYLESHEET)

    def test_gui_theme_risk_colors_defined(self):
        from gdlex_inspector.gui_theme import RISK_COLORS
        for level in ("none", "low", "medium", "high", "critical"):
            self.assertIn(level, RISK_COLORS)

    def test_cli_gui_help(self):
        """The gui subcommand must respond to --help with exit code 0."""
        result = subprocess.run(
            [sys.executable, "-m", "gdlex_inspector", "gui", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
        self.assertIn("gui", result.stdout.lower())

    def test_cli_help_lists_gui(self):
        """The top-level --help must mention the gui subcommand."""
        result = subprocess.run(
            [sys.executable, "-m", "gdlex_inspector", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("gui", result.stdout)


if __name__ == "__main__":
    unittest.main()
