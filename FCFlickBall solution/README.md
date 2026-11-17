# FCFlickBall: Initial Challenge submission

This folder is a self-contained submission repository. The frozen model reads the supplied **tactical tracking**, then generates one `H`, `A`, `D` or `X` label for each of the 199,319 tactical-video frames. It does not read an MP4 or train on the competition match.

The approach, external training data, possession interpretation, evaluation and limitations are described in [FCFlickBall.md](FCFlickBall.md).

Competition assets and prediction files are not distributed in this repository. Authorised participants can generate the submission using the instructions below.

## Install and reproduce

Use **CPython 3.11.9** and run these commands in PowerShell from this folder's root. Replace `D:\participant-data` with the authorised bundle location. That directory must contain:

```text
tactical/
  BAR-ATH_tactical_atd.xml
  BAR-ATH_tactical_atd.txt
```

These are the only two competition input files used. No video, Smart Tagging, homography, public labels, training-data download or network service is required for prediction.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m possession.submit --data-dir "D:\participant-data" --output submission_files\FCFlickBall.csv
.\.venv\Scripts\python.exe evaluation\validate_submission.py submission_files\FCFlickBall.csv
Get-FileHash submission_files\FCFlickBall.csv -Algorithm SHA256
```

On Linux or macOS use `.venv/bin/python` and forward slashes. Exact reproduction has been checked on Windows with Python 3.11.9; another operating system has not been independently verified.

The single reproduction command is `python -m possession.submit --data-dir "<participant-data-directory>" --output submission_files/FCFlickBall.csv` once the dependencies are installed. The model is loaded from this repository, independent of the data location. The program verifies the model hash and writes the CSV plus an ignored `.run.json` provenance record. Load only the supplied, trusted model; joblib files can execute code.

Expected CSV SHA-256:

```text
abda45972282c7d39a2e73d46ad4764c263b098701389e83ec0656d5c89e92c3
```

Expected model SHA-256:

```text
493eed8a1d3287fea0b3d58468a39b9ed9acc75ceaa4af563dbd407a9408c8ae
```

The hash proves identical bytes, not prediction accuracy. The official validator checks the header, row count, frame sequence and allowed labels without reading ground truth. Only format validation is used in this workflow. Competition scores and video are not used to select settings or inspect prediction errors.

## Inspecting the implementation

1. `possession/tactical.py` reads the metadata and tracking, checks frame order and separates the halves.
2. `possession/ml_features.py` calculates 105 measurements from player/ball geometry and past/future observations.
3. `possession/ml_model.py` predicts frame probabilities and selects a coherent whole-half sequence.
4. `possession/ml_cli.py` writes and validates the complete CSV. `possession/submit.py` selects the frozen model.

The seven artificial tests cover feature ordering, track-slot permutation, missing-ball features, half boundaries, deflections, short possessions, stoppages, external-label mapping and model persistence. They neither read nor label the provided game. A tiny artificial model is fitted only to test saving/loading; it never replaces the submission model.

## Optional: reproduce external training

This is unnecessary for regenerating the final CSV. The bundled model is the submission artifact. To inspect training, use the same environment and approximately 2.63 GB of external downloads, plus space for prepared arrays:

```powershell
.\.venv\Scripts\python.exe -m training.download_idsse --dest external_data\idsse
.\.venv\Scripts\python.exe -m training.idsse --source external_data\idsse --dest external_data\prepared
.\.venv\Scripts\python.exe -m training.train --prepared external_data\prepared --model artifacts\retrained.joblib --report artifacts\retrained_validation.json
```

Only licensed external IDSSE matches may enter this procedure. The commands save new artifacts separately; they do not replace the frozen submission model. Published validation and held-out reports are in `reports/`. The held-out match was used once for reporting after selection, not as a tuning loop. Retraining is not required to produce byte-identical submission predictions.
