"""Matrix dark theme constants and stylesheet for GD LEX Inspector PySide6 GUI."""

BG_DARK = "#0a0f0a"
BG_PANEL = "#0d1a0d"
BG_TABLE_HEADER = "#0d2b0d"
FG_BRIGHT = "#00ff41"
FG_NORMAL = "#c8ffc8"
FG_DIM = "#6af06a"
FG_ACCENT = "#39ff14"
BORDER_COLOR = "#1a4d1a"

RISK_COLORS = {
    "none": FG_NORMAL,
    "low": FG_NORMAL,
    "medium": "#ffcc00",
    "high": "#ff6060",
    "critical": "#ff2222",
}

STYLESHEET = f"""
QMainWindow, QDialog, QWidget {{
    background-color: {BG_DARK};
    color: {FG_NORMAL};
    font-family: 'Courier New', Courier, monospace;
    font-size: 13px;
}}
QLabel {{
    color: {FG_DIM};
    background: transparent;
}}
QGroupBox {{
    color: {FG_ACCENT};
    border: 1px solid {BORDER_COLOR};
    margin-top: 10px;
    padding-top: 4px;
}}
QGroupBox::title {{
    color: {FG_ACCENT};
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
}}
QLineEdit, QSpinBox {{
    background-color: {BG_PANEL};
    color: {FG_BRIGHT};
    border: 1px solid {BORDER_COLOR};
    padding: 3px 6px;
    selection-background-color: #1a4d1a;
    selection-color: {FG_BRIGHT};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER_COLOR};
    width: 16px;
}}
QPushButton {{
    background-color: {BG_PANEL};
    color: {FG_ACCENT};
    border: 1px solid {BORDER_COLOR};
    padding: 5px 14px;
    min-width: 70px;
}}
QPushButton:hover {{
    background-color: #1a3d1a;
    border-color: {FG_ACCENT};
}}
QPushButton:pressed {{
    background-color: {BG_TABLE_HEADER};
}}
QPushButton:disabled {{
    color: #2a4a2a;
    border-color: #1a2b1a;
}}
QTextEdit {{
    background-color: {BG_PANEL};
    color: {FG_DIM};
    border: 1px solid {BORDER_COLOR};
    font-family: 'Courier New', Courier, monospace;
    font-size: 12px;
}}
QTableWidget {{
    background-color: {BG_PANEL};
    color: {FG_NORMAL};
    border: 1px solid {BORDER_COLOR};
    gridline-color: #0d1a0d;
    selection-background-color: #1a4d1a;
    selection-color: {FG_BRIGHT};
    alternate-background-color: #0b160b;
}}
QTableWidget::item:selected {{
    background-color: #1a4d1a;
    color: {FG_BRIGHT};
}}
QHeaderView::section {{
    background-color: {BG_TABLE_HEADER};
    color: {FG_ACCENT};
    border: none;
    border-right: 1px solid {BORDER_COLOR};
    border-bottom: 1px solid {BORDER_COLOR};
    padding: 4px 8px;
    font-weight: bold;
    font-size: 12px;
}}
QTabWidget::pane {{
    border: 1px solid {BORDER_COLOR};
    background-color: {BG_PANEL};
}}
QTabBar::tab {{
    background-color: {BG_PANEL};
    color: {FG_DIM};
    border: 1px solid {BORDER_COLOR};
    border-bottom: none;
    padding: 5px 16px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {BG_TABLE_HEADER};
    color: {FG_BRIGHT};
}}
QTabBar::tab:hover:!selected {{
    background-color: #1a3d1a;
    color: {FG_NORMAL};
}}
QStatusBar {{
    background-color: {BG_PANEL};
    color: {FG_DIM};
    border-top: 1px solid {BORDER_COLOR};
    font-size: 12px;
}}
QScrollBar:vertical {{
    background: {BG_PANEL};
    width: 10px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_COLOR};
    min-height: 20px;
    border-radius: 3px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {BG_PANEL};
    height: 10px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER_COLOR};
    min-width: 20px;
    border-radius: 3px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QSplitter::handle {{
    background-color: {BORDER_COLOR};
    height: 3px;
}}
"""
