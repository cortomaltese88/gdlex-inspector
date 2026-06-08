"""Tests for open_path utilities."""

import unittest

from gdlex_inspector.open_path import (
    build_open_command,
    is_wsl_windows_path,
    wsl_to_windows_path,
)


class TestOpenPath(unittest.TestCase):

    def test_is_wsl_windows_path_true(self):
        self.assertTrue(is_wsl_windows_path("/mnt/c/Users/Utente"))

    def test_is_wsl_windows_path_false_regular(self):
        self.assertFalse(is_wsl_windows_path("/home/user/docs"))

    def test_is_wsl_windows_path_false_no_drive(self):
        self.assertFalse(is_wsl_windows_path("/mnt/"))

    def test_wsl_to_windows_path_file(self):
        result = wsl_to_windows_path("/mnt/c/Users/Utente/file.txt")
        self.assertEqual(result, r"C:\Users\Utente\file.txt")

    def test_wsl_to_windows_path_drive_d(self):
        result = wsl_to_windows_path("/mnt/d/Projects")
        self.assertEqual(result, r"D:\Projects")

    def test_wsl_to_windows_path_root(self):
        result = wsl_to_windows_path("/mnt/c")
        self.assertEqual(result, "C:")

    def test_wsl_to_windows_path_invalid(self):
        with self.assertRaises(ValueError):
            wsl_to_windows_path("/home/user/file.txt")

    def test_build_open_command_linux_dir(self):
        cmd = build_open_command("/home/user/docs", is_file=False, platform_kind="linux")
        self.assertEqual(cmd, ["xdg-open", "/home/user/docs"])

    def test_build_open_command_linux_file(self):
        cmd = build_open_command("/home/user/file.txt", is_file=True, platform_kind="linux")
        self.assertEqual(cmd, ["xdg-open", "/home/user/file.txt"])

    def test_build_open_command_windows_file(self):
        cmd = build_open_command(r"C:\Users\file.txt", is_file=True, platform_kind="windows")
        self.assertIn("explorer.exe", cmd[0])
        self.assertTrue(any("/select," in arg for arg in cmd))

    def test_build_open_command_wsl_windows_path_file(self):
        cmd = build_open_command("/mnt/c/Users/Utente/file.txt", is_file=True, platform_kind="wsl")
        self.assertIn("explorer.exe", cmd[0])
        self.assertTrue(any("/select," in arg for arg in cmd))

    def test_build_open_command_wsl_linux_path(self):
        cmd = build_open_command("/home/user/docs", is_file=False, platform_kind="wsl")
        self.assertEqual(cmd, ["xdg-open", "/home/user/docs"])


if __name__ == "__main__":
    unittest.main()
