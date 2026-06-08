"""Tests for outlook_backup utilities."""

import unittest

from gdlex_inspector.outlook_backup import (
    build_candidate,
    classify_outlook_archive,
    is_outlook_archive,
    outlook_archive_warning,
)


class TestOutlookBackup(unittest.TestCase):

    def test_pst_is_outlook_archive(self):
        self.assertTrue(is_outlook_archive("/home/user/mail.pst"))

    def test_ost_is_outlook_archive(self):
        self.assertTrue(is_outlook_archive("/home/user/cache.ost"))

    def test_docx_not_outlook_archive(self):
        self.assertFalse(is_outlook_archive("/home/user/report.docx"))

    def test_classify_pst(self):
        self.assertEqual(classify_outlook_archive("/home/user/mail.pst"), "pst")

    def test_classify_ost(self):
        self.assertEqual(classify_outlook_archive("/home/user/cache.ost"), "ost")

    def test_classify_other(self):
        self.assertEqual(classify_outlook_archive("/home/user/file.txt"), "other")

    def test_pst_warning_contains_backup(self):
        w = outlook_archive_warning("pst")
        self.assertIn("backup", w.lower())

    def test_ost_warning_contains_cache(self):
        w = outlook_archive_warning("ost")
        self.assertIn("cache", w.lower())

    def test_build_candidate_pst(self):
        c = build_candidate("/home/user/archive.pst", 1024 * 1024 * 500)
        self.assertIsNotNone(c)
        self.assertEqual(c.kind, "pst")
        self.assertTrue(c.backup_eligible)

    def test_build_candidate_ost_not_backup_eligible(self):
        c = build_candidate("/home/user/outlook.ost", 2 * 1024 ** 3)
        self.assertIsNotNone(c)
        self.assertEqual(c.kind, "ost")
        self.assertFalse(c.backup_eligible)

    def test_build_candidate_non_outlook_returns_none(self):
        c = build_candidate("/home/user/file.txt", 1024)
        self.assertIsNone(c)


if __name__ == "__main__":
    unittest.main()
