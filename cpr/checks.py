"""Checks and metrics for project logs.

The checks find the faults that make a log useless as a record: duplicate and missing numbers, dates in the
wrong order, answers with no date, open items nobody owns, notices that may be late, and days with no daily
report. The metrics are the numbers a PM reviews every week: what is open, what is overdue, how long answers
take, and what is at risk.
"""

from __future__ import annotations

import datetime as dt
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

from .records import Finding, Table, read_folder

CHECKS = {
    "Q01": ("error", "The same number appears twice in a log"),
    "Q02": ("error", "A value is missing, malformed or not an allowed option"),
    "Q03": ("warning", "A numbered sequence has gaps"),
    "Q04": ("error", "Dates are in an impossible order, such as an answer before the question"),
    "Q05": ("error", "An item is answered, returned or closed but has no date for it"),
    "Q06": ("warning", "An open item has nobody holding the ball"),
    "Q07": ("warning", "An RFI has no date needed, so nobody can tell if the answer is late"),
    "Q08": ("warning", "Written notice for a change event may be late or missing"),
    "Q09": ("warning", "A working day has no daily report"),
    "Q10": ("warning", "An approved change event has no change order number"),
    "Q11": ("warning", "A submittal will not be approved in time for its lead time and required-on-site date"),
    "Q12": ("warning", "An answered RFI with a cost or time impact has no change event"),
    "Q13": ("info", "Items are dated after the as-of date"),
}

OPEN_RFI = {"open"}
OPEN_SUBMITTAL = {"not_submitted", "in_review", "revise_and_resubmit"}
APPROVED_SUBMITTAL = {"approved", "approved_as_noted"}
OPEN_EVENT = {"open", "priced", "submitted"}
OPEN_PUNCH = {"open", "ready_for_review"}


@dataclass
class Result:
    folder: Path
    as_of: dt.date
    findings: list[Finding] = field(default_factory=list)
    metrics: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]


def _number_gaps(numbers: list[str]) -> list[str]:
    """Missing numbers in a sequence like RFI-001, RFI-002, RFI-004 (only where a numeric suffix exists)."""
    parsed = {}
    for n in numbers:
        m = re.match(r"^(.*?)(\d+)$", n or "")
        if m:
            parsed.setdefault(m.group(1), set()).add(int(m.group(2)))
    gaps = []
    for prefix, nums in parsed.items():
        example = next(n for n in numbers if n and n.startswith(prefix))
        width = len(example) - len(prefix)
        for missing in sorted(set(range(min(nums), max(nums) + 1)) - nums):
            gaps.append(f"{prefix}{missing:0{width}d}")
    return gaps


def _age_bucket(days: int) -> str:
    if days <= 7:
        return "0-7 days"
    if days <= 14:
        return "8-14 days"
    if days <= 30:
        return "15-30 days"
    return "over 30 days"


def _by_project(table: Table) -> dict[str, list[tuple[int, dict[str, Any]]]]:
    out: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for line, row in table.items():
        if row.get("project_id"):
            out[row["project_id"]].append((line, row))
    return out


def _add(findings: list[Finding], check: str, message: str, record: str = "", line: int = 0, project: str = "") -> None:
    findings.append(Finding(check, CHECKS[check][0], message, record, line, project))


def check_folder(folder: Path, as_of: dt.date) -> Result:
    tables, findings = read_folder(folder)
    result = Result(folder, as_of, findings)
    projects: set[str] = set()
    for t in tables.values():
        projects |= set(_by_project(t))
    for project in sorted(projects):
        result.metrics[project] = {}

    _rfis(tables["rfis"], as_of, result, tables["change_events"])
    _submittals(tables["submittals"], as_of, result)
    _change_events(tables["change_events"], as_of, result)
    _daily_reports(tables["daily_reports"], as_of, result)
    _punch(tables["punch_items"], as_of, result)

    order = {"error": 0, "warning": 1, "info": 2}
    result.findings.sort(key=lambda f: (order[f.severity], f.project_id, f.check, f.record, f.line))
    return result


def _future(findings, record, line, project, label, value, as_of):
    if value and value > as_of:
        _add(findings, "Q13", f"{label} {value} is after the as-of date {as_of}", record, line, project)


