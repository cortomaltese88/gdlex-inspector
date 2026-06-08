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

echo "[1/7] --help"
$PYTHON -m gdlex_inspector --help > /dev/null
echo "  OK"

echo "[2/7] version"
$PYTHON -m gdlex_inspector version
echo "  OK"

echo "[3/7] scan on temp directory"
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

echo "[4/7] export JSON"
JSON_OUT="$TMPDIR_TEST/report.json"
$PYTHON -m gdlex_inspector scan "$TMPDIR_TEST" --json "$JSON_OUT" > /dev/null
if [[ ! -s "$JSON_OUT" ]]; then
  echo "  FAIL: JSON report missing or empty" >&2
  exit 1
fi
echo "  OK: $JSON_OUT ($(wc -c < "$JSON_OUT") bytes)"

echo "[5/7] export HTML"
HTML_OUT="$TMPDIR_TEST/report.html"
$PYTHON -m gdlex_inspector scan "$TMPDIR_TEST" --html "$HTML_OUT" > /dev/null
if [[ ! -s "$HTML_OUT" ]]; then
  echo "  FAIL: HTML report missing or empty" >&2
  exit 1
fi
echo "  OK: $HTML_OUT ($(wc -c < "$HTML_OUT") bytes)"

echo "[6/7] export CSV"
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

echo "[7/7] unit tests"
$PYTHON -m unittest discover -s tests -v 2>&1 | tail -5
echo "  OK"

echo ""
echo "=== ALL SMOKE TESTS PASSED ==="
