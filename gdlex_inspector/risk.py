"""Prudential risk classification for gdlex-inspector.

No files are deleted or modified — this module only produces advisory messages.
"""

from __future__ import annotations

import os

RISK_NONE = "none"
RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"
RISK_CRITICAL = "critical"


_PATH_CRITICAL_FRAGMENTS = (
    "windows/system32",
    "windows\\system32",
    "windows/winsxs",
    "windows\\winsxs",
    "windows/installer",
    "windows\\installer",
    "/boot",
    "/etc",
    "/usr/lib",
    "/lib",
)

_CATEGORY_RULES: dict[str, tuple[str, str]] = {
    "pst": (RISK_HIGH, "Backup consigliabile: file PST Outlook di grandi dimensioni."),
    "ost": (RISK_HIGH, "Non cancellare manualmente: l'OST è normalmente una cache gestita da Outlook."),
    "onedrive": (RISK_MEDIUM, "Prudenza alta: cartella OneDrive/SharePoint — verificare sincronizzazione prima di agire."),
    "browser_cache": (RISK_MEDIUM, "Prudenza media: la cache browser può essere eliminata con gli strumenti del browser."),
    "downloads": (RISK_LOW, "Da verificare: cartella Downloads — controllare il contenuto prima di agire."),
    "node_modules": (RISK_LOW, "Eliminabile solo se il progetto è ricreabile con npm/yarn install."),
    "venv": (RISK_LOW, "Eliminabile solo se l'ambiente virtuale è ricreabile con pip."),
    "snap_flatpak": (RISK_LOW, "Gestire con i comandi snap/flatpak, non manualmente."),
    "docker": (RISK_MEDIUM, "Prudenza: dati Docker — usare 'docker system prune' solo se consapevole."),
    "temp": (RISK_LOW, "Gestire preferibilmente con strumenti di sistema, non manualmente."),
    "other": (RISK_NONE, ""),
}


def classify_risk(path: str, category: str) -> tuple[str, str]:
    """Return (risk_level, advisory_message) for a path and its category."""
    lower = path.lower().replace("\\", "/")

    for fragment in _PATH_CRITICAL_FRAGMENTS:
        if fragment in lower:
            return (RISK_CRITICAL, "Non cancellare manualmente: percorso di sistema critico.")

    return _CATEGORY_RULES.get(category, (RISK_NONE, ""))