def _rfis(table: Table, as_of: dt.date, result: Result, events: Table) -> None:
    f = result.findings
    linked = {(r["project_id"], r["related_rfi"]) for r in events.rows if r.get("related_rfi")}
    for project, items in _by_project(table).items():
        rows = [r for _, r in items]
        for gap in _number_gaps([r["rfi_number"] for r in rows]):
            _add(f, "Q03", f"RFI {gap} is missing from the log", "rfis", 0, project)
        answer_days, open_ages = [], Counter()
        overdue = []
        for line, r in items:
            num, status = r["rfi_number"], r["status"]
            _future(f, "rfis", line, project, f"RFI {num} created", r["created_date"], as_of)
            if status in ("answered", "closed") and not r["answered_date"]:
                _add(f, "Q05", f"RFI {num} is {status} but has no answered date", "rfis", line, project)
            if r["answered_date"] and r["created_date"] and r["answered_date"] < r["created_date"]:
                _add(f, "Q04", f"RFI {num} was answered before it was asked", "rfis", line, project)
            if r["date_needed"] and r["created_date"] and r["date_needed"] < r["created_date"]:
                _add(f, "Q04", f"RFI {num} is needed before it was raised", "rfis", line, project)
            if status == "open":
                if not r["ball_in_court"]:
                    _add(f, "Q06", f"RFI {num} is open with nobody holding the ball", "rfis", line, project)
                if not r["date_needed"]:
                    _add(f, "Q07", f"RFI {num} has no date needed", "rfis", line, project)
                if r["created_date"]:
                    open_ages[_age_bucket((as_of - r["created_date"]).days)] += 1
                if r["date_needed"] and r["date_needed"] < as_of:
                    overdue.append((num, (as_of - r["date_needed"]).days))
            if r["answered_date"] and r["created_date"]:
                answer_days.append((r["answered_date"] - r["created_date"]).days)
            if status in ("answered", "closed") and "yes" in (r["cost_impact"], r["schedule_impact"]) and (project, num) not in linked:
                _add(f, "Q12", f"RFI {num} answer has a cost or time impact but no change event refers to it", "rfis", line, project)
        result.metrics[project]["rfis"] = {
            "total": len(rows),
            "open": sum(r["status"] == "open" for r in rows),
            "overdue": len(overdue),
            "most_overdue": sorted(overdue, key=lambda x: -x[1])[:5],
            "open_by_age": {b: open_ages.get(b, 0) for b in ("0-7 days", "8-14 days", "15-30 days", "over 30 days")},
            "median_days_to_answer": statistics.median(answer_days) if answer_days else None,
            "open_by_ball_in_court": dict(Counter(r["ball_in_court"] or "(nobody)" for r in rows if r["status"] == "open")),
        }


def _submittals(table: Table, as_of: dt.date, result: Result) -> None:
    f = result.findings
    for project, items in _by_project(table).items():
        latest: dict[str, tuple[int, dict[str, Any]]] = {}
        for line, r in items:
            num = r["submittal_number"]
            if num and (num not in latest or (r["revision"] or 0) > (latest[num][1]["revision"] or 0)):
                latest[num] = (line, r)
        for gap in _number_gaps(list(latest)):
            _add(f, "Q03", f"submittal {gap} is missing from the register", "submittals", 0, project)
        review_days, overdue_reviews, at_risk = [], [], []
        for line, r in items:
            label = f"submittal {r['submittal_number']} rev {r['revision']}"
            _future(f, "submittals", line, project, f"{label} submitted", r["submitted_date"], as_of)
            if r["status"] in APPROVED_SUBMITTAL | {"revise_and_resubmit", "rejected"} and not r["returned_date"]:
                _add(f, "Q05", f"{label} is {r['status']} but has no returned date", "submittals", line, project)
            if r["returned_date"] and r["submitted_date"] and r["returned_date"] < r["submitted_date"]:
                _add(f, "Q04", f"{label} came back before it was sent", "submittals", line, project)
            if r["returned_date"] and r["submitted_date"]:
                review_days.append((r["returned_date"] - r["submitted_date"]).days)
        for num, (line, r) in latest.items():
            label = f"submittal {num} rev {r['revision']}"
            if r["status"] == "in_review":
                if not r["ball_in_court"]:
                    _add(f, "Q06", f"{label} is in review with nobody holding the ball", "submittals", line, project)
                if r["review_due_date"] and r["review_due_date"] < as_of:
                    overdue_reviews.append((num, (as_of - r["review_due_date"]).days))
            if r["status"] in OPEN_SUBMITTAL and r["required_on_site"] and r["lead_time_days"] is not None:
                latest_approval = r["required_on_site"] - dt.timedelta(days=r["lead_time_days"])
                if latest_approval < as_of:
                    days_late = (as_of - latest_approval).days
                    at_risk.append((num, days_late))
                    _add(
                        f,
                        "Q11",
                        f"{label} needed on site {r['required_on_site']} with a {r['lead_time_days']}-day lead time: approval was due {latest_approval} ({days_late} days ago)",
                        "submittals",
                        line,
                        project,
                    )
        statuses = Counter(r["status"] for _, r in latest.values())
        resubmitted = sum(1 for _, r in latest.values() if (r["revision"] or 0) > 0)
        result.metrics[project]["submittals"] = {
            "submittals": len(latest),
            "by_status": dict(statuses),
            "reviews_overdue": len(overdue_reviews),
            "procurement_at_risk": sorted(at_risk, key=lambda x: -x[1]),
            "median_review_days": statistics.median(review_days) if review_days else None,
            "resubmitted_percent": round(100 * resubmitted / len(latest), 1) if latest else None,
        }


