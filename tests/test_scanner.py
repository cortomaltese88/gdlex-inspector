"""Tests for recursive directory size computation in scan_directory()."""

import os
import shutil
import tempfile
import unittest

from gdlex_inspector.scanner import scan_directory


class TestRecursiveDirSizes(unittest.TestCase):
    """scan_directory() must accumulate sizes recursively across the subtree."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Structure:
        # tmpdir/
        #   file_a.txt   100 bytes
        #   subdir/
        #     file_b.txt 200 bytes
        #     deep/
        #       file_c.txt 300 bytes
        self._write(self.tmpdir, "file_a.txt", 100)
        subdir = os.path.join(self.tmpdir, "subdir")
        os.makedirs(subdir)
        self._write(subdir, "file_b.txt", 200)
        deep = os.path.join(subdir, "deep")
        os.makedirs(deep)
        self._write(deep, "file_c.txt", 300)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write(self, directory, name, size):
        with open(os.path.join(directory, name), "wb") as f:
            f.write(b"x" * size)

    def _sizes(self, result):
        return {e.path: e.size for e in result.top_dirs}

    def test_root_includes_full_subtree(self):
        result = scan_directory(self.tmpdir, top_n=10)
        self.assertEqual(self._sizes(result)[self.tmpdir], 600)

    def test_subdir_includes_deeper_files(self):
        result = scan_directory(self.tmpdir, top_n=10)
        subdir = os.path.join(self.tmpdir, "subdir")
        self.assertEqual(self._sizes(result)[subdir], 500)

    def test_leaf_dir_has_own_size(self):
        result = scan_directory(self.tmpdir, top_n=10)
        deep = os.path.join(self.tmpdir, "subdir", "deep")
        self.assertEqual(self._sizes(result)[deep], 300)

    def test_top_dirs_sorted_largest_first(self):
        result = scan_directory(self.tmpdir, top_n=10)
        sizes = [e.size for e in result.top_dirs]
        self.assertEqual(sizes, sorted(sizes, reverse=True))

    def test_exclude_removes_subtree_from_parent(self):
        result = scan_directory(
            self.tmpdir, top_n=10, exclude_patterns=["subdir"]
        )
        sizes = self._sizes(result)
        self.assertEqual(sizes[self.tmpdir], 100)
        self.assertNotIn(os.path.join(self.tmpdir, "subdir"), sizes)

    def test_max_depth_limits_walk(self):
        # max_depth=1: depth-1 dirs are pruned, only root files are counted
        result = scan_directory(self.tmpdir, top_n=10, max_depth=1)
        sizes = self._sizes(result)
        self.assertEqual(sizes[self.tmpdir], 100)
        self.assertNotIn(os.path.join(self.tmpdir, "subdir"), sizes)


if __name__ == "__main__":
    unittest.main()
