# Initial Challenge working checklist

Read `RULES_CLARIFICATION.md` first. The organisers' clarification takes precedence over conflicting older documents and earlier advice.

## What the system must answer

For every tactical frame, output `H`, `A`, `D`, or `X`. Control changes only when the opposing team gains it. A loose ball stays with the last controlling team. A stoppage ends a possession. Recovering complete possessions drives `spellF1`; frame-level `macroF1` is the first tie-break.

## Permitted work

- Use the authorised automatic tracking, tags, video, and homography locally.
- Inspect the video to understand what counts as possession, without checking predictions against it.
- Run automatic input-integrity, file-format, and reproducibility checks.
- Test implementation behavior with synthetic examples unrelated to provided-game frames.
- Train and tune only on licensed external datasets; record the rights and validation process.
- Provide intermediate files through authorised organiser channels, subject to data-use permissions.
- Use accessible external methods only if their use and reproduction are documented.

## Prohibited work

- No human labels or manual corrections for this match, including individual transitions.
- No checking predictions, transitions, or overlays against the provided video.
- No training, fitting, calibration, tuning, or model selection on the provided game, including its public labels or automatic pseudo-labels.
- No private ground truth or human-produced event/possession data about this match.
- No provided data or extracts uploaded to AI services.
- No redistribution of supplied data or reconstructable derived data.
- No final CSV that the public source cannot regenerate exactly.

The signed registration terms govern detailed data-use permissions. A malformed file is skipped by the official scorer. See `RULES.md`, `FAQ.md`, `EVALUATION.md`, and `SUBMISSION.md` for the full competition instructions.

## Completion gates

1. Local environment and supplied baseline reproducible.
2. Tracking and tags aligned to zero-based tactical frames.
3. A complete algorithmic CSV generated from the supplied data.
4. Synthetic behavior tests pass; fixed assumptions are documented, and any tuning has external-only provenance.
5. Exact final CSV passes the official validator.
6. Independent local rebuild produces the same SHA-256 hash.
7. Public repository contains source, pinned dependencies, and reproduction instructions, with no restricted files in Git history.
8. Technical document and CSV use the registered team name; form access, deadline time zone, and submission receipt are confirmed.

Target readiness: November 10, 2026. Official repository deadline: November 17, 2026. The repository does not state a cutoff time or time zone.
