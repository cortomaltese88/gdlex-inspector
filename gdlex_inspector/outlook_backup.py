"""Outlook PST/OST detection and backup preparation for gdlex-inspector.

IMPORTANT: No real file copies are performed in this version.
This module only locates and classifies Outlook archive files.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class OutlookArchiveCandidate:
    path: str
    kind: str  # 'pst', 'ost', 'other'
    size: int
    warning: str
    backup_eligible: bool


def is_outlook_archive(path: str) -> bool:
    """Return True if the path points to an Outlook PST or OST file."""
    return path.lower().endswith((".pst", ".ost"))


def classify_outlook_archive(path: str) -> str:
    """Return 'pst', 'ost', or 'other'."""
    lower = path.lower()
    if lower.endswith(".pst"):
        return "pst"
    if lower.endswith(".ost"):
        return "ost"
    return "other"


def outlook_archive_warning(kind: str) -> str:
    if kind == "pst":
        return (
            "File PST Outlook: backup consigliabile. "
            "Chiudere Outlook prima di copiare."
        )
    if kind == "ost":
        return (
            "File OST Outlook: normalmente è una cache gestita da Outlook. "
            "Non cancellare manualmente. L'OST si ricrea automaticamente."
        )
    return ""


def build_candidate(path: str, size: int) -> Optional[OutlookArchiveCandidate]:
    """Build an OutlookArchiveCandidate for a given path, or None if not Outlook."""
    kind = classify_outlook_archive(path)
    if kind == "other":
        return None
    return OutlookArchiveCandidate(
        path=path,
        kind=kind,
        size=size,
        warning=outlook_archive_warning(kind),
        backup_eligible=(kind == "pst"),
    )


def copy_pst_stub(src: str, dst_dir: str) -> None:
    """STUB — future function to copy a PST file to a backup destination.

    Not implemented in v0.1. Will require:
    - Outlook closed verification
    - destination free space check
    - no-overwrite policy
    - optional SHA-256 verification
    - backup report generation
    """
    raise NotImplementedError(
        "PST backup copy is not implemented in this version. "
        "See ROADMAP.md Phase 4."
    )
