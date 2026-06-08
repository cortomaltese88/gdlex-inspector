"""Report generation (JSON, HTML, CSV) for gdlex-inspector."""

from __future__ import annotations

import csv
import io
import json
import os
from datetime import datetime

from .models import ScanResult

_MATRIX_CSS = """
body {
    background: #0a0f0a;
    color: #c8ffc8;
    font-family: 'Courier New', Courier, monospace;
    font-size: 14px;
    margin: 0;
    padding: 20px;
}
h1 { color: #00ff41; font-size: 1.4em; margin-bottom: 4px; }
h2 { color: #39ff14; font-size: 1.1em; border-bottom: 1px solid #1a4d1a; padding-bottom: 4px; margin-top: 24px; }
.meta { color: #6af06a; font-size: 0.9em; margin-bottom: 16px; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 0.82em; }
.badge-ok { background: #0d2b0d; color: #39ff14; border: 1px solid #1f5e1f; }
.badge-low { background: #1a2b00; color: #aaff00; border: 1px solid #3a5c00; }
.badge-medium { background: #2b1a00; color: #ffcc00; border: 1px solid #5c3a00; }
.badge-high { background: #2b0000; color: #ff6060; border: 1px solid #5c0000; }
.badge-critical { background: #400000; color: #ff2222; border: 1px solid #800000; font-weight: bold; }
table { width: 100%; border-collapse: collapse; margin-top: 8px; }
th { background: #0d2b0d; color: #39ff14; text-align: left; padding: 6px 8px; font-size: 0.9em; }
td { padding: 5px 8px; border-bottom: 1px solid #0d1a0d; word-break: break-all; }
tr:hover td { background: #0d1a0d; }
.size { text-align: right; white-space: nowrap; }
.path { font-size: 0.85em; }
.warn { color: #ffcc00; font-size: 0.85em; }
.issue { color: #ff6060; font-size: 0.85em; }
.footer { color: #2a5c2a; font-size: 0.8em; margin-top: 32px; border-top: 1px solid #1a3a1a; padding-top: 8px; }
"""


def _fmt_size(n: int) -> str:
    for unit in ("B", "K", "M", "G", "T"):
        if abs(n) < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} P"


def _risk_badge(level: str) -> str:
    cls = {
        "none": "badge-ok", "low": "badge-low",
        "medium": "badge-medium", "high": "badge-high", "critical": "badge-critical",
    }.get(level, "badge-ok")
    return f'<span class="badge {cls}">{level}</span>'


