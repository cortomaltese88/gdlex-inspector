"""Themes for GD LEX Inspector PySide6 GUI.

Three built-in themes:
  - Matrix  : dark green-on-black Matrix aesthetic (default)
  - Scuro   : professional dark blue/grey
  - Chiaro  : bright light theme for maximum readability
"""

from __future__ import annotations

AVAILABLE_THEMES: tuple[str, ...] = ("Matrix", "Scuro", "Chiaro")

# ---------------------------------------------------------------------------
# Per-theme colour palettes
# ---------------------------------------------------------------------------

_MATRIX: dict[str, str] = {
    "bg_dark":           "#0a0f0a",
    "bg_panel":          "#0d1a0d",
    "bg_panel_alt":      "#102210",
    "bg_table_header":   "#0d2b0d",
    "fg_bright":         "#00ff41",
    "fg_normal":         "#d0ecd0",
    "fg_dim":            "#7ec87e",
    "fg_accent":         "#00cc44",
    "border":            "#1a4d1a",
    "sel_bg":            "#1a4d1a",
    "sel_fg":            "#e0ffe0",
    "alt_row":           "#0b160b",
    "btn_hover":         "#1a3d1a",
    "btn_pressed":       "#0d2b0d",
    "btn_disabled_fg":   "#2a4a2a",
    "btn_disabled_brd":  "#1a2b1a",
    "scrollbar_handle":  "#1a4d1a",
    "bar_track":         "#102810",
    "bar_fill":          "#00d948",
    "chart_bg":          "#0b140b",
    "chart_track":       "#163116",
    "legend_text":       "#d0ecd0",
    "muted_text":        "#75ad75",
    "primary_bg":        "#087a2d",
    "primary_hover":     "#0a9b39",
    "primary_pressed":   "#056523",
    "font_family":       "'Noto Sans', 'DejaVu Sans', sans-serif",
}

_SCURO: dict[str, str] = {
    "bg_dark":           "#111519",
    "bg_panel":          "#181e24",
    "bg_panel_alt":      "#1d252d",
    "bg_table_header":   "#202c36",
    "fg_bright":         "#f2f8fc",
    "fg_normal":         "#c7d2db",
    "fg_dim":            "#8596a3",
    "fg_accent":         "#35c9ff",
    "border":            "#31414d",
    "sel_bg":            "#164f68",
    "sel_fg":            "#f5fbff",
    "alt_row":           "#141a20",
    "btn_hover":         "#243541",
    "btn_pressed":       "#172d39",
    "btn_disabled_fg":   "#59656e",
    "btn_disabled_brd":  "#29333a",
    "scrollbar_handle":  "#416071",
    "bar_track":         "#0d252f",
    "bar_fill":          "#26bde8",
    "chart_bg":          "#131a20",
    "chart_track":       "#263640",
    "legend_text":       "#d5e0e7",
    "muted_text":        "#8295a2",
    "primary_bg":        "#087da5",
    "primary_hover":     "#0798c8",
    "primary_pressed":   "#066783",
    "font_family":       "'Segoe UI', 'DejaVu Sans', 'Liberation Sans', sans-serif",
}

_CHIARO: dict[str, str] = {
    "bg_dark":           "#f2f4f3",
    "bg_panel":          "#ffffff",
    "bg_panel_alt":      "#f8faf9",
    "bg_table_header":   "#e7eef2",
    "fg_bright":         "#15242d",
    "fg_normal":         "#263842",
    "fg_dim":            "#60727c",
    "fg_accent":         "#126a96",
    "border":            "#c7d2d7",
    "sel_bg":            "#d4eaf4",
    "sel_fg":            "#102c3a",
    "alt_row":           "#f6f9fa",
    "btn_hover":         "#e5f1f6",
    "btn_pressed":       "#d4e7ef",
    "btn_disabled_fg":   "#929fa5",
    "btn_disabled_brd":  "#d8dfe2",
    "scrollbar_handle":  "#9bafb9",
    "bar_track":         "#dbe7eb",
    "bar_fill":          "#1687b8",
    "chart_bg":          "#fbfcfc",
    "chart_track":       "#dce8ec",
    "legend_text":       "#2b3e48",
    "muted_text":        "#667983",
    "primary_bg":        "#126a96",
    "primary_hover":     "#0f7eaf",
    "primary_pressed":   "#0c587d",
    "font_family":       "'Segoe UI', 'DejaVu Sans', 'Liberation Sans', sans-serif",
}

THEMES: dict[str, dict[str, str]] = {
    "Matrix": _MATRIX,
    "Scuro":  _SCURO,
    "Chiaro": _CHIARO,
}

