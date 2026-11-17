# FCFlickBall: Frame-level possession inference

**Competition:** More than a Hack 2027, Initial Challenge  
**Registered team name:** FCFlickBall  
**Technical document:** November 17, 2026

## 1. Objective and approach

Our solution assigns one label to every tactical-video frame: `H` for home-team live possession, `A` for away-team live possession, `D` for stopped play and `X` for abstention. The output contains 199,319 rows, with frames numbered from 0 to 199318.

We use a histogram gradient-boosted classifier, implemented by scikit-learn's `HistGradientBoostingClassifier`, followed by whole-half sequence decoding. The classifier estimates home, away and dead-ball probabilities from tracking measurements. The decoder combines these probabilities with learned state-transition frequencies to select a sequence of labels. This approach is practical on a CPU and can use subsequent observations to interpret an ambiguous touch without requiring a video detector or a large neural network.

The model is frozen before competition inference. Feature extraction uses observations from the past and future, so this is an offline method, not a real-time predictor.

## 2. Competition assets and alignment

The selected method reads only `tactical/BAR-ATH_tactical_atd.xml` and `tactical/BAR-ATH_tactical_atd.txt`. The XML identifies team membership for tracking slots; the text supplies player and ball coordinates. Supplied MP4 files, broadcast tracking, homography and Smart Tagging are not inputs to the final model. An earlier rule-based approach used Smart Tagging; it was superseded and is not included in this final package.

Participant tracking frame 1 maps to output frame 0. Normalised positions are converted to metres using the published 105.3 by 68 metre pitch. Historical corrected-tracking offsets are not applied to participant ATD records. Track slots represent team membership rather than stable player identities. Frame order and count are checked, and each half is processed independently.

The published graded blocks are frames 11185-90651 and 110808-190197, inclusive. Other frames receive `X`. The published pre-kickoff interval of the second graded block receives `D` until frame 113742, as specified by the organisers' FAQ. These are supplied timeline constants, not corrections inferred by watching the game. A wholly unobservable half receives `X`.

## 3. External training data and attribution

All training and parameter selection use **IDSSE version 1**, an external collection of seven Bundesliga matches. The data are published by Manuel Bassek, Robert Rein, Hendrik Weber and Daniel Memmert (2025), *An integrated dataset of spatiotemporal and event data in elite soccer*, Scientific Data 12, 195.

- Dataset: https://doi.org/10.6084/m9.figshare.28196177.v1
- Paper: https://doi.org/10.1038/s41597-025-04505-y
- Licence: Creative Commons Attribution 4.0 International; attribution and transformations are recorded in `THIRD_PARTY_NOTICES.md`.

Targets come from the DFL / Sportec Solutions provider fields, not from annotations created by our team: inactive `BallStatus` maps to `D`; active play with `BallPossession` 1 maps to `H`, and 2 maps to `A`. Unknown targets are excluded. These are provider-supplied external labels; their semantics may differ from the challenge's corrected tracking. We make no claim that the team independently audited each provider label.

| Use | Match identifiers | Amount |
|---|---|---|
| Training | J03WMX, J03WN1, J03WOH, J03WOY | Four matches, eight halves |
| Validation and decoder selection | J03WPY, J03WQQ | Two matches, four halves |
| Final held-out reporting | J03WR9 | One match, two halves |

Both halves of each match stay in the same split. Training takes every fifth valid frame after full-resolution feature extraction and contains **453,832 samples after augmentation**. Evaluation uses full-resolution halves. The release, file identifiers, checksums and splits are recorded in `training/idsse_manifest.json`. External raw data are not bundled but can be retrieved by the supplied downloader.

## 4. Features, learning and possession decisions

The 105 inputs include distances from the ball to the nearest three players on each team, differences between team distances, observed player counts, ball observation status, position, speed, speed change and distance from pitch boundaries. They also include time since/until a ball observation and one- and three-second past/future samples and rolling summaries. Missing measurements remain missing, with observation indicators. Context never crosses halftime. Possession labels, ball-status targets, event labels, identities and match minute are excluded from predictor inputs.

Training adds fixed-seed missing-ball bursts lasting 0.2-3 seconds, covering approximately 30% of each external half, and home/away swaps with corresponding target swaps. Features are recomputed after masking. This teaches robustness to missing observations and team ordering without using the competition game.

