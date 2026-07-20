#!/usr/bin/env python3
"""
Codebase Audit HTML Report Generator

Reads an audit state JSON file and produces a self-contained, navigable,
filterable HTML report.

Usage:
    python generate-html-report.py --state .audit-state.json --output /tmp/audit-report.html
"""

import argparse
import json
import os
import sys
from datetime import datetime


SEVERITY_COLORS = {
    "critical": "#dc2626",
    "high": "#ea580c",
    "medium": "#ca8a04",
    "low": "#2563eb",
    "info": "#6b7280",
}

CONFIDENCE_COLORS = {
    "confirmed": "#16a34a",
    "probable": "#ca8a04",
    "hypothesis": "#9ca3af",
}

CATEGORY_LABELS = {
    "performance": "Performance",
    "bugs": "Bugs",
    "security": "Security",
}


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def escape_js(text: str) -> str:
    """Escape for JavaScript string context."""
    if not text:
        return ""
    return escape_html(text).replace("\n", "\\n").replace("`", "\\`")


def generate_stats(findings: list) -> dict:
    """Compute statistics from findings."""
    stats = {
        "total": len(findings),
        "by_category": {},
        "by_severity": {},
        "by_confidence": {},
        "by_module": {},
        "by_status": {},
    }
    for f in findings:
        cat = f.get("category", "unknown")
        sev = f.get("severity", "unknown")
        conf = f.get("confidence", "unknown")
        mod = f.get("module", "unknown")
        status = f.get("status", "open")

        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
        stats["by_confidence"][conf] = stats["by_confidence"].get(conf, 0) + 1
        stats["by_module"][mod] = stats["by_module"].get(mod, 0) + 1
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
    return stats


def render_severity_badge(severity: str) -> str:
    color = SEVERITY_COLORS.get(severity, "#6b7280")
    return f'<span class="inline-block px-2 py-0.5 rounded text-xs font-semibold text-white" style="background:{color}">{escape_html(severity.upper())}</span>'


def render_confidence_badge(confidence: str) -> str:
    color = CONFIDENCE_COLORS.get(confidence, "#9ca3af")
    return f'<span class="inline-block px-2 py-0.5 rounded text-xs font-semibold text-white" style="background:{color}">{escape_html(confidence)}</span>'