_CHART_SERIES: dict[str, tuple[str, ...]] = {
    "Matrix": ("#00e846", "#9aff00", "#ffd166", "#43c7e8", "#91ad91", "#00a86b"),
    "Scuro":  ("#35c9ff", "#6ee7b7", "#f4c95d", "#a78bfa", "#ff826e", "#5c7cfa"),
    "Chiaro": ("#1687b8", "#3b9b72", "#c48716", "#7357b2", "#c95c4b", "#5b76b7"),
}

_RISK_COLORS: dict[str, dict[str, str]] = {
    "Matrix": {
        "none":     "#d0ecd0",
        "low":      "#d0ecd0",
        "medium":   "#ffcc00",
        "high":     "#ff6060",
        "critical": "#ff2222",
    },
    "Scuro": {
        "none":     "#c7d2db",
        "low":      "#8fd5b2",
        "medium":   "#f4c95d",
        "high":     "#ff826e",
        "critical": "#ff4f64",
    },
    "Chiaro": {
        "none":     "#263842",
        "low":      "#26734d",
        "medium":   "#946200",
        "high":     "#b23a24",
        "critical": "#8e1428",
    },
}

# ---------------------------------------------------------------------------
# Theme state
# ---------------------------------------------------------------------------

_current_theme_name: str = "Matrix"


def set_current_theme(name: str) -> None:
    global _current_theme_name
    if name not in THEMES:
        raise ValueError(f"Unknown theme: {name!r}")
    _current_theme_name = name


def get_current_theme_name() -> str:
    return _current_theme_name


def get_current_colors() -> dict[str, str]:
    return THEMES[_current_theme_name]


def get_current_risk_colors() -> dict[str, str]:
    return _RISK_COLORS.get(_current_theme_name, _RISK_COLORS["Matrix"])


def get_chart_series_color(index: int) -> str:
    colors = _CHART_SERIES.get(_current_theme_name, _CHART_SERIES["Matrix"])
    return colors[index % len(colors)]


# ---------------------------------------------------------------------------
# Stylesheet builder
# ---------------------------------------------------------------------------

