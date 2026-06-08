"""Tests for dynamic scan profiles and their CLI integration."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

from gdlex_inspector.scan_profiles import (
    ScanProfile,
    get_default_profiles,
    get_profile,
)
from gdlex_inspector.system_profile import MountInfo, SystemProfile


def _system_profile(*mounts, is_wsl=False):
    return SystemProfile(
        os_family="linux",
        platform="Linux-test",
        is_wsl=is_wsl,
        desktop_environment=None,
        hostname="test",
        mounts=list(mounts),
    )


def _mount(path, role, fs_type="ext4"):
    return MountInfo(
        mount_point=path,
        device="test",
        fs_type=fs_type,
        options=["rw"],
        role=role,
        is_read_only=False,
        is_remote=role in {"cloud_fuse", "network"},
        is_virtual=False,
    )


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "gdlex_inspector", *args],
        capture_output=True,
        text=True,
    )


class TestScanProfiles(unittest.TestCase):

    def test_base_profiles_are_available(self):
        ids = {profile.id for profile in get_default_profiles(_system_profile())}
        self.assertTrue({
            "quick-home",
            "standard-home",
            "deep-home",
            "system-safe",
            "dev-cleanup",
        }.issubset(ids))

    def test_to_dict_is_json_serializable(self):
        profile = get_profile("quick-home", _system_profile())
        data = profile.to_dict()
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_quick_home_uses_home_and_prudent_depth(self):
        profile = get_profile("quick-home", _system_profile())
        self.assertEqual(profile.target_path, os.path.expanduser("~"))
        self.assertEqual(profile.max_depth, 3)

    def test_system_safe_excludes_virtual_filesystems(self):
        profile = get_profile("system-safe", _system_profile())
        self.assertTrue({"/proc", "/sys", "/dev"}.issubset(profile.excludes))

    def test_windows_profile_is_dynamic(self):
        system = _system_profile(_mount("/mnt/c", "windows_mount", "ntfs3"))
        profile = get_profile("windows-mount-safe", system)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.target_path, "/mnt/c")
        self.assertIn("*/Windows/System32", profile.excludes)

    def test_cloud_fuse_profile_is_dynamic(self):
        system = _system_profile(
            _mount("/home/test/cloud", "cloud_fuse", "fuse.rclone")
        )
        profile = get_profile("cloud-fuse-safe", system)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.target_path, "/home/test/cloud")

    def test_get_existing_profile(self):
        self.assertIsNotNone(get_profile("quick-home", _system_profile()))

    def test_get_missing_profile(self):
        self.assertIsNone(get_profile("missing", _system_profile()))

    def test_cli_profiles_json(self):
        result = _run("profiles", "--json")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("quick-home", {profile["id"] for profile in data})

    def test_cli_profiles_readable(self):
        result = _run("profiles")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Profili di scansione disponibili:", result.stdout)
        self.assertIn("quick-home", result.stdout)

    def test_cli_scan_profile_with_path_override(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "file.txt"), "w") as handle:
                handle.write("test")
            result = _run("scan", "--profile", "quick-home", tmpdir)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Profile:  quick-home", result.stdout)

    def test_cli_explicit_options_override_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ("keep.txt", "skip.log"):
                with open(os.path.join(tmpdir, name), "w") as handle:
                    handle.write("test")
            result = _run(
                "scan",
                "--profile", "quick-home",
                "--top", "1",
                "--min-size", "0",
                "--max-depth", "1",
                "--exclude", "*.log",
                tmpdir,
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Top 1 files by size:", result.stdout)
        self.assertNotIn("skip.log", result.stdout)

    def test_scan_profile_dataclass_can_be_constructed(self):
        profile = ScanProfile(
            id="test",
            label="Test",
            description="Test profile",
            target_path="$HOME",
            max_depth=None,
            top=10,
            min_size=0,
            excludes=[],
            follow_symlinks=False,
            estimated_speed="Veloce",
            caution=None,
            recommended_for_roles=[],
        )
        self.assertEqual(profile.to_dict()["id"], "test")


if __name__ == "__main__":
    unittest.main()
