"""Tests for the local Debian packaging definition."""

import os
import stat
import tomllib
import unittest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "build_deb.sh")
CONTROL_TEMPLATE = os.path.join(PROJECT_ROOT, "packaging", "debian", "control.in")
LAUNCHER = os.path.join(PROJECT_ROOT, "packaging", "debian", "gdlex-inspector")
DESKTOP_FILE = os.path.join(
    PROJECT_ROOT, "packaging", "linux", "gdlex-inspector.desktop"
)
ICON_FILE = os.path.join(
    PROJECT_ROOT, "gdlex_inspector", "assets", "gdlex-inspector.svg"
)
PYPROJECT = os.path.join(PROJECT_ROOT, "pyproject.toml")


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class TestDebianPackaging(unittest.TestCase):

    def test_build_script_exists_and_is_executable(self):
        self.assertTrue(os.path.isfile(BUILD_SCRIPT))
        self.assertTrue(os.stat(BUILD_SCRIPT).st_mode & stat.S_IXUSR)

    def test_build_script_is_strict_and_has_no_local_home_path(self):
        content = _read(BUILD_SCRIPT)
        self.assertIn("set -euo pipefail", content)
        self.assertNotIn("/home/marco", content)

    def test_build_script_uses_project_version(self):
        content = _read(BUILD_SCRIPT)
        self.assertIn("pyproject.toml", content)
        self.assertIn('["project"]["version"]', content)

    def test_build_script_installs_required_assets(self):
        content = _read(BUILD_SCRIPT)
        for path in (
            "/usr/bin/gdlex-inspector",
            "/usr/share/applications/gdlex-inspector.desktop",
            "/usr/share/icons/hicolor/scalable/apps/gdlex-inspector.svg",
        ):
            self.assertIn(path, content)

    def test_build_script_normalizes_payload_permissions(self):
        content = _read(BUILD_SCRIPT)
        self.assertIn("-type d -exec chmod 0755", content)
        self.assertIn("-type f -exec chmod 0644", content)

    def test_control_template_metadata(self):
        content = _read(CONTROL_TEMPLATE)
        self.assertIn("Package: gdlex-inspector", content)
        self.assertIn("Version: @VERSION@", content)
        self.assertIn("Architecture: all", content)
        self.assertIn("Depends: python3 (>= 3.10), python3-pyside6", content)

    def test_project_version_is_valid_for_template(self):
        with open(PYPROJECT, "rb") as handle:
            version = tomllib.load(handle)["project"]["version"]
        self.assertRegex(version, r"^[0-9][0-9A-Za-z.+:~-]*$")

    def test_launcher_uses_system_python_and_installed_code(self):
        content = _read(LAUNCHER)
        self.assertTrue(content.startswith("#!/usr/bin/python3"))
        self.assertIn("/usr/lib/gdlex-inspector", content)
        self.assertIn("gdlex_inspector.cli import main", content)

    def test_desktop_entry_and_icon_match_package(self):
        desktop = _read(DESKTOP_FILE)
        self.assertIn("Exec=gdlex-inspector gui", desktop)
        self.assertIn("Icon=gdlex-inspector", desktop)
        self.assertTrue(os.path.isfile(ICON_FILE))


if __name__ == "__main__":
    unittest.main()