def _build_stylesheet(c: dict[str, str]) -> str:
    return f"""
QMainWindow, QDialog, QWidget {{
    background-color: {c['bg_dark']};
    color: {c['fg_normal']};
    font-family: {c['font_family']};
    font-size: 13px;
}}
QLabel {{
    color: {c['fg_dim']};
    background: transparent;
}}
QGroupBox {{
    color: {c['fg_bright']};
    background-color: {c['bg_panel']};
    border: 1px solid {c['border']};
    border-radius: 7px;
    margin-top: 16px;
    padding: 10px 6px 8px 6px;
}}
QGroupBox::title {{
    color: {c['fg_accent']};
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 2px 6px;
    background-color: {c['bg_panel']};
    font-weight: bold;
}}
QLineEdit, QSpinBox {{
    background-color: {c['bg_panel']};
    color: {c['fg_bright']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    padding: 6px 9px;
    selection-background-color: {c['sel_bg']};
    selection-color: {c['sel_fg']};
    min-height: 22px;
}}
QLineEdit:focus, QSpinBox:focus {{
    border: 2px solid {c['fg_accent']};
    padding: 5px 8px;
}}
QLineEdit:hover, QSpinBox:hover {{
    border-color: {c['fg_accent']};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {c['bg_panel']};
    border: 1px solid {c['border']};
    width: 18px;
}}
QPushButton {{
    background-color: {c['bg_panel_alt']};
    color: {c['fg_normal']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    padding: 6px 18px;
    min-width: 80px;
    min-height: 28px;
}}
QPushButton:hover {{
    background-color: {c['btn_hover']};
    border-color: {c['fg_accent']};
}}
QPushButton:pressed {{
    background-color: {c['btn_pressed']};
}}
QPushButton:disabled {{
    color: {c['btn_disabled_fg']};
    border-color: {c['btn_disabled_brd']};
}}
QPushButton#PrimaryAction {{
    background-color: {c['primary_bg']};
    color: #ffffff;
    border: 1px solid {c['fg_accent']};
    font-weight: bold;
    padding: 7px 20px;
}}
QPushButton#PrimaryAction:hover {{
    background-color: {c['primary_hover']};
}}
QPushButton#PrimaryAction:pressed {{
    background-color: {c['primary_pressed']};
}}
QTextEdit {{
    background-color: {c['bg_panel']};
    color: {c['fg_dim']};
    border: 1px solid {c['border']};
    border-radius: 4px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 12px;
    padding: 4px;
}}
QProgressBar {{
    background-color: {c['bar_track']};
    border: 1px solid {c['fg_accent']};
    border-radius: 5px;
    color: {c['fg_normal']};
    text-align: center;
    font-size: 11px;
    min-height: 18px;
}}
QProgressBar::chunk {{
    background-color: {c['bar_fill']};
    border-radius: 4px;
}}
QLabel#LogTitle {{
    color: {c['fg_accent']};
    font-weight: bold;
    font-size: 11px;
    padding: 2px 0;
}}
QTableWidget {{
    background-color: {c['bg_panel']};
    color: {c['fg_normal']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    gridline-color: {c['border']};
    selection-background-color: {c['sel_bg']};
    selection-color: {c['sel_fg']};
    alternate-background-color: {c['alt_row']};
}}
QTableWidget::item {{
    padding: 5px 10px;
}}
QTableWidget::item:selected {{
    background-color: {c['sel_bg']};
    color: {c['sel_fg']};
}}
QHeaderView::section {{
    background-color: {c['bg_table_header']};
    color: {c['fg_accent']};
    border: none;
    border-right: 1px solid {c['border']};
    border-bottom: 2px solid {c['fg_accent']};
    padding: 7px 10px;
    font-weight: bold;
    font-size: 12px;
}}
QTabWidget::pane {{
    border: 1px solid {c['border']};
    background-color: {c['bg_panel']};
    border-radius: 5px;
    top: -1px;
}}
QTabBar::tab {{
    background-color: {c['bg_panel_alt']};
    color: {c['fg_dim']};
    border: 1px solid {c['border']};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 7px 20px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {c['bg_table_header']};
    color: {c['fg_bright']};
    border-color: {c['fg_accent']};
    border-top: 3px solid {c['fg_accent']};
    padding-top: 5px;
    font-weight: bold;
}}
QTabBar::tab:hover:!selected {{
    background-color: {c['btn_hover']};
    color: {c['fg_normal']};
}}
QStatusBar {{
    background-color: {c['bg_panel']};
    color: {c['fg_dim']};
    border-top: 1px solid {c['border']};
    font-size: 12px;
    padding: 2px 6px;
}}
QMenuBar {{
    background-color: {c['bg_dark']};
    color: {c['fg_normal']};
    border-bottom: 1px solid {c['border']};
    padding: 2px 4px;
    spacing: 2px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 5px 12px;
    border-radius: 3px;
}}
QMenuBar::item:selected {{
    background-color: {c['btn_hover']};
    color: {c['fg_bright']};
}}
QMenuBar::item:pressed {{
    background-color: {c['btn_pressed']};
}}
QMenu {{
    background-color: {c['bg_panel']};
    color: {c['fg_normal']};
    border: 1px solid {c['border']};
    padding: 4px 0;
}}
QMenu::item {{
    padding: 7px 28px 7px 18px;
}}
QMenu::item:selected {{
    background-color: {c['sel_bg']};
    color: {c['sel_fg']};
}}
QMenu::separator {{
    height: 1px;
    background: {c['border']};
    margin: 4px 8px;
}}
QMenu::indicator {{
    width: 16px;
    height: 16px;
    margin-left: 2px;
}}
QScrollBar:vertical {{
    background: {c['bg_panel']};
    width: 10px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {c['scrollbar_handle']};
    min-height: 24px;
    border-radius: 4px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {c['bg_panel']};
    height: 10px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {c['scrollbar_handle']};
    min-width: 24px;
    border-radius: 4px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QSplitter::handle {{
    background-color: {c['border']};
}}
QSplitter::handle:vertical {{
    height: 4px;
}}
QSplitter::handle:horizontal {{
    width: 4px;
}}
QDialogButtonBox QPushButton {{
    min-width: 90px;
}}
"""


def get_stylesheet(theme_name: str | None = None) -> str:
    name = theme_name or _current_theme_name
    return _build_stylesheet(THEMES[name])


# ---------------------------------------------------------------------------
# Backward-compatible module-level constants (Matrix theme)
# ---------------------------------------------------------------------------

BG_DARK           = _MATRIX["bg_dark"]
BG_PANEL          = _MATRIX["bg_panel"]
BG_TABLE_HEADER   = _MATRIX["bg_table_header"]
FG_BRIGHT         = _MATRIX["fg_bright"]
FG_NORMAL         = _MATRIX["fg_normal"]
FG_DIM            = _MATRIX["fg_dim"]
FG_ACCENT         = _MATRIX["fg_accent"]
BORDER_COLOR      = _MATRIX["border"]

RISK_COLORS: dict[str, str] = _RISK_COLORS["Matrix"]

STYLESHEET: str = _build_stylesheet(_MATRIX)
