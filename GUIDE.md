# Keeping project records that hold up

Project logs are the job's memory. When a question comes up in month nine, what happened in month two is only
as good as the RFI log, the submittal register, the change event log, the daily reports and the punch list. When
there is a dispute, those same logs become evidence, and a log with gaps, undated answers and renumbered items
helps whoever is arguing against you.

This guide covers what a good record contains for each log, the traps that make logs useless, and a fifteen-minute
weekly review that keeps them honest. The `cpr check` tool in this repository runs the mechanical part of that
review. The judgement stays with the project team.

This is general guidance on record keeping, not legal advice. Notice requirements, time limits and what counts as
proper notice are set by your contract and your jurisdiction. Take those questions to whoever manages the contract.

## Rules for every log

1. **Numbers are permanent.** An item keeps its number for life. Never reuse, renumber or delete. If an item was
   raised in error, mark it `void` and say why. A gap in the sequence (`Q03`) is a question someone will ask later.
2. **Every status change has a date.** "Answered" without an answered date (`Q05`) cannot be measured and cannot be
   proved. Dates must be in a possible order (`Q04`): nothing is answered before it was asked.
3. **Every open item has a ball in court.** A named party who owes the next action (`Q06`). "TBD" is nobody.
4. **One item, one thing.** One question per RFI, one scope per change event, one defect per punch item. Bundled
   items get half-answered and never close.
5. **Attachments travel with the item.** A sketch, photo or marked-up drawing that lives in someone's inbox is not
   part of the record.
6. **Close the loop.** An answer that changes cost or time must lead somewhere: a change event, a schedule update, a
   revised drawing. The log should show where.
7. **Do not rewrite history.** Correct an error with a new dated entry, not by editing the old one. If your system keeps
   an audit trail, keep it switched on.

## RFIs

**A good RFI contains:**

| Field | Why |
| --- | --- |
| A subject that makes sense in a list | The log is read as a list. "Question" is not a subject |
| One specific question | Open questions get open answers |
| Our proposed answer | It turns a research task for the designer into a confirmation, and fast answers follow |
| References: drawings, details, spec sections | So the reviewer does not have to hunt |
| Date needed, and the reason | "Needed by the 14th because the steel order goes then" is what makes lateness measurable (`Q07`) |
| Cost and schedule impact | Possible, yes or none. It flags the RFIs that must become change events |

**Measure:** open RFIs by age, overdue RFIs (past their date needed), and median days to answer. Report overdue RFIs by
who holds the ball. That is the conversation to have at the design meeting.

**Traps:**

- **RFIs answered by email** that never make it into the log. The log then shows the RFI open, and the answer is
  somewhere in an inbox.
- **An RFI used as a notice.** An RFI asks a question. If the answer changes cost or time, the contract's notice
  requirements usually still apply. Do not assume the RFI counts as notice.
- **Answers with an impact and no change event** (`Q12`). The answer said "add supports at grid C". Someone has to
  price that, or it is free.
- **RFIs that are really change requests.** "Please confirm we can substitute product X" is a substitution request,
  which usually has its own contract procedure.

## Submittals

**Build the register from the specification at the start of the job,** not as submittals arrive. Every section that calls
for a submittal gets a line, with the responsible subcontractor.

**Work backwards from site.** For each item:

> approve-by date = required-on-site date − lead time

If today is past the approve-by date and the submittal is not approved, the item will arrive late unless something
changes. That is `Q11`, and it is the most valuable check in this repository. It finds procurement problems while there
is still time to expedite, resequence or substitute.

