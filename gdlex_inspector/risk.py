"""Prudential risk classification for gdlex-inspector.

No files are deleted or modified — this module only produces advisory messages.
"""

from __future__ import annotations

RISK_NONE = "none"
RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"
RISK_CRITICAL = "critical"

SENSITIVITY_SYSTEM = "system"


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

_PROTECTED_UNIX_ROOTS = (
    "/etc",
    "/usr",
    "/bin",
    "/sbin",
    "/lib",
    "/boot",
    "/var/lib",
)

_RISK_DISPLAY_LABELS = {
    RISK_NONE: "Normale",
    RISK_LOW: "Bassa",
    RISK_MEDIUM: "Media",
    RISK_HIGH: "Alta",
    RISK_CRITICAL: "Critica",
}


def classify_risk(path: str, category: str) -> tuple[str, str]:
    """Return (risk_level, advisory_message) for a path and its category."""
    lower = path.lower().replace("\\", "/")

    for fragment in _PATH_CRITICAL_FRAGMENTS:
        if fragment in lower:
            return (RISK_CRITICAL, "Non cancellare manualmente: percorso di sistema critico.")

    return _CATEGORY_RULES.get(category, (RISK_NONE, ""))


def is_protected_system_path(path: str) -> bool:
    """Return whether path belongs to a protected Unix system tree."""
    normalized = path.lower().replace("\\", "/").rstrip("/") or "/"
    return any(
        normalized == root or normalized.startswith(root + "/")
        for root in _PROTECTED_UNIX_ROOTS
    )


def risk_label_for_display(
    risk: str,
    category: str = "",
    path: str = "",
    size: int = 0,
) -> str:
    """Return an Italian sensitivity label without changing technical risk data."""
    del category, size
    if is_protected_system_path(path):
        return "Sistema"
    return _RISK_DISPLAY_LABELS.get(risk, risk.capitalize() or "Normale")


def risk_style_for_display(
    risk: str,
    category: str = "",
    path: str = "",
    size: int = 0,
) -> str:
    """Return the presentation style key associated with a sensitivity label."""
    del category, size
    if is_protected_system_path(path):
        return SENSITIVITY_SYSTEM
    return risk
