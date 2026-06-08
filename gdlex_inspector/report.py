"""Report generation (JSON, HTML, CSV) for gdlex-inspector."""

from __future__ import annotations

import csv
import io
import json
import os
from datetime import datetime, timezone
from html import escape

from .models import CategorySummary, DirectoryEntry, ScanResult
from .risk import risk_label_for_display, risk_style_for_display

_CATEGORY_COLORS = {
    "pst": "#00ff41",
    "ost": "#39ff14",
    "downloads": "#aaff00",
    "browser_cache": "#00e5ff",
    "temp": "#ffcc00",
    "node_modules": "#ff8c42",
    "venv": "#b388ff",
    "docker": "#00b8d4",
    "snap_flatpak": "#ff5c8a",
    "onedrive": "#448aff",
    "other": "#8aa68a",
}
_FALLBACK_COLORS = (
    "#00ff41", "#00e5ff", "#ffcc00", "#ff8c42",
    "#b388ff", "#ff5c8a", "#448aff", "#aaff00",
)

_MATRIX_CSS = """
body {
    background: #0a0f0a;
    color: #c8ffc8;
    font-family: "Noto Sans", "DejaVu Sans", system-ui, sans-serif;
    font-size: 15px;
    margin: 0;
    padding: 20px;
}
h1 { color: #00ff41; font-size: 1.4em; margin-bottom: 4px; }
h2 { color: #39ff14; font-size: 1.1em; border-bottom: 1px solid #1a4d1a; padding-bottom: 4px; margin-top: 24px; }
.meta { color: #6af06a; font-size: 0.9em; margin-bottom: 16px; }
.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
    margin: 18px 0;
}
.summary-card, .chart-card {
    background: #0b160b;
    border: 1px solid #1a4d1a;
    border-radius: 6px;
    padding: 14px;
}
.summary-label { color: #6af06a; font-size: 0.82em; }
.summary-value { color: #e0ffe0; font-size: 1.35em; font-weight: bold; margin-top: 5px; }
.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 16px;
    margin-top: 20px;
}
.chart-card h2 { margin-top: 0; }
.chart-svg { display: block; width: 100%; height: auto; }
.category-chart-layout {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 18px;
}
.category-chart-layout .chart-svg { max-width: 260px; }
.chart-legend { flex: 1 1 220px; min-width: 0; }
.legend-item {
    display: grid;
    grid-template-columns: 12px minmax(90px, 1fr) auto;
    gap: 8px;
    align-items: center;
    padding: 4px 0;
    border-bottom: 1px solid #122412;
}
.legend-swatch { width: 10px; height: 10px; border-radius: 50%; }
.legend-value { color: #9bd69b; white-space: nowrap; text-align: right; }
.empty-state { color: #6f936f; text-align: center; padding: 20px 8px; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 0.82em; }
.badge-ok { background: #0d2b0d; color: #39ff14; border: 1px solid #1f5e1f; }
.badge-low { background: #1a2b00; color: #aaff00; border: 1px solid #3a5c00; }
.badge-medium { background: #2b1a00; color: #ffcc00; border: 1px solid #5c3a00; }
.badge-high { background: #2b0000; color: #ff6060; border: 1px solid #5c0000; }
.badge-critical { background: #400000; color: #ff2222; border: 1px solid #800000; font-weight: bold; }
.badge-system { background: #0b2633; color: #63c7ee; border: 1px solid #24576b; }
table { width: 100%; border-collapse: collapse; margin-top: 8px; }
th { background: #0d2b0d; color: #39ff14; text-align: left; padding: 7px 10px; font-size: 0.9em; }
td { padding: 6px 10px; border-bottom: 1px solid #0d1a0d; word-break: break-all; }
tr:hover td { background: #0d1a0d; }
.size { text-align: right; white-space: nowrap; }
.path { font-family: 'Courier New', Courier, monospace; font-size: 0.85em; }
.warn { color: #ffcc00; font-size: 0.85em; }
.issue { color: #ff6060; font-size: 0.85em; }
.footer { color: #2a5c2a; font-size: 0.8em; margin-top: 32px; border-top: 1px solid #1a3a1a; padding-top: 8px; }
"""


