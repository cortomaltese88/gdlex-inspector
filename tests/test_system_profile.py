"""Tests for operating system and mount detection."""

import json
from collections import namedtuple
import subprocess
import sys
import unittest

from gdlex_inspector.system_profile import (
    MountInfo,
    SystemProfile,
    classify_fs_type,
    classify_mount_role,
    build_scan_scope_warning,
    detect_os_family,
    detect_wsl,
    find_mount_for_path,
    get_volume_usage,
    parse_mountinfo,
    parse_proc_mounts,
)


class TestSystemProfile(unittest.TestCase):

    def test_parse_mountinfo_cifs_source_and_share_details(self):
        mounts = parse_mountinfo(
            "42 31 0:55 / /home/marco/mnt/pc-marco-users "
            "rw,relatime shared:12 - cifs //192.168.178.25/Users "
            "rw,vers=3.1.1,cache=strict\n"
        )
        self.assertEqual(len(mounts), 1)
        mount = mounts[0]
        self.assertEqual(mount.mount_point, "/home/marco/mnt/pc-marco-users")
        self.assertEqual(mount.device, "//192.168.178.25/Users")
        self.assertEqual(mount.fs_type, "cifs")
        self.assertEqual(mount.remote_host, "192.168.178.25")
        self.assertEqual(mount.share_name, "Users")
        self.assertTrue(mount.is_remote)

    def test_find_mount_for_path_uses_most_specific_mount(self):
        mounts = parse_mountinfo(
            "20 1 8:1 / / rw - ext4 /dev/sda1 rw\n"
            "21 20 0:55 / /home/marco/mnt rw - cifs //server/Users rw\n"
            "22 21 0:56 / /home/marco/mnt/archive rw - cifs //server/Archive rw\n"
        )
        mount = find_mount_for_path(
            "/home/marco/mnt/archive/cases/2026",
            mounts=mounts,
        )
        self.assertIsNotNone(mount)
        self.assertEqual(mount.device, "//server/Archive")

    def test_volume_usage_calculates_percentage(self):
        Usage = namedtuple("Usage", "total used free")
        usage = get_volume_usage(
            "/remote/path",
            disk_usage=lambda path: Usage(1000, 920, 80),
        )
        self.assertEqual(usage["total_bytes"], 1000)
        self.assertEqual(usage["used_bytes"], 920)
        self.assertEqual(usage["free_bytes"], 80)
        self.assertEqual(usage["percent_used"], 92.0)

    def test_scan_scope_warning_for_small_cifs_scope(self):
        mount = parse_proc_mounts(
            "//server/Users /mnt/users cifs rw 0 0\n"
        )[0]
        warning = build_scan_scope_warning(
            mount,
            {"used_bytes": 219 * 1024**3, "percent_used": 92.0},
            scanned_total=4.5 * 1024**3,
        )
        self.assertIsNotNone(warning)
        self.assertIn("partial share", warning)
        self.assertIn("219.0 GiB", warning)
        self.assertIn("4.5 GiB", warning)

    def test_no_scan_scope_warning_for_local_filesystem(self):
        mount = parse_proc_mounts("/dev/sda2 / ext4 rw 0 0\n")[0]
        warning = build_scan_scope_warning(
            mount,
            {"used_bytes": 900, "percent_used": 90.0},
            scanned_total=10,
        )
        self.assertIsNone(warning)

    def test_no_scan_scope_warning_when_scanned_total_is_coherent(self):
        mount = parse_proc_mounts(
            "//server/Users /mnt/users smb3 rw 0 0\n"
        )[0]
        warning = build_scan_scope_warning(
            mount,
            {"used_bytes": 1000, "percent_used": 90.0},
            scanned_total=250,
        )
        self.assertIsNone(warning)

    def test_detect_os_family_returns_supported_value(self):
        self.assertIn(
            detect_os_family(),
            {"linux", "windows", "macos", "unknown"},
        )

    def test_parse_ext4_root(self):
        mount = parse_proc_mounts("/dev/sda2 / ext4 rw,relatime 0 0\n")[0]
        self.assertEqual(mount.mount_point, "/")
        self.assertEqual(mount.role, "system")
        self.assertFalse(mount.is_read_only)
        self.assertEqual(classify_fs_type(mount.fs_type), "local_linux")

    def test_parse_ntfs_windows_mount(self):
        mount = parse_proc_mounts(
            "/dev/sda3 /mnt/windows ntfs3 ro,relatime 0 0\n"
        )[0]
        self.assertEqual(mount.role, "windows_mount")
        self.assertTrue(mount.is_read_only)

    def test_parse_cloud_fuse_mount_and_escaped_space(self):
        mount = parse_proc_mounts(
            "ExpanDrive /home/marco/ExpanDrive/Google\\040Drive "
            "fuse.exfs rw,nosuid 0 0\n"
        )[0]
        self.assertEqual(
            mount.mount_point,
            "/home/marco/ExpanDrive/Google Drive",
        )
        self.assertEqual(mount.role, "cloud_fuse")
        self.assertTrue(mount.is_remote)

    def test_parse_network_mounts(self):
        mounts = parse_proc_mounts(
            "//server/share /srv/share cifs rw 0 0\n"
            "server:/data /srv/data nfs4 rw 0 0\n"
            "sshfs#host:/data /srv/ssh fuse.sshfs rw 0 0\n"
        )
        self.assertEqual(
            [mount.role for mount in mounts],
            ["network", "network", "network"],
        )
        self.assertTrue(all(mount.is_remote for mount in mounts))

    def test_parse_tmpfs_mount(self):
        mount = parse_proc_mounts("tmpfs /run tmpfs rw,nosuid 0 0\n")[0]
        self.assertEqual(mount.role, "temporary")
        self.assertTrue(mount.is_virtual)

    def test_classify_home_mount(self):
        self.assertEqual(
            classify_mount_role("/home/marco", "/dev/sda2", "ext4", ["rw"]),
            "home",
        )

    def test_classify_boot_mount(self):
        self.assertEqual(
            classify_mount_role("/boot", "/dev/sda1", "ext4", ["rw"]),
            "system",
        )

    def test_detect_wsl_with_simulated_inputs(self):
        self.assertTrue(detect_wsl(
            proc_version="Linux version 5.15.0-microsoft-standard",
            environ={},
            os_family="linux",
        ))
        self.assertTrue(detect_wsl(
            proc_version="Linux version 6.8.0",
            environ={"WSL_DISTRO_NAME": "Ubuntu"},
            os_family="linux",
        ))
        self.assertFalse(detect_wsl(
            proc_version="Linux version 6.8.0",
            environ={},
            os_family="linux",
        ))
        self.assertFalse(detect_wsl(
            proc_version="microsoft",
            environ={"WSL_INTEROP": "/run/WSL/1_interop"},
            os_family="windows",
        ))

    def test_profile_to_dict_is_json_serializable(self):
        profile = SystemProfile(
            os_family="linux",
            platform="Linux-test",
            is_wsl=False,
            desktop_environment="KDE",
            hostname="test-host",
            mounts=[MountInfo(
                mount_point="/",
                device="/dev/sda2",
                fs_type="ext4",
                options=["rw"],
                role="system",
                is_read_only=False,
                is_remote=False,
                is_virtual=False,
            )],
        )
        data = profile.to_dict()
        self.assertEqual(json.loads(json.dumps(data)), data)
        self.assertEqual(data["mounts"][0]["role"], "system")
        self.assertIn("source", data["mounts"][0])

    def test_cli_system_info_json(self):
        result = subprocess.run(
            [sys.executable, "-m", "gdlex_inspector", "system-info", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("os_family", data)
        self.assertIn("mounts", data)

    def test_cli_system_info_readable(self):
        result = subprocess.run(
            [sys.executable, "-m", "gdlex_inspector", "system-info"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("GD LEX Inspector", result.stdout)
        self.assertIn("Mount rilevati:", result.stdout)


if __name__ == "__main__":
    unittest.main()
