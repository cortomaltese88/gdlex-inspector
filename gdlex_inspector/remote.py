"""Remote host profiles and SSH command preparation for gdlex-inspector.

IMPORTANT: No real connections are made in this version.
No passwords or secrets are stored in profiles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RemoteProfile:
    name: str
    host: str
    port: int = 22
    user: str = ""
    identity_file: Optional[str] = None
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Return a list of validation error messages, empty if valid."""
        errors = []
        if not self.name.strip():
            errors.append("Profile name cannot be empty.")
        if not self.host.strip():
            errors.append("Host cannot be empty.")
        if not (1 <= self.port <= 65535):
            errors.append(f"Invalid port: {self.port}")
        return errors


def build_ssh_command(profile: RemoteProfile, remote_command: Optional[str] = None) -> list[str]:
    """Build an SSH command list for a remote profile. Does NOT execute it."""
    cmd = ["ssh"]
    if profile.port != 22:
        cmd += ["-p", str(profile.port)]
    if profile.identity_file:
        cmd += ["-i", profile.identity_file]
    target = f"{profile.user}@{profile.host}" if profile.user else profile.host
    cmd.append(target)
    if remote_command:
        cmd.append(remote_command)
    return cmd
