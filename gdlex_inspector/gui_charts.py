"""Chart widgets for GD LEX Inspector — Matrix dark theme.

Uses QPainter for donut and horizontal bar charts.
No extra dependencies beyond PySide6.
Helpers (calculate_percentages, category_color, _fmt_size) are reused from report.py.
"""
from __future__ import annotations

import math

try:
    from PySide6.QtCore import Qt, QRectF
    from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath
    from PySide6.QtWidgets import (
        QLabel,
        QScrollArea,
        QSizePolicy,
        QSplitter,
        QVBoxLayout,
        QWidget,
    )
    _PYSIDE6_AVAILABLE = True
except ImportError:
    _PYSIDE6_AVAILABLE = False

from .report import _fmt_size, calculate_percentages, category_color
from . import gui_theme


def chart_data_from_result(result) -> tuple[list, list, list[float]]:
    """Extract (categories, top_dirs, category_percentages) from a ScanResult.

    Returns empty lists when result is None so callers need no None-checks.
    """
    if result is None:
        return [], [], []
    categories = list(result.categories) if result.categories else []
    top_dirs = list(result.top_dirs) if result.top_dirs else []
    percentages = calculate_percentages([c.total_size for c in categories])
    return categories, top_dirs, percentages


if _PYSIDE6_AVAILABLE:

    class _DonutWidget(QWidget):
        """Custom-painted donut chart for category size distribution."""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._categories: list = []
            self._percentages: list[float] = []
            self.setMinimumSize(180, 180)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        def set_data(self, categories: list, percentages: list[float]) -> None:
            self._categories = categories
            self._percentages = percentages
            self.update()

        def paintEvent(self, event) -> None:  # noqa: N802
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            w, h = float(self.width()), float(self.height())

            small_font = QFont("Courier New", 9)
            painter.setFont(small_font)

            if not self._categories:
                painter.setPen(QColor(gui_theme.FG_DIM))
                painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "—")
                return

            margin = 16.0
            size = min(w, h) - 2.0 * margin
            cx, cy = w / 2.0, h / 2.0
            outer_r = size / 2.0
            inner_r = outer_r * 0.54

            # Start at 12 o'clock (90°), sweep clockwise (negative in Qt)
            angle = 90.0

            for cat, pct in zip(self._categories, self._percentages):
                if pct <= 0.0:
                    continue
                sweep = -(pct / 100.0 * 360.0)

                outer_rect = QRectF(cx - outer_r, cy - outer_r, outer_r * 2.0, outer_r * 2.0)
                inner_rect = QRectF(cx - inner_r, cy - inner_r, inner_r * 2.0, inner_r * 2.0)

                # Build annulus sector via QPainterPath
                path = QPainterPath()
                start_rad = math.radians(angle)
                path.moveTo(
                    cx + outer_r * math.cos(start_rad),
                    cy - outer_r * math.sin(start_rad),
                )
                path.arcTo(outer_rect, angle, sweep)
                path.arcTo(inner_rect, angle + sweep, -sweep)
                path.closeSubpath()

                painter.setBrush(QBrush(QColor(category_color(cat.category))))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawPath(path)

                angle += sweep

            # Center total label
            total = sum(max(0, c.total_size) for c in self._categories)
            inner_rect = QRectF(cx - inner_r, cy - inner_r, inner_r * 2.0, inner_r * 2.0)
            bold_font = QFont("Courier New", 9, QFont.Weight.Bold)
            painter.setFont(bold_font)
            painter.setPen(QColor(gui_theme.FG_BRIGHT))
            painter.drawText(inner_rect, Qt.AlignmentFlag.AlignCenter, _fmt_size(total))

    class _LegendWidget(QWidget):
        """Colored swatches + labels + sizes for the donut chart legend."""

        _ROW_H = 22
        _SWATCH = 10

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._categories: list = []
            self._percentages: list[float] = []
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.setMinimumHeight(self._ROW_H)

        def set_data(self, categories: list, percentages: list[float]) -> None:
            self._categories = categories
            self._percentages = percentages
            self.setFixedHeight(max(self._ROW_H, len(categories) * self._ROW_H + 4))
            self.update()

        def paintEvent(self, event) -> None:  # noqa: N802
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            w = float(self.width())

            font = QFont("Courier New", 9)
            painter.setFont(font)

            for i, (cat, pct) in enumerate(zip(self._categories, self._percentages)):
                y = float(i * self._ROW_H)
                # Swatch circle
                swatch_y = y + (self._ROW_H - self._SWATCH) / 2.0
                painter.setBrush(QBrush(QColor(category_color(cat.category))))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QRectF(4.0, swatch_y, self._SWATCH, self._SWATCH))

                # Category name
                painter.setPen(QColor(gui_theme.FG_NORMAL))
                painter.drawText(
                    QRectF(20.0, y, max(w - 145.0, 40.0), self._ROW_H),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    cat.category,
                )

                # Size + percentage (right-aligned)
                size_text = f"{_fmt_size(cat.total_size)} ({pct:.1f}%)"
                painter.setPen(QColor(gui_theme.FG_DIM))
                painter.drawText(
                    QRectF(w - 140.0, y, 136.0, self._ROW_H),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    size_text,
                )

    class _BarsWidget(QWidget):
        """Custom-painted horizontal bar chart for top directories."""

        _ROW_H = 34
        _MARGIN_TOP = 8

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._dirs: list = []
            self.setMinimumHeight(self._MARGIN_TOP + self._ROW_H)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        def set_data(self, dirs: list) -> None:
            self._dirs = dirs
            total_h = self._MARGIN_TOP + max(1, len(dirs)) * self._ROW_H
            self.setFixedHeight(total_h)
            self.update()

        def paintEvent(self, event) -> None:  # noqa: N802
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            w, h = float(self.width()), float(self.height())

            font = QFont("Courier New", 9)
            painter.setFont(font)

            if not self._dirs:
                painter.setPen(QColor(gui_theme.FG_DIM))
                painter.drawText(QRectF(0.0, 0.0, w, h), Qt.AlignmentFlag.AlignCenter, "—")
                return

            label_w = min(max(120.0, w * 0.35), 280.0)
            size_col_w = 80.0
            bar_x = label_w + 8.0
            bar_max_w = max(10.0, w - bar_x - size_col_w - 10.0)
            maximum = max((max(0, d.size) for d in self._dirs), default=1) or 1

            for i, d in enumerate(self._dirs):
                y = float(self._MARGIN_TOP + i * self._ROW_H)
                bar_y = y + self._ROW_H * 0.2
                bar_h = self._ROW_H * 0.55

                # Truncated path label
                label = d.path
                if len(label) > 38:
                    label = "..." + label[-35:]
                painter.setPen(QColor(gui_theme.FG_NORMAL))
                painter.drawText(
                    QRectF(8.0, y, label_w - 12.0, self._ROW_H),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    label,
                )

                # Background track
                painter.setBrush(QBrush(QColor("#102810")))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_max_w, bar_h), 3.0, 3.0)

                # Filled bar
                fill_w = max(0.0, d.size / maximum * bar_max_w)
                if fill_w > 0.0:
                    painter.setBrush(QBrush(QColor(category_color(d.category))))
                    painter.drawRoundedRect(QRectF(bar_x, bar_y, fill_w, bar_h), 3.0, 3.0)

                # Size label
                painter.setPen(QColor(gui_theme.FG_DIM))
                painter.drawText(
                    QRectF(bar_x + bar_max_w + 6.0, y, size_col_w - 6.0, self._ROW_H),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    _fmt_size(d.size),
                )

    class ChartsTab(QWidget):
        """Tab container: donut + bar charts with empty-state label."""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            outer = QVBoxLayout(self)
            outer.setContentsMargins(8, 8, 8, 8)
            outer.setSpacing(0)

            # Empty-state label (shown initially)
            self._empty_label = QLabel(
                "Esegui una scansione per visualizzare i grafici."
            )
            self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._empty_label.setStyleSheet(
                f"color: {gui_theme.FG_DIM}; font-size: 14px; padding: 40px;"
            )
            outer.addWidget(self._empty_label)

            # Content area (hidden until first scan)
            self._content = QWidget()
            outer.addWidget(self._content, 1)
            self._content.hide()

            content_layout = QVBoxLayout(self._content)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(6)

            splitter = QSplitter(Qt.Orientation.Horizontal)

            # --- Left pane: donut + legend ---
            left = QWidget()
            left_layout = QVBoxLayout(left)
            left_layout.setContentsMargins(0, 0, 4, 0)
            left_layout.setSpacing(4)

            title_cat = QLabel("Distribuzione per categoria")
            title_cat.setStyleSheet(
                f"color: {gui_theme.FG_ACCENT}; font-weight: bold; padding-bottom: 2px;"
            )
            left_layout.addWidget(title_cat)

            self._donut = _DonutWidget()
            left_layout.addWidget(self._donut, 2)

            legend_scroll = QScrollArea()
            legend_scroll.setWidgetResizable(True)
            legend_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
            legend_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            legend_scroll.setStyleSheet(f"background: {gui_theme.BG_PANEL};")
            self._legend = _LegendWidget()
            legend_scroll.setWidget(self._legend)
            legend_scroll.setMaximumHeight(200)
            left_layout.addWidget(legend_scroll, 1)

            splitter.addWidget(left)

            # --- Right pane: bars ---
            right = QWidget()
            right_layout = QVBoxLayout(right)
            right_layout.setContentsMargins(4, 0, 0, 0)
            right_layout.setSpacing(4)

            title_bars = QLabel("Top cartelle per dimensione")
            title_bars.setStyleSheet(
                f"color: {gui_theme.FG_ACCENT}; font-weight: bold; padding-bottom: 2px;"
            )
            right_layout.addWidget(title_bars)

            bars_scroll = QScrollArea()
            bars_scroll.setWidgetResizable(True)
            bars_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
            bars_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            bars_scroll.setStyleSheet(f"background: {gui_theme.BG_PANEL};")
            self._bars = _BarsWidget()
            bars_scroll.setWidget(self._bars)
            right_layout.addWidget(bars_scroll)

            splitter.addWidget(right)
            splitter.setStretchFactor(0, 1)
            splitter.setStretchFactor(1, 2)

            content_layout.addWidget(splitter)

        def set_data(self, result) -> None:
            """Update charts from a ScanResult. Call with None to reset to empty state."""
            categories, top_dirs, percentages = chart_data_from_result(result)

            if not categories and not top_dirs:
                self._content.hide()
                self._empty_label.show()
                return

            self._donut.set_data(categories, percentages)
            self._legend.set_data(categories, percentages)
            self._bars.set_data(top_dirs)

            self._empty_label.hide()
            self._content.show()