def render_finding_card(f: dict, index: int) -> str:
    """Render a single finding card."""
    fid = escape_html(f.get("id", ""))
    title = escape_html(f.get("title", ""))
    category = f.get("category", "")
    severity = f.get("severity", "")
    confidence = f.get("confidence", "")
    status = f.get("status", "open")
    module = escape_html(f.get("module", ""))
    file_path = escape_html(f.get("file", ""))
    lines = escape_html(f.get("lines", ""))
    description = escape_html(f.get("description", ""))
    evidence = escape_html(f.get("evidence", ""))
    reasoning = escape_html(f.get("reasoning", ""))
    impact = escape_html(f.get("impact", ""))
    reproduction = escape_html(f.get("reproduction", ""))
    recommendation = escape_html(f.get("recommendation", ""))
    fix_risk = escape_html(f.get("fix_risk", ""))
    tests_needed = escape_html(f.get("tests_needed", ""))
    dependencies = f.get("dependencies", [])
    source = escape_html(f.get("source", ""))
    detected_by = escape_html(f.get("detected_by", ""))

    deps_html = ""
    if dependencies:
        deps_html = '<div class="mt-2 text-sm"><strong>Dependencies:</strong> ' + ", ".join(
            f'<a href="#{escape_html(d)}" class="text-blue-600 hover:underline">{escape_html(d)}</a>'
            for d in dependencies
        ) + "</div>"

    repro_html = ""
    if reproduction:
        repro_html = f'<div class="mt-3 p-3 bg-gray-50 rounded border-l-4 border-yellow-400"><strong>Reproduction:</strong><pre class="mt-1 text-sm whitespace-pre-wrap font-mono">{reproduction}</pre></div>'

    source_html = ""
    if source:
        source_html = f'<div class="mt-2 text-sm text-gray-600"><strong>Source:</strong> {source}</div>'

    detected_html = ""
    if detected_by:
        detected_html = f'<div class="mt-1 text-sm text-gray-600"><strong>Detected by:</strong> {detected_by}</div>'

    return f"""
    <div data-finding data-category="{category}" data-severity="{severity}"
         data-confidence="{confidence}" data-module="{module}" data-status="{status}"
         id="{fid}"
         class="finding-card mb-6 p-5 bg-white rounded-lg shadow border border-gray-200">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-3">
          <a href="#{fid}" class="text-lg font-bold text-gray-800">{fid}</a>
          <span class="text-lg font-semibold text-gray-700">{title}</span>
        </div>
        <div class="flex items-center gap-2">
          {render_severity_badge(severity)}
          {render_confidence_badge(confidence)}
          <span class="inline-block px-2 py-0.5 rounded text-xs font-semibold bg-gray-200 text-gray-700">{escape_html(status)}</span>
        </div>
      </div>
      <div class="mt-2 text-sm text-gray-600">
        <strong>Category:</strong> {escape_html(CATEGORY_LABELS.get(category, category))} |
        <strong>Module:</strong> {module} |
        <strong>File:</strong> <code>{file_path}:{lines}</code>
      </div>
      <div class="mt-3 text-gray-700">{description}</div>
      <div class="mt-3 p-3 bg-gray-900 rounded overflow-x-auto">
        <pre class="text-sm text-green-400 font-mono whitespace-pre">{evidence}</pre>
      </div>
      <div class="mt-3 text-sm text-gray-700"><strong>Reasoning:</strong> {reasoning}</div>
      <div class="mt-2 text-sm"><strong class="text-red-600">Impact:</strong> {impact}</div>
      {repro_html}
      <div class="mt-3 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
        <strong>Recommendation:</strong> {recommendation}
      </div>
      <div class="mt-2 text-sm">
        <strong>Fix Risk:</strong> <span class="{'text-red-600' if fix_risk=='high' else 'text-yellow-600' if fix_risk=='medium' else 'text-green-600'}">{fix_risk}</span> |
        <strong>Tests Needed:</strong> {tests_needed}
      </div>
      {deps_html}
      {source_html}
      {detected_html}
    </div>
    """


