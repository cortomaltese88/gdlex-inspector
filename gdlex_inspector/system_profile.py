"""Read-only operating system and filesystem detection."""

from __future__ import annotations

from dataclasses import dataclass
import os
import platform as platform_module
import socket
from typing import Mapping


_LOCAL_LINUX_FS = {
    "btrfs", "ext2", "ext3", "ext4", "f2fs", "jfs", "reiserfs", "xfs", "zfs",
}
_WINDOWS_FS = {"ntfs", "ntfs3"}
_REMOVABLE_FS = {"exfat", "iso9660", "udf", "vfat"}
_NETWORK_FS = {"cifs", "nfs", "nfs4", "smb3", "sshfs"}
_TEMPORARY_FS = {"devtmpfs", "tmpfs"}
_VIRTUAL_FS = {
    "autofs", "cgroup", "cgroup2", "debugfs", "devpts", "efivarfs",
    "fusectl", "hugetlbfs", "mqueue", "overlay", "proc", "pstore",
    "securityfs", "squashfs", "sysfs", "tracefs",
}
_SYSTEM_MOUNTS = {
    "/", "/bin", "/boot", "/etc", "/lib", "/lib64", "/opt", "/sbin",
    "/usr", "/var", "/var/lib",
}
_CLOUD_MARKERS = (
    "expandrive", "onedrive", "sharepoint", "google drive", "googledrive",
    "dropbox", "rclone",
)


@dataclass
class MountInfo:
    mount_point: str
    device: str
    fs_type: str
    options: list[str]
    role: str
    is_read_only: bool
    is_remote: bool
    is_virtual: bool
    note: str | None = None

    def to_dict(self) -> dict:
        return {
            "mount_point": self.mount_point,
            "device": self.device,
            "fs_type": self.fs_type,
            "options": list(self.options),
            "role": self.role,
            "is_read_only": self.is_read_only,
            "is_remote": self.is_remote,
            "is_virtual": self.is_virtual,
            "note": self.note,
        }


@dataclass
class SystemProfile:
    os_family: str
    platform: str
    is_wsl: bool
    desktop_environment: str | None
    hostname: str | None
    mounts: list[MountInfo]

    def to_dict(self) -> dict:
        return {
            "os_family": self.os_family,
            "platform": self.platform,
            "is_wsl": self.is_wsl,
            "desktop_environment": self.desktop_environment,
            "hostname": self.hostname,
            "mounts": [mount.to_dict() for mount in self.mounts],
        }


def detect_os_family(system_name: str | None = None) -> str:
    """Return a stable OS family name."""
    name = (system_name if system_name is not None else platform_module.system()).lower()
    if name == "linux":
        return "linux"
    if name == "windows":
        return "windows"
    if name in {"darwin", "mac", "macos"}:
        return "macos"
    return "unknown"


