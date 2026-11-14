# Team handoffs: Pranav, Jilla, Ashwin and Sriva

Working template only: assignments and checkpoints below are planned, not reports of completed ML work. Each owner updates their row at the end of a work block. Record UTC timestamps with dates, since Australia and the USA may be on different calendar days.

## Ownership

| Owner | Responsibility | Current starting point | Next deliverable |
|---|---|---|---|
| Pranav - Brisbane | Tactical adapter, inference integration, fallback, repository preparation | Packaged fallback tested; ML integration not implemented | Common-schema tactical inputs and tested inference command |
| Jilla - Sydney | Licensed external data, adapter, common features, label/split QA | Source research/manifest available; full external data not yet processed | Tiny invented fixture, schema and first external half |
| Ashwin - USA | Training, temporal decoder, external validation, frozen artifacts | ML candidate not implemented | Fit/save/load/predict using the invented fixture |
| Sriva - USA | Independent metrics/checks, clean reproduction, technical document, final release | Fallback technical-document template exists | Verify authorised data access, repo/form access and clean environment |

## End-of-block update template

```text
Owner:
UTC date/time:
Branch and commit:
Completed:
Next owner and next action:
Command to run (no credentials):
Feature schema / config / model hash:
External-data version and split:
Tests passed / known software defects:
Blocker and fallback decision if applicable:
Next planned availability (date, time, timezone):
```

Do not paste competition tracking rows, screenshots, clips, per-frame predictions or feature arrays here. Public handoffs contain code references, external provenance, test summaries and hashes. Keep restricted files local and use only permitted participant-data access methods.

## Gates and release checklist

- Data gate: Jilla's first two working hours; one parsed external half and verified labels, or stop the new ML attempt.
- First proposed checkpoint: 2026-11-14 22:00 UTC (Sunday 08:00 Brisbane / 09:00 Sydney; Saturday afternoon/evening in much of the USA). A written update is enough.
- Before Australia Sunday sign-off: Pranav leaves the reproducible fallback, tactical inference command and repository contents; Jilla leaves schema/caches/provenance. Confirm Sriva can legally access the supplied assets and can submit. No Monday Australia availability is assumed.
- Final model/integration gate: 2026-11-15 22:00 UTC. Ashwin supplies the qualifying frozen ML candidate or declares fallback; Sriva verifies the release.
- Target submission completion: 2026-11-16 02:00 UTC, still Sunday evening in the continental-USA examples in the plan.
- Only Sriva submits the team form by default. If access requires Pranav, agree and record a real available upload window before relying on that arrangement.

Final release record (fill when actually completed):

```text
Selected method:
Selection evidence (external data only):
Code commit:
Model/config hash, if used:
Validated CSV filename and SHA-256:
Clean reproduction completed by:
Registered team name:
Public repository URL:
Technical document filename:
Deadline time/timezone verified from:
Submitted by / UTC timestamp:
Confirmation retained at (private location):
```
