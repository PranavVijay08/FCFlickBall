# Run the possession submission

This is a local, CPU-only implementation of the Initial Challenge. It predicts the tactical video's 199,319 frames using the supplied automatic tactical tracking and Smart Tagging. It does not train on, import, or require ground-truth labels.

## Before you run it

Read `RULES_CLARIFICATION.md` first: the organisers' email takes precedence over conflicting older instructions. Also read `RULES.md`, `DATA.md`, `EVALUATION.md`, `SUBMISSION.md`, and your signed data-use terms. Keep downloaded match assets local. Do not check predictions or transition logs against the video. Do not send provided data or extracts to AI services. Intermediate files may be provided through the organisers' authorised channel; keep them out of public Git unless their redistribution is explicitly permitted.

Use CPython 3.11.9 and install the exact versions in `requirements-submission.txt`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-submission.txt
```

Place the authorised data bundle under `data/`. The required files are the tactical `*_atd.txt`, `*_atd.xml`, and `*_smart_tagging.xml` in their original names. The tactical video is optional for this inference pipeline. The delivered video here is named `BAR-ATH_tactical-001.mp4`, whereas `games.py` expects `BAR-ATH_tactical.mp4`; the CLI detects the single suffixed variant or accepts `--tactical-video PATH`. No video frames enter the predictions.

## Generate the file

From the repository root:

```powershell
python -m possession.cli --data-dir .\data --config configs\default.json --output evaluation\results\TEAM.csv
python evaluation\validate_submission.py evaluation\results\TEAM.csv
```

Rename `TEAM.csv` and `TEAM.md` to your registered team name for submission, then run the same command with the final CSV name. The inference command writes a local `*.run.json` manifest beside the CSV, with dependency versions and SHA-256 hashes for the source, inputs, configuration, and output. The manifest and CSV are ignored by Git. `--diagnostics artifacts\transitions_local.csv` adds a local transition log for debugging; it must never be published.

To test behavior without any match labels:

```powershell
python -m unittest discover -s tests -v
```

To regenerate the provided references in a local ignored directory:

```powershell
python starter\baseline.py --out artifacts\baselines
```

Use the format validator, synthetic tests, input-integrity checks, and byte-for-byte reproduction checks. Do not train, tune, fit, calibrate, or select a version using this match. The candidate was scored once on the public five-minute labels before the clarification, after its settings were fixed; no settings changed because of that result. Our updated workflow avoids further possession-score comparisons on this match unless organisers confirm their diagnostic use. Any future tuning must use licensed external data.

## What the program does

1. Verifies every raw tracking record is present and in frame order. ATD frame 1 maps to tactical video frame 0.
2. Reads the ball and player positions in metres, computes each team's nearest player, and marks only clear observed control as strong evidence.
3. Interpolates gaps of up to ten frames for supporting context. Estimated positions cannot by themselves trigger a possession change or stoppage.
4. Turns overlapping attacking and defending phase tags into at most one team clue per frame. A contradictory pair becomes neutral.
5. Processes each half separately. A brief opposing touch leaves possession unchanged; sustained geometric evidence, or a sustained unopposed phase tag during a tracking gap, changes it. Positive outside-pitch or set-piece evidence marks a stoppage. Renewed motion or sustained live-phase evidence marks a restart.
6. Emits exactly one of `H`, `A`, `D`, or `X` for each tactical frame and applies the official format validator.

The fixed thresholds are in `configs/default.json`. They are initial implementation assumptions, not externally tuned or proven optimal values. See `PARAMETER_PROVENANCE.md` for their origin and the external-data-only policy for future changes. The program has no training step. Its local transition log explains automatic decisions; do not compare it against the provided video.

## Release checklist

- Confirm all members registered under the same team name and accepted the data-use terms.
- Run the synthetic tests and regenerate the final CSV from clean source.
- Check the final CSV with `evaluation/validate_submission.py`.
- Rebuild on a second local machine and compare the CSV SHA-256 values.
- Confirm no restricted assets or generated match predictions appear anywhere in public Git history.
- Confirm the public repository includes code, pinned dependencies, configuration, this run command, and the technical document.
- Confirm the emailed form URL, Google account, and actual deadline time zone. The repository specifies November 17, 2026, but no cutoff time.
- Submit one response per team and retain the final file hash and submission confirmation.
