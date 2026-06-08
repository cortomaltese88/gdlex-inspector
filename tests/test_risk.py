"""Tests for classify_risk() in gdlex_inspector.risk."""

import unittest

from gdlex_inspector.risk import (
    RISK_CRITICAL,
    RISK_HIGH,
    RISK_LOW,
    RISK_MEDIUM,
    RISK_NONE,
    classify_risk,
)


class TestRisk(unittest.TestCase):

    def test_ost_high_risk(self):
        level, msg = classify_risk("/home/user/mail.ost", "ost")
        self.assertEqual(level, RISK_HIGH)
        self.assertIn("OST", msg.upper())

    def test_pst_backup_recommended(self):
        level, msg = classify_risk("/home/user/archive.pst", "pst")
        self.assertEqual(level, RISK_HIGH)
        self.assertIn("backup", msg.lower())

    def test_system32_critical(self):
        level, msg = classify_risk("C:/Windows/System32/kernel32.dll", "other")
        self.assertEqual(level, RISK_CRITICAL)

    def test_winsxs_critical(self):
        level, msg = classify_risk("C:/Windows/WinSxS/x86_policy", "other")
        self.assertEqual(level, RISK_CRITICAL)

    def test_browser_cache_medium(self):
        level, msg = classify_risk("/home/user/.cache/chrome/data", "browser_cache")
        self.assertEqual(level, RISK_MEDIUM)

    def test_downloads_low(self):
        level, msg = classify_risk("/home/user/downloads/file.zip", "downloads")
        self.assertEqual(level, RISK_LOW)

    def test_other_no_risk(self):
        level, msg = classify_risk("/home/user/documents/report.txt", "other")
        self.assertEqual(level, RISK_NONE)

    def test_onedrive_medium(self):
        level, msg = classify_risk("/home/user/OneDrive/file.docx", "onedrive")
        self.assertEqual(level, RISK_MEDIUM)


if __name__ == "__main__":
    unittest.main()
