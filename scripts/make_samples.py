#!/usr/bin/env python3
"""Generate the synthetic sample logs in samples/.

One invented project, P-2041 Sample Library Renovation, reviewed as of 2026-09-18. Every name, number and date
is made up. The logs are realistic, which means they contain the usual problems; samples/README.md lists them.

    python3 scripts/make_samples.py
"""

from __future__ import annotations

import csv
import datetime as dt
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cpr.records import RECORDS, load_schema  # noqa: E402

OUT = Path(os.environ.get("CPR_SAMPLES_OUT") or ROOT / "samples")
P = "P-2041"
D = dt.date


def rfis():
    rows = []
    base = [
        # n, subject, created, needed, reason, ball, status, answered, cost, time
        (1, "Existing beam size at grid C/4 differs from drawings", D(2026, 7, 6), D(2026, 7, 13), "Steel order for new opening", "", "closed", D(2026, 7, 10), "none", "none"),
        (2, "Fire rating of corridor wall at stair 2", D(2026, 7, 8), D(2026, 7, 17), "Framing starts in corridor", "", "closed", D(2026, 7, 15), "none", "none"),
        (3, "Abandoned conduit found in ceiling of reading room", D(2026, 7, 14), D(2026, 7, 21), "Ceiling demolition sequence", "", "closed", D(2026, 7, 24), "yes", "none"),
        (4, "Floor leveling compound depth at stacks area", D(2026, 7, 20), D(2026, 7, 29), "Flooring subcontractor mobilisation", "", "answered", D(2026, 7, 28), "possible", "none"),
        (5, "Door hardware set for staff room not scheduled", D(2026, 7, 22), D(2026, 8, 5), "Hardware submittal", "", "closed", D(2026, 8, 3), "none", "none"),
        (6, "Location of new data rack in lower level", D(2026, 7, 27), D(2026, 8, 7), "Electrical rough-in", "", "answered", D(2026, 8, 12), "none", "possible"),
        (8, "Skylight curb height conflicts with roof insulation", D(2026, 8, 3), D(2026, 8, 12), "Roofing subcontractor start", "", "answered", D(2026, 8, 19), "yes", "yes"),
        (9, "Paint colour for existing radiators", D(2026, 8, 5), None, "", "Architect", "open", None, "none", "none"),
        (10, "Acoustic panel mounting at reading room ceiling", D(2026, 8, 11), D(2026, 8, 25), "Ceiling close-in", "Architect", "open", None, "possible", "possible"),
        (11, "Structural support for relocated rooftop unit", D(2026, 8, 17), D(2026, 8, 31), "Crane booking", "Structural engineer", "open", None, "possible", "yes"),
        (12, "Casework finish at circulation desk", D(2026, 8, 24), D(2026, 9, 21), "Millwork shop drawings", "Architect", "open", None, "none", "none"),
        (13, "Existing sprinkler main in conflict with new duct", D(2026, 9, 1), D(2026, 9, 8), "Duct installation, level 1", "", "open", None, "possible", "possible"),
        (14, "Clarify extent of wall patching at removed shelving", D(2026, 9, 8), D(2026, 9, 15), "Painting start", "Architect", "answered", None, "none", "none"),
        (15, "Threshold detail at accessible entrance", D(2026, 9, 14), D(2026, 9, 28), "Entrance paving", "Architect", "open", None, "none", "none"),
    ]
    for n, subject, created, needed, reason, ball, status, answered, cost, time in base:
        rows.append(
            {
                "project_id": P,
                "rfi_number": f"RFI-{n:03d}",
                "subject": subject,
                "question": f"{subject}. Please confirm the intended detail.",
                "proposed_answer": "See attached sketch for our proposed approach." if n % 2 else "",
                "references": f"A-{200 + n}, spec 09 21 16" if n % 3 else f"S-{100 + n}",
                "created_date": created,
                "date_needed": needed,
                "reason_needed": reason,
                "ball_in_court": ball,
                "status": status,
                "answered_date": answered,
                "answer": "Response attached." if status != "open" else "",
                "cost_impact": cost,
                "schedule_impact": time,
                "created_by": "Project engineer",
            }
        )
    return rows


