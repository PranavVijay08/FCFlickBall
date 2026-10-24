# Initial Challenge working checklist

## What the system must answer

For every tactical frame, output `H`, `A`, `D`, or `X`. Control changes only when the opposing team gains it. A loose ball stays with the last controlling team. A stoppage ends a possession. Recovering complete possessions drives `spellF1`; frame-level `macroF1` is the first tie-break.

## Permitted work

- Use the authorised automatic tracking, tags, video, and homography locally.
- Inspect the video to understand and debug a general algorithm.
- Make algorithmic improvements and test them with synthetic examples.
- Use accessible external methods only if their use and reproduction are documented.

## Prohibited work

- No human labels or manual corrections for this match, including individual transitions.
- No tuning, training, or model selection against the public five-minute ground truth.
- No private ground truth or human-produced event/possession data about this match.
- No restricted assets or extracts sent to hosted/cloud LLMs.
- No redistribution of supplied data or reconstructable derived data.
- No final CSV that the public source cannot regenerate exactly.

The signed registration terms govern detailed data-use permissions. A malformed file is skipped by the official scorer. See `RULES.md`, `FAQ.md`, `EVALUATION.md`, and `SUBMISSION.md` for the full competition instructions.

## Completion gates

1. Local environment and supplied baseline reproducible.
2. Tracking and tags aligned to zero-based tactical frames.
3. A complete algorithmic CSV generated from the supplied data.
4. Synthetic behavior tests pass, then configuration is frozen.
5. Exact final CSV passes the official validator.
6. Independent local rebuild produces the same SHA-256 hash.
7. Public repository contains source, pinned dependencies, and reproduction instructions, with no restricted files in Git history.
8. Technical document and CSV use the registered team name; form access, deadline time zone, and submission receipt are confirmed.

Target readiness: November 10, 2026. Official repository deadline: November 17, 2026. The repository does not state a cutoff time or time zone.