Classifier settings are learning rate 0.1, 100 iterations, 15 maximum leaf nodes, minimum 20 samples per leaf, L2 regularisation 1, no early stopping and random seed 2026. A three-state transition table is learned from consecutive external training targets with add-one smoothing. Whole-half Viterbi decoding maximises the sum of log frame probabilities plus a weighted sum of log transition probabilities. Decoder strengths 0, 0.25, 1 and 2 were compared on external validation matches only; **2** was selected. The classifier settings and augmentation recipe were fixed initial choices, not parameters calibrated on competition output.

The intended possession interpretation is continued ownership during passes and loose balls until the opponent establishes control. For example, a brief opposing touch followed by continued home control should remain `H`; sustained opposing control should become `A`. Later observations and the transition model support this distinction. They do not explicitly recognise or guarantee successful-pass and interception events, and they do not justify moving a turnover back to the original pass. `D` is learned separately: `H, D, H` describes two home possessions. Missing ball observations alone do not force `D`. There is no fixed minimum possession length or manually supplied transition list.

## 5. External evaluation

We use the organisers' metric functions: `spellF1` measures possession intervals and determines ranking; `macroF1` measures frame labels and breaks ties. Scores below average halves within matches, then matches equally. The comparator uses nearest-player ownership with a plus/minus 50-frame majority window on the same external inputs.

| External condition | Model spellF1 | Model macroF1 | Comparator spellF1 | Comparator macroF1 |
|---|---:|---:|---:|---:|
| Validation, clean | 0.6300 | 0.9306 | 0.3402 | 0.4052 |
| Validation, masked | 0.5766 | 0.9112 | 0.2797 | 0.3997 |
| Held-out, clean | 0.6304 | 0.9365 | 0.3143 | 0.4104 |
| Held-out, masked | 0.5740 | 0.9239 | 0.2793 | 0.4129 |

Adoption required better `spellF1` and no worse `macroF1` on both clean and masked validation. Eligible settings were ranked by masked `spellF1`, then masked `macroF1`, then smaller decoder strength. The held-out match was evaluated once after selection, with no subsequent model changes. Detailed reports are included.

These are **external dataset results, not competition scores**. The comparator rarely predicts `D` on clean external tracking, explaining part of its weak frame score. These comparisons do not establish improvement over the private competition benchmark or the earlier tag-assisted method.

## 6. Rules and limitations

The organisers' November 3 clarification takes precedence over conflicting older guidance. For the selected ML method, fitting and tuning used external data only. Competition inference reads neither video nor ground truth, does not update the model and makes no manual tracking or prediction corrections. Output is not checked against the supplied video. Restricted match assets and extracts are not uploaded to AI services or included in the public repository. Local automatic checks verify software, file format and reproduction, without assessing possession accuracy against the video.

For development transparency, an earlier untrained fallback received one historical public-window pipeline score check, with no subsequent parameter changes from that check. It did not guide selection of this ML model. The selected ML attempt was not scored against competition ground truth.

Limitations include only seven external matches, one reporting holdout and differences between provider label definitions and tracking quality. Artificial missing-ball bursts do not capture every occlusion, identity error or aerial challenge. Geometry may not reveal referee decisions, and sequence decoding may suppress short genuine possessions. The system does not accept arbitrary MP4 input; a separate detection/tracking stage would be needed. With more time, additional licensed external matches and external validation of stoppage and transition behaviour would be priorities.

## 7. Reproduction and deliverables

Use Python 3.11.9 and the pinned `requirements.txt`. From this repository root, with the environment active:

```powershell
python -m possession.submit --data-dir "D:\participant-data" --output submission_files\FCFlickBall.csv
python evaluation\validate_submission.py submission_files\FCFlickBall.csv
```

The bundled model eliminates any need to retrain or download external data to reproduce the submission. Its hash is checked before loading. The expected CSV SHA-256 is:

```text
abda45972282c7d39a2e73d46ad4764c263b098701389e83ec0656d5c89e92c3
```

`README.md` provides installation, tests, optional external training and publication instructions. `reports/package_verification.json` records packaging checks. The final CSV is uploaded privately to the organisers; source, frozen model and this document belong in the public repository. The format validator and file hash establish structural validity and reproduction, not competitive accuracy or organiser approval.