def _change_events(table: Table, as_of: dt.date, result: Result) -> None:
    f = result.findings
    for project, items in _by_project(table).items():
        rows = [r for _, r in items]
        for gap in _number_gaps([r["event_number"] for r in rows]):
            _add(f, "Q03", f"change event {gap} is missing from the log", "change_events", 0, project)
        exposure = Decimal("0.00")
        exposure_days = 0
        oldest_open = None
        for line, r in items:
            num = r["event_number"]
            _future(f, "change_events", line, project, f"change event {num}", r["event_date"], as_of)
            if r["notice_date"] and r["event_date"] and r["notice_date"] < r["event_date"]:
                _add(f, "Q04", f"change event {num} notice is dated before the event", "change_events", line, project)
            due = r["notice_required_by"]
            if due and r["status"] != "void":
                if r["notice_date"] and r["notice_date"] > due:
                    _add(f, "Q08", f"change event {num}: notice given {r['notice_date']}, required by {due}. Take this to whoever manages the contract", "change_events", line, project)
                elif not r["notice_date"] and due < as_of:
                    _add(f, "Q08", f"change event {num}: no notice recorded and the notice date {due} has passed. Check now", "change_events", line, project)
            if r["status"] == "approved" and not r["change_order_number"]:
                _add(f, "Q10", f"change event {num} is approved but has no change order number", "change_events", line, project)
            if r["status"] in OPEN_EVENT:
                exposure += r["estimated_cost"] or Decimal("0.00")
                exposure_days += r["estimated_days"] or 0
                if r["event_date"] and (oldest_open is None or r["event_date"] < oldest_open[1]):
                    oldest_open = (num, r["event_date"])
        result.metrics[project]["change_events"] = {
            "total": len(rows),
            "by_status": dict(Counter(r["status"] for r in rows)),
            "open_exposure_cost": str(exposure),
            "open_exposure_days": exposure_days,
            "oldest_open": {"event": oldest_open[0], "days_open": (as_of - oldest_open[1]).days} if oldest_open else None,
        }


def _daily_reports(table: Table, as_of: dt.date, result: Result) -> None:
    f = result.findings
    for project, items in _by_project(table).items():
        dates = sorted({r["report_date"] for _, r in items if r["report_date"]})
        if not dates:
            continue
        missing = []
        day = dates[0]
        have = set(dates)
        while day <= min(as_of, dates[-1] + dt.timedelta(days=7)):
            if day.weekday() < 5 and day not in have and day < as_of:
                missing.append(day)
            day += dt.timedelta(days=1)
        for d in missing:
            _add(f, "Q09", f"no daily report for {d:%a %Y-%m-%d}", "daily_reports", 0, project)
        manpower = [r["manpower_total"] for _, r in items if r["manpower_total"] is not None]
        delays = sum(1 for _, r in items if r["delays"])
        result.metrics[project]["daily_reports"] = {
            "reports": len(dates),
            "first": str(dates[0]),
            "last": str(dates[-1]),
            "working_days_missing": len(missing),
            "average_manpower": round(sum(manpower) / len(manpower), 1) if manpower else None,
            "days_with_delays_recorded": delays,
        }


def _punch(table: Table, as_of: dt.date, result: Result) -> None:
    f = result.findings
    for project, items in _by_project(table).items():
        rows = [r for _, r in items]
        for line, r in items:
            num = r["item_number"]
            if r["status"] == "closed" and not r["closed_date"]:
                _add(f, "Q05", f"punch item {num} is closed but has no closed date", "punch_items", line, project)
            if r["closed_date"] and r["created_date"] and r["closed_date"] < r["created_date"]:
                _add(f, "Q04", f"punch item {num} was closed before it was listed", "punch_items", line, project)
        open_rows = [r for r in rows if r["status"] in OPEN_PUNCH]
        result.metrics[project]["punch_items"] = {
            "total": len(rows),
            "open": len(open_rows),
            "ready_for_review": sum(r["status"] == "ready_for_review" for r in rows),
            "overdue": sum(1 for r in open_rows if r["due_date"] and r["due_date"] < as_of),
            "open_by_responsible_party": dict(Counter(r["responsible_party"] for r in open_rows).most_common()),
            "closed_without_verifier": sum(1 for r in rows if r["status"] == "closed" and not r["verified_by"]),
        }
