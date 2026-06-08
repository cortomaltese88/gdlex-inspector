"""Wake-on-LAN magic packet builder for gdlex-inspector."""

from __future__ import annotations

import re
import socket


_MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}$")
_MAC_BARE_RE = re.compile(r"^[0-9A-Fa-f]{12}$")


def normalize_mac(mac: str) -> str:
    """Normalize a MAC address to XX:XX:XX:XX:XX:XX uppercase format.

    Accepts colon, hyphen, or no separator.
    Raises ValueError on invalid input.
    """
    cleaned = mac.strip()
    if _MAC_RE.match(cleaned):
        return cleaned.upper().replace("-", ":")
    bare = cleaned.replace(":", "").replace("-", "")
    if _MAC_BARE_RE.match(bare):
        return ":".join(bare[i:i+2] for i in range(0, 12, 2)).upper()
    raise ValueError(f"Invalid MAC address: {mac!r}")


def build_magic_packet(mac: str) -> bytes:
    """Build a Wake-on-LAN magic packet for the given MAC address.

    Returns 102 bytes: 6x 0xFF followed by 16 repetitions of the MAC.
    """
    normalized = normalize_mac(mac)
    mac_bytes = bytes(int(b, 16) for b in normalized.split(":"))
    return b"\xff" * 6 + mac_bytes * 16


def send_magic_packet(mac: str, broadcast: str = "255.255.255.255", port: int = 9) -> None:
    """Send a Wake-on-LAN magic packet via UDP broadcast.

    This function is kept separate and is not called by default in any scan.
    Use only when explicitly requested by the user.
    """
    packet = build_magic_packet(mac)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (broadcast, port))