def calculate_percentages(values: list[int]) -> list[float]:
    """Return non-negative percentages that add up to 100 when data exists."""
    normalized = [max(0, value) for value in values]
    total = sum(normalized)
    if total == 0:
        return [0.0] * len(values)

    percentages = []
    accumulated = 0.0
    last_positive = max(i for i, value in enumerate(normalized) if value > 0)
    for i, value in enumerate(normalized):
        if i == last_positive:
            percentage = 100.0 - accumulated
        else:
            percentage = value / total * 100.0
            accumulated += percentage
        percentages.append(percentage)
    return percentages


def category_color(category: str) -> str:
    """Return a stable Matrix-compatible color for a category name."""
    if category in _CATEGORY_COLORS:
        return _CATEGORY_COLORS[category]
    index = sum(category.encode("utf-8")) % len(_FALLBACK_COLORS)
    return _FALLBACK_COLORS[index]


def category_donut_svg(categories: list[CategorySummary]) -> str:
    """Render category sizes as an inline SVG donut chart."""
    values = [category.total_size for category in categories]
    percentages = calculate_percentages(values)
    total = sum(max(0, value) for value in values)
    radius = 72
    segments = []
    offset = 0.0

    for category, percentage in zip(categories, percentages):
        if percentage <= 0:
            continue
        segments.append(
            f'<circle cx="110" cy="110" r="{radius}" fill="none" '
            f'stroke="{category_color(category.category)}" stroke-width="28" '
            f'stroke-dasharray="{percentage:.6f} {100 - percentage:.6f}" '
            f'stroke-dashoffset="{-offset:.6f}" pathLength="100">'
            f'<title>{escape(category.category)}: {_fmt_size(category.total_size)} '
            f'({percentage:.1f}%)</title></circle>'
        )
        offset += percentage

    center_text = _fmt_size(total) if total else "Nessun dato"
    center_class = "donut-total" if total else "donut-empty"
    return (
        '<svg id="category-chart" class="chart-svg" viewBox="0 0 220 220" '
        'role="img" aria-labelledby="category-chart-title category-chart-desc">'
        '<title id="category-chart-title">Distribuzione dimensioni per categoria</title>'
        '<desc id="category-chart-desc">Grafico donut statico delle categorie rilevate.</desc>'
        '<circle cx="110" cy="110" r="72" fill="none" stroke="#153015" stroke-width="28"/>'
        f'<g transform="rotate(-90 110 110)">{"".join(segments)}</g>'
        f'<text x="110" y="106" text-anchor="middle" fill="#39ff14" '
        f'font-size="13" font-weight="bold">{escape(center_text)}</text>'
        f'<text class="{center_class}" x="110" y="126" text-anchor="middle" '
        f'fill="#6af06a" font-size="9">totale categorie</text>'
        '</svg>'
    )


def top_directories_bar_svg(directories: list[DirectoryEntry]) -> str:
    """Render top directory sizes as an inline horizontal SVG bar chart."""
    chart_width = 900
    label_width = 330
    bar_width = 430
    row_height = 48
    height = max(120, len(directories) * row_height + 24)
    maximum = max((max(0, directory.size) for directory in directories), default=0)
    rows = []

    for index, directory in enumerate(directories):
        y = 18 + index * row_height
        width = (max(0, directory.size) / maximum * bar_width) if maximum else 0
        label = directory.path
        if len(label) > 43:
            label = "..." + label[-40:]
        rows.append(
            f'<g><title>{escape(directory.path)}: {_fmt_size(directory.size)}</title>'
            f'<text x="8" y="{y + 17}" fill="#c8ffc8" font-size="12">'
            f'{escape(label)}</text>'
            f'<rect x="{label_width}" y="{y}" width="{bar_width}" height="22" '
            f'rx="3" fill="#102810"/>'
            f'<rect x="{label_width}" y="{y}" width="{width:.2f}" height="22" '
            f'rx="3" fill="{category_color(directory.category)}"/>'
            f'<text x="{label_width + bar_width + 10}" y="{y + 16}" '
            f'fill="#9bd69b" font-size="11">{_fmt_size(directory.size)}</text></g>'
        )

    empty = ""
    if not directories:
        empty = (
            '<text x="450" y="60" text-anchor="middle" fill="#6f936f" '
            'font-size="14">Nessuna cartella disponibile</text>'
        )

    return (
        f'<svg id="top-directories-chart" class="chart-svg" '
        f'viewBox="0 0 {chart_width} {height}" role="img" '
        'aria-labelledby="directories-chart-title directories-chart-desc">'
        '<title id="directories-chart-title">Top cartelle per dimensione</title>'
        '<desc id="directories-chart-desc">Grafico statico a barre orizzontali.</desc>'
        f'{"".join(rows)}{empty}</svg>'
    )


