"""Read-only disk scanner for gdlex-inspector.

No files are modified, deleted, or moved.
Symlinks are not followed by default to prevent loops.
"""

from __future__ import annotations

import fnmatch
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from .categories import classify_path
from .models import (
    CategorySummary,
    DirectoryEntry,
    ExtensionSummary,
    FileEntry,
    ScanIssue,
    ScanResult,
)
from .risk import classify_risk


def parse_size(value: str) -> int:
    """Parse a human-readable size string to bytes.

    Accepts: 100K, 100M, 1G, 2T, or plain integer (bytes).
    Raises ValueError on invalid input.
    """
    value = value.strip()
    if not value:
        raise ValueError("Empty size string")
    suffixes = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    upper = value.upper()
    for suffix, multiplier in suffixes.items():
        if upper.endswith(suffix):
            numeric = upper[:-1]
            try:
                return int(float(numeric) * multiplier)
            except ValueError:
                raise ValueError(f"Invalid size value: {value!r}")
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid size value: {value!r}")


def _matches_any_exclude(path: str, patterns: list[str]) -> bool:
    name = os.path.basename(path)
    for pat in patterns:
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(path, pat):
            return True
    return False


def scan_directory(
    root: str,
    top_n: int = 10,
    min_size: int = 0,
    max_depth: Optional[int] = None,
    follow_symlinks: bool = False,
    exclude_patterns: Optional[list[str]] = None,
) -> ScanResult:
    """Scan a directory tree and return a ScanResult.

    Read-only. No files are modified or deleted.
    """
    exclude_patterns = exclude_patterns or []

    result = ScanResult(
        root_path=os.path.abspath(root),
        scan_timestamp=datetime.now(timezone.utc).isoformat(),
    )

    all_files: list[FileEntry] = []
    dir_sizes: dict[str, int] = defaultdict(int)
    dir_counts: dict[str, int] = defaultdict(int)
    ext_sizes: dict[str, int] = defaultdict(int)
    ext_counts: dict[str, int] = defaultdict(int)
    cat_sizes: dict[str, int] = defaultdict(int)
    cat_counts: dict[str, int] = defaultdict(int)

    for dirpath, dirnames, filenames in os.walk(
        root, followlinks=follow_symlinks, onerror=lambda e: result.issues.append(
            ScanIssue(path=e.filename, error=str(e))
        )
    ):
        # Depth check
        if max_depth is not None:
            rel = os.path.relpath(dirpath, root)
            depth = 0 if rel == "." else len(rel.split(os.sep))
            if depth >= max_depth:
                dirnames.clear()
                continue

        # Exclude patterns on directories (in-place to prune os.walk)
        dirnames[:] = [
            d for d in dirnames
            if not _matches_any_exclude(os.path.join(dirpath, d), exclude_patterns)
        ]

        # Skip symlink dirs if not following
        if not follow_symlinks:
            dirnames[:] = [d for d in dirnames if not os.path.islink(os.path.join(dirpath, d))]

        result.total_dirs += 1

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            if _matches_any_exclude(filepath, exclude_patterns):
                continue

            if not follow_symlinks and os.path.islink(filepath):
                continue

            try:
                stat = os.stat(filepath)
            except OSError as e:
                result.issues.append(ScanIssue(path=filepath, error=str(e)))
                continue

            size = stat.st_size
            mtime = stat.st_mtime
            result.total_files += 1
            result.total_size += size

            category = classify_path(filepath)
            risk_level, risk_message = classify_risk(filepath, category)
            ext = os.path.splitext(filename)[1].lower() or "(no ext)"

            dir_sizes[dirpath] += size
            dir_counts[dirpath] += 1
            ext_sizes[ext] += size
            ext_counts[ext] += 1
            cat_sizes[category] += size
            cat_counts[category] += 1

            entry = FileEntry(
                path=filepath,
                size=size,
                category=category,
                risk_level=risk_level,
                risk_message=risk_message,
                last_modified=mtime,
            )
            all_files.append(entry)

    # Top files by size
    all_files.sort(key=lambda f: f.size, reverse=True)
    result.top_files = [f for f in all_files if f.size >= min_size][:top_n]

    # Compute recursive directory sizes: propagate each dir's direct file
    # sizes up to all ancestor directories within root.
    abs_root = os.path.abspath(root)
    recursive_dir_sizes: dict[str, int] = defaultdict(int)
    recursive_dir_counts: dict[str, int] = defaultdict(int)
    for dirpath, direct_size in dir_sizes.items():
        d = dirpath
        while True:
            recursive_dir_sizes[d] += direct_size
            recursive_dir_counts[d] += dir_counts[dirpath]
            if os.path.abspath(d) == abs_root:
                break
            parent = os.path.dirname(d)
            if parent == d:  # filesystem root, safety stop
                break
            d = parent

    # Top directories
    dir_entries = [
        DirectoryEntry(
            path=d,
            size=s,
            file_count=recursive_dir_counts[d],
            category=classify_path(d),
            risk_level=classify_risk(d, classify_path(d))[0],
            risk_message=classify_risk(d, classify_path(d))[1],
        )
        for d, s in recursive_dir_sizes.items()
    ]
    dir_entries.sort(key=lambda d: d.size, reverse=True)
    result.top_dirs = dir_entries[:top_n]

    # Extensions summary
    result.extensions = sorted(
        [ExtensionSummary(e, ext_sizes[e], ext_counts[e]) for e in ext_sizes],
        key=lambda x: x.total_size,
        reverse=True,
    )

    # Categories summary
    from .risk import RISK_NONE
    result.categories = sorted(
        [
            CategorySummary(
                category=c,
                total_size=cat_sizes[c],
                file_count=cat_counts[c],
                risk_level=classify_risk("", c)[0],
            )
            for c in cat_sizes
        ],
        key=lambda x: x.total_size,
        reverse=True,
    )

    return result