def generate_html(state: dict, output_path: str) -> str:
    """Generate the full HTML report."""
    findings = state.get("findings", [])
    stats = generate_stats(findings)
    meta = state.get("metadata", {})
    project_map = state.get("project_map", {})
    capabilities = state.get("capabilities", {})
    config = state.get("config", {})
    validation = state.get("validation", {})
    limitations = state.get("limitations", [])
    sources = state.get("sources_consulted", [])

    # Technologies
    technologies = project_map.get("technologies", [])
    tech_html = ""
    if technologies:
        tech_items = [
            f"<tr><td class='px-3 py-1 font-mono'>{escape_html(t.get('name',''))}</td><td class='px-3 py-1'>{escape_html(t.get('version',''))}</td><td class='px-3 py-1'>{escape_html(t.get('role',''))}</td></tr>"
            for t in technologies
        ]
        tech_html = f"""
        <div class="mb-6">
          <h2 class="text-lg font-bold mb-2">Technologies Detected</h2>
          <table class="w-full text-sm border">
            <thead><tr class="bg-gray-100"><th class="px-3 py-1 text-left">Name</th><th class="px-3 py-1 text-left">Version</th><th class="px-3 py-1 text-left">Role</th></tr></thead>
            <tbody>{"".join(tech_items)}</tbody>
          </table>
        </div>
        """

    # Capability map
    cap_html = ""
    if capabilities:
        cap_rows = []
        for cap, info in capabilities.items():
            available = info.get("available", False) if isinstance(info, dict) else False
            tool = info.get("tool", "") if isinstance(info, dict) else str(info)
            notes = info.get("notes", "") if isinstance(info, dict) else ""
            status = "✅ Available" if available else "❌ Missing"
            color = "text-green-600" if available else "text-red-600"
            cap_rows.append(
                f"<tr><td class='px-3 py-1 font-mono'>{escape_html(cap)}</td>"
                f"<td class='px-3 py-1 {color}'>{status}</td>"
                f"<td class='px-3 py-1'>{escape_html(tool)}</td>"
                f"<td class='px-3 py-1 text-gray-600'>{escape_html(notes)}</td></tr>"
            )
        cap_html = f"""
        <div class="mb-6">
          <h2 class="text-lg font-bold mb-2">Tools & Capabilities</h2>
          <table class="w-full text-sm border">
            <thead><tr class="bg-gray-100"><th class="px-3 py-1 text-left">Capability</th><th class="px-3 py-1 text-left">Status</th><th class="px-3 py-1 text-left">Tool</th><th class="px-3 py-1 text-left">Notes</th></tr></thead>
            <tbody>{"".join(cap_rows)}</tbody>
          </table>
        </div>
        """

    # Stats cards
    cat_cards = ""
    for cat, label in CATEGORY_LABELS.items():
        count = stats["by_category"].get(cat, 0)
        cat_cards += f"""
        <div class="bg-white p-4 rounded-lg shadow border border-gray-200 text-center">
          <div class="text-3xl font-bold text-gray-800">{count}</div>
          <div class="text-sm text-gray-600">{label}</div>
        </div>
        """

    sev_bars = ""
    for sev in ["critical", "high", "medium", "low", "info"]:
        count = stats["by_severity"].get(sev, 0)
        color = SEVERITY_COLORS.get(sev, "#6b7280")
        pct = (count / stats["total"] * 100) if stats["total"] else 0
        sev_bars += f"""
        <div class="flex items-center gap-2 mb-1">
          <span class="text-xs w-20 capitalize">{sev}</span>
          <div class="flex-1 bg-gray-200 rounded h-5 relative">
            <div style="width:{pct:.0f}%;background:{color}" class="h-5 rounded"></div>
          </div>
          <span class="text-xs w-8 text-right">{count}</span>
        </div>
        """

    # Module filter options
    modules = sorted(stats["by_module"].keys())
    module_options = '<option value="all">All Modules</option>' + "".join(
        f'<option value="{escape_html(m)}">{escape_html(m)}</option>' for m in modules
    )

    # Finding cards
    finding_cards = "".join(render_finding_card(f, i) for i, f in enumerate(findings))

    # Limitations
    lim_html = ""
    if limitations:
        lim_items = "".join(f"<li>{escape_html(l)}</li>" for l in limitations)
        lim_html = f"""
        <div class="mb-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
          <h2 class="text-lg font-bold mb-2">Limitations</h2>
          <ul class="list-disc list-inside text-sm text-gray-700">{lim_items}</ul>
        </div>
        """

    # Sources
    src_html = ""
    if sources:
        src_items = "".join(f"<li><a href='{escape_html(s)}' class='text-blue-600 hover:underline' target='_blank'>{escape_html(s)}</a></li>" for s in sources)
        src_html = f"""
        <div class="mb-6">
          <h2 class="text-lg font-bold mb-2">Sources Consulted</h2>
          <ul class="list-disc list-inside text-sm text-blue-600">{src_items}</ul>
        </div>
        """

    # Validation results
    val_html = ""
    if validation:
        val_result = validation.get("result", "not_run")
        val_checks = validation.get("checks", [])
        val_color = {"passed": "text-green-600", "failed": "text-red-600", "partial": "text-yellow-600", "not_run": "text-gray-600", "impossible": "text-red-600"}.get(val_result, "text-gray-600")
        check_rows = ""
        for chk in val_checks:
            cr = chk.get("result", "not_run")
            cc = {"passed": "text-green-600", "failed": "text-red-600", "not_run": "text-gray-600", "unavailable": "text-gray-400"}.get(cr, "text-gray-600")
            check_rows += f"<tr><td class='px-3 py-1'>{escape_html(chk.get('name',''))}</td><td class='px-3 py-1 {cc}'>{escape_html(cr)}</td><td class='px-3 py-1 text-gray-600'><pre class='text-xs whitespace-pre-wrap'>{escape_html(chk.get('output',''))}</pre></td></tr>"
        val_html = f"""
        <div class="mb-6">
          <h2 class="text-lg font-bold mb-2">Validation Results</h2>
          <p class="text-sm mb-2">Overall: <span class="font-bold {val_color}">{escape_html(val_result)}</span></p>
          <table class="w-full text-sm border">
            <thead><tr class="bg-gray-100"><th class="px-3 py-1 text-left">Check</th><th class="px-3 py-1 text-left">Result</th><th class="px-3 py-1 text-left">Output</th></tr></thead>
            <tbody>{check_rows}</tbody>
          </table>
        </div>
        """

    # Config summary
    config_html = ""
    if config:
        areas = ", ".join(config.get("areas", []))
        config_html = f"""
        <div class="mb-4 text-sm text-gray-600">
          <strong>Audit areas:</strong> {escape_html(areas)} |
          <strong>Scope:</strong> {escape_html(str(config.get('scope','')))} |
          <strong>Depth:</strong> {escape_html(str(config.get('depth','')))} |
          <strong>Mode:</strong> {escape_html(str(config.get('mode','')))}
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Codebase Audit Report — {escape_html(meta.get("repo_root", "Unknown"))}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    .finding-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
    @media print {{ .no-print {{ display: none; }} .finding-card {{ break-inside: avoid; }} }}
  </style>
</head>
<body class="bg-gray-100 min-h-screen">
  <div class="max-w-5xl mx-auto p-6">

    <!-- Header -->
    <div class="bg-white p-6 rounded-lg shadow mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Codebase Audit Report</h1>
      <p class="text-sm text-gray-600 mt-1">
        <strong>Repository:</strong> {escape_html(meta.get("repo_root", "Unknown"))} |
        <strong>Date:</strong> {escape_html(meta.get("last_updated", datetime.now().isoformat()))} |
        <strong>Harness:</strong> {escape_html(meta.get("harness", "Unknown"))}
      </p>
      <div class="mt-4 p-3 bg-gray-50 rounded text-sm">
        <strong>Executive Summary:</strong> {stats["total"]} findings —
        {stats["by_severity"].get("critical", 0)} critical,
        {stats["by_severity"].get("high", 0)} high,
        {stats["by_severity"].get("medium", 0)} medium,
        {stats["by_severity"].get("low", 0)} low.
        {stats["by_confidence"].get("confirmed", 0)} confirmed,
        {stats["by_confidence"].get("probable", 0)} probable,
        {stats["by_confidence"].get("hypothesis", 0)} hypothesis.
      </div>
      {config_html}
    </div>

    <!-- Stats Dashboard -->
    <div class="mb-6">
      <h2 class="text-lg font-bold mb-3">Statistics</h2>
      <div class="grid grid-cols-3 gap-4 mb-4">{cat_cards}</div>
      <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-sm font-bold mb-2">By Severity</h3>
        {sev_bars}
      </div>
    </div>

    {tech_html}
    {cap_html}

    <!-- Filter Bar -->
    <div class="no-print mb-6 p-4 bg-white rounded-lg shadow sticky top-0 z-10">
      <div class="flex flex-wrap gap-3 items-center">
        <span class="font-bold text-sm">Filter:</span>
        <select id="f-category" class="text-sm border rounded px-2 py-1">
          <option value="all">All Categories</option>
          <option value="performance">Performance</option>
          <option value="bugs">Bugs</option>
          <option value="security">Security</option>
        </select>
        <select id="f-severity" class="text-sm border rounded px-2 py-1">
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
          <option value="info">Info</option>
        </select>
        <select id="f-confidence" class="text-sm border rounded px-2 py-1">
          <option value="all">All Confidence</option>
          <option value="confirmed">Confirmed</option>
          <option value="probable">Probable</option>
          <option value="hypothesis">Hypothesis</option>
        </select>
        <select id="f-module" class="text-sm border rounded px-2 py-1">
          {module_options}
        </select>
        <select id="f-status" class="text-sm border rounded px-2 py-1">
          <option value="all">All Status</option>
          <option value="open">Open</option>
          <option value="fixing">Fixing</option>
          <option value="fixed">Fixed</option>
          <option value="wontfix">Won't Fix</option>
          <option value="skipped">Skipped</option>
        </select>
        <input type="text" id="f-search" placeholder="Search..." class="text-sm border rounded px-2 py-1 flex-1 min-w-[150px]" oninput="applyFilters()">
        <button onclick="resetFilters()" class="text-sm px-3 py-1 bg-gray-200 rounded hover:bg-gray-300">Reset</button>
      </div>
      <div id="filter-count" class="text-xs text-gray-500 mt-2">Showing all {len(findings)} findings</div>
    </div>

    <!-- Findings -->
    <div id="findings-container">
      {finding_cards if finding_cards else '<p class="text-gray-500 italic">No findings to display.</p>'}
    </div>

    {lim_html}
    {src_html}
    {val_html}

    <!-- Footer -->
    <div class="text-center text-xs text-gray-400 mt-6 mb-6">
      Generated by Codebase Audit Skill — {escape_html(datetime.now().isoformat())}
    </div>
  </div>

  <script>
    const filters = {{ category: 'all', severity: 'all', confidence: 'all', module: 'all', status: 'all', search: '' }};

    function applyFilters() {{
      const cards = document.querySelectorAll('[data-finding]');
      let visible = 0;
      cards.forEach(el => {{
        const match = (
          (filters.category === 'all' || el.dataset.category === filters.category) &&
          (filters.severity === 'all' || el.dataset.severity === filters.severity) &&
          (filters.confidence === 'all' || el.dataset.confidence === filters.confidence) &&
          (filters.module === 'all' || el.dataset.module === filters.module) &&
          (filters.status === 'all' || el.dataset.status === filters.status) &&
          (filters.search === '' || el.textContent.toLowerCase().includes(filters.search.toLowerCase()))
        );
        el.style.display = match ? 'block' : 'none';
        if (match) visible++;
      }});
      document.getElementById('filter-count').textContent = `Showing ${{visible}} of ${{cards.length}} findings`;
    }}

    function resetFilters() {{
      filters.category = 'all'; filters.severity = 'all'; filters.confidence = 'all';
      filters.module = 'all'; filters.status = 'all'; filters.search = '';
      document.getElementById('f-category').value = 'all';
      document.getElementById('f-severity').value = 'all';
      document.getElementById('f-confidence').value = 'all';
      document.getElementById('f-module').value = 'all';
      document.getElementById('f-status').value = 'all';
      document.getElementById('f-search').value = '';
      applyFilters();
    }}

    ['f-category', 'f-severity', 'f-confidence', 'f-module', 'f-status'].forEach(id => {{
      const el = document.getElementById(id);
      const key = id.replace('f-', '');
      el.addEventListener('change', (e) => {{ filters[key] = e.target.value; applyFilters(); }});
    }});

    document.getElementById('f-search').addEventListener('input', (e) => {{ filters.search = e.target.value; applyFilters(); }});
  </script>
</body>
</html>
"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate HTML report from audit state JSON.")
    parser.add_argument("--state", required=True, help="Path to audit state JSON file")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    args = parser.parse_args()

    if not os.path.exists(args.state):
        print(f"Error: State file not found: {args.state}", file=sys.stderr)
        sys.exit(1)

    with open(args.state, "r") as f:
        state = json.load(f)

    html = generate_html(state, args.output)

    with open(args.output, "w") as f:
        f.write(html)

    print(f"Report generated: {args.output}")
    print(f"Findings: {len(state.get('findings', []))}")


if __name__ == "__main__":
    main()