# Reproducible possession submission package

Status on 14 November 2026: this folder contains the existing, untrained CPU fallback and a two-day plan for an external-data ML candidate. The ML candidate is NOT implemented or trained here. See [TWO_DAY_PLAN.md](TWO_DAY_PLAN.md).

The plan now covers four members: Pranav (Brisbane), Jilla (Sydney), Ashwin and Sriva (USA), each contributing 7-10 hours. It uses a 28-hour core budget, asynchronous handoffs in [HANDOFF.md](HANDOFF.md), and Sriva as the proposed final verification/submission owner during the USA weekend.

The fallback source and original technical document were copied from commit `7c35045dce2838a79133a38abc75acb285289290` on `feature/AI_attempt`. The original branch and its history were not changed. No match assets, competition ground truth, existing prediction files, or Git history were copied into this package.

## Run the current fallback

Use Python 3.11. These PowerShell commands assume you are inside this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-submission.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m possession.cli --data-dir ..\data --config configs\default.json --output artifacts\TEAM.csv
.\.venv\Scripts\python.exe evaluation\validate_submission.py artifacts\TEAM.csv
Get-FileHash artifacts\TEAM.csv -Algorithm SHA256
```

After moving this folder to another repository, replace `..\data` with the absolute path of the participant data bundle. The inference code does not depend on source files in the parent repository. It requires the tactical ATD XML, ATD TXT and Smart Tagging XML. It does not need a video decoder or network access.

Use your registered team name in the final CSV and technical-document filenames. `TEAM.md` currently documents the fallback; rewrite it if the ML candidate becomes the submitted method.

The expected fallback CSV SHA-256 on the current data is:

```text
9db578ab1f2d275f3f4bfca183082d2dfc8fe3e4d1c728016b9cad96d0bce909
```

This is an integrity check, not evidence of possession accuracy. The CSV has 199,319 data rows and the exact header `frame,label`.

## Rules and validation

Read [RULES_CLARIFICATION.md](RULES_CLARIFICATION.md) and [PARAMETER_PROVENANCE.md](PARAMETER_PROVENANCE.md). The organisers' 3 November email overrides conflicting older repository advice. Do not compare predictions with the supplied video; do not train or tune on any competition-match material; do not upload those assets or extracts to AI services.

The official format validator is included. Its inherited final message suggests public scoring; do not follow that suggestion for tuning or candidate selection. This package intentionally contains no public ground-truth file and no public-score notebook. Use external-match labels for development evaluation.

## What to publish

Copy this folder's contents to the root of a fresh public submission repository, including `.gitignore`. Do not copy the parent `.git`, `.venv`, data, caches, generated outputs or the email PDF. Keep the MIT copyright notice and `CITATION.cff` for reused organiser code. Upload the final CSV and technical document through the organisers' form. The public repository supplies their reproduction source.

If ML is adopted, publish the frozen model, its configuration and provenance, plus the training code and exact external-data retrieval manifest. Add the external dataset's attribution and licence notice. A training recipe alone is not enough when the submitted prediction file depends on weights that are not available to the organisers.
