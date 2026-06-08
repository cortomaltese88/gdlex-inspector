"""Heuristic file/path category classification for gdlex-inspector."""

from __future__ import annotations

import os

CATEGORIES = {
    "pst": "Outlook PST",
    "ost": "Outlook OST",
    "downloads": "Downloads",
    "browser_cache": "Browser Cache",
    "temp": "Temp",
    "node_modules": "Node Modules",
    "venv": "Python venv",
    "docker": "Docker",
    "snap_flatpak": "Snap/Flatpak Cache",
    "onedrive": "OneDrive/SharePoint Cache",
    "other": "Other",
}

_LOWER_PARTS_CHECKS = {
    "node_modules": "node_modules",
    ".venv": "venv",
    "venv": "venv",
    "__pycache__": "temp",
    "downloads": "downloads",
    "scaricati": "downloads",
}

_SUFFIX_CHECKS = {
    ".pst": "pst",
    ".ost": "ost",
}


def classify_path(path: str) -> str:
    """Return a category key for the given path using heuristic rules."""
    lower = path.lower()
    parts = lower.replace("\\", "/").split("/")

    suffix = os.path.splitext(lower)[1]
    if suffix in _SUFFIX_CHECKS:
        return _SUFFIX_CHECKS[suffix]

    for part in parts:
        if part in _LOWER_PARTS_CHECKS:
            return _LOWER_PARTS_CHECKS[part]

    if "docker" in lower and ("overlay2" in lower or "volumes" in lower or "containers" in lower):
        return "docker"

    if any(p in lower for p in ("/snap/", "\\snap\\", "/flatpak/", "\\flatpak\\")):
        return "snap_flatpak"

    if any(p in lower for p in ("onedrive", "sharepoint", "onedrivetemp")):
        return "onedrive"

    if any(p in lower for p in (
        "google/chrome", "chromium", "mozilla/firefox", "microsoft/edge",
        "chrome/default/cache", "firefox/profiles",
    )):
        return "browser_cache"

    if any(p in lower for p in ("/tmp/", "\\temp\\", "\\tmp\\", "/var/tmp/")):
        return "temp"

    return "other"
