"""Tests for classify_path() in gdlex_inspector.categories."""

import unittest

from gdlex_inspector.categories import classify_path


class TestCategories(unittest.TestCase):

    def test_pst_file(self):
        self.assertEqual(classify_path("/home/user/backup/archive.pst"), "pst")

    def test_ost_file(self):
        self.assertEqual(classify_path("/home/user/.local/outlook.ost"), "ost")

    def test_pst_windows_path(self):
        self.assertEqual(classify_path(r"C:\Users\Utente\Documents\Outlook.pst"), "pst")

    def test_downloads_linux(self):
        self.assertEqual(classify_path("/home/user/downloads/file.zip"), "downloads")

    def test_downloads_italian(self):
        self.assertEqual(classify_path("/home/user/scaricati/file.zip"), "downloads")

    def test_browser_cache_chrome(self):
        self.assertEqual(
            classify_path("/home/user/.config/google/chrome/default/cache/data"),
            "browser_cache",
        )

    def test_browser_cache_firefox(self):
        self.assertEqual(
            classify_path("/home/user/.mozilla/firefox/profiles/cache"),
            "browser_cache",
        )

    def test_node_modules(self):
        self.assertEqual(classify_path("/home/user/myproject/node_modules/lodash"), "node_modules")

    def test_venv(self):
        self.assertEqual(classify_path("/home/user/myproject/.venv/lib/python3.11"), "venv")

    def test_venv_plain(self):
        self.assertEqual(classify_path("/home/user/myproject/venv/lib"), "venv")

    def test_other_fallback(self):
        self.assertEqual(classify_path("/home/user/documents/report.docx"), "other")

    def test_onedrive(self):
        self.assertIn(classify_path("/home/user/OneDrive/file.txt"), ("onedrive",))


if __name__ == "__main__":
    unittest.main()
