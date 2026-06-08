"""Tests for platform_info utilities."""

import unittest
from unittest.mock import patch

from gdlex_inspector import platform_info


class TestPlatformInfo(unittest.TestCase):

    def test_get_hostname_returns_string(self):
        h = platform_info.get_hostname()
        self.assertIsInstance(h, str)
        self.assertTrue(len(h) > 0)

    def test_get_username_returns_string(self):
        u = platform_info.get_username()
        self.assertIsInstance(u, str)

    def test_get_platform_summary_keys(self):
        info = platform_info.get_platform_summary()
        for key in ("system", "hostname", "platform_kind", "python_version"):
            self.assertIn(key, info)

    def test_is_wsl_false_when_proc_version_empty(self):
        with patch.object(platform_info, "_read_proc_version", return_value=""):
            self.assertFalse(platform_info.is_wsl())

    def test_is_wsl_true_when_microsoft_in_proc(self):
        with patch.object(platform_info, "_read_proc_version",
                          return_value="linux version 5.15.0-microsoft-standard"):
            self.assertTrue(platform_info.is_wsl())

    def test_is_wsl_true_when_wsl_in_proc(self):
        with patch.object(platform_info, "_read_proc_version",
                          return_value="linux version 5.15.0-wsl2"):
            self.assertTrue(platform_info.is_wsl())

    def test_platform_kind_wsl(self):
        with patch.object(platform_info, "is_windows", return_value=False), \
             patch.object(platform_info, "is_linux", return_value=True), \
             patch.object(platform_info, "is_wsl", return_value=True):
            self.assertEqual(platform_info.get_platform_kind(), "wsl")

    def test_platform_kind_linux(self):
        with patch.object(platform_info, "is_windows", return_value=False), \
             patch.object(platform_info, "is_linux", return_value=True), \
             patch.object(platform_info, "is_wsl", return_value=False):
            self.assertEqual(platform_info.get_platform_kind(), "linux")


if __name__ == "__main__":
    unittest.main()
