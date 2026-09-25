"""Text and Markdown reports for a checked set of logs."""

from __future__ import annotations

import json

from .checks import CHECKS, Result

LABELS = {
    "rfis": "RFIs",
    "submittals": "Submittals",
    "change_events": "Change events",
    "daily_reports": "Daily reports",
    "punch_items": "Punch list",
}


def _fmt(value) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{k} {v}" for k, v in value.items()) or "none"
    if isinstance(value, list):
        return ", ".join(f"{a} ({b} days)" for a, b in value) or "none"
    return "n/a" if value is None else str(value)


def text_report(result: Result) -> str:
    out = [f"Project logs in {result.folder}, as of {result.as_of}", ""]
    for project, sections in result.metrics.items():
        out.append(project)
        for key, label in LABELS.items():
            if key in sections:
                out.append(f"  {label}")
                for name, value in sections[key].items():
                    out.append(f"    {name.replace('_', ' '):<28} {_fmt(value)}")
        out.append("")
    for f in result.findings:
        project = f"[{f.project_id}] " if f.project_id else ""
        where = f"  ({f.where()})" if f.where() else ""
        out.append(f"{f.severity.upper():<7} {f.check} {project}{f.message}{where}")
    counts = {s: sum(1 for f in result.findings if f.severity == s) for s in ("error", "warning", "info")}
    out.append("")
    out.append(f"{counts['error']} errors, {counts['warning']} warnings, {counts['info']} notes")
    return "\n".join(out) + "\n"


def markdown_report(result: Result) -> str:
    out = [f"# Project log review, as of {result.as_of}", ""]
    for project, sections in result.metrics.items():
        out += [f"## {project}", ""]
        for key, label in LABELS.items():
            if key in sections:
                out += [f"### {label}", "", "| Measure | Value |", "| --- | --- |"]
                out += [f"| {name.replace('_', ' ')} | {_fmt(value)} |" for name, value in sections[key].items()]
                out.append("")
        mine = [f for f in result.findings if f.project_id == project]
        if mine:
            out += ["### Needs attention", "", "| | Check | Finding | Where |", "| --- | --- | --- | --- |"]
            out += [f"| {f.severity} | {f.check} | {f.message} | {f.where()} |" for f in mine]
            out.append("")
    if result.findings:
        out += ["## What the checks mean", "", "| Check | Meaning |", "| --- | --- |"]
        out += [f"| {c} | {CHECKS[c][1]} |" for c in sorted({f.check for f in result.findings})]
        out.append("")
    return "\n".join(out)


def json_report(result: Result) -> str:
    return json.dumps(
        {
            "as_of": str(result.as_of),
            "metrics": result.metrics,
            "findings": [vars(f) for f in result.findings],
        },
        indent=2,
        default=str,
    )
