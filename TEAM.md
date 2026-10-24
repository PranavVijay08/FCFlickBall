# TEAM: Technical document for Phase 1 possession inference

Replace `TEAM` with the registered team name before submission.

## Task and approach

The system emits `H` for home possession, `A` for away possession, `D` for a dead ball, and `X` when ownership is unresolved. It writes one row for every frame of the tactical recording. A possession is a continuous live interval owned by one team. A stoppage separates possessions even when the same team restarts.

The method is deterministic and runs locally on a CPU. It reads the supplied automatic tactical tracking and Smart Tagging, extracts team-level evidence, then applies a small temporal state machine. The state machine remembers the previous owner through a loose ball or short loss of tracking. It changes owner only when opposing control persists. This is designed to limit false possession splits, which the competition's `spellF1` penalises. There is no learned model, human-made label, or manually corrected competition frame in the pipeline.

## Inputs and alignment

**Used:** tactical ATD metadata and raw tracking, plus tactical Smart Tagging. The metadata maps each track slot to a team. A slot is not treated as a player identity. The raw file is checked record by record: ATD `frame_id` 1 maps to tactical frame 0. Tag intervals are rounded from seconds at 25 frames per second. Normalised coordinates become metres using a 105.3 × 68 m pitch.

**Not used for inference:** tactical video, tactical homography, broadcast video and tracking, or external match data. Video and homography can be used locally to debug alignment. The broadcast recording has its own timeline and was excluded to keep the method reproducible within the project schedule.

The halves are processed separately. The published kickoff frame for each half starts its play-state inference. Frames before the second kickoff inside the graded second-half interval receive `D`. Frames before the first graded half, between halves, and after the match receive `X`.

## Evidence and missing data

For each observed ball position, the method finds the nearest tracked player from each team in pitch metres. A team supplies strong control evidence when its nearest player is within 2 m of the ball and at least 1 m closer than the opponent's nearest player. The method uses team membership only, so track fragmentation and slot swaps do not create a false player history.

Missing ball locations remain marked as missing. Gaps up to ten frames are linearly interpolated inside a half, but these estimated locations cannot establish a turnover, stoppage, or restart. A missing ball alone does not mean that play has stopped.

Automatic attacking phase tags supply a clue for the tagged team; defensive phase tags support its opponent. Overlapping contradictory clues cancel. Multiple agreeing tags still produce only one team clue. Set-piece tags support stoppage and restart decisions but their boundaries are not copied into the output as possession boundaries. Unassigned team tags, such as `N/A`, give no team clue.

## Possession and stoppage rules

The state stores whether play is live, dead, or unresolved, and the current owner if live. An isolated opposing touch does not switch possession. A turnover needs strong opponent evidence in at least 8 of 12 frames; its boundary is placed at the first supporting frame in that confirmation window. Where the ball or both teams' positions are unavailable, a single unambiguous opposing phase clue must persist for one second without contradictory strong geometry.

The ball is marked dead after five consecutive observed positions more than 0.5 m outside the pitch. A set-piece tag and an observed ball remaining within a 0.5 m area for two seconds also establish a stoppage. The same tag and two seconds without an observed ball supply weaker stoppage evidence when geometry is unavailable. Confirmation moves the boundary to the start of the supporting interval.

After a stoppage, the system waits for five consecutive observed, on-pitch frames moving faster than 1 m/s, or for one second of unambiguous live-phase evidence outside a set-piece interval. The restart owner comes from consistent observed control in that interval, or from a single unambiguous phase clue. Otherwise the frame is `X` until ownership becomes clear. State is reset at halftime.

All values are fixed in `configs/default.json`. They are reasoned starting assumptions, not parameters fitted to the competition match or selected against the public five-minute labels.

## Training and validation data

There is **no training data** and no human-labelled dataset. Synthetic sequences with invented answers test passes, deflections, turnovers, stoppages, restarts, missing observations, tags, track slots, and half boundaries. The supplied public ground truth may be used only for final alignment and label-meaning checks. It is not a training or tuning set and cannot establish full-match performance.

The inference module neither reads nor imports a ground-truth file. The public five-minute score and the private competition score are distinct. The published `spellF1 = 0.2433` baseline is a target to beat, not a measurement of this method.

## Limitations

The tracking misses the ball on many graded frames. Long gaps can hide a genuine turnover or restart, and automatic tags can be wrong or absent. A ball outside the pitch is not always easy to identify from noisy coordinates. A stationary ball during a set piece does not by itself identify the exact whistle frame. The fixed rules can therefore miss short possessions or place boundaries late or early. There is no independent, permitted full-match answer set for choosing improved settings before submission.

## Reproduce the CSV

Use CPython 3.11.9, install `requirements-submission.txt`, place the authorised match bundle under `data/`, and run:

```powershell
python -m possession.cli --data-dir .\data --config configs\default.json --output evaluation\results\TEAM.csv
python evaluation\validate_submission.py evaluation\results\TEAM.csv
```

The command writes a local manifest with the exact input, configuration, and output hashes. Re-run with the same inputs and compare the output hash. `SOLUTION.md` contains setup and submission checks. The public repository must exclude the match assets, generated predictions, and frame-level diagnostics.
