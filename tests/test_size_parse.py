"""Tests for parse_size() in gdlex_inspector.scanner."""

import unittest

from gdlex_inspector.scanner import parse_size


class TestSizeParse(unittest.TestCase):

    def test_kilobytes(self):
        self.assertEqual(parse_size("100K"), 100 * 1024)

    def test_megabytes(self):
        self.assertEqual(parse_size("100M"), 100 * 1024 ** 2)

    def test_gigabytes(self):
        self.assertEqual(parse_size("1G"), 1024 ** 3)

    def test_terabytes(self):
        self.assertEqual(parse_size("2T"), 2 * 1024 ** 4)

    def test_bytes_no_suffix(self):
        self.assertEqual(parse_size("4096"), 4096)

    def test_bytes_zero(self):
        self.assertEqual(parse_size("0"), 0)

    def test_lowercase_suffix(self):
        self.assertEqual(parse_size("50m"), 50 * 1024 ** 2)

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            parse_size("abc")

    def test_invalid_suffix(self):
        with self.assertRaises(ValueError):
            parse_size("100X")

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            parse_size("")


if __name__ == "__main__":
    unittest.main()
