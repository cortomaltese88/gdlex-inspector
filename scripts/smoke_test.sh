#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Smoke test for gdlex-inspector — runs from project root
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" &>/dev/null; then
  PYTHON="python"
fi

echo "=== gdlex-inspector smoke test ==="
echo "Project root: $PROJECT_ROOT"
echo ""

echo "[1/14] --help"
$PYTHON -m gdlex_inspector --help > /dev/null
echo "  OK"

echo "[2/14] version"
$PYTHON -m gdlex_inspector version
echo "  OK"

echo "[3/14] scan on temp directory"
TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

# Create test files of varying sizes
echo "hello world" > "$TMPDIR_TEST/file_a.txt"
$PYTHON -c "open('$TMPDIR_TEST/file_b.dat','wb').write(b'x'*10240)"
$PYTHON -c "open('$TMPDIR_TEST/file_c.log','wb').write(b'y'*51200)"
mkdir -p "$TMPDIR_TEST/subdir"
echo "nested" > "$TMPDIR_TEST/subdir/nested.txt"
$PYTHON -c "open('$TMPDIR_TEST/subdir/big.bin','wb').write(b'z'*102400)"

$PYTHON -m gdlex_inspector scan "$TMPDIR_TEST" --top 5
echo "  OK"

echo "[4/14] export JSON"
JSON_OUT="$TMPDIR_TEST/report.json"
$PYTHON -m gdlex_inspector scan "$TMPDIR_TEST" --json "$JSON_OUT" > /dev/null
if [[ ! -s "$JSON_OUT" ]]; then
  echo "  FAIL: JSON report missing or empty" >&2
  exit 1
fi
echo "  OK: $JSON_OUT ($(wc -c < "$JSON_OUT") bytes)"

echo "[5/14] export HTML"
HTML_OUT="$TMPDIR_TEST/report.html"
$PYTHON -m gdlex_inspector scan "$TMPDIR_TEST" --html "$HTML_OUT" > /dev/null
if [[ ! -s "$HTML_OUT" ]]; then
  echo "  FAIL: HTML report missing or empty" >&2
  exit 1
fi
echo "  OK: $HTML_OUT ($(wc -c < "$HTML_OUT") bytes)"

echo "[6/14] export CSV"
CSV_OUT="$TMPDIR_TEST/report.csv"
$PYTHON -m gdlex_inspector scan "$TMPDIR_TEST" --csv "$CSV_OUT" > /dev/null
if [[ ! -s "$CSV_OUT" ]]; then
  echo "  FAIL: CSV report missing or empty" >&2
  exit 1
fi
# Verify all five sections are present
for section in top_files top_dirs extensions categories issues; do
  if ! grep -q "$section" "$CSV_OUT"; then
    echo "  FAIL: section '$section' missing from CSV" >&2
    exit 1
  fi
done
echo "  OK: $CSV_OUT ($(wc -c < "$CSV_OUT") bytes)"

echo "[7/14] system info"
$PYTHON -m gdlex_inspector system-info > /dev/null
echo "  OK"

echo "[8/14] system info JSON"
SYSTEM_JSON="$TMPDIR_TEST/system-info.json"
$PYTHON -m gdlex_inspector system-info --json > "$SYSTEM_JSON"
$PYTHON -c "import json; json.load(open('$SYSTEM_JSON', encoding='utf-8'))"
echo "  OK: valid JSON"

echo "[9/14] scan profiles"
$PYTHON -m gdlex_inspector profiles > /dev/null
echo "  OK"

echo "[10/14] scan profiles JSON"
PROFILES_JSON="$TMPDIR_TEST/profiles.json"
$PYTHON -m gdlex_inspector profiles --json > "$PROFILES_JSON"
$PYTHON -c "import json; json.load(open('$PROFILES_JSON', encoding='utf-8'))"
echo "  OK: valid JSON"

echo "[11/14] scan with profile and path override"
$PYTHON -m gdlex_inspector scan --profile quick-home "$TMPDIR_TEST" \
  --max-depth 1 --top 5 > /dev/null
echo "  OK"

echo "[12/14] desktop integration files"
DESKTOP_FILE="$PROJECT_ROOT/packaging/linux/gdlex-inspector.desktop"
ICON_FILE="$PROJECT_ROOT/gdlex_inspector/assets/gdlex-inspector.svg"
INSTALL_SCRIPT="$PROJECT_ROOT/scripts/install_desktop_entry.sh"
if [[ ! -f "$DESKTOP_FILE" ]]; then
  echo "  FAIL: desktop file missing: $DESKTOP_FILE" >&2
  exit 1
fi
if ! grep -q "Exec=gdlex-inspector gui" "$DESKTOP_FILE"; then
  echo "  FAIL: Exec field missing in desktop file" >&2
  exit 1
fi
if [[ ! -f "$ICON_FILE" ]]; then
  echo "  FAIL: icon missing: $ICON_FILE" >&2
  exit 1
fi
if [[ ! -x "$INSTALL_SCRIPT" ]]; then
  echo "  FAIL: install script not executable: $INSTALL_SCRIPT" >&2
  exit 1
fi
echo "  OK"

echo "[13/14] Debian package build"
BUILD_SCRIPT="$PROJECT_ROOT/scripts/build_deb.sh"
if [[ ! -x "$BUILD_SCRIPT" ]]; then
  echo "  FAIL: build script missing or not executable: $BUILD_SCRIPT" >&2
  exit 1
fi
"$BUILD_SCRIPT" > /dev/null
DEB_FILE="$(find "$PROJECT_ROOT/dist" -maxdepth 1 -name 'gdlex-inspector_*_all.deb' -print -quit)"
if [[ -z "$DEB_FILE" || ! -s "$DEB_FILE" ]]; then
  echo "  FAIL: Debian package missing or empty" >&2
  exit 1
fi
dpkg-deb --info "$DEB_FILE" > /dev/null
DEB_CONTENTS="$(dpkg-deb --contents "$DEB_FILE")"
for packaged_path in \
  "./usr/bin/gdlex-inspector" \
  "./usr/lib/gdlex-inspector/gdlex_inspector/scan_profiles.py" \
  "./usr/share/applications/gdlex-inspector.desktop" \
  "./usr/share/icons/hicolor/scalable/apps/gdlex-inspector.svg"; do
  if ! grep -q "$packaged_path" <<< "$DEB_CONTENTS"; then
    echo "  FAIL: package does not contain $packaged_path" >&2
    exit 1
  fi
done
echo "  OK: $DEB_FILE"

echo "[14/14] unit tests"
$PYTHON -m unittest discover -s tests -v 2>&1 | tail -5
echo "  OK"

echo ""
echo "=== ALL SMOKE TESTS PASSED ==="
