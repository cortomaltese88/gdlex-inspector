"""Tests for classify_risk() in gdlex_inspector.risk."""

import unittest

from gdlex_inspector.risk import (
    RISK_CRITICAL,
    RISK_HIGH,
    RISK_LOW,
    RISK_MEDIUM,
    RISK_NONE,
    classify_risk,
    risk_label_for_display,
    risk_style_for_display,
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

    def test_small_etc_file_is_displayed_as_system(self):
        path = "/etc/ssh/moduli"
        level, _ = classify_risk(path, "other")
        self.assertEqual(level, RISK_CRITICAL)
        self.assertEqual(
            risk_label_for_display(level, "other", path, 605 * 1024),
            "Sistema",
        )
        self.assertEqual(
            risk_style_for_display(level, "other", path, 605 * 1024),
            "system",
        )

    def test_non_system_critical_is_displayed_as_critical(self):
        path = "C:/Windows/System32/kernel32.dll"
        level, _ = classify_risk(path, "other")
        self.assertEqual(risk_label_for_display(level, "other", path, 1024), "Critica")

    def test_protected_path_is_system_even_if_technical_risk_is_none(self):
        path = "/usr/bin/example"
        level, _ = classify_risk(path, "other")
        self.assertEqual(level, RISK_NONE)
        self.assertEqual(risk_label_for_display(level, "other", path, 1024), "Sistema")
        self.assertEqual(risk_style_for_display(level, "other", path, 1024), "system")


if __name__ == "__main__":
    unittest.main()
