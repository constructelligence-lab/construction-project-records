"""The record schema, reading record files against it, and generating JSON Schema from it.

The schema lives in ``schema/fields.csv`` so that a project engineer can read it in a spreadsheet and a script
can read it in CI. Each record type is one CSV file named after it (``rfis.csv``, ``submittals.csv`` ...).
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from . import values

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "fields.csv"
RECORDS = ["rfis", "submittals", "change_events", "daily_reports", "punch_items"]


@dataclass(frozen=True)
class Field:
    record: str
    name: str
    type: str
    required: bool
    key: bool
    allowed: tuple[str, ...]
    description: str


@dataclass
class Finding:
    check: str
    severity: str  # error | warning | info
    message: str
    record: str = ""
    line: int = 0
    project_id: str = ""

    def where(self) -> str:
        return f"{self.record}.csv line {self.line}" if self.record and self.line else self.record


@dataclass
class Table:
    record: str
    rows: list[dict[str, Any]] = field(default_factory=list)
    lines: list[int] = field(default_factory=list)
    present: bool = False

    def items(self):
        return zip(self.lines, self.rows)


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, list[Field]]:
    schema: dict[str, list[Field]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            schema.setdefault(row["record"], []).append(
                Field(
                    row["record"],
                    row["field"],
                    row["type"],
                    row["required"] == "yes",
                    row["key"] == "yes",
                    tuple(a for a in row["allowed"].split("|") if a),
                    row["description"],
                )
            )
    return schema


PARSERS: dict[str, Callable[[str], Any]] = {
    "text": lambda s: s.strip() or None,
    "enum": lambda s: s.strip() or None,
    "money": values.parse_money,
    "date": values.parse_date,
    "int": values.parse_int,
}


def read_table(folder: Path, record: str, fields: list[Field], findings: list[Finding]) -> Table:
    path = folder / f"{record}.csv"
    table = Table(record)
    if not path.exists():
        return table
    table.present = True
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing = [f.name for f in fields if f.required and f.name not in header]
        if missing:
            findings.append(Finding("Q02", "error", f"missing required column(s): {', '.join(missing)}", record))
            return table
        keys: dict[tuple, int] = {}
        key_fields = [f.name for f in fields if f.key]
        for line, raw in enumerate(reader, start=2):
            row: dict[str, Any] = {}
            project = (raw.get("project_id") or "").strip()
            for f in fields:
                text = raw.get(f.name) or ""
                try:
                    value = PARSERS[f.type](text)
                except ValueError as exc:
                    findings.append(Finding("Q02", "error", f"{f.name}: {exc}", record, line, project))
                    value = None
                if value is None and f.required and not text.strip():
                    findings.append(Finding("Q02", "error", f"{f.name} is required", record, line, project))
                if value is not None and f.allowed and value not in f.allowed:
                    findings.append(Finding("Q02", "error", f"{f.name} {value!r} is not one of {', '.join(f.allowed)}", record, line, project))
                row[f.name] = value
            key = tuple(row[k] for k in key_fields)
            if all(k is not None for k in key):
                if key in keys:
                    findings.append(
                        Finding("Q01", "error", f"duplicate {'/'.join(map(str, key))} (first on line {keys[key]})", record, line, project)
                    )
                else:
                    keys[key] = line
            table.rows.append(row)
            table.lines.append(line)
    return table


def read_folder(folder: Path) -> tuple[dict[str, Table], list[Finding]]:
    schema = load_schema()
    findings: list[Finding] = []
    return {r: read_table(folder, r, schema[r], findings) for r in RECORDS}, findings


def json_schema(record: str) -> dict[str, Any]:
    """A JSON Schema (draft 2020-12) for one record, generated from fields.csv so the two never disagree."""
    fields = load_schema()[record]
    props: dict[str, Any] = {}
    for f in fields:
        prop: dict[str, Any] = {"description": f.description}
        if f.type == "date":
            prop.update(type="string", format="date")
        elif f.type == "int":
            prop.update(type="integer")
        elif f.type == "money":
            prop.update(type="string", pattern=r"^-?\d+(\.\d{1,2})?$")
        elif f.type == "enum":
            prop.update(type="string", enum=list(f.allowed))
        else:
            prop.update(type="string")
        props[f.name] = prop
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://github.com/constructelligence-lab/construction-project-records/schema/json/{record}.schema.json",
        "title": record.replace("_", " "),
        "type": "object",
        "properties": props,
        "required": [f.name for f in fields if f.required],
        "additionalProperties": False,
    }


def write_json_schemas(folder: Path) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    out = []
    for record in RECORDS:
        path = folder / f"{record}.schema.json"
        path.write_text(json.dumps(json_schema(record), indent=2) + "\n", encoding="utf-8")
        out.append(path)
    return out
