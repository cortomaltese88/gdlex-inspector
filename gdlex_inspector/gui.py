"""PySide6 GUI for GD LEX Inspector — Matrix dark theme. Experimental.

Launch with: python3 -m gdlex_inspector gui
Requires PySide6: pip install PySide6
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

from . import gui_theme

try:
    from PySide6.QtCore import Qt, QSettings, QThread, Signal
    from PySide6.QtGui import QAction, QColor, QIcon
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QApplication,
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPushButton,
        QSpinBox,
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


if _PYSIDE6_AVAILABLE:

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

    class MainWindow(QMainWindow):
        def __init__(self, initial_path: str = "") -> None:
            super().__init__()
            self._result = None
            self._worker: ScanWorker | None = None
            self._setup_ui(initial_path)

        # ------------------------------------------------------------------
        # UI construction
        # ------------------------------------------------------------------

        def _setup_ui(self, initial_path: str) -> None:
            self.setWindowTitle("GD LEX Inspector")
            self.resize(1100, 750)
            self.setMinimumSize(800, 550)
            self.setStyleSheet(gui_theme.STYLESHEET)

            svg_path = os.path.join(os.path.dirname(__file__), "assets", "gdlex-inspector.svg")
            if os.path.isfile(svg_path):
                self.setWindowIcon(QIcon(svg_path))

            central = QWidget()
            self.setCentralWidget(central)
            root_layout = QVBoxLayout(central)
            root_layout.setSpacing(8)
            root_layout.setContentsMargins(10, 10, 10, 10)

            root_layout.addWidget(self._build_path_group(initial_path))
            root_layout.addWidget(self._build_options_group())
            root_layout.addWidget(self._build_splitter(), 1)
            root_layout.addLayout(self._build_export_bar())

            self._statusbar = self.statusBar()
            self._statusbar.showMessage("Pronto.")

            self._connect_signals()
            self._load_settings(initial_path)

        def _build_path_group(self, initial_path: str) -> QGroupBox:
            group = QGroupBox("Percorso da analizzare")
            layout = QHBoxLayout(group)
            self._path_edit = QLineEdit(initial_path)
            self._path_edit.setPlaceholderText("Seleziona o inserisci il percorso...")
            browse_btn = QPushButton("Sfoglia")
            browse_btn.clicked.connect(self._browse_path)
            layout.addWidget(QLabel("Percorso:"))
            layout.addWidget(self._path_edit, 1)
            layout.addWidget(browse_btn)
            return group

        def _build_options_group(self) -> QGroupBox:
            group = QGroupBox("Opzioni scansione")
            layout = QHBoxLayout(group)
            layout.setSpacing(10)

            layout.addWidget(QLabel("Top N:"))
            self._top_spin = QSpinBox()
            self._top_spin.setRange(1, 500)
            self._top_spin.setValue(10)
            self._top_spin.setFixedWidth(70)
            layout.addWidget(self._top_spin)

            layout.addSpacing(8)
            layout.addWidget(QLabel("Min size:"))
            self._min_size_edit = QLineEdit()
            self._min_size_edit.setPlaceholderText("es. 100M")
            self._min_size_edit.setFixedWidth(90)
            layout.addWidget(self._min_size_edit)

            layout.addSpacing(8)
            layout.addWidget(QLabel("Max depth (0=illimitato):"))
            self._depth_spin = QSpinBox()
            self._depth_spin.setRange(0, 99)
            self._depth_spin.setValue(0)
            self._depth_spin.setFixedWidth(70)
            layout.addWidget(self._depth_spin)

            layout.addStretch()
            self._scan_btn = QPushButton("Scansiona")
            self._scan_btn.setDefault(True)
            self._scan_btn.clicked.connect(self._start_scan)
            layout.addWidget(self._scan_btn)
            return group

        def _build_splitter(self) -> QSplitter:
            splitter = QSplitter(Qt.Orientation.Vertical)

            self._log = QTextEdit()
            self._log.setReadOnly(True)
            self._log.setMaximumHeight(140)
            self._log.setMinimumHeight(60)
            splitter.addWidget(self._log)

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

            self._tab_widget.addTab(self._files_table, "Top file")
            self._tab_widget.addTab(self._dirs_table, "Top cartelle")
            self._tab_widget.addTab(self._cats_table, "Categorie")
            splitter.addWidget(self._tab_widget)

            splitter.setStretchFactor(0, 0)
            splitter.setStretchFactor(1, 1)
            return splitter

        def _build_export_bar(self) -> QHBoxLayout:
            bar = QHBoxLayout()
            self._html_btn = QPushButton("Esporta HTML")
            self._json_btn = QPushButton("Esporta JSON")
            self._csv_btn = QPushButton("Esporta CSV")
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
            hh = table.horizontalHeader()
            hh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            hh.setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)
            hh.setStretchLastSection(False)
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

        # ------------------------------------------------------------------
        # Settings persistence
        # ------------------------------------------------------------------

        def _load_settings(self, initial_path: str) -> None:
            s = QSettings(_SETTINGS_ORG, _SETTINGS_APP)
            path = initial_path or s.value("last_path", "")
            self._path_edit.setText(path)
            try:
                self._top_spin.setValue(int(s.value("top_n", 10)))
            except (TypeError, ValueError):
                pass
            self._min_size_edit.setText(s.value("min_size", "") or "")
            try:
                self._depth_spin.setValue(int(s.value("max_depth", 0)))
            except (TypeError, ValueError):
                pass

        def _save_settings(self) -> None:
            s = QSettings(_SETTINGS_ORG, _SETTINGS_APP)
            s.setValue("last_path", self._path_edit.text().strip())
            s.setValue("top_n", self._top_spin.value())
            s.setValue("min_size", self._min_size_edit.text().strip())
            s.setValue("max_depth", self._depth_spin.value())

        def closeEvent(self, event) -> None:
            self._save_settings()
            super().closeEvent(event)

        # ------------------------------------------------------------------
        # Scan logic
        # ------------------------------------------------------------------

        def _browse_path(self) -> None:
            start = self._path_edit.text().strip() or os.path.expanduser("~")
            path = QFileDialog.getExistingDirectory(self, "Seleziona cartella", start)
            if path:
                self._path_edit.setText(path)

        def _log_msg(self, msg: str) -> None:
            self._log.append(msg)
            sb = self._log.verticalScrollBar()
            sb.setValue(sb.maximum())

        def _set_scan_running(self, running: bool) -> None:
            self._scan_btn.setEnabled(not running)
            for btn in (self._html_btn, self._json_btn, self._csv_btn, self._open_btn):
                btn.setEnabled(False)
            if running:
                self._statusbar.showMessage("Scansione in corso...")
                self._files_table.setRowCount(0)
                self._dirs_table.setRowCount(0)
                self._cats_table.setRowCount(0)

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
            self._statusbar.showMessage(summary)
            self._scan_btn.setEnabled(True)
            for btn in (self._html_btn, self._json_btn, self._csv_btn):
                btn.setEnabled(True)
            self._update_open_btn()

        def _on_scan_error(self, msg: str) -> None:
            self._log_msg(f"[ERRORE] {msg}")
            self._statusbar.showMessage(f"Errore durante la scansione: {msg}")
            self._scan_btn.setEnabled(True)
            self._result = None

        # ------------------------------------------------------------------
        # Table population
        # ------------------------------------------------------------------

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
            color_hex = gui_theme.RISK_COLORS.get(risk_value, gui_theme.FG_NORMAL)
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                if col == risk_col:
                    item.setForeground(QColor(color_hex))
                table.setItem(row, col, item)

        # ------------------------------------------------------------------
        # Context menu
        # ------------------------------------------------------------------

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
            copy_action = QAction("Copia percorso", self)
            open_action.triggered.connect(lambda: self._open_path_in_fm(path, is_file=is_file))
            copy_action.triggered.connect(lambda: QApplication.clipboard().setText(path))
            menu.addAction(open_action)
            menu.addAction(copy_action)
            menu.exec(table.viewport().mapToGlobal(pos))

        # ------------------------------------------------------------------
        # Open path
        # ------------------------------------------------------------------

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

        # ------------------------------------------------------------------
        # Export
        # ------------------------------------------------------------------

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
    window = MainWindow(initial_path=initial_path)
    window.show()
    return app.exec()