**A good submittal record contains:** number and revision (resubmittals keep the number and increase the revision), spec
section, type, submitted date, review due date (from the contract's review period), returned date, status, required on
site, lead time and responsible party.

**Measure:** submittals by status, reviews overdue, median review days, the resubmittal rate, and procurement at risk
sorted by days late.

**Traps:**

- **"Approved as noted" treated as "approved".** The notes are the point. Someone must read them and pass them to the
  trade and the field.
- **No required-on-site date.** Without it, nobody can tell whether a slow review matters.
- **Resubmittals logged as new numbers.** The history of how long an item really took to approve disappears.
- **Submittals approved in the log but never returned** (`Q05`). Check the returned copy exists.

## Change events

A change event is anything that might change the contract sum or time: an owner directive, an RFI answer, a design
change, an unforeseen condition, a delay. **Log it the day it happens,** before anyone knows whether it will turn into a
change order. Most lost money on change is lost at this step, when an event is never written down.

**A good change event record contains:** number, title, origin, the date of the event, the date written notice is
required by under the contract, the date notice was given, status, estimated cost and time, the related RFI, and the
change order number once approved.

**Notice dates.** Many contracts require written notice of a claim or change within a set period of the event. Record the
notice-required-by date when you log the event, and the date notice was actually given. `Q08` flags notice given after the
date, and events whose notice date has passed with no notice recorded. It cannot tell you what your contract requires or
whether a notice is valid. It tells you which events to take to whoever manages the contract, today.

**Measure:** open exposure (cost and days of events not yet approved or rejected), events by status, and the oldest open
event. Exposure is the number the monthly cost report should show next to the forecast.

**Traps:**

- **Events that only exist in a PM's head** until month-end.
- **Approved events with no change order number** (`Q10`). If the paperwork never issues, the money may never be billed.
- **Delay events logged without a cost.** Time is money under most contracts. Estimate it, even roughly.

## Daily reports

The daily report is the most important record on the job and the one most often skipped. Write it the same day, every
working day (`Q09`), even when "nothing happened". A day with no report is a day nobody can prove anything about.

**A good daily report contains:**

- weather, and whether it affected work;
- manpower, by trade if you can;
- work performed, by area and trade;
- delays and disruptions, with the cause as observed ("waiting on RFI-013 at corridor duct");
- inspections and tests, with results;
- deliveries, visitors and instructions received on site;
- safety observations, incidents and toolbox talks.

**Write facts, not opinions.** "Duct crew stood down at 10:00, sprinkler main in conflict, RFI-013 raised" is evidence.
"Engineer's fault again" is not.

**Traps:** reports written days later from memory; copy-pasted reports that say the same thing every day; delays recorded
without the cause; photos with no date or location.

## Punch lists

**A good punch item contains:** a location precise enough to find it, a description of what is wrong and what fixes it, the
responsible trade, the date listed and the due date, a photo, and who verified the fix.

**"Ready for review" is not "closed".** The trade says it is fixed; someone else checks. An item closed without a verifier
or without a date (`Q05`) is an item that may come back at handover.

**Measure:** open items by responsible trade, overdue items, items waiting for review, and items closed without a
verifier.

## The weekly log review

Fifteen minutes, once a week, with the PM, the project engineer and the superintendent:

1. Export the logs and run `python3 -m cpr check logs/ --as-of <today> --markdown review.md`.
2. **Errors first.** Fix the records: missing dates, duplicate numbers, impossible dates.
3. **Procurement at risk** (`Q11`): for each item, decide expedite, resequence, substitute, or accept the delay.
4. **Notice** (`Q08`): anything flagged goes to whoever manages the contract today.
5. **Overdue RFIs by ball in court:** who is chased, by whom, by when.
6. **Answers with impact and no change event** (`Q12`): open the change event now.
7. **Missing daily reports** (`Q09`): write them from notes while memories are fresh, dated as written, and say so.
8. File the review. Over a job, the reviews themselves show the logs were kept properly.

## The checks

| Check | Severity | Finds |
| --- | --- | --- |
| `Q01` | error | The same number twice in a log |
| `Q02` | error | A missing, malformed or disallowed value |
| `Q03` | warning | Gaps in a numbered sequence |
| `Q04` | error | Dates in an impossible order |
| `Q05` | error | Answered, returned or closed with no date |
| `Q06` | warning | Open items with nobody holding the ball |
| `Q07` | warning | RFIs with no date needed |
| `Q08` | warning | Change event notice that may be late or missing |
| `Q09` | warning | Working days with no daily report |
| `Q10` | warning | Approved change events with no change order number |
| `Q11` | warning | Submittals that will not be approved in time for their lead time |
| `Q12` | warning | RFI answers with a cost or time impact and no change event |
| `Q13` | note | Items dated after the as-of date |

## When logs become evidence

If a dispute is likely, or has started, speak to counsel before changing anything in the logs. Keep the original exports,
with their dates, somewhere they cannot be edited. The [construction-data-migration](https://github.com/constructelligence-lab/construction-data-migration)
toolkit's `manifest` command records a hash of every file, so you can show later that nothing changed.

---

*Maintained by [Constructelligence](https://constructelligence.co) — building the AI infrastructure for construction.*
