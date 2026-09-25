# AGENTS.md

Instructions for AI agents (Claude Code, Codex, Cursor and others) working in this repository.

## Running a log review for someone

1. Put their exported logs in `work/` (git-ignored), one CSV per log, with the columns in `schema/fields.csv`. If their
   export has different column names, map them first; never edit the exports themselves.
2. Run `python3 -m cpr check work/<project> --as-of <date> --markdown work/review.md`. Use the date they give you, not
   today's date, when reviewing a past period.
3. Report in the order of [the weekly review in GUIDE.md](GUIDE.md#the-weekly-log-review): errors, procurement at risk,
   notice, overdue RFIs by ball in court, answers needing change events, missing daily reports.

## Rules

- **Do not decide notice questions.** `Q08` flags possible late or missing notice. Say it needs to go to whoever manages
  the contract. Do not say whether notice was valid, late in law, or what the contract requires.
- **Do not edit records to clear a finding.** Report it; the project team corrects the source system.
- **Do not invent dates or answers** to fill gaps. A missing date is a finding, not a blank to fill.
- **Keep project data local.** Do not send logs to outside services, and do not paste real project names, people or
  contents into commits, issues or pull requests.
- **Report exactly what ran,** with the as-of date, and what was not checked.

## Changing this repository

- Run `python3 -m unittest discover -s tests` before finishing. It must pass.
- The schema is `schema/fields.csv`. After changing it, run `python3 -m cpr schema` and `python3 -m cpr templates`, and
  commit the regenerated files; a test fails if they are stale.
- Samples are generated: change `scripts/make_samples.py` and re-run it. Synthetic data only.
- A new check needs an entry in `CHECKS`, a row in the table in `GUIDE.md` (a test enforces it), and a test.
- Standard library only, Python 3.9 compatible.
