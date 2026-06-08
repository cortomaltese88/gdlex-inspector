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


class TestGuiThemes(unittest.TestCase):
    """Tests for multi-theme support in gui_theme."""

    def setUp(self):
        from gdlex_inspector.gui_theme import get_current_theme_name, set_current_theme
        self._original_theme = get_current_theme_name()
        set_current_theme("Matrix")

    def tearDown(self):
        from gdlex_inspector.gui_theme import set_current_theme
        set_current_theme(self._original_theme)

    def test_available_themes_contains_three(self):
        from gdlex_inspector.gui_theme import AVAILABLE_THEMES
        self.assertIn("Matrix", AVAILABLE_THEMES)
        self.assertIn("Scuro", AVAILABLE_THEMES)
        self.assertIn("Chiaro", AVAILABLE_THEMES)

    def test_all_themes_produce_stylesheet(self):
        from gdlex_inspector.gui_theme import get_stylesheet
        for name in ("Matrix", "Scuro", "Chiaro"):
            ss = get_stylesheet(name)
            self.assertIsInstance(ss, str)
            self.assertIn("background-color", ss)
            self.assertGreater(len(ss), 100)

    def test_theme_colors_have_required_keys(self):
        from gdlex_inspector.gui_theme import THEMES
        required = (
            "bg_dark", "bg_panel", "bg_panel_alt", "bg_table_header",
            "fg_bright", "fg_normal", "fg_dim", "fg_accent",
            "border", "sel_bg", "sel_fg", "alt_row",
            "btn_hover", "btn_pressed", "bar_track", "bar_fill",
            "chart_bg", "chart_track", "legend_text", "muted_text",
            "primary_bg", "primary_hover", "primary_pressed",
        )
        for theme_name, colors in THEMES.items():
            for key in required:
                self.assertIn(
                    key, colors,
                    msg=f"Key {key!r} missing in theme {theme_name!r}",
                )

    def test_set_and_get_current_theme(self):
        from gdlex_inspector.gui_theme import set_current_theme, get_current_theme_name
        set_current_theme("Chiaro")
        self.assertEqual(get_current_theme_name(), "Chiaro")
        set_current_theme("Scuro")
        self.assertEqual(get_current_theme_name(), "Scuro")
        set_current_theme("Matrix")
        self.assertEqual(get_current_theme_name(), "Matrix")

    def test_set_unknown_theme_raises(self):
        from gdlex_inspector.gui_theme import set_current_theme
        with self.assertRaises(ValueError):
            set_current_theme("Unicorn")

    def test_get_current_risk_colors_all_themes(self):
        from gdlex_inspector.gui_theme import set_current_theme, get_current_risk_colors
        for theme in ("Matrix", "Scuro", "Chiaro"):
            set_current_theme(theme)
            rc = get_current_risk_colors()
            for level in ("none", "low", "medium", "high", "critical"):
                self.assertIn(level, rc, msg=f"Missing risk level {level!r} for theme {theme!r}")

    def test_get_current_colors_returns_dict(self):
        from gdlex_inspector.gui_theme import set_current_theme, get_current_colors
        for theme in ("Matrix", "Scuro", "Chiaro"):
            set_current_theme(theme)
            c = get_current_colors()
            self.assertIsInstance(c, dict)
            self.assertIn("bg_dark", c)

    def test_light_theme_has_light_background(self):
        """Chiaro theme must have a genuinely light background."""
        from gdlex_inspector.gui_theme import THEMES
        bg = THEMES["Chiaro"]["bg_dark"]
        # Parse as hex RGB
        r = int(bg[1:3], 16)
        g = int(bg[3:5], 16)
        b = int(bg[5:7], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        self.assertGreater(luminance, 180, msg=f"Chiaro bg_dark too dark: {bg}")

    def test_matrix_theme_has_dark_background(self):
        """Matrix theme must have a dark background."""
        from gdlex_inspector.gui_theme import THEMES
        bg = THEMES["Matrix"]["bg_dark"]
        r = int(bg[1:3], 16)
        g = int(bg[3:5], 16)
        b = int(bg[5:7], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        self.assertLess(luminance, 30, msg=f"Matrix bg_dark too light: {bg}")

    def test_get_stylesheet_no_arg_uses_current_theme(self):
        from gdlex_inspector.gui_theme import set_current_theme, get_stylesheet
        set_current_theme("Chiaro")
        ss = get_stylesheet()
        chiaro_bg = "#f2f4f3"
        self.assertIn(chiaro_bg, ss)

    def test_matrix_is_first_in_available_themes(self):
        """Matrix must be the first (default) theme in AVAILABLE_THEMES."""
        from gdlex_inspector.gui_theme import AVAILABLE_THEMES
        self.assertEqual(AVAILABLE_THEMES[0], "Matrix")

    def test_matrix_uses_sans_serif_font(self):
        """Matrix theme must use sans-serif UI font, not monospace."""
        from gdlex_inspector.gui_theme import THEMES
        font_family = THEMES["Matrix"]["font_family"]
        self.assertIn("sans", font_family.lower())
        self.assertNotIn("monospace", font_family.lower())
        self.assertNotIn("courier", font_family.lower())

    def test_matrix_stylesheet_log_uses_monospace(self):
        """QTextEdit in Matrix stylesheet must keep monospace for log readability."""
        from gdlex_inspector.gui_theme import get_stylesheet
        ss = get_stylesheet("Matrix")
        self.assertIn("monospace", ss)

    def test_matrix_stylesheet_has_progressbar(self):
        """Matrix stylesheet must include QProgressBar styling."""
        from gdlex_inspector.gui_theme import get_stylesheet
        ss = get_stylesheet("Matrix")
        self.assertIn("QProgressBar", ss)

    def test_stylesheets_have_distinct_primary_action(self):
        from gdlex_inspector.gui_theme import get_stylesheet
        for name in ("Matrix", "Scuro", "Chiaro"):
            self.assertIn("QPushButton#PrimaryAction", get_stylesheet(name))

    def test_dark_and_light_palettes_are_visually_distinct(self):
        from gdlex_inspector.gui_theme import THEMES
        self.assertNotEqual(THEMES["Scuro"]["bg_dark"], THEMES["Matrix"]["bg_dark"])
        self.assertNotEqual(THEMES["Chiaro"]["fg_accent"], THEMES["Scuro"]["fg_accent"])

    def test_chart_palette_entries_are_nonempty_hex_colors(self):
        from gdlex_inspector.gui_theme import THEMES
        keys = ("chart_bg", "chart_track", "bar_fill", "legend_text", "muted_text")
        for colors in THEMES.values():
            for key in keys:
                self.assertRegex(colors[key], r"^#[0-9a-fA-F]{6}$")

    def test_chart_series_are_theme_aware_and_cycle(self):
        from gdlex_inspector.gui_theme import get_chart_series_color, set_current_theme
        first_colors = {}
        for name in ("Matrix", "Scuro", "Chiaro"):
            set_current_theme(name)
            first_colors[name] = get_chart_series_color(0)
            self.assertRegex(first_colors[name], r"^#[0-9a-fA-F]{6}$")
            self.assertEqual(get_chart_series_color(0), get_chart_series_color(6))
        self.assertEqual(len(set(first_colors.values())), 3)

    def test_scuro_and_chiaro_stylesheets_unchanged(self):
        """Scuro and Chiaro themes must still produce valid stylesheets."""
        from gdlex_inspector.gui_theme import get_stylesheet
        for name in ("Scuro", "Chiaro"):
            ss = get_stylesheet(name)
            self.assertIn("background-color", ss)
            self.assertGreater(len(ss), 200)


class TestDigitalRainHelpers(unittest.TestCase):
    """Splash animation logic stays testable without rendering."""

    def test_columns_are_stable_and_bounded(self):
        from gdlex_inspector.gui import digital_rain_columns
        columns = digital_rain_columns(100, 18)
        self.assertEqual(columns, digital_rain_columns(100, 18))
        self.assertTrue(columns)
        self.assertGreaterEqual(columns[0], 0)
        self.assertLess(columns[-1], 100)

    def test_invalid_column_dimensions_return_empty(self):
        from gdlex_inspector.gui import digital_rain_columns
        self.assertEqual(digital_rain_columns(0), ())
        self.assertEqual(digital_rain_columns(100, 0), ())

    def test_cells_are_deterministic_and_animated(self):
        from gdlex_inspector.gui import digital_rain_cell
        first = digital_rain_cell(2, 4, 3)
        self.assertEqual(first, digital_rain_cell(2, 4, 3))
        self.assertNotEqual(first, digital_rain_cell(2, 4, 4))
        self.assertTrue(first[0])
        self.assertGreaterEqual(first[1], 0)
        self.assertLessEqual(first[1], 255)


if __name__ == "__main__":
    unittest.main()
