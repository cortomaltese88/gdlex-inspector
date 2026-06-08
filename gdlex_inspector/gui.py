"""PySide6 GUI for GD LEX Inspector — multi-theme, splash screen, menu bar.

Launch with: python3 -m gdlex_inspector gui
Requires PySide6: pip install PySide6
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

from . import gui_theme
from . import gui_charts

try:
    from PySide6.QtCore import Qt, QEventLoop, QRectF, QSettings, QThread, QTimer, Signal
    from PySide6.QtGui import (
        QAction,
        QActionGroup,
        QBrush,
        QColor,
        QFont,
        QIcon,
        QPainter,
        QPen,
        QPixmap,
    )
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QApplication,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenu,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QSpinBox,
        QSplashScreen,
        QSplitter,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    _PYSIDE6_AVAILABLE = True
except ImportError:
    _PYSIDE6_AVAILABLE = False


_SETTINGS_ORG = "GDLex"
_SETTINGS_APP = "Inspector"
_DIGITAL_RAIN_GLYPHS = "01アイウエオカキクケコサシスセソ<>/{}[]"


def digital_rain_columns(width: int, column_width: int = 18) -> tuple[int, ...]:
    """Return stable x coordinates for splash rain columns."""
    if width <= 0 or column_width <= 0:
        return ()
    return tuple(range(column_width // 2, width, column_width))


def digital_rain_cell(column: int, row: int, frame: int) -> tuple[str, int]:
    """Return a deterministic glyph and alpha for one animated rain cell."""
    seed = column * 17 + row * 31 + frame
    glyph = _DIGITAL_RAIN_GLYPHS[seed % len(_DIGITAL_RAIN_GLYPHS)]
    trail = (row - (frame // 2 + column * 3)) % 17
    if trail == 0:
        alpha = 190
    elif trail < 5:
        alpha = 105 - trail * 15
    else:
        alpha = 18
    return glyph, alpha


def _get_version() -> str:
    try:
        from . import __version__
        return __version__
    except Exception:
        return "?"


def _get_svg_path() -> str:
    return os.path.join(os.path.dirname(__file__), "assets", "gdlex-inspector.svg")


if _PYSIDE6_AVAILABLE:

    # ------------------------------------------------------------------
    # Splash screen
    # ------------------------------------------------------------------

    class _SplashScreen(QSplashScreen):
        """Matrix-styled animated splash screen with progress bar."""

        _W = 560
        _H = 320

        def __init__(self) -> None:
            pixmap = QPixmap(self._W, self._H)
            pixmap.fill(QColor("#0a0f0a"))
            super().__init__(pixmap, Qt.WindowType.SplashScreen)
            self._progress = 0
            self._frame = 0
            self._version = _get_version()
            self._render()
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._tick)
            self._timer.start(25)

        def _tick(self) -> None:
            self._progress = min(100, self._progress + 2)
            self._frame += 1
            self._render()
            if self._progress >= 100:
                self._timer.stop()

        def _render(self) -> None:
            pixmap = QPixmap(self._W, self._H)
            pixmap.fill(QColor("#0a0f0a"))
            p = QPainter(pixmap)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            w, h = float(self._W), float(self._H)

            # Quiet digital rain background, deterministic to avoid timer jitter.
            rain_font = QFont("DejaVu Sans Mono", 10)
            p.setFont(rain_font)
            for column, x in enumerate(digital_rain_columns(self._W)):
                phase = (self._frame + column * 5) % 19
                for row in range(-1, 20):
                    glyph, alpha = digital_rain_cell(column, row, self._frame)
                    y = ((row + phase) % 19) * 17 - 4
                    p.setPen(QColor(0, 255, 65, alpha))
                    p.drawText(x, y, glyph)

            # A translucent reading panel keeps the identity text crisp.
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(5, 13, 7, 218)))
            p.drawRoundedRect(QRectF(66.0, 20.0, w - 132.0, 210.0), 10.0, 10.0)

            # Border
            p.setPen(QPen(QColor("#1a4d1a"), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(QRectF(1.0, 1.0, w - 2.0, h - 2.0))

            # Inner subtle glow border
            p.setPen(QPen(QColor("#0d2b0d"), 1))
            p.drawRect(QRectF(4.0, 4.0, w - 8.0, h - 8.0))

            # Title
            title_font = QFont("Courier New", 26, QFont.Weight.Bold)
            p.setFont(title_font)
            p.setPen(QColor("#00ff41"))
            p.drawText(QRectF(20.0, 28.0, w - 40.0, 52.0), Qt.AlignmentFlag.AlignCenter,
                       "GD LEX Inspector")

            # Subtitle
            sub_font = QFont("Courier New", 10)
            p.setFont(sub_font)
            p.setPen(QColor("#6af06a"))
            p.drawText(QRectF(20.0, 92.0, w - 40.0, 28.0), Qt.AlignmentFlag.AlignCenter,
                       "Disk inspection and prudential reporting tool")

            # Separator line
            p.setPen(QPen(QColor("#1a4d1a"), 1))
            p.drawLine(int(w * 0.15), 132, int(w * 0.85), 132)

            # Version
            ver_font = QFont("Courier New", 11, QFont.Weight.Bold)
            p.setFont(ver_font)
            p.setPen(QColor("#39ff14"))
            p.drawText(QRectF(20.0, 142.0, w - 40.0, 26.0), Qt.AlignmentFlag.AlignCenter,
                       f"v{self._version}")

            # Credits
            cred_font = QFont("Courier New", 9)
            p.setFont(cred_font)
            p.setPen(QColor("#6af06a"))
            p.drawText(QRectF(20.0, 178.0, w - 40.0, 22.0), Qt.AlignmentFlag.AlignCenter,
                       "STUDIO GD LEX")
            p.drawText(QRectF(20.0, 198.0, w - 40.0, 20.0), Qt.AlignmentFlag.AlignCenter,
                       "GPL-3.0-or-later")

            # Progress bar track
            bar_x, bar_y = 40.0, h - 52.0
            bar_w, bar_h = w - 80.0, 12.0
            p.setBrush(QBrush(QColor("#0d1a0d")))
            p.setPen(QPen(QColor("#1a4d1a"), 1))
            p.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 4.0, 4.0)

            # Progress bar fill
            fill_w = bar_w * self._progress / 100.0
            if fill_w > 0.0:
                p.setBrush(QBrush(QColor("#00ff41")))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawRoundedRect(QRectF(bar_x, bar_y, fill_w, bar_h), 4.0, 4.0)

            # Progress label
            pct_font = QFont("Courier New", 8)
            p.setFont(pct_font)
            p.setPen(QColor("#6af06a"))
            p.drawText(
                QRectF(bar_x, bar_y + bar_h + 6.0, bar_w, 16.0),
                Qt.AlignmentFlag.AlignCenter,
                f"Avvio... {self._progress}%",
            )

            p.end()
            self.setPixmap(pixmap)

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------

    class _AboutDialog(QDialog):
        """Information dialog for GD LEX Inspector."""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self.setWindowTitle("Informazioni su GD LEX Inspector")
            self.setFixedSize(440, 360)
            self.setModal(True)
            self._build_ui()

        def _build_ui(self) -> None:
            from . import __version__, __author__, __license__
            colors = gui_theme.get_current_colors()
            accent = colors["fg_accent"]

            layout = QVBoxLayout(self)
            layout.setSpacing(10)
            layout.setContentsMargins(28, 24, 28, 20)

            svg_path = _get_svg_path()
            if os.path.isfile(svg_path):
                icon_lbl = QLabel()
                icon_lbl.setPixmap(QIcon(svg_path).pixmap(56, 56))
                icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(icon_lbl)

            name_lbl = QLabel("GD LEX Inspector")
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_lbl.setStyleSheet(
                f"color: {accent}; font-size: 20px; font-weight: bold;"
            )
            layout.addWidget(name_lbl)

            ver_lbl = QLabel(f"Versione {__version__}")
            ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ver_lbl.setStyleSheet(f"color: {colors['fg_normal']}; font-size: 13px;")
            layout.addWidget(ver_lbl)

            layout.addSpacing(6)

            desc_lbl = QLabel("Disk inspection and prudential reporting tool")
            desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_lbl.setWordWrap(True)
            layout.addWidget(desc_lbl)

            layout.addSpacing(6)

            credits_lbl = QLabel(f"Sviluppato da <b>{__author__}</b>")
            credits_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            credits_lbl.setStyleSheet(f"color: {colors['fg_normal']};")
            layout.addWidget(credits_lbl)

            lic_lbl = QLabel(f"Licenza: {__license__}")
            lic_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lic_lbl)

            layout.addSpacing(4)

            repo_lbl = QLabel(
                f'<a href="https://github.com/studiogdlex/gdlex-inspector"'
                f' style="color:{accent};">'
                "github.com/studiogdlex/gdlex-inspector</a>"
            )
            repo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            repo_lbl.setOpenExternalLinks(True)
            layout.addWidget(repo_lbl)

            layout.addStretch()

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            buttons.accepted.connect(self.accept)
            layout.addWidget(buttons)

    # ------------------------------------------------------------------
    # Scan worker
    # ------------------------------------------------------------------

    class ScanWorker(QThread):
        log = Signal(str)
        done = Signal(object)
        error = Signal(str)

        def __init__(self, path: str, top_n: int, min_size: str, max_depth: int) -> None:
            super().__init__()
            self._path = path
            self._top_n = top_n
            self._min_size = min_size
            self._max_depth = max_depth

        def run(self) -> None:
            from .scanner import parse_size, scan_directory
            from .backend import choose_backend
            from .platform_info import get_platform_summary

            try:
                min_size_bytes = 0
                if self._min_size.strip():
                    min_size_bytes = parse_size(self._min_size.strip())

                max_depth = self._max_depth if self._max_depth > 0 else None
                self.log.emit(f"Avvio scansione: {self._path}")
                result = scan_directory(
                    root=self._path,
                    top_n=self._top_n,
                    min_size=min_size_bytes,
                    max_depth=max_depth,
                )
                result.backend_used = choose_backend(None)
                result.platform_info = get_platform_summary()
                self.done.emit(result)
            except Exception as exc:
                self.error.emit(str(exc))

    # ------------------------------------------------------------------
    # Main window
    # ------------------------------------------------------------------

    class MainWindow(QMainWindow):
        def __init__(self, initial_path: str = "") -> None:
            super().__init__()
            self._result = None
            self._worker: ScanWorker | None = None
            self._theme_actions: dict[str, QAction] = {}
            self._setup_ui(initial_path)

        # --------------------------------------------------------------
        # UI construction
        # --------------------------------------------------------------

        def _setup_ui(self, initial_path: str) -> None:
            version = _get_version()
            self.setWindowTitle(f"GD LEX Inspector  v{version}")
            self.resize(1180, 780)
            self.setMinimumSize(860, 580)

            svg_path = _get_svg_path()
            if os.path.isfile(svg_path):
                self.setWindowIcon(QIcon(svg_path))

            # Apply theme (loads theme from settings first)
            self._load_settings(initial_path)
            self.setStyleSheet(gui_theme.get_stylesheet())

            self._build_menu_bar()

            central = QWidget()
            self.setCentralWidget(central)
            root_layout = QVBoxLayout(central)
            root_layout.setSpacing(10)
            root_layout.setContentsMargins(12, 12, 12, 12)

            root_layout.addWidget(self._build_path_group(initial_path))
            root_layout.addWidget(self._build_options_group())
            root_layout.addWidget(self._build_progress_bar())
            root_layout.addWidget(self._build_splitter(), 1)
            root_layout.addLayout(self._build_export_bar())

            self._statusbar = self.statusBar()
            self._statusbar.showMessage("Pronto.")

            ver_label = QLabel(f"GD LEX Inspector v{version}  |  STUDIO GD LEX")
            ver_label.setObjectName("statusVersionLabel")
            self._statusbar.addPermanentWidget(ver_label)

            self._connect_signals()

        def _build_menu_bar(self) -> None:
            menubar = self.menuBar()

            # --- File ---
            file_menu = menubar.addMenu("&File")
            quit_act = QAction("E&sci", self)
            quit_act.setShortcut("Ctrl+Q")
            quit_act.triggered.connect(self.close)
            file_menu.addAction(quit_act)

            # --- Visualizza ---
            view_menu = menubar.addMenu("&Visualizza")
            theme_menu = QMenu("&Tema", self)
            view_menu.addMenu(theme_menu)

            theme_group = QActionGroup(self)
            theme_group.setExclusive(True)
            current_theme = gui_theme.get_current_theme_name()

            for name in gui_theme.AVAILABLE_THEMES:
                act = QAction(name, self)
                act.setCheckable(True)
                act.setChecked(name == current_theme)
                act.triggered.connect(lambda checked, n=name: self._apply_theme(n))
                theme_group.addAction(act)
                theme_menu.addAction(act)
                self._theme_actions[name] = act

            # --- Aiuto ---
            help_menu = menubar.addMenu("&Aiuto")
            about_act = QAction("&Informazioni su GD LEX Inspector...", self)
            about_act.setShortcut("F1")
            about_act.triggered.connect(self._show_about)
            help_menu.addAction(about_act)

            help_menu.addSeparator()

            repo_act = QAction("Apri repository GitHub", self)
            repo_act.triggered.connect(self._open_github)
            help_menu.addAction(repo_act)

        def _build_path_group(self, initial_path: str) -> QGroupBox:
            group = QGroupBox("Percorso da analizzare")
            layout = QHBoxLayout(group)
            layout.setSpacing(10)
            layout.setContentsMargins(12, 8, 12, 10)
            self._path_edit = QLineEdit(initial_path)
            self._path_edit.setPlaceholderText("Seleziona o inserisci il percorso...")
            self._path_edit.returnPressed.connect(self._start_scan)
            browse_btn = QPushButton("Sfoglia…")
            browse_btn.setFixedWidth(100)
            browse_btn.clicked.connect(self._browse_path)
            lbl = QLabel("Percorso:")
            lbl.setFixedWidth(72)
            layout.addWidget(lbl)
            layout.addWidget(self._path_edit, 1)
            layout.addWidget(browse_btn)
            return group

        def _build_options_group(self) -> QGroupBox:
            group = QGroupBox("Opzioni scansione")
            layout = QHBoxLayout(group)
            layout.setSpacing(14)
            layout.setContentsMargins(12, 8, 12, 10)

            top_lbl = QLabel("Top N:")
            top_lbl.setFixedWidth(50)
            layout.addWidget(top_lbl)
            self._top_spin = QSpinBox()
            self._top_spin.setRange(1, 500)
            self._top_spin.setValue(10)
            self._top_spin.setFixedWidth(75)
            layout.addWidget(self._top_spin)

            layout.addSpacing(6)
            ms_lbl = QLabel("Min size:")
            ms_lbl.setFixedWidth(66)
            layout.addWidget(ms_lbl)
            self._min_size_edit = QLineEdit()
            self._min_size_edit.setPlaceholderText("es. 100M")
            self._min_size_edit.setFixedWidth(96)
            layout.addWidget(self._min_size_edit)

            layout.addSpacing(6)
            depth_lbl = QLabel("Max depth (0=∞):")
            layout.addWidget(depth_lbl)
            self._depth_spin = QSpinBox()
            self._depth_spin.setRange(0, 99)
            self._depth_spin.setValue(0)
            self._depth_spin.setFixedWidth(75)
            layout.addWidget(self._depth_spin)

            layout.addStretch()
            self._scan_btn = QPushButton("▶  Scansiona")
            self._scan_btn.setObjectName("PrimaryAction")
            self._scan_btn.setDefault(True)
            self._scan_btn.setMinimumWidth(130)
            self._scan_btn.clicked.connect(self._start_scan)
            layout.addWidget(self._scan_btn)
            return group

        def _build_progress_bar(self) -> QWidget:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 2, 0, 2)
            layout.setSpacing(10)
            self._scan_status_label = QLabel("Pronto.")
            self._scan_status_label.setFixedWidth(180)
            layout.addWidget(self._scan_status_label)
            self._progress_bar = QProgressBar()
            self._progress_bar.setRange(0, 100)
            self._progress_bar.setValue(0)
            self._progress_bar.setTextVisible(True)
            self._progress_bar.setFormat("")
            self._progress_bar.setMinimumHeight(18)
            layout.addWidget(self._progress_bar, 1)
            return widget

        def _build_log_panel(self) -> QWidget:
            panel = QWidget()
            vbox = QVBoxLayout(panel)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(2)

            header = QHBoxLayout()
            header.setContentsMargins(4, 0, 4, 0)
            title = QLabel("Log / Debug")
            title.setObjectName("LogTitle")
            header.addWidget(title)
            header.addStretch()
            clear_btn = QPushButton("Pulisci")
            clear_btn.setMinimumWidth(0)
            clear_btn.setFixedHeight(22)
            clear_btn.setStyleSheet("min-width: 54px; padding: 2px 8px;")
            clear_btn.clicked.connect(lambda: self._log.clear())
            copy_btn = QPushButton("Copia log")
            copy_btn.setMinimumWidth(0)
            copy_btn.setFixedHeight(22)
            copy_btn.setStyleSheet("min-width: 72px; padding: 2px 8px;")
            copy_btn.clicked.connect(self._copy_log)
            header.addWidget(clear_btn)
            header.addWidget(copy_btn)
            vbox.addLayout(header)

            self._log = QTextEdit()
            self._log.setReadOnly(True)
            self._log.setMaximumHeight(140)
            self._log.setMinimumHeight(60)
            self._log.setPlaceholderText("Il log delle operazioni comparirà qui…")
            vbox.addWidget(self._log)
            return panel

        def _build_splitter(self) -> QSplitter:
            splitter = QSplitter(Qt.Orientation.Vertical)

            splitter.addWidget(self._build_log_panel())

            self._tab_widget = QTabWidget()
            self._files_table = self._make_table(
                ["#", "Percorso", "Dimensione", "Categoria", "Rischio"], stretch_col=1
            )
            self._dirs_table = self._make_table(
                ["#", "Percorso", "Dimensione", "File", "Rischio"], stretch_col=1
            )
            self._cats_table = self._make_table(
                ["Categoria", "Dimensione", "File", "Rischio"], stretch_col=0
            )
            self._files_table.itemDoubleClicked.connect(self._open_table_item)
            self._dirs_table.itemDoubleClicked.connect(self._open_table_item)

            self._charts_tab = gui_charts.ChartsTab()

            self._tab_widget.addTab(self._files_table, "  Top file  ")
            self._tab_widget.addTab(self._dirs_table, "  Top cartelle  ")
            self._tab_widget.addTab(self._cats_table, "  Categorie  ")
            self._tab_widget.addTab(self._charts_tab, "  Grafici  ")
            splitter.addWidget(self._tab_widget)

            splitter.setStretchFactor(0, 0)
            splitter.setStretchFactor(1, 1)
            return splitter

        def _build_export_bar(self) -> QHBoxLayout:
            bar = QHBoxLayout()
            bar.setSpacing(8)
            self._html_btn = QPushButton("Esporta HTML")
            self._json_btn = QPushButton("Esporta JSON")
            self._csv_btn  = QPushButton("Esporta CSV")
            self._open_btn = QPushButton("Apri percorso")

            for btn in (self._html_btn, self._json_btn, self._csv_btn, self._open_btn):
                btn.setEnabled(False)

            self._html_btn.clicked.connect(self._export_html)
            self._json_btn.clicked.connect(self._export_json)
            self._csv_btn.clicked.connect(self._export_csv)
            self._open_btn.clicked.connect(self._open_selected_path)

            bar.addWidget(self._html_btn)
            bar.addWidget(self._json_btn)
            bar.addWidget(self._csv_btn)
            bar.addStretch()
            bar.addWidget(self._open_btn)
            return bar

        @staticmethod
        def _make_table(headers: list[str], stretch_col: int = 1) -> QTableWidget:
            table = QTableWidget(0, len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setAlternatingRowColors(True)
            table.setShowGrid(True)
            table.verticalHeader().setVisible(False)
            table.verticalHeader().setDefaultSectionSize(28)
            hh = table.horizontalHeader()
            hh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            hh.setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)
            hh.setStretchLastSection(False)
            hh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            return table

        def _connect_signals(self) -> None:
            for table in (self._files_table, self._dirs_table):
                table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self._files_table.customContextMenuRequested.connect(
                lambda pos: self._show_context_menu(self._files_table, pos)
            )
            self._dirs_table.customContextMenuRequested.connect(
                lambda pos: self._show_context_menu(self._dirs_table, pos)
            )
            self._files_table.itemSelectionChanged.connect(self._update_open_btn)
            self._dirs_table.itemSelectionChanged.connect(self._update_open_btn)
            self._tab_widget.currentChanged.connect(lambda _: self._update_open_btn())

        # --------------------------------------------------------------
        # Theme handling
        # --------------------------------------------------------------

        def _apply_theme(self, name: str) -> None:
            gui_theme.set_current_theme(name)
            self.setStyleSheet(gui_theme.get_stylesheet())
            for n, act in self._theme_actions.items():
                act.setChecked(n == name)
            self._charts_tab.apply_theme()
            if self._result is not None:
                self._populate_tables(self._result)
            s = QSettings(_SETTINGS_ORG, _SETTINGS_APP)
            s.setValue("theme", name)
            self._statusbar.showMessage(f"Tema applicato: {name}")

        # --------------------------------------------------------------
        # Settings persistence
        # --------------------------------------------------------------

        def _load_settings(self, initial_path: str) -> None:
            s = QSettings(_SETTINGS_ORG, _SETTINGS_APP)

            # Theme (loaded early, before stylesheet is set)
            saved_theme = s.value("theme", "Matrix")
            if saved_theme not in gui_theme.AVAILABLE_THEMES:
                saved_theme = "Matrix"
            gui_theme.set_current_theme(saved_theme)

            path = initial_path or s.value("last_path", "")
            if hasattr(self, "_path_edit"):
                self._path_edit.setText(path)
            try:
                if hasattr(self, "_top_spin"):
                    self._top_spin.setValue(int(s.value("top_n", 10)))
            except (TypeError, ValueError):
                pass
            if hasattr(self, "_min_size_edit"):
                self._min_size_edit.setText(s.value("min_size", "") or "")
            try:
                if hasattr(self, "_depth_spin"):
                    self._depth_spin.setValue(int(s.value("max_depth", 0)))
            except (TypeError, ValueError):
                pass

        def _save_settings(self) -> None:
            s = QSettings(_SETTINGS_ORG, _SETTINGS_APP)
            s.setValue("last_path", self._path_edit.text().strip())
            s.setValue("top_n", self._top_spin.value())
            s.setValue("min_size", self._min_size_edit.text().strip())
            s.setValue("max_depth", self._depth_spin.value())
            s.setValue("theme", gui_theme.get_current_theme_name())

        def closeEvent(self, event) -> None:
            self._save_settings()
            super().closeEvent(event)

        # --------------------------------------------------------------
        # Dialogs
        # --------------------------------------------------------------

        def _show_about(self) -> None:
            dlg = _AboutDialog(self)
            dlg.exec()

        def _open_github(self) -> None:
            url = "https://github.com/studiogdlex/gdlex-inspector"
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception:
                QMessageBox.information(self, "Repository", url)

        # --------------------------------------------------------------
        # Scan logic
        # --------------------------------------------------------------

        def _browse_path(self) -> None:
            start = self._path_edit.text().strip() or os.path.expanduser("~")
            path = QFileDialog.getExistingDirectory(self, "Seleziona cartella", start)
            if path:
                self._path_edit.setText(path)

        def _log_msg(self, msg: str) -> None:
            self._log.append(msg)
            sb = self._log.verticalScrollBar()
            sb.setValue(sb.maximum())

        def _copy_log(self) -> None:
            text = self._log.toPlainText()
            if text:
                QApplication.clipboard().setText(text)

        def _set_scan_running(self, running: bool) -> None:
            self._scan_btn.setEnabled(not running)
            for btn in (self._html_btn, self._json_btn, self._csv_btn, self._open_btn):
                btn.setEnabled(False)
            if running:
                self._progress_bar.setRange(0, 0)
                self._progress_bar.setFormat("")
                self._scan_status_label.setText("Scansione in corso…")
                self._statusbar.showMessage("Scansione in corso…")
                self._files_table.setRowCount(0)
                self._dirs_table.setRowCount(0)
                self._cats_table.setRowCount(0)
                self._charts_tab.set_data(None)

        def _start_scan(self) -> None:
            path = self._path_edit.text().strip()
            if not path:
                self._log_msg("[ERRORE] Nessun percorso specificato.")
                self._statusbar.showMessage("Errore: percorso mancante.")
                return
            if not os.path.exists(path):
                self._log_msg(f"[ERRORE] Percorso inesistente: {path}")
                self._statusbar.showMessage("Errore: percorso inesistente.")
                return
            if not os.path.isdir(path):
                self._log_msg(f"[ERRORE] Non è una cartella: {path}")
                self._statusbar.showMessage("Errore: non è una cartella.")
                return

            min_size_str = self._min_size_edit.text().strip()
            if min_size_str:
                from .scanner import parse_size
                try:
                    parse_size(min_size_str)
                except ValueError as exc:
                    self._log_msg(f"[ERRORE] Min size non valida: {exc}")
                    self._statusbar.showMessage("Errore: min size non valida.")
                    return

            self._log_msg(
                f"Scansione avviata — percorso: {path} | "
                f"top {self._top_spin.value()} | "
                f"min size: {min_size_str or '—'} | "
                f"max depth: {self._depth_spin.value() or '∞'}"
            )
            self._set_scan_running(True)
            self._worker = ScanWorker(
                path=path,
                top_n=self._top_spin.value(),
                min_size=min_size_str,
                max_depth=self._depth_spin.value(),
            )
            self._worker.log.connect(self._log_msg)
            self._worker.done.connect(self._on_scan_done)
            self._worker.error.connect(self._on_scan_error)
            self._worker.start()

        def _on_scan_done(self, result) -> None:
            from .report import _fmt_size
            self._result = result
            self._populate_tables(result)
            self._charts_tab.set_data(result)

            self._log_msg("Scansione completata.")
            self._log_msg(f"  Percorso: {result.root_path}")
            self._log_msg(f"  Dimensione totale: {_fmt_size(result.total_size)}")
            self._log_msg(f"  File: {result.total_files}  Cartelle: {result.total_dirs}")
            if result.issues:
                self._log_msg(f"  Percorsi non accessibili: {len(result.issues)}")

            summary = (
                f"Completata — {result.total_files} file, "
                f"{result.total_dirs} dir, "
                f"{_fmt_size(result.total_size)} totale"
            )
            self._progress_bar.setRange(0, 100)
            self._progress_bar.setValue(100)
            self._progress_bar.setFormat("Completata")
            self._scan_status_label.setText(
                f"{result.total_files} file  {result.total_dirs} dir  {_fmt_size(result.total_size)}"
            )
            self._statusbar.showMessage(summary)
            self._scan_btn.setEnabled(True)
            for btn in (self._html_btn, self._json_btn, self._csv_btn):
                btn.setEnabled(True)
            self._update_open_btn()

        def _on_scan_error(self, msg: str) -> None:
            self._log_msg(f"[ERRORE] {msg}")
            self._progress_bar.setRange(0, 100)
            self._progress_bar.setValue(0)
            self._progress_bar.setFormat("Errore")
            self._scan_status_label.setText("Errore")
            self._statusbar.showMessage(f"Errore durante la scansione: {msg}")
            self._scan_btn.setEnabled(True)
            self._result = None

        # --------------------------------------------------------------
        # Table population
        # --------------------------------------------------------------

        def _populate_tables(self, result) -> None:
            from .report import _fmt_size

            self._files_table.setRowCount(len(result.top_files))
            for row, f in enumerate(result.top_files):
                self._fill_row(
                    self._files_table, row,
                    [str(row + 1), f.path, _fmt_size(f.size), f.category, f.risk_level],
                    risk_col=4, risk_value=f.risk_level,
                )

            self._dirs_table.setRowCount(len(result.top_dirs))
            for row, d in enumerate(result.top_dirs):
                self._fill_row(
                    self._dirs_table, row,
                    [str(row + 1), d.path, _fmt_size(d.size), str(d.file_count), d.risk_level],
                    risk_col=4, risk_value=d.risk_level,
                )

            self._cats_table.setRowCount(len(result.categories))
            for row, c in enumerate(result.categories):
                self._fill_row(
                    self._cats_table, row,
                    [c.category, _fmt_size(c.total_size), str(c.file_count), c.risk_level],
                    risk_col=3, risk_value=c.risk_level,
                )

        @staticmethod
        def _fill_row(
            table: QTableWidget,
            row: int,
            values: list[str],
            risk_col: int,
            risk_value: str,
        ) -> None:
            risk_colors = gui_theme.get_current_risk_colors()
            color_hex = risk_colors.get(risk_value, gui_theme.get_current_colors()["fg_normal"])
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                if col == risk_col:
                    item.setForeground(QColor(color_hex))
                    item.setFont(QFont("", -1, QFont.Weight.Bold if risk_value in ("high", "critical") else QFont.Weight.Normal))
                table.setItem(row, col, item)

        # --------------------------------------------------------------
        # Context menu
        # --------------------------------------------------------------

        def _show_context_menu(self, table: QTableWidget, pos) -> None:
            row = table.rowAt(pos.y())
            if row < 0:
                return
            path_item = table.item(row, 1)
            if path_item is None:
                return
            path = path_item.text()
            is_file = table is self._files_table

            menu = QMenu(self)
            open_action = QAction("Apri percorso", self)
            copy_action = QAction("Copia percorso negli appunti", self)
            open_action.triggered.connect(lambda: self._open_path_in_fm(path, is_file=is_file))
            copy_action.triggered.connect(lambda: QApplication.clipboard().setText(path))
            menu.addAction(open_action)
            menu.addAction(copy_action)
            menu.exec(table.viewport().mapToGlobal(pos))

        # --------------------------------------------------------------
        # Open path
        # --------------------------------------------------------------

        def _update_open_btn(self) -> None:
            if self._result is None:
                self._open_btn.setEnabled(False)
                return
            idx = self._tab_widget.currentIndex()
            if idx == 0:
                enabled = self._files_table.currentRow() >= 0
            elif idx == 1:
                enabled = self._dirs_table.currentRow() >= 0
            else:
                enabled = False
            self._open_btn.setEnabled(enabled)

        def _open_table_item(self, item: QTableWidgetItem) -> None:
            table = item.tableWidget()
            row = item.row()
            path_item = table.item(row, 1)
            if path_item is None:
                return
            is_file = table is self._files_table
            self._open_path_in_fm(path_item.text(), is_file=is_file)

        def _open_selected_path(self) -> None:
            current_tab = self._tab_widget.currentIndex()
            if current_tab == 0:
                table, is_file = self._files_table, True
            elif current_tab == 1:
                table, is_file = self._dirs_table, False
            else:
                self._log_msg("[INFO] Seleziona una riga nella tab File o Cartelle.")
                return

            row = table.currentRow()
            if row < 0:
                self._log_msg("[INFO] Nessuna riga selezionata.")
                return
            path_item = table.item(row, 1)
            if path_item is None:
                return
            self._open_path_in_fm(path_item.text(), is_file=is_file)

        def _open_path_in_fm(self, path: str, is_file: bool) -> None:
            from .open_path import build_open_command
            from .platform_info import get_platform_kind
            try:
                cmd = build_open_command(path, is_file=is_file, platform_kind=get_platform_kind())
                subprocess.Popen(cmd, start_new_session=True)  # noqa: S603
                self._log_msg(f"Apertura: {path}")
            except Exception as exc:
                self._log_msg(f"[ERRORE] Impossibile aprire {path}: {exc}")

        # --------------------------------------------------------------
        # Export
        # --------------------------------------------------------------

        def _export_html(self) -> None:
            self._export("HTML", "html")

        def _export_json(self) -> None:
            self._export("JSON", "json")

        def _export_csv(self) -> None:
            self._export("CSV", "csv")

        def _export(self, fmt: str, ext: str) -> None:
            if self._result is None:
                return
            from .report import to_html, to_json, to_csv

            basename = re.sub(r"[^\w]", "_", os.path.basename(
                self._result.root_path.rstrip("/\\")
            )) or "report"
            default_name = os.path.expanduser(f"~/gdlex_{basename}.{ext}")

            path, _ = QFileDialog.getSaveFileName(
                self,
                f"Salva report {fmt}",
                default_name,
                f"{fmt} (*.{ext})",
            )
            if not path:
                return
            try:
                if ext == "html":
                    content = to_html(self._result)
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(content)
                elif ext == "json":
                    content = to_json(self._result)
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(content)
                else:
                    content = to_csv(self._result)
                    with open(path, "w", encoding="utf-8", newline="") as fh:
                        fh.write(content)
                self._log_msg(f"Report {fmt} salvato: {path}")
                self._statusbar.showMessage(f"Report {fmt} salvato: {path}")
            except Exception as exc:
                msg = str(exc)
                self._log_msg(f"[ERRORE] Esportazione {fmt} fallita: {msg}")
                self._statusbar.showMessage(f"Errore export {fmt}: {msg}")
                QMessageBox.warning(self, f"Errore esportazione {fmt}", msg)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def launch_gui(initial_path: str = "") -> int:
    """Launch the GD LEX Inspector GUI. Returns the process exit code."""
    if not _PYSIDE6_AVAILABLE:
        print(
            "Errore: PySide6 non è installato.\n"
            "Per installare la dipendenza GUI:\n"
            "  pip install PySide6\n"
            "oppure:\n"
            "  pip install 'gdlex-inspector[gui]'",
            file=sys.stderr,
        )
        return 1

    app = QApplication.instance() or QApplication(sys.argv)

    # Show splash
    splash = _SplashScreen()
    splash.show()
    app.processEvents()

    # Build main window while splash is visible
    window = MainWindow(initial_path=initial_path)

    # Wait for splash animation to complete (50 ticks × 25ms = 1250ms)
    wait_loop = QEventLoop()
    QTimer.singleShot(1400, wait_loop.quit)
    wait_loop.exec()

    splash.finish(window)
    window.show()
    return app.exec()