def submittals():
    rows = []
    items = [
        # number, rev, spec, title, type, submitted, due, returned, status, on_site, lead, ball, party
        ("S-001", 0, "05 50 00", "Miscellaneous metals shop drawings", "shop_drawing", D(2026, 7, 10), D(2026, 7, 24), D(2026, 7, 22), "revise_and_resubmit", D(2026, 9, 1), 21, "", "Sample Metals"),
        ("S-001", 1, "05 50 00", "Miscellaneous metals shop drawings", "shop_drawing", D(2026, 7, 29), D(2026, 8, 12), D(2026, 8, 10), "approved_as_noted", D(2026, 9, 1), 21, "", "Sample Metals"),
        ("S-002", 0, "08 71 00", "Door hardware schedule", "product_data", D(2026, 7, 15), D(2026, 7, 29), D(2026, 7, 30), "approved", D(2026, 10, 5), 42, "", "Sample Hardware"),
        ("S-003", 0, "09 21 16", "Gypsum board assemblies", "product_data", D(2026, 7, 17), D(2026, 7, 31), D(2026, 7, 28), "approved", D(2026, 8, 10), 5, "", "Sample Drywall"),
        ("S-004", 0, "09 65 19", "Resilient tile flooring", "sample", D(2026, 8, 3), D(2026, 8, 17), D(2026, 8, 20), "revise_and_resubmit", D(2026, 10, 12), 35, "", "Sample Flooring"),
        ("S-004", 1, "09 65 19", "Resilient tile flooring", "sample", D(2026, 8, 27), D(2026, 9, 10), None, "in_review", D(2026, 10, 12), 35, "Architect", "Sample Flooring"),
        ("S-005", 0, "12 36 61", "Circulation desk casework", "shop_drawing", None, None, None, "not_submitted", D(2026, 10, 19), 49, "Sample Millwork", "Sample Millwork"),
        ("S-006", 0, "23 31 13", "Ductwork shop drawings", "shop_drawing", D(2026, 8, 12), D(2026, 8, 26), D(2026, 8, 25), "approved", D(2026, 9, 14), 10, "", "Sample Mechanical"),
        ("S-007", 0, "23 74 13", "Rooftop unit", "product_data", D(2026, 8, 14), D(2026, 8, 28), None, "approved", D(2026, 11, 2), 56, "", "Sample Mechanical"),
        ("S-008", 0, "26 51 00", "Interior lighting fixtures", "product_data", D(2026, 8, 20), D(2026, 9, 3), None, "in_review", D(2026, 10, 26), 42, "", "Sample Electric"),
        ("S-010", 0, "09 91 23", "Interior paint colours", "sample", D(2026, 9, 9), D(2026, 9, 23), None, "in_review", D(2026, 10, 5), 5, "Architect", "Sample Painting"),
    ]
    for num, rev, spec, title, kind, sub, due, ret, status, site, lead, ball, party in items:
        rows.append(
            {
                "project_id": P,
                "submittal_number": num,
                "revision": rev,
                "spec_section": spec,
                "title": title,
                "submittal_type": kind,
                "submitted_date": sub,
                "review_due_date": due,
                "returned_date": ret,
                "status": status,
                "required_on_site": site,
                "lead_time_days": lead,
                "ball_in_court": ball,
                "responsible_party": party,
            }
        )
    return rows