def _fmt_size(n: int) -> str:
    if abs(n) < 1024:
        return f"{n} B"
    value = float(n)
    for unit in ("KiB", "MiB", "GiB", "TiB"):
        value /= 1024.0
        if abs(value) < 1024.0:
            return f"{value:.1f} {unit}"
    return f"{value / 1024.0:.1f} PiB"


def _risk_badge(level: str, category: str = "", path: str = "", size: int = 0) -> str:
    style = risk_style_for_display(level, category, path, size)
    label = risk_label_for_display(level, category, path, size)
    cls = {
        "none": "badge-ok", "low": "badge-low",
        "medium": "badge-medium", "high": "badge-high",
        "critical": "badge-critical", "system": "badge-system",
    }.get(style, "badge-ok")
    return f'<span class="badge {cls}">{escape(label)}</span>'


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
    w.writerow([
        "rank", "path", "size_bytes", "size_human", "category",
        "sensitivity", "risk_level", "risk_message",
    ])
    for i, f in enumerate(result.top_files, 1):
        w.writerow([
            i, f.path, f.size, _fmt_size(f.size), f.category,
            risk_label_for_display(f.risk_level, f.category, f.path, f.size),
            f.risk_level, f.risk_message,
        ])
    w.writerow([])

    w.writerow(["SECTION", "top_dirs"])
    w.writerow([
        "rank", "path", "size_bytes", "size_human", "file_count", "category",
        "sensitivity", "risk_level",
    ])
    for i, d in enumerate(result.top_dirs, 1):
        w.writerow([
            i, d.path, d.size, _fmt_size(d.size), d.file_count, d.category,
            risk_label_for_display(d.risk_level, d.category, d.path, d.size),
            d.risk_level,
        ])
    w.writerow([])

    w.writerow(["SECTION", "extensions"])
    w.writerow(["extension", "total_size_bytes", "total_size_human", "file_count"])
    for e in result.extensions:
        w.writerow([e.extension, e.total_size, _fmt_size(e.total_size), e.file_count])
    w.writerow([])

    w.writerow(["SECTION", "categories"])
    w.writerow([
        "category", "total_size_bytes", "total_size_human", "file_count",
        "sensitivity", "risk_level",
    ])
    for c in result.categories:
        w.writerow([
            c.category, c.total_size, _fmt_size(c.total_size), c.file_count,
            risk_label_for_display(c.risk_level, c.category, size=c.total_size),
            c.risk_level,
        ])
    w.writerow([])

    w.writerow(["SECTION", "issues"])
    w.writerow(["path", "error"])
    for iss in result.issues:
        w.writerow([iss.path, iss.error])

    return buf.getvalue()


