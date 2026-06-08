"""Tests for backend selection in gdlex_inspector.backend."""

import unittest
from unittest.mock import patch

from gdlex_inspector.backend import (
    BACKEND_DUF,
    BACKEND_DUST,
    BACKEND_GDU,
    BACKEND_PYTHON,
    choose_backend,
    is_external_backend_available,
    list_available_backends,
)


class TestBackend(unittest.TestCase):

    def test_python_always_available(self):
        self.assertTrue(is_external_backend_available(BACKEND_PYTHON))

    def test_external_available_when_on_path(self):
        with patch("shutil.which", return_value="/usr/bin/gdu"):
            self.assertTrue(is_external_backend_available(BACKEND_GDU))

    def test_external_unavailable_when_not_on_path(self):
        with patch("shutil.which", return_value=None):
            self.assertFalse(is_external_backend_available(BACKEND_DUST))

    def test_choose_backend_defaults_to_python(self):
        self.assertEqual(choose_backend(), BACKEND_PYTHON)

    def test_choose_backend_python_explicit(self):
        self.assertEqual(choose_backend(BACKEND_PYTHON), BACKEND_PYTHON)

    def test_choose_backend_external_when_available(self):
        with patch("shutil.which", return_value="/usr/bin/gdu"):
            result = choose_backend(BACKEND_GDU)
        self.assertEqual(result, BACKEND_GDU)

    def test_choose_backend_falls_back_when_external_missing(self):
        with patch("shutil.which", return_value=None):
            result = choose_backend(BACKEND_DUST)
        self.assertEqual(result, BACKEND_PYTHON)

    def test_list_available_backends_always_includes_python(self):
        with patch("shutil.which", return_value=None):
            available = list_available_backends()
        self.assertIn(BACKEND_PYTHON, available)

    def test_list_available_backends_includes_external_when_present(self):
        with patch("shutil.which", return_value="/usr/bin/gdu"):
            available = list_available_backends()
        self.assertIn(BACKEND_GDU, available)


if __name__ == "__main__":
    unittest.main()
