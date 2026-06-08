#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Build a local Debian package without network access or root privileges.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist"

if ! command -v dpkg-deb &>/dev/null; then
  echo "ERROR: dpkg-deb is required to build the Debian package." >&2
  exit 1
fi

if [[ -n "$(git -C "$PROJECT_ROOT" status --porcelain 2>/dev/null || true)" ]]; then
  echo "WARNING: building from a working tree with uncommitted changes." >&2
fi

VERSION="$(
  PROJECT_ROOT="$PROJECT_ROOT" python3 - <<'PY'
import os
import pathlib
import tomllib

root = pathlib.Path(os.environ["PROJECT_ROOT"])
with (root / "pyproject.toml").open("rb") as handle:
    print(tomllib.load(handle)["project"]["version"])
PY
)"

if [[ ! "$VERSION" =~ ^[0-9][0-9A-Za-z.+:~-]*$ ]]; then
  echo "ERROR: invalid Debian package version from pyproject.toml: $VERSION" >&2
  exit 1
fi

PACKAGE_NAME="gdlex-inspector_${VERSION}_all.deb"
PACKAGE_PATH="$DIST_DIR/$PACKAGE_NAME"
BUILD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/gdlex-inspector-deb.XXXXXX")"
trap 'rm -rf "$BUILD_ROOT"' EXIT

install -d \
  "$BUILD_ROOT/DEBIAN" \
  "$BUILD_ROOT/usr/bin" \
  "$BUILD_ROOT/usr/lib/gdlex-inspector" \
  "$BUILD_ROOT/usr/share/applications" \
  "$BUILD_ROOT/usr/share/doc/gdlex-inspector" \
  "$BUILD_ROOT/usr/share/icons/hicolor/scalable/apps"

sed "s/@VERSION@/$VERSION/g" \
  "$PROJECT_ROOT/packaging/debian/control.in" \
  > "$BUILD_ROOT/DEBIAN/control"

cp -a "$PROJECT_ROOT/gdlex_inspector" "$BUILD_ROOT/usr/lib/gdlex-inspector/"
find "$BUILD_ROOT/usr/lib/gdlex-inspector" \
  -type d -name __pycache__ -prune -exec rm -rf {} +
find "$BUILD_ROOT/usr/lib/gdlex-inspector" \
  -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
find "$BUILD_ROOT/usr/lib/gdlex-inspector" -type d -exec chmod 0755 {} +
find "$BUILD_ROOT/usr/lib/gdlex-inspector" -type f -exec chmod 0644 {} +

install -m 0755 \
  "$PROJECT_ROOT/packaging/debian/gdlex-inspector" \
  "$BUILD_ROOT/usr/bin/gdlex-inspector"
install -m 0644 \
  "$PROJECT_ROOT/packaging/linux/gdlex-inspector.desktop" \
  "$BUILD_ROOT/usr/share/applications/gdlex-inspector.desktop"
install -m 0644 \
  "$PROJECT_ROOT/gdlex_inspector/assets/gdlex-inspector.svg" \
  "$BUILD_ROOT/usr/share/icons/hicolor/scalable/apps/gdlex-inspector.svg"
install -m 0644 "$PROJECT_ROOT/LICENSE" \
  "$BUILD_ROOT/usr/share/doc/gdlex-inspector/copyright"
install -m 0644 "$PROJECT_ROOT/README.md" \
  "$BUILD_ROOT/usr/share/doc/gdlex-inspector/README.md"

chmod 0755 "$BUILD_ROOT"
mkdir -p "$DIST_DIR"
rm -f "$PACKAGE_PATH"
dpkg-deb --root-owner-group --build "$BUILD_ROOT" "$PACKAGE_PATH"

echo "Debian package created: $PACKAGE_PATH"
