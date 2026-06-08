"""Tests for Linux/KDE desktop integration files."""

import os
import stat
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DESKTOP_FILE = os.path.join(PROJECT_ROOT, "packaging", "linux", "gdlex-inspector.desktop")
ICON_FILE = os.path.join(PROJECT_ROOT, "gdlex_inspector", "assets", "gdlex-inspector.svg")
INSTALL_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "install_desktop_entry.sh")
UNINSTALL_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "uninstall_desktop_entry.sh")
PYPROJECT = os.path.join(PROJECT_ROOT, "pyproject.toml")


class TestDesktopFile(unittest.TestCase):

    def test_desktop_file_exists(self):
        self.assertTrue(os.path.isfile(DESKTOP_FILE), f"Missing: {DESKTOP_FILE}")

    def test_desktop_file_required_fields(self):
        with open(DESKTOP_FILE) as f:
            content = f.read()
        for field in ("[Desktop Entry]", "Name=", "Exec=", "Icon=", "Type=Application"):
            self.assertIn(field, content, f"Missing field: {field}")

    def test_desktop_file_exec_uses_entry_point(self):
        with open(DESKTOP_FILE) as f:
            content = f.read()
        self.assertIn("Exec=gdlex-inspector gui", content)

    def test_desktop_file_icon_name(self):
        with open(DESKTOP_FILE) as f:
            content = f.read()
        self.assertIn("Icon=gdlex-inspector", content)

    def test_desktop_file_not_terminal(self):
        with open(DESKTOP_FILE) as f:
            content = f.read()
        self.assertIn("Terminal=false", content)

    def test_desktop_file_categories(self):
        with open(DESKTOP_FILE) as f:
            content = f.read()
        self.assertIn("Categories=", content)


class TestIconFile(unittest.TestCase):

    def test_icon_file_exists(self):
        self.assertTrue(os.path.isfile(ICON_FILE), f"Missing: {ICON_FILE}")

    def test_icon_file_is_svg(self):
        with open(ICON_FILE) as f:
            content = f.read(1024)
        self.assertIn("<svg", content)


class TestInstallScript(unittest.TestCase):

    def test_install_script_exists(self):
        self.assertTrue(os.path.isfile(INSTALL_SCRIPT), f"Missing: {INSTALL_SCRIPT}")

    def test_install_script_is_executable(self):
        mode = os.stat(INSTALL_SCRIPT).st_mode
        self.assertTrue(mode & stat.S_IXUSR, "install_desktop_entry.sh not executable")

    def test_install_script_has_set_euo(self):
        with open(INSTALL_SCRIPT) as f:
            content = f.read()
        self.assertIn("set -euo pipefail", content)

    def test_uninstall_script_exists(self):
        self.assertTrue(os.path.isfile(UNINSTALL_SCRIPT), f"Missing: {UNINSTALL_SCRIPT}")

    def test_uninstall_script_is_executable(self):
        mode = os.stat(UNINSTALL_SCRIPT).st_mode
        self.assertTrue(mode & stat.S_IXUSR, "uninstall_desktop_entry.sh not executable")


class TestPyprojectEntryPoint(unittest.TestCase):

    def test_entry_point_defined(self):
        with open(PYPROJECT) as f:
            content = f.read()
        self.assertIn("gdlex-inspector", content)
        self.assertIn("gdlex_inspector.cli:main", content)


if __name__ == "__main__":
    unittest.main()
