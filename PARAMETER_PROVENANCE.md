# Parameter provenance and change policy

The parameters in `configs/default.json` are fixed initial engineering assumptions. There is no training, fitting, calibration, or automatic parameter search in the current pipeline. No external dataset was used to select them, so they must not be described as externally tuned or proven optimal.

| Parameter group | Initial basis |
|---|---|
| Pitch dimensions | Published competition metadata |
| Control distance and distance advantage | Initial geometric proxy for control |
| Turnover confirmation window | Initial rule for rejecting brief opposing contacts |
| Short-gap limit | Initial conservative limit on estimated positions; estimates do not establish changes |
| Tag persistence | Initial rule for requiring sustained automatic evidence |
| Boundary, stationary-ball, and restart rules | Initial tolerances for noise and short transients |

The fixed settings predate the candidate's public five-minute scoring check. They were not revised in response to that score. Artificial sequences test whether the code implements the rules; they are not human labels for the provided match or a fitting dataset.

Published frame counts, frame rates, and kickoff boundaries describe the input contract. They are not parameters discovered by comparing predictions with the match video.

## Any future tuning

Under `RULES_CLARIFICATION.md`, use only external data for training, fitting, calibration, parameter tuning, or choosing between variants. This includes tuning hand-written rules as well as machine-learning models.

Before replacing the current configuration, record:

1. External dataset source, rights, licence restrictions, and organiser access.
2. Label definitions and how they match this challenge's possession and dead-ball definitions.
3. Separate training and validation matches, with no provided-game examples.
4. Parameters or model choices compared and the external validation procedure.
5. Selected configuration, model weights if any, dependencies, and reproduction command.

Do not use this match's video, ground-truth labels, manual observations of prediction errors, or its automatically generated pseudo-labels as training/tuning data. Running inference on the provided match must not update model weights or configuration.