def change_events():
    items = [
        # n, title, origin, date, notice_by, notice, status, cost, days, rfi, co
        (1, "Abandoned conduit removal in reading room", "rfi", D(2026, 7, 24), D(2026, 8, 7), D(2026, 7, 27), "approved", "4850.00", 0, "RFI-003", "CO-001"),
        (2, "Owner-requested additional data outlets", "owner_directive", D(2026, 8, 4), D(2026, 8, 18), D(2026, 8, 5), "approved", "12640.00", 2, "", ""),
        (3, "Extra floor leveling at stacks area", "unforeseen_condition", D(2026, 7, 28), D(2026, 8, 11), D(2026, 8, 14), "submitted", "7920.00", 1, "RFI-004", ""),
        (4, "Relocated rooftop unit support steel", "design_change", D(2026, 8, 20), D(2026, 9, 3), None, "open", "18500.00", 5, "RFI-011", ""),
        (5, "Asbestos-containing mastic under carpet", "unforeseen_condition", D(2026, 8, 26), D(2026, 9, 9), D(2026, 8, 27), "priced", "22300.00", 6, "", ""),
        (6, "Upgraded circulation desk finish", "owner_directive", D(2026, 9, 2), D(2026, 9, 16), D(2026, 9, 3), "rejected", "9100.00", 0, "", ""),
        (7, "Delay awaiting sprinkler main relocation answer", "delay", D(2026, 9, 9), D(2026, 9, 23), None, "open", "0.00", 3, "RFI-013", ""),
    ]
    return [
        {
            "project_id": P,
            "event_number": f"CE-{n:03d}",
            "title": title,
            "origin": origin,
            "event_date": date,
            "notice_required_by": notice_by,
            "notice_date": notice,
            "status": status,
            "estimated_cost": cost,
            "estimated_days": days,
            "related_rfi": rfi,
            "change_order_number": co,
        }
        for n, title, origin, date, notice_by, notice, status, cost, days, rfi, co in items
    ]


def daily_reports():
    rows = []
    day = D(2026, 8, 3)
    skipped = {D(2026, 8, 21), D(2026, 9, 4)}  # two working days nobody wrote up
    n = 0
    while day <= D(2026, 9, 17):
        if day.weekday() < 5 and day not in skipped:
            n += 1
            rain = n % 9 == 0
            rows.append(
                {
                    "project_id": P,
                    "report_date": day,
                    "weather": "Rain from 10:00, roof work stopped" if rain else "Dry",
                    "work_performed": "Framing level 1 east; MEP rough-in reading room; ceiling demolition stacks" if n % 2 else "Board hanging level 1; duct install corridor; floor prep stacks",
                    "manpower_total": 18 + (n * 7) % 11,
                    "delays": "Roofing stood down for rain" if rain else ("Waiting on RFI-013 at corridor duct" if day >= D(2026, 9, 9) else ""),
                    "inspections": "Above-ceiling inspection, reading room: passed" if day == D(2026, 9, 10) else "",
                    "safety_notes": "Toolbox talk: ladders" if day.weekday() == 0 else "",
                    "author": "Superintendent",
                }
            )
        day += dt.timedelta(days=1)
    return rows


def punch_items():
    trades = ["Sample Drywall", "Sample Painting", "Sample Electric", "Sample Mechanical", "Sample Flooring"]
    rows = []
    for n in range(1, 25):
        status = "closed" if n <= 10 else ("ready_for_review" if n <= 14 else "open")
        closed = D(2026, 9, 10) if status == "closed" and n != 7 else None  # item 7: closed with no date
        rows.append(
            {
                "project_id": P,
                "item_number": f"PL-{n:03d}",
                "location": f"Room {100 + (n % 6) * 2}",
                "description": ["Touch up paint at door frame", "Fill screw pops", "Missing cover plate", "Diffuser not aligned", "Base cove loose"][n % 5],
                "responsible_party": trades[n % 5],
                "created_date": D(2026, 9, 1),
                "due_date": D(2026, 9, 15),
                "status": status,
                "closed_date": closed,
                "verified_by": "Superintendent" if status == "closed" and n % 4 else "",
            }
        )
    return rows


def main() -> None:
    schema = load_schema()
    data = {"rfis": rfis(), "submittals": submittals(), "change_events": change_events(), "daily_reports": daily_reports(), "punch_items": punch_items()}
    folder = OUT / "library-renovation"
    folder.mkdir(parents=True, exist_ok=True)
    for record in RECORDS:
        names = [f.name for f in schema[record]]
        with (folder / f"{record}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(names)
            for row in data[record]:
                writer.writerow(["" if row.get(n) is None else str(row.get(n)) for n in names])
    print(f"samples written to {folder}")


if __name__ == "__main__":
    main()
