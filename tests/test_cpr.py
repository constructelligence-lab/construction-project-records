"""Tests. Run: python3 -m unittest discover -s tests"""

from __future__ import annotations

import csv
import datetime as dt
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cpr.checks import CHECKS, _number_gaps, check_folder  # noqa: E402
from cpr.records import RECORDS, json_schema, load_schema  # noqa: E402

SAMPLE = ROOT / "samples" / "library-renovation"
AS_OF = dt.date(2026, 9, 18)


def edit(folder: Path, record: str, change) -> None:
    path = folder / f"{record}.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    fields = list(rows[0])
    change(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


class Sample(unittest.TestCase):
    def setUp(self):
        self.result = check_folder(SAMPLE, AS_OF)
        self.found = [(f.check, f.message) for f in self.result.findings]

    def has(self, check, text):
        self.assertTrue(any(c == check and text in m for c, m in self.found), f"{check} {text!r} not in {self.found}")

    def test_every_planted_problem_is_found(self):
        self.has("Q03", "RFI-007")
        self.has("Q03", "S-009")
        self.has("Q05", "RFI-014")
        self.has("Q05", "S-007")
        self.has("Q05", "PL-007")
        self.has("Q06", "RFI-013")
        self.has("Q07", "RFI-009")
        self.has("Q08", "CE-003")
        self.has("Q08", "CE-004")
        self.has("Q09", "2026-08-21")
        self.has("Q09", "2026-09-04")
        self.has("Q10", "CE-002")
        self.has("Q11", "S-005")
        self.has("Q12", "RFI-008")
        self.assertEqual(len(self.result.errors), 3)

    def test_no_false_alarms(self):
        # RFI-003 has a cost impact but CE-001 refers to it; CE-007's notice date has not passed
        self.assertFalse(any("RFI-003" in m for _, m in self.found))
        self.assertFalse(any("CE-007" in m for _, m in self.found))
        self.assertFalse(any(c == "Q11" and "S-002" in m for c, m in self.found), "S-002 is approved")

    def test_metrics(self):
        m = self.result.metrics["P-2041"]
        self.assertEqual((m["rfis"]["total"], m["rfis"]["open"], m["rfis"]["overdue"]), (14, 6, 3))
        self.assertEqual(m["rfis"]["most_overdue"][0], ("RFI-010", 24))
        self.assertEqual(m["submittals"]["submittals"], 9, "revisions count once, at their latest")
        self.assertEqual(m["change_events"]["open_exposure_cost"], "48720.00")
        self.assertEqual(m["daily_reports"]["working_days_missing"], 2)
        self.assertEqual(m["punch_items"]["closed_without_verifier"], 2)


class Checks(unittest.TestCase):
    def run_with(self, record, change):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "logs"
            shutil.copytree(SAMPLE, folder)
            edit(folder, record, change)
            return check_folder(folder, AS_OF)

    def test_duplicate_number(self):
        r = self.run_with("rfis", lambda rows: rows.append(dict(rows[0])))
        self.assertIn("Q01", {f.check for f in r.errors})

    def test_answer_before_question(self):
        def change(rows):
            rows[0]["answered_date"] = "2026-07-01"
        r = self.run_with("rfis", change)
        self.assertIn("Q04", {f.check for f in r.errors})

    def test_bad_status(self):
        def change(rows):
            rows[0]["status"] = "pending"
        r = self.run_with("rfis", change)
        self.assertTrue(any(f.check == "Q02" and "pending" in f.message for f in r.errors))

    def test_future_items_are_noted(self):
        def change(rows):
            rows[-1]["created_date"] = "2026-10-01"
        r = self.run_with("rfis", change)
        self.assertIn("Q13", {f.check for f in r.findings})

    def test_number_gaps(self):
        self.assertEqual(_number_gaps(["RFI-001", "RFI-002", "RFI-005"]), ["RFI-003", "RFI-004"])
        self.assertEqual(_number_gaps(["S-1", "S-3"]), ["S-2"])
        self.assertEqual(_number_gaps(["ABC"]), [])


class Schema(unittest.TestCase):
    def test_json_schemas_are_current(self):
        for record in RECORDS:
            path = ROOT / "schema" / "json" / f"{record}.schema.json"
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), json_schema(record), f"{path} is stale: run python3 -m cpr schema")

    def test_templates_match_schema(self):
        schema = load_schema()
        for record in RECORDS:
            with (ROOT / "templates" / f"{record}.csv").open(encoding="utf-8") as handle:
                self.assertEqual(next(csv.reader(handle)), [f.name for f in schema[record]])

    def test_samples_are_current(self):
        import filecmp
        import os
        import subprocess

        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, CPR_SAMPLES_OUT=tmp)
            subprocess.run([sys.executable, str(ROOT / "scripts" / "make_samples.py")], check=True, env=env, capture_output=True)
            for fresh in (Path(tmp) / "library-renovation").glob("*.csv"):
                self.assertTrue(filecmp.cmp(fresh, SAMPLE / fresh.name, shallow=False), f"{fresh.name} is stale: run scripts/make_samples.py")

    def test_every_check_is_documented(self):
        guide = (ROOT / "GUIDE.md").read_text(encoding="utf-8")
        for check in CHECKS:
            self.assertIn(f"`{check}`", guide, f"{check} is not in GUIDE.md")


if __name__ == "__main__":
    unittest.main()
