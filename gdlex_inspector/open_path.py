"""Path opening utilities for gdlex-inspector.

These are pure functions — no commands are executed here.
Callers are responsible for running the returned command lists.
"""

from __future__ import annotations

import re


def is_wsl_windows_path(path: str) -> bool:
    """Return True if path is a WSL mount path like /mnt/c/..."""
    return bool(re.match(r"^/mnt/[a-zA-Z]/", path))


def wsl_to_windows_path(path: str) -> str:
    """Convert /mnt/c/Users/... to C:\\Users\\..."""
    match = re.match(r"^/mnt/([a-zA-Z])(/.*)?$", path)
    if not match:
        raise ValueError(f"Not a WSL Windows mount path: {path!r}")
    drive = match.group(1).upper()
    rest = (match.group(2) or "").replace("/", "\\")
    return f"{drive}:{rest}"


def build_open_command(path: str, is_file: bool, platform_kind: str) -> list[str]:
    """Build a shell command list to open a path in the file manager.

    Does NOT execute the command — returns it as a list suitable for subprocess.
    """
    if platform_kind == "windows":
        if is_file:
            win_path = path.replace("/", "\\")
            return ["explorer.exe", f"/select,{win_path}"]
        return ["explorer.exe", path.replace("/", "\\")]

    if platform_kind == "wsl":
        if is_wsl_windows_path(path):
            win_path = wsl_to_windows_path(path)
            if is_file:
                return ["explorer.exe", f"/select,{win_path}"]
            return ["explorer.exe", win_path]
        return ["xdg-open", path]

    # linux
    return ["xdg-open", path]
