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

echo "[1/8] --help"
$PYTHON -m gdlex_inspector --help > /dev/null
echo "  OK"

echo "[2/8] version"
$PYTHON -m gdlex_inspector version
echo "  OK"

echo "[3/8] scan on temp directory"
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

echo "[4/8] export JSON"
JSON_OUT="$TMPDIR_TEST/report.json"
$PYTHON -m gdlex_inspector scan "$TMPDIR_TEST" --json "$JSON_OUT" > /dev/null
if [[ ! -s "$JSON_OUT" ]]; then
  echo "  FAIL: JSON report missing or empty" >&2
  exit 1
fi
echo "  OK: $JSON_OUT ($(wc -c < "$JSON_OUT") bytes)"

echo "[5/8] export HTML"
HTML_OUT="$TMPDIR_TEST/report.html"
$PYTHON -m gdlex_inspector scan "$TMPDIR_TEST" --html "$HTML_OUT" > /dev/null
if [[ ! -s "$HTML_OUT" ]]; then
  echo "  FAIL: HTML report missing or empty" >&2
  exit 1
fi
echo "  OK: $HTML_OUT ($(wc -c < "$HTML_OUT") bytes)"

echo "[6/8] export CSV"
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

echo "[7/8] desktop integration files"
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

echo "[8/8] unit tests"
$PYTHON -m unittest discover -s tests -v 2>&1 | tail -5
echo "  OK"

echo ""
echo "=== ALL SMOKE TESTS PASSED ==="
