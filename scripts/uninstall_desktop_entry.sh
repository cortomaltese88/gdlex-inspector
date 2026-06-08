#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Remove GD LEX Inspector desktop entry and icon for current user (no sudo required).
set -euo pipefail

DESKTOP_DEST="$HOME/.local/share/applications/gdlex-inspector.desktop"
ICON_DEST="$HOME/.local/share/icons/hicolor/scalable/apps/gdlex-inspector.svg"

echo "=== GD LEX Inspector — desktop integration uninstall ==="
echo ""

removed=0

if [[ -f "$DESKTOP_DEST" ]]; then
    rm "$DESKTOP_DEST"
    echo "  Removed: $DESKTOP_DEST"
    removed=1
else
    echo "  Not found (already removed?): $DESKTOP_DEST"
fi

if [[ -f "$ICON_DEST" ]]; then
    rm "$ICON_DEST"
    echo "  Removed: $ICON_DEST"
    removed=1
else
    echo "  Not found (already removed?): $ICON_DEST"
fi

echo ""

if [[ $removed -eq 1 ]]; then
    # Update caches best-effort
    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "$HOME/.local/share/applications" && echo "  update-desktop-database: OK" || true
    fi

    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" && echo "  gtk-update-icon-cache: OK" || true
    fi

    if command -v kbuildsycoca6 &>/dev/null; then
        kbuildsycoca6 && echo "  kbuildsycoca6: OK" || true
    elif command -v kbuildsycoca5 &>/dev/null; then
        kbuildsycoca5 && echo "  kbuildsycoca5: OK" || true
    fi
fi

echo ""
echo "=== Uninstall complete ==="
