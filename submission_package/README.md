# External-data ML possession solution

The selected solution is a CPU gradient-boosted classifier trained only on four licensed external IDSSE matches, followed by a whole-half sequence decoder. It reads the supplied tactical tracking locally and outputs one H/A/D/X label per tactical-video frame. Selection is fixed in configs/selected.json; the model passed the predeclared external validation gate. The earlier state-machine fallback remains available.

## Regenerate the submission

Use Python 3.11.9. From this folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m possession.submit --data-dir ..\data --output artifacts\TEAM.csv
.\.venv\Scripts\python.exe evaluation\validate_submission.py artifacts\TEAM.csv
Get-FileHash artifacts\TEAM.csv -Algorithm SHA256
```

After moving this folder, replace the data path with the authorised participant bundle location. Prediction uses tactical ATD XML/TXT and the bundled model. No external training data, ground truth, video decoder, network or retraining is required. This is tracking-based inference; arbitrary MP4 detection/tracking is outside this implementation. Rename TEAM yourself before submission.

Expected final ML CSV SHA-256:

```text
abda45972282c7d39a2e73d46ad4764c263b098701389e83ec0656d5c89e92c3
```

The hash checks reproduction, not accuracy. The CSV contains 199,319 data rows. The official validator's inherited suggestion to score public GT is not part of this workflow.

## External results

Each score averages halves within matches, then matches equally. Masked tracking hides external ball observations in fixed-seed bursts covering about 30% of frames. None of these scores is on the competition match.

| External split / condition | ML spellF1 | ML macroF1 | Baseline spellF1 | Baseline macroF1 |
|---|---:|---:|---:|---:|
| Validation clean | 0.6300 | 0.9306 | 0.3402 | 0.4052 |
| Validation masked | 0.5766 | 0.9112 | 0.2797 | 0.3997 |
| Held-out clean | 0.6304 | 0.9365 | 0.3143 | 0.4104 |
| Held-out masked | 0.5740 | 0.9239 | 0.2793 | 0.4129 |

The comparator is nearest-player assignment with +/-50-frame smoothing. On clean external tracking it rarely predicts D, contributing to its weak macroF1. This does not prove superiority over the earlier tag-assisted fallback or predict the private competition score. Tracking noise and provider label definitions differ.

Full reports are in reports/. Selection used two validation matches and four decoder strengths only. The held-out match was evaluated once afterward; no retraining or selection followed it. Decoder strength 2.0 was frozen before competition inference. No public competition score was used for the ML attempt.

## Optional external-only training reproduction

The frozen model is supplied in models/idsse_hgb.joblib. Only load trusted joblib artifacts; they can execute code. To reproduce training without overwriting deployment weights:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-training.txt
.\.venv\Scripts\python.exe -m training.download_idsse --dest external_data\idsse
.\.venv\Scripts\python.exe -m training.idsse --source external_data\idsse --dest external_data\prepared
.\.venv\Scripts\python.exe -m training.train --prepared external_data\prepared --model artifacts\retrained.joblib --report artifacts\retrained_validation.json
```

This downloads about 2.63 GB of external XML. The downloader verifies published MD5 checksums and records SHA-256 hashes. Verified file provenance is in training/idsse_manifest.json. Training uses every fifth labelled frame after full-resolution feature extraction; evaluation retains every frame. Normal inference never calls fitting routines. Do not use the held-out match as an experiment loop.

## Retained fallback

```powershell
.\.venv\Scripts\python.exe -m possession.cli --data-dir ..\data --config configs\default.json --output artifacts\FALLBACK.csv
```

Fallback CSV SHA-256: 9db578ab1f2d275f3f4bfca183082d2dfc8fe3e4d1c728016b9cad96d0bce909. Its historical public-score check did not guide this ML attempt.

## Handover

TEAM.md describes the selected method; rename it for upload. THIRD_PARTY_NOTICES.md records data rights and attribution. PARAMETER_PROVENANCE.md records the training/selection process. PACKAGING_AUDIT.md records completed checks. TWO_DAY_PLAN.md and HANDOFF.md preserve the original team coordination plan; implementation was subsequently performed locally by the agent at the user's request.

The organisers' 3 November clarification governs this work: external-only training/tuning, no manual competition labels or output repair, no checking output against supplied video, and no uploads of participant assets to AI services. This source package contains neither participant inputs nor competition ground truth.

Copy the reviewed folder contents, including .gitignore, into your submission repository. Retain models/, configs/, reports/, source, tests and required notices. Omit .venv/, external_data/, artifacts/, caches and personal correspondence. Publication, commits, team naming, the form and final upload remain the user's responsibilities.
