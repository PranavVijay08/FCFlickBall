# TEAM: External-data temporal possession model

Replace TEAM with the registered team name before uploading this Markdown technical document. This document describes the selected trained method.

## Approach and assets

We emit H for home live possession, A for away live possession, D for stopped play, and X outside the graded periods or for wholly unobservable halves. The input is the supplied automatic tactical tracking; we use it instead of rebuilding video detection. Raw video, broadcast assets, homography and Smart Tagging are not inputs to the selected learned model. The earlier untrained tag-assisted method remains available as a fallback.

A scikit-learn HistGradientBoostingClassifier estimates H/A/D probabilities. Explicit past/future context and a whole-half sequence decoder allow subsequent observations to resolve an earlier ambiguous touch. All fitting and model selection use external matches. Competition inference loads frozen weights and never trains.

## External data and rights

IDSSE version 1 is attributed to Manuel Bassek, Robert Rein, Hendrik Weber and Daniel Memmert (2025), An integrated dataset of spatiotemporal and event data in elite soccer, Scientific Data 12, 195. Paper: https://doi.org/10.1038/s41597-025-04505-y. Dataset: https://doi.org/10.6084/m9.figshare.28196177.v1. The authors document DFL permission and CC BY 4.0 licensing. THIRD_PARTY_NOTICES.md and training/idsse_manifest.json record attribution, transformations, file IDs and verified checksums.

We use the provider's BallStatus/BallPossession as external targets: inactive -> D; active and possession 1 -> H; active and possession 2 -> A. Unknown labels are excluded. The team created no manual annotations. These are external provider annotations, not information about the competition match.

Training matches: J03WMX, J03WN1, J03WOH, J03WOY. Validation: J03WPY, J03WQQ. Held-out report: J03WR9. Both halves remain in the same split. There is no shuffled-frame train/test split. The held-out match was evaluated once after selection, with no subsequent model or configuration changes.

## Alignment and features

DFL object records are aligned by frame number within each half. Centred metre coordinates are translated using the actual pitch dimensions. Participant ATD frame 1 becomes submission frame 0; normalised positions are converted using 105.3 x 68 metres. Historical corrected-tracking offsets are not applied. Track slots are used for team membership rather than permanent player identity.

The 105 features include nearest three player-to-ball distances per team; nearest-team distance difference; observed player counts; ball observation flag; ball speed and speed change computed at 25 Hz; relative ball coordinates and signed boundary distance; time since/until an observed ball; and one-/three-second past/future samples and rolling summaries. Missing values remain NaN with observation/coverage information. Context never crosses halves. BallStatus, possession, event fields, identities, match minute and ball height are excluded from predictor inputs.

## Training and decoding

Fixed classifier settings: learning_rate=0.1, max_iter=100, max_leaf_nodes=15, min_samples_leaf=20, l2_regularization=1, early_stopping=False, random_state=2026. These are initial engineering choices, not an exhaustive parameter search. Every fifth valid training frame is sampled after full-resolution features are computed. Training includes 453,832 samples after augmentation.

Augmentation uses a fixed-seed external copy with missing ball observations in 0.2-3-second bursts covering approximately 30% of each half, plus home/away swapping with corresponding target swapping. All dependent features are recomputed after masking. The mask is independent of labels and competition output.

A 3x3 transition table is estimated from consecutive valid training labels with add-one smoothing, including swapped counts. Viterbi-style decoding maximises sum(log frame probabilities) plus lambda times sum(log transition probabilities). This is a discriminative sequence score. Only lambda values 0, 0.25, 1 and 2 were tested on validation; 2 was selected. There is no fixed minimum possession duration or transition list tied to competition frames.

## Possession interpretation

The intended behaviour is continuous ownership through passes and loose balls until the opponent gains control. A slight interception without subsequent control should not change ownership. Learned temporal features and decoding can support these distinctions but do not guarantee them. Future context helps interpret the transition; it does not justify moving a turnover back to the original misplaced pass.

D is a learned separate state and separates possessions even when the same team restarts. Missing ball observations alone do not force D. We do not use an uncalibrated confidence threshold to manufacture X within otherwise observed halves. Halves reset independently. Outside published graded blocks output is X; the publicly documented second-half pre-kickoff interval is D until frame 113742.

## External evaluation and selection

The official metric functions are applied separately to full-resolution external halves, then averaged within matches and equally across matches. The reference is the nearest-player baseline with +/-50-frame majority smoothing, evaluated on identical inputs.

| Split / condition | ML spellF1 | ML macroF1 | Baseline spellF1 | Baseline macroF1 |
|---|---:|---:|---:|---:|
| Validation clean | 0.6300 | 0.9306 | 0.3402 | 0.4052 |
| Validation masked | 0.5766 | 0.9112 | 0.2797 | 0.3997 |
| Held-out clean | 0.6304 | 0.9365 | 0.3143 | 0.4104 |
| Held-out masked | 0.5740 | 0.9239 | 0.2793 | 0.4129 |

Adoption required better spellF1 and no lower macroF1 on both clean and masked validation. Qualifying settings were ranked by masked spellF1, then masked macroF1, then smaller lambda. Full reports are in reports/. The clean baseline rarely predicts D, explaining part of its macroF1 weakness.

These scores are not competition scores and do not establish superiority over the earlier tag-assisted fallback. Provider semantics and input quality differ. The ML attempt did not score competition ground truth or use it for selection. The earlier fallback's historical public check is retained in EXPERIMENT_LOG.md; it did not guide this model.

## Rules and limitations

We follow the 3 November clarification: external-only training, fitting and tuning; no labels, tracking repair, prediction edits or pseudo-label training on the supplied game; no comparison of output against its video; no uploading participant assets or extracts to AI services. Prediction imports neither external training data nor any ground-truth file. Automatic local checks verify software and file integrity.

Limitations include seven external matches, a single reporting holdout, provider-specific control definitions and the difference between clean DFL tracking and noisy participant data. Masking does not simulate every tracking error, aerial ball or long correlated gap. Geometry cannot always establish whistle timing; temporal decoding can suppress short real possessions. Arbitrary MP4 input requires a separate tracking system and is outside this submission.

## Reproduction

Use Python 3.11.9, install requirements-ml.txt, and run from the package root:

```powershell
python -m possession.submit --data-dir <participant-data-folder> --output artifacts/TEAM.csv
python evaluation/validate_submission.py artifacts/TEAM.csv
```

The bundled frozen model is models/idsse_hgb.joblib; configs/selected.json pins its hash. No training-data download or retraining is required for submission reproduction. Expected CSV SHA-256: abda45972282c7d39a2e73d46ad4764c263b098701389e83ec0656d5c89e92c3. README.md includes installation, tests, external training and fallback commands. Keep participant assets, environments, caches and generated predictions out of public commits.