def to_html(result: ScanResult) -> str:
    """Render a ScanResult to an HTML report with Matrix dark theme."""
    ts = result.scan_timestamp or datetime.now(timezone.utc).isoformat()
    platform = result.platform_info.get("platform_kind", "unknown")
    hostname = result.platform_info.get("hostname", "unknown")

    rows_files = ""
    for f in result.top_files:
        rows_files += (
            f'<tr><td class="path">{f.path}</td>'
            f'<td class="size">{_fmt_size(f.size)}</td>'
            f'<td>{f.category}</td>'
            f'<td>{_risk_badge(f.risk_level, f.category, f.path, f.size)}</td>'
            f'<td class="warn">{f.risk_message}</td></tr>\n'
        )

    rows_dirs = ""
    for d in result.top_dirs:
        rows_dirs += (
            f'<tr><td class="path">{d.path}</td>'
            f'<td class="size">{_fmt_size(d.size)}</td>'
            f'<td>{d.file_count}</td>'
            f'<td>{d.category}</td>'
            f'<td>{_risk_badge(d.risk_level, d.category, d.path, d.size)}</td></tr>\n'
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
            f'<td>{_risk_badge(c.risk_level, c.category, size=c.total_size)}</td></tr>\n'
        )

    rows_issues = ""
    for i in result.issues:
        rows_issues += f'<tr><td class="path">{i.path}</td><td class="issue">{i.error}</td></tr>\n'

    category_percentages = calculate_percentages(
        [category.total_size for category in result.categories]
    )
    legend_items = ""
    for category, percentage in zip(result.categories, category_percentages):
        legend_items += (
            '<div class="legend-item">'
            f'<span class="legend-swatch" style="background:{category_color(category.category)}"></span>'
            f'<span>{escape(category.category)}</span>'
            f'<span class="legend-value">{_fmt_size(category.total_size)} '
            f'({percentage:.1f}%)</span></div>'
        )
    if not legend_items:
        legend_items = '<div class="empty-state">Nessuna categoria disponibile</div>'

    category_chart = category_donut_svg(result.categories)
    directories_chart = top_directories_bar_svg(result.top_dirs)

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
<section class="summary-grid" aria-label="Riepilogo scansione">
  <div class="summary-card"><div class="summary-label">Dimensione totale</div><div class="summary-value">{_fmt_size(result.total_size)}</div></div>
  <div class="summary-card"><div class="summary-label">File totali</div><div class="summary-value">{result.total_files}</div></div>
  <div class="summary-card"><div class="summary-label">Cartelle totali</div><div class="summary-value">{result.total_dirs}</div></div>
  <div class="summary-card"><div class="summary-label">Percorsi non accessibili</div><div class="summary-value">{len(result.issues)}</div></div>
</section>
<p style="color:#6af06a; font-size:0.85em;">
  &#x26A0;&#xFE0F; Questo report è solo diagnostico. Nessun file è stato modificato o cancellato.
  La sensibilità indica il rischio di rimozione o modifica, non la dimensione.
</p>

<section class="charts-grid" aria-label="Grafici statici">
  <article class="chart-card">
    <h2>Distribuzione per categoria</h2>
    <div class="category-chart-layout">
      {category_chart}
      <div class="chart-legend" aria-label="Legenda categorie">{legend_items}</div>
    </div>
  </article>
  <article class="chart-card">
    <h2>Top cartelle — grafico</h2>
    {directories_chart}
  </article>
</section>

<h2>Top file per dimensione</h2>
<table><thead><tr><th>Percorso</th><th>Dim.</th><th>Categoria</th><th>Sensibilità</th><th>Avviso</th></tr></thead>
<tbody>{rows_files}</tbody></table>

<h2>Top cartelle per dimensione</h2>
<table><thead><tr><th>Percorso</th><th>Dim.</th><th>File</th><th>Categoria</th><th>Sensibilità</th></tr></thead>
<tbody>{rows_dirs}</tbody></table>

<h2>Riepilogo per estensione</h2>
<table><thead><tr><th>Estensione</th><th>Dimensione</th><th>File</th></tr></thead>
<tbody>{rows_ext}</tbody></table>

<h2>Riepilogo per categoria</h2>
<table><thead><tr><th>Categoria</th><th>Dimensione</th><th>File</th><th>Sensibilità</th></tr></thead>
<tbody>{rows_cat}</tbody></table>

{issues_section}

<div class="footer">
  GD LEX Inspector v0.1.0 &mdash; GPL-3.0-or-later &mdash; Report generato il {ts}
</div>
</body>
</html>
"""
