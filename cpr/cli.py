"""Command line: ``python3 -m cpr <command>``.

Commands
  check DIR [--as-of DATE]     validate the logs in DIR and report metrics and findings
  schema [--out DIR]           write JSON Schema files generated from schema/fields.csv
  templates [--out DIR]        write empty CSV templates, one per record type
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from pathlib import Path

from . import __version__, report
from .checks import check_folder
from .records import RECORDS, load_schema, write_json_schemas


def _check(args) -> int:
    as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    result = check_folder(Path(args.folder), as_of)
    sys.stdout.write(report.text_report(result))
    if args.markdown:
        Path(args.markdown).write_text(report.markdown_report(result), encoding="utf-8")
        print(f"review written to {args.markdown}")
    if args.json:
        Path(args.json).write_text(report.json_report(result), encoding="utf-8")
    return 1 if result.errors else 0


def _schema(args) -> int:
    for path in write_json_schemas(Path(args.out)):
        print(path)
    return 0


def _templates(args) -> int:
    folder = Path(args.out)
    folder.mkdir(parents=True, exist_ok=True)
    schema = load_schema()
    for record in RECORDS:
        path = folder / f"{record}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle, lineterminator="\n").writerow([f.name for f in schema[record]])
        print(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m cpr", description="Construction project records")
    parser.add_argument("--version", action="version", version=f"cpr {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check", help="validate logs and report metrics and findings")
    p.add_argument("folder")
    p.add_argument("--as-of", help="YYYY-MM-DD; defaults to today")
    p.add_argument("--markdown", help="write a review document to this file")
    p.add_argument("--json", help="write metrics and findings as JSON")
    p.set_defaults(run=_check)
    p = sub.add_parser("schema", help="write JSON Schema files")
    p.add_argument("--out", default="schema/json")
    p.set_defaults(run=_schema)
    p = sub.add_parser("templates", help="write empty CSV templates")
    p.add_argument("--out", default="templates")
    p.set_defaults(run=_templates)
    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
