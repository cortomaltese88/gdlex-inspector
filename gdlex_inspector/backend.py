"""External backend detection and selection for gdlex-inspector.

In v0.1, the Python internal scanner is always used.
This module prepares the architecture for future optional backends:
gdu, dust, duf — none are required or executed in this version.
"""

from __future__ import annotations

import shutil

BACKEND_PYTHON = "python"
BACKEND_GDU = "gdu"
BACKEND_DUST = "dust"
BACKEND_DUF = "duf"

ALL_BACKENDS = [BACKEND_PYTHON, BACKEND_GDU, BACKEND_DUST, BACKEND_DUF]

_EXTERNAL_BACKENDS = [BACKEND_GDU, BACKEND_DUST, BACKEND_DUF]


def is_external_backend_available(name: str) -> bool:
    """Return True if the named external binary is on PATH."""
    if name == BACKEND_PYTHON:
        return True
    return shutil.which(name) is not None


def choose_backend(preferred: str | None = None) -> str:
    """Return the best available backend name.

    In v0.1, always returns BACKEND_PYTHON unless an external backend is
    explicitly preferred AND available. Falls back to Python otherwise.
    """
    if preferred and preferred != BACKEND_PYTHON:
        if is_external_backend_available(preferred):
            return preferred
    return BACKEND_PYTHON


def list_available_backends() -> list[str]:
    """Return a list of all backends currently available on this system."""
    return [b for b in ALL_BACKENDS if is_external_backend_available(b)]
