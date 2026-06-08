"""Platform detection utilities for gdlex-inspector."""

from __future__ import annotations

import os
import platform
import socket


def _read_proc_version() -> str:
    try:
        with open("/proc/version", "r") as f:
            return f.read().lower()
    except OSError:
        return ""


def is_wsl() -> bool:
    """Return True if running inside WSL (Windows Subsystem for Linux)."""
    proc = _read_proc_version()
    return "microsoft" in proc or "wsl" in proc


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def is_linux() -> bool:
    return platform.system().lower() == "linux"


def get_platform_kind() -> str:
    """Return 'wsl', 'windows', or 'linux'."""
    if is_windows():
        return "windows"
    if is_linux() and is_wsl():
        return "wsl"
    return "linux"


def get_hostname() -> str:
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def get_username() -> str:
    try:
        return os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
    except Exception:
        return "unknown"


def get_platform_summary() -> dict:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "hostname": get_hostname(),
        "username": get_username(),
        "platform_kind": get_platform_kind(),
    }
