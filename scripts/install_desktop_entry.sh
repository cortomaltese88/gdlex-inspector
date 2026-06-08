#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Install GD LEX Inspector desktop entry and icon for current user (no sudo required).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

DESKTOP_SRC="$PROJECT_ROOT/packaging/linux/gdlex-inspector.desktop"
ICON_SRC="$PROJECT_ROOT/gdlex_inspector/assets/gdlex-inspector.svg"

DESKTOP_DEST="$HOME/.local/share/applications/gdlex-inspector.desktop"
ICON_DEST="$HOME/.local/share/icons/hicolor/scalable/apps/gdlex-inspector.svg"

echo "=== GD LEX Inspector — desktop integration install ==="
echo ""

# Verify source files exist
if [[ ! -f "$DESKTOP_SRC" ]]; then
    echo "ERROR: desktop file not found: $DESKTOP_SRC" >&2
    exit 1
fi
if [[ ! -f "$ICON_SRC" ]]; then
    echo "ERROR: icon file not found: $ICON_SRC" >&2
    exit 1
fi

# Create target directories if missing
mkdir -p "$(dirname "$DESKTOP_DEST")"
mkdir -p "$(dirname "$ICON_DEST")"

# Install desktop file
cp "$DESKTOP_SRC" "$DESKTOP_DEST"
echo "  Desktop file installed: $DESKTOP_DEST"

# Install icon
cp "$ICON_SRC" "$ICON_DEST"
echo "  Icon installed:         $ICON_DEST"

echo ""

# Update caches (best-effort — skip silently if commands not available)
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

echo ""
echo "=== Installation complete ==="
echo ""
echo "You can now launch GD LEX Inspector from the application menu,"
echo "or from the terminal with:"
echo "  gdlex-inspector gui"
echo "  python3 -m gdlex_inspector gui"
