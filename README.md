# Construction project records

Open schemas, templates and a checker for the five logs every construction project keeps: **RFIs, submittals, change
events, daily reports and punch lists.** Plus a practical [guide](GUIDE.md) to keeping them so they hold up when
someone asks, months later, what happened and when.

Export your logs to CSV from whatever system you use, and one command gives you the weekly review: what is open, what is
overdue, which materials will arrive late, which change events may have missed their notice date, and which records are
incomplete.

**Standard-library Python 3.9+, no dependencies, no network access.**

![logs](https://img.shields.io/badge/logs-5-1f6feb) ![checks](https://img.shields.io/badge/checks-13-2ea043) ![dependencies](https://img.shields.io/badge/dependencies-none-2ea043) ![licence](https://img.shields.io/badge/licence-CC%20BY%204.0%20%2B%20MIT-6e7781)

## What it finds

Run against the synthetic sample project:

```text
$ python3 -m cpr check samples/library-renovation --as-of 2026-09-18
P-2041
  RFIs
    open                         6
    overdue                      3
    most overdue                 RFI-010 (24 days), RFI-011 (18 days), RFI-013 (10 days)
  Submittals
    procurement at risk          S-005 (18 days), S-004 (11 days), S-008 (4 days)
  Change events
    open exposure cost           48720.00
    open exposure days           15
...
ERROR   Q05 [P-2041] RFI RFI-014 is answered but has no answered date
...
WARNING Q08 [P-2041] change event CE-004: no notice recorded and the notice date 2026-09-03 has passed. Check now
WARNING Q09 [P-2041] no daily report for Fri 2026-08-21
...
WARNING Q11 [P-2041] submittal S-005 rev 0 needed on site 2026-10-19 with a 49-day lead time: approval was due 2026-08-31 (18 days ago)
WARNING Q12 [P-2041] RFI RFI-008 answer has a cost or time impact but no change event refers to it

3 errors, 14 warnings, 0 notes
```

`--markdown review.md` writes the same thing as a document to file with the weekly meeting notes. `--json` writes it
for a dashboard.

## What is in it

| Piece | What it is |
| --- | --- |
| [`GUIDE.md`](GUIDE.md) | What a good RFI, submittal, change event, daily report and punch item contains; the traps; a fifteen-minute weekly log review |
| [`schema/fields.csv`](schema/fields.csv) | The five record types, every field typed and described. Readable in a spreadsheet |
| [`schema/json/`](schema/json/) | JSON Schema (draft 2020-12) for each record, generated from `fields.csv` |
| [`templates/`](templates/) | Empty CSV templates, one per log, to start a job with |
| [`cpr/`](cpr/) | The checker: 13 checks and the log metrics |
| [`samples/`](samples/README.md) | A synthetic project's logs, with the usual problems in them |

## Use it

```bash
git clone https://github.com/constructelligence-lab/construction-project-records.git
cd construction-project-records
python3 -m cpr check path/to/your/logs --as-of 2026-09-18 --markdown review.md
```

The folder holds up to five CSV files named `rfis.csv`, `submittals.csv`, `change_events.csv`, `daily_reports.csv` and
`punch_items.csv`, with the columns in [`schema/fields.csv`](schema/fields.csv). Any subset works. Dates are
`YYYY-MM-DD`.

Most project management platforms export these logs to CSV with their own column names. To rename the columns and
translate statuses repeatably, the mapping tool in
[construction-data-migration](https://github.com/constructelligence-lab/construction-data-migration) works with a
mapping file pointed at this schema.

## Linking the logs to everything else

The five logs are one corner of a project. The
[construction schema](https://github.com/constructelligence-lab/construction-schema) carries the same records with
the rest (spec sections, subcontracts, change orders, costs, pay applications, schedule, assets) and links them, so
an RFI can be followed to the change order and the costs behind it. Its converter reads this repository's CSVs
directly:

```bash
python3 -m cschema convert construction-project-records path/to/your/logs -o project.jsonl --system procore
python3 -m cschema trace project.jsonl rfi:RFI-011
```

Names in the logs become party records, and spec section and sheet numbers in `references` become linked records.
The same records can be validated and traced by an AI assistant through
[construction-mcp](https://github.com/constructelligence-lab/construction-mcp).

## What it does not do

- **It does not judge.** It finds late notices, but cannot tell you what your contract requires or whether a notice is
  valid. It finds procurement at risk, but the team decides what to do about it.
- **It does not connect to anything.** No network, no accounts, no integrations. It reads the CSV files you give it.
- **It does not change your records.** It only reads.

## AI agents

[`AGENTS.md`](AGENTS.md) tells an AI agent how to run the weekly review with this repository, and what it must leave to
people.

<!-- begin:family -->
## More from Constructelligence

Open construction resources from the same team, all maintained alongside this one:

| Repository | What it is |
| --- | --- |
| [AI in construction](https://github.com/constructelligence-lab/ai-in-construction) | A practical guide to AI in construction: what works today, what the data has to look like, the risks, and a 90-day plan. |
| [Construction data migration](https://github.com/constructelligence-lab/construction-data-migration) | A guide and toolkit for moving a contractor between systems, and proving nothing was lost. |
| [Construction schema](https://github.com/constructelligence-lab/construction-schema) | One record format for construction project data, with provenance, classifications and links, built for AI. |
| [Construction reference data](https://github.com/constructelligence-lab/construction-data) | Cost codes, units, waste factors, pay units, trade sequence, glossary and metric formulas in CSV. |
| [Construction reference MCP server](https://github.com/constructelligence-lab/construction-mcp) | An offline MCP server that gives AI assistants construction reference data and calculators. |
| [Construction prompts](https://github.com/constructelligence-lab/construction-prompts) | 28 prompts for ChatGPT, Claude and Gemini, from bid go/no-go to notice letters. |
| [Construction agent skills](https://github.com/constructelligence-lab/construction-agent-skills) | 28 installable agent skills for Claude Code and any agent that reads SKILL.md. |
| [Open source construction tools](https://github.com/constructelligence-lab/open-source-construction-tools) | Open source software for BIM, CAD, scheduling and site work, verified against the GitHub API. |

<!-- end:family -->


## Licence

Guide, schema, templates and samples: **CC BY 4.0**. Code: **MIT**. See [`LICENSE`](LICENSE).

---

*Maintained by [Constructelligence](https://constructelligence.co) — building the AI infrastructure for construction.*