def to_json(result: ScanResult) -> str:
    """Serialize a ScanResult to a JSON string."""
    def _file_entry(f):
        return {
            "path": f.path, "size": f.size,
            "category": f.category, "risk_level": f.risk_level,
            "risk_message": f.risk_message, "last_modified": f.last_modified,
        }

    def _dir_entry(d):
        return {
            "path": d.path, "size": d.size, "file_count": d.file_count,
            "category": d.category, "risk_level": d.risk_level,
        }

    data = {
        "gdlex_inspector_version": "0.1.0",
        "scan_timestamp": result.scan_timestamp,
        "root_path": result.root_path,
        "total_size": result.total_size,
        "total_files": result.total_files,
        "total_dirs": result.total_dirs,
        "backend_used": result.backend_used,
        "platform_info": result.platform_info,
        "top_files": [_file_entry(f) for f in result.top_files],
        "top_dirs": [_dir_entry(d) for d in result.top_dirs],
        "extensions": [
            {"extension": e.extension, "total_size": e.total_size, "file_count": e.file_count}
            for e in result.extensions
        ],
        "categories": [
            {"category": c.category, "total_size": c.total_size, "file_count": c.file_count,
             "risk_level": c.risk_level}
            for c in result.categories
        ],
        "issues": [{"path": i.path, "error": i.error} for i in result.issues],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def to_csv(result: ScanResult) -> str:
    """Serialize a ScanResult to a multi-section CSV string (stdlib csv only)."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")

    w.writerow(["SECTION", "top_files"])
    w.writerow(["rank", "path", "size_bytes", "size_human", "category", "risk_level", "risk_message"])
    for i, f in enumerate(result.top_files, 1):
        w.writerow([i, f.path, f.size, _fmt_size(f.size), f.category, f.risk_level, f.risk_message])
    w.writerow([])

    w.writerow(["SECTION", "top_dirs"])
    w.writerow(["rank", "path", "size_bytes", "size_human", "file_count", "category", "risk_level"])
    for i, d in enumerate(result.top_dirs, 1):
        w.writerow([i, d.path, d.size, _fmt_size(d.size), d.file_count, d.category, d.risk_level])
    w.writerow([])

    w.writerow(["SECTION", "extensions"])
    w.writerow(["extension", "total_size_bytes", "total_size_human", "file_count"])
    for e in result.extensions:
        w.writerow([e.extension, e.total_size, _fmt_size(e.total_size), e.file_count])
    w.writerow([])

    w.writerow(["SECTION", "categories"])
    w.writerow(["category", "total_size_bytes", "total_size_human", "file_count", "risk_level"])
    for c in result.categories:
        w.writerow([c.category, c.total_size, _fmt_size(c.total_size), c.file_count, c.risk_level])
    w.writerow([])

    w.writerow(["SECTION", "issues"])
    w.writerow(["path", "error"])
    for iss in result.issues:
        w.writerow([iss.path, iss.error])

    return buf.getvalue()


def to_html(result: ScanResult) -> str:
    """Render a ScanResult to an HTML report with Matrix dark theme."""
    ts = result.scan_timestamp or datetime.utcnow().isoformat()
    platform = result.platform_info.get("platform_kind", "unknown")
    hostname = result.platform_info.get("hostname", "unknown")

    rows_files = ""
    for f in result.top_files:
        rows_files += (
            f'<tr><td class="path">{f.path}</td>'
            f'<td class="size">{_fmt_size(f.size)}</td>'
            f'<td>{f.category}</td>'
            f'<td>{_risk_badge(f.risk_level)}</td>'
            f'<td class="warn">{f.risk_message}</td></tr>\n'
        )

    rows_dirs = ""
    for d in result.top_dirs:
        rows_dirs += (
            f'<tr><td class="path">{d.path}</td>'
            f'<td class="size">{_fmt_size(d.size)}</td>'
            f'<td>{d.file_count}</td>'
            f'<td>{d.category}</td>'
            f'<td>{_risk_badge(d.risk_level)}</td></tr>\n'
        )

    rows_ext = ""
    for e in result.extensions[:20]:
        rows_ext += (
            f'<tr><td>{e.extension}</td>'
            f'<td class="size">{_fmt_size(e.total_size)}</td>'
            f'<td>{e.file_count}</td></tr>\n'
        )

    rows_cat = ""
    for c in result.categories:
        rows_cat += (
            f'<tr><td>{c.category}</td>'
            f'<td class="size">{_fmt_size(c.total_size)}</td>'
            f'<td>{c.file_count}</td>'
            f'<td>{_risk_badge(c.risk_level)}</td></tr>\n'
        )

    rows_issues = ""
    for i in result.issues:
        rows_issues += f'<tr><td class="path">{i.path}</td><td class="issue">{i.error}</td></tr>\n'

    issues_section = ""
    if result.issues:
        issues_section = f"""
<h2>Percorsi non accessibili ({len(result.issues)})</h2>
<table><thead><tr><th>Percorso</th><th>Errore</th></tr></thead>
<tbody>{rows_issues}</tbody></table>
"""

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GD LEX Inspector — Report occupazione disco</title>
<style>{_MATRIX_CSS}</style>
</head>
<body>
<h1>&#x1F50D; GD LEX Inspector — Report occupazione disco</h1>
<div class="meta">
  <b>Data scansione:</b> {ts}<br>
  <b>Host:</b> {hostname} &nbsp;|&nbsp; <b>Piattaforma:</b> {platform}<br>
  <b>Percorso analizzato:</b> {result.root_path}<br>
  <b>Backend:</b> {result.backend_used}
</div>
<table style="width:auto; margin-bottom:16px;">
  <tr><td>Dimensione totale</td><td class="size"><b>{_fmt_size(result.total_size)}</b></td></tr>
  <tr><td>File totali</td><td class="size"><b>{result.total_files}</b></td></tr>
  <tr><td>Cartelle totali</td><td class="size"><b>{result.total_dirs}</b></td></tr>
  <tr><td>Percorsi non accessibili</td><td class="size">{len(result.issues)}</td></tr>
</table>
<p style="color:#6af06a; font-size:0.85em;">
  &#x26A0;&#xFE0F; Questo report è solo diagnostico. Nessun file è stato modificato o cancellato.
</p>

<h2>Top file per dimensione</h2>
<table><thead><tr><th>Percorso</th><th>Dim.</th><th>Categoria</th><th>Rischio</th><th>Avviso</th></tr></thead>
<tbody>{rows_files}</tbody></table>

<h2>Top cartelle per dimensione</h2>
<table><thead><tr><th>Percorso</th><th>Dim.</th><th>File</th><th>Categoria</th><th>Rischio</th></tr></thead>
<tbody>{rows_dirs}</tbody></table>

<h2>Riepilogo per estensione</h2>
<table><thead><tr><th>Estensione</th><th>Dimensione</th><th>File</th></tr></thead>
<tbody>{rows_ext}</tbody></table>

<h2>Riepilogo per categoria</h2>
<table><thead><tr><th>Categoria</th><th>Dimensione</th><th>File</th><th>Rischio</th></tr></thead>
<tbody>{rows_cat}</tbody></table>

{issues_section}

<div class="footer">
  GD LEX Inspector v0.1.0 &mdash; GPL-3.0-or-later &mdash; Report generato il {ts}
</div>
</body>
</html>
"""
