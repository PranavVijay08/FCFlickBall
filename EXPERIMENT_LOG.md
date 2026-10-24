# Experiment and decision log

Only record general design reasons, synthetic test results, and reproducibility checks here. Do not add match-specific answer labels, tracking extracts, or transition corrections.

| Decision | Reason | Evidence |
|---|---|---|
| Use tactical tracking and automatic tags | Both are on the submission timeline; broadcast is not synchronised | `DATA.md` and asset loader documentation |
| Use fixed temporal confirmation | Isolated nearest-player changes can fragment possessions | `EVALUATION.md` and synthetic tests |
| Keep missing ball separate from dead ball | The ball is frequently not tracked during live play | `DATA.md` and synthetic missing-ball test |
| Freeze `configs/default.json` before public score inspection | Public five-minute labels are a pipeline check only | `RULES.md` and `EVALUATION.md` |
