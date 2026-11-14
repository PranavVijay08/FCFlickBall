# Experiment and decision log

Only record general design reasons, synthetic test results, and reproducibility checks here. Do not add match-specific answer labels, tracking extracts, or transition corrections.

| Decision | Reason | Evidence |
|---|---|---|
| Use tactical tracking and automatic tags | Both are on the submission timeline; broadcast is not synchronised | `DATA.md` and asset loader documentation |
| Use fixed temporal confirmation | Isolated nearest-player changes can fragment possessions | `EVALUATION.md` and synthetic tests |
| Keep missing ball separate from dead ball | The ball is frequently not tracked during live play | `DATA.md` and synthetic missing-ball test |
| Freeze `configs/default.json` before the historical public score check | No training or parameter selection on competition answers | Original rules; no settings changed after the check |

## November 7 clarification

The organisers' email in `RULES_CLARIFICATION.md` supersedes older advice. The fixed candidate had already received one public five-minute scoring check, with no subsequent parameter changes based on it. This history is retained; it does not authorise future tuning or video-based output checks.

The prediction code and configuration remain unchanged. Output must not be compared against the provided video. Any future training, fitting, calibration, tuning, or variant selection must use licensed external data. Earlier suggestions of training on this game's pseudo-labels or debugging output against video are withdrawn. Further match possession-score comparisons are paused unless organisers confirm diagnostic use; automatic format and reproducibility checks remain part of the workflow.