def _read_proc_version() -> str:
    try:
        with open("/proc/version", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def detect_wsl(
    proc_version: str | None = None,
    environ: Mapping[str, str] | None = None,
    os_family: str | None = None,
) -> bool:
    """Detect WSL, accepting simulated inputs for deterministic tests."""
    family = os_family if os_family is not None else detect_os_family()
    if family != "linux":
        return False

    environment = os.environ if environ is None else environ
    if environment.get("WSL_DISTRO_NAME") or environment.get("WSL_INTEROP"):
        return True

    version_text = _read_proc_version() if proc_version is None else proc_version
    lowered = version_text.lower()
    return "microsoft" in lowered or "wsl" in lowered


def detect_desktop_environment(
    environ: Mapping[str, str] | None = None,
) -> str | None:
    """Return a readable desktop environment name when one is advertised."""
    environment = os.environ if environ is None else environ
    for variable in ("XDG_CURRENT_DESKTOP", "DESKTOP_SESSION"):
        value = environment.get(variable)
        if value:
            return value.strip() or None
    if environment.get("KDE_FULL_SESSION"):
        return "KDE"
    if environment.get("GNOME_DESKTOP_SESSION_ID"):
        return "GNOME"
    return None


def _unescape_mount_field(value: str) -> str:
    replacements = {
        r"\040": " ",
        r"\011": "\t",
        r"\012": "\n",
        r"\134": "\\",
    }
    for escaped, unescaped in replacements.items():
        value = value.replace(escaped, unescaped)
    return value


def classify_fs_type(fs_type: str) -> str:
    """Group a filesystem type into a broad family."""
    normalized = fs_type.lower()
    if normalized in _LOCAL_LINUX_FS:
        return "local_linux"
    if normalized in _WINDOWS_FS:
        return "windows"
    if normalized in _REMOVABLE_FS:
        return "removable"
    if (
        normalized in _NETWORK_FS
        or normalized.startswith(("nfs.", "cifs."))
        or normalized.endswith(".sshfs")
    ):
        return "network"
    if "fuse" in normalized:
        return "fuse"
    if normalized in _TEMPORARY_FS:
        return "temporary"
    if normalized in _VIRTUAL_FS:
        return "virtual"
    return "unknown"


def classify_mount_role(
    mount_point: str,
    device: str,
    fs_type: str,
    options: list[str],
) -> str:
    """Assign a practical scanning role to a mount."""
    del device, options  # Reserved for richer classification rules.
    normalized_point = mount_point.rstrip("/") or "/"
    lowered_point = normalized_point.lower()
    normalized_fs = fs_type.lower()

    if normalized_point in _SYSTEM_MOUNTS:
        return "system"
    if normalized_fs in _WINDOWS_FS or lowered_point in {
        "/mnt/c", "/mnt/d", "/mnt/windows",
    }:
        return "windows_mount"
    if (
        lowered_point.startswith(("/media/", "/run/media/"))
        or normalized_fs in _REMOVABLE_FS
    ):
        return "removable"
    if (
        normalized_fs in _NETWORK_FS
        or normalized_fs.startswith(("nfs.", "cifs."))
        or normalized_fs.endswith(".sshfs")
    ):
        return "network"
    if "fuse" in normalized_fs or any(
        marker in lowered_point for marker in _CLOUD_MARKERS
    ):
        return "cloud_fuse"
    if (
        normalized_fs in _TEMPORARY_FS
        or normalized_point in {"/tmp", "/run", "/dev/shm"}
    ):
        return "temporary"
    if normalized_fs == "overlay":
        return "container"
    if normalized_fs in _VIRTUAL_FS:
        return "virtual"
    if normalized_point == "/home" or lowered_point.startswith("/home/"):
        return "home"
    return "unknown"


def parse_proc_mounts(text: str) -> list[MountInfo]:
    """Parse Linux /proc/mounts content without querying the live system."""
    mounts = []
    for line in text.splitlines():
        fields = line.split()
        if len(fields) < 4:
            continue

        device = _unescape_mount_field(fields[0])
        mount_point = _unescape_mount_field(fields[1])
        fs_type = _unescape_mount_field(fields[2])
        options = [_unescape_mount_field(option) for option in fields[3].split(",")]
        role = classify_mount_role(mount_point, device, fs_type, options)
        mounts.append(MountInfo(
            mount_point=mount_point,
            device=device,
            fs_type=fs_type,
            options=options,
            role=role,
            is_read_only="ro" in options,
            is_remote=role in {"network", "cloud_fuse"},
            is_virtual=role in {"container", "temporary", "virtual"},
        ))
    return mounts


def list_mounts(os_family: str | None = None) -> list[MountInfo]:
    """List Linux mounts using /proc/mounts; return an empty list elsewhere."""
    family = os_family if os_family is not None else detect_os_family()
    if family != "linux":
        return []
    try:
        with open("/proc/mounts", encoding="utf-8", errors="replace") as handle:
            return parse_proc_mounts(handle.read())
    except OSError:
        return []


def detect_system_profile() -> SystemProfile:
    """Build a serializable snapshot of the current system."""
    os_family = detect_os_family()
    try:
        hostname = socket.gethostname()
    except OSError:
        hostname = None
    return SystemProfile(
        os_family=os_family,
        platform=platform_module.platform(),
        is_wsl=detect_wsl(os_family=os_family),
        desktop_environment=detect_desktop_environment(),
        hostname=hostname,
        mounts=list_mounts(os_family=os_family),
    )
