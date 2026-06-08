"""Dynamic read-only scan profiles."""

from __future__ import annotations

from dataclasses import dataclass
import os

from .system_profile import SystemProfile, detect_system_profile


@dataclass
class ScanProfile:
    id: str
    label: str
    description: str
    target_path: str
    max_depth: int | None
    top: int
    min_size: int
    excludes: list[str]
    follow_symlinks: bool
    estimated_speed: str
    caution: str | None
    recommended_for_roles: list[str]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "target_path": self.target_path,
            "max_depth": self.max_depth,
            "top": self.top,
            "min_size": self.min_size,
            "excludes": list(self.excludes),
            "follow_symlinks": self.follow_symlinks,
            "estimated_speed": self.estimated_speed,
            "caution": self.caution,
            "recommended_for_roles": list(self.recommended_for_roles),
        }


def resolve_target_path(path: str) -> str:
    """Expand user and environment markers without requiring path existence."""
    return os.path.expanduser(os.path.expandvars(path))


def _system_root(system_profile: SystemProfile) -> str:
    if system_profile.os_family == "windows":
        return os.environ.get("SystemDrive", "C:") + os.sep
    return "/"


def get_default_profiles(
    system_profile: SystemProfile | None = None,
) -> list[ScanProfile]:
    """Return profiles suited to the detected system and mounted filesystems."""
    profile = system_profile or detect_system_profile()
    home = resolve_target_path("~")

    profiles = [
        ScanProfile(
            id="quick-home",
            label="Rapida Home",
            description="Scansione veloce delle aree principali della home utente.",
            target_path=home,
            max_depth=3,
            top=30,
            min_size=1024,
            excludes=[".cache", "*/.local/share/Trash", ".Trash-*"],
            follow_symlinks=False,
            estimated_speed="Veloce",
            caution=None,
            recommended_for_roles=["home"],
        ),
        ScanProfile(
            id="standard-home",
            label="Home standard",
            description="Scansione bilanciata della home con profondita prudente.",
            target_path=home,
            max_depth=6,
            top=50,
            min_size=0,
            excludes=[".cache", "*/.local/share/Trash", ".Trash-*"],
            follow_symlinks=False,
            estimated_speed="Media",
            caution=None,
            recommended_for_roles=["home"],
        ),
        ScanProfile(
            id="deep-home",
            label="Home completa",
            description="Scansione completa della home utente.",
            target_path=home,
            max_depth=None,
            top=100,
            min_size=0,
            excludes=["*/.local/share/Trash", ".Trash-*"],
            follow_symlinks=False,
            estimated_speed="Lenta",
            caution="La scansione completa puo richiedere tempo.",
            recommended_for_roles=["home"],
        ),
        ScanProfile(
            id="system-safe",
            label="Sistema prudente",
            description="Scansione read-only del sistema a profondita limitata.",
            target_path=_system_root(profile),
            max_depth=4,
            top=50,
            min_size=0,
            excludes=["/proc", "/sys", "/dev", "/run", "/tmp", "/var/run"],
            follow_symlinks=False,
            estimated_speed="Media",
            caution=(
                "Profilo read-only: non cancellare manualmente file di sistema."
            ),
            recommended_for_roles=["system"],
        ),
        ScanProfile(
            id="dev-cleanup",
            label="Sviluppo",
            description=(
                "Analizza la home incluse .venv, node_modules, build, dist, "
                "__pycache__, cache di test, .gradle e target."
            ),
            target_path=home,
            max_depth=8,
            top=100,
            min_size=0,
            excludes=[".git", ".cache", "*/.local/share/Trash", ".Trash-*"],
            follow_symlinks=False,
            estimated_speed="Media",
            caution="Il profilo segnala soltanto i dati: non esegue cleanup.",
            recommended_for_roles=["home"],
        ),
    ]

    windows_mount = next(
        (mount for mount in profile.mounts if mount.role == "windows_mount"),
        None,
    )
    if windows_mount is not None or profile.is_wsl:
        profiles.append(ScanProfile(
            id="windows-mount-safe",
            label="Windows prudente",
            description="Scansione limitata del primo mount Windows rilevato.",
            target_path=(
                windows_mount.mount_point if windows_mount is not None else "/mnt/c"
            ),
            max_depth=5,
            top=50,
            min_size=1024,
            excludes=[
                "*/Windows/System32",
                "*/Windows/WinSxS",
                "Program Files",
                "Program Files (x86)",
                "$Recycle.Bin",
                "System Volume Information",
            ],
            follow_symlinks=False,
            estimated_speed="Media",
            caution="Prestazioni e permessi del mount Windows possono variare.",
            recommended_for_roles=["windows_mount"],
        ))

    remote_mount = next(
        (
            mount for mount in profile.mounts
            if mount.role in {"cloud_fuse", "network"}
        ),
        None,
    )
    if remote_mount is not None:
        profiles.append(ScanProfile(
            id="cloud-fuse-safe",
            label="Cloud/FUSE prudente",
            description="Scansione limitata del primo mount cloud, FUSE o di rete.",
            target_path=remote_mount.mount_point,
            max_depth=3,
            top=30,
            min_size=1024,
            excludes=[".Trash-*", ".cache"],
            follow_symlinks=False,
            estimated_speed="Lenta",
            caution="I mount cloud, FUSE o di rete possono essere lenti.",
            recommended_for_roles=["cloud_fuse", "network"],
        ))

    return profiles


def get_profile(
    profile_id: str,
    system_profile: SystemProfile | None = None,
) -> ScanProfile | None:
    """Return a scan profile by id, or None when it is unavailable."""
    return next(
        (
            profile for profile in get_default_profiles(system_profile)
            if profile.id == profile_id
        ),
        None,
    )
