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
    "font_family":       "'Noto Sans', 'DejaVu Sans', sans-serif",
}

_SCURO: dict[str, str] = {
    "bg_dark":           "#14172b",
    "bg_panel":          "#1c2240",
    "bg_table_header":   "#0f3460",
    "fg_bright":         "#e8e8f8",
    "fg_normal":         "#c0c4d8",
    "fg_dim":            "#8088a8",
    "fg_accent":         "#7ecfff",
    "border":            "#2a4a70",
    "sel_bg":            "#1e4a80",
    "sel_fg":            "#e8e8f8",
    "alt_row":           "#111528",
    "btn_hover":         "#1a3a5e",
    "btn_pressed":       "#0f2e52",
    "btn_disabled_fg":   "#3a4a60",
    "btn_disabled_brd":  "#202c40",
    "scrollbar_handle":  "#2a4a70",
    "bar_track":         "#0a1628",
    "font_family":       "'Segoe UI', 'DejaVu Sans', 'Liberation Sans', sans-serif",
}

_CHIARO: dict[str, str] = {
    "bg_dark":           "#eef1f6",
    "bg_panel":          "#ffffff",
    "bg_table_header":   "#dce6f0",
    "fg_bright":         "#0d0d1a",
    "fg_normal":         "#1e2232",
    "fg_dim":            "#4a5070",
    "fg_accent":         "#004ea8",
    "border":            "#b0bccf",
    "sel_bg":            "#c2d8f0",
    "sel_fg":            "#0d0d1a",
    "alt_row":           "#f4f6fa",
    "btn_hover":         "#d8e6f4",
    "btn_pressed":       "#c2d8f0",
    "btn_disabled_fg":   "#8890a0",
    "btn_disabled_brd":  "#c8d2dc",
    "scrollbar_handle":  "#a0afc0",
    "bar_track":         "#d8e4f0",
    "font_family":       "'Segoe UI', 'DejaVu Sans', 'Liberation Sans', sans-serif",
}

THEMES: dict[str, dict[str, str]] = {
    "Matrix": _MATRIX,
    "Scuro":  _SCURO,
    "Chiaro": _CHIARO,
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
        "none":     "#c0c4d8",
        "low":      "#c0c4d8",
        "medium":   "#ffd060",
        "high":     "#ff7070",
        "critical": "#ff3535",
    },
    "Chiaro": {
        "none":     "#1e2232",
        "low":      "#1e2232",
        "medium":   "#a06000",
        "high":     "#c02000",
        "critical": "#8a0000",
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
    color: {c['fg_accent']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    margin-top: 16px;
    padding: 10px 6px 8px 6px;
}}
QGroupBox::title {{
    color: {c['fg_accent']};
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 2px 6px;
    background-color: {c['bg_dark']};
}}
QLineEdit, QSpinBox {{
    background-color: {c['bg_panel']};
    color: {c['fg_bright']};
    border: 1px solid {c['border']};
    border-radius: 4px;
    padding: 5px 8px;
    selection-background-color: {c['sel_bg']};
    selection-color: {c['sel_fg']};
    min-height: 22px;
}}
QLineEdit:focus, QSpinBox:focus {{
    border-color: {c['fg_accent']};
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
    background-color: {c['bg_panel']};
    color: {c['fg_normal']};
    border: 1px solid {c['border']};
    border-radius: 4px;
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
    border: 1px solid {c['border']};
    border-radius: 4px;
    color: {c['fg_normal']};
    text-align: center;
    font-size: 11px;
    min-height: 16px;
}}
QProgressBar::chunk {{
    background-color: {c['fg_accent']};
    border-radius: 3px;
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
    border-radius: 0px;
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
    border-bottom: 2px solid {c['border']};
    padding: 7px 10px;
    font-weight: bold;
    font-size: 12px;
}}
QTabWidget::pane {{
    border: 1px solid {c['border']};
    background-color: {c['bg_panel']};
}}
QTabBar::tab {{
    background-color: {c['bg_panel']};
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
