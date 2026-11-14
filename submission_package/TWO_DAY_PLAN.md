# Two-day completion plan: 14-15 November 2026 local weekends

## Decision and success criteria

The four members are Pranav (Brisbane), Jilla (Sydney), Ashwin (USA) and Sriva (USA). Budget seven hours each: **28 person-hours guaranteed**, with up to **40 person-hours** if everyone can contribute ten. The extra twelve hours are contingency, not required work or justification for adding a video pipeline. Use each person's local 14-15 November weekend. Final release during Sunday in the USA falls on Monday 16 November in Australia; no Monday work from Pranav or Jilla is assumed. Target final submission by Monday 16 November, 12:00 Brisbane / 13:00 Sydney, with a ready fallback before the Australian team goes offline on Sunday. The documented deadline is 17 November, but its time and timezone must be checked in official communications.

Use tactical tracking as the submission input. Pursue one small, trained CPU model using licensed external tracking, with a firm cutoff and the existing reproducible fallback. Do not start video detection, broadcast alignment, streaming infrastructure, a dashboard, a large neural network, or manual annotation of complete matches in this sprint.

Success means: one valid automatically generated CSV; a standalone public source repository that regenerates the exact bytes; a technical document matching the actual submitted method; recorded rules/data provenance; and a confirmed form submission. Better private spellF1 and macroF1 are aims, not results that can be guaranteed or measured locally.

## Verified starting point

- Active branch: `feature/ML_algo_solution`, initially clean at `f8f2629`. It has the official starter source, not a trained ML model. The `possession/` and `tests/` leftovers had no current Python source outside caches.
- Existing source on `feature/AI_attempt`, commit `7c35045`, is a fixed state-machine fallback. All 10 artificial tests passed again during this audit. Regeneration from a temporary clean source export produced exactly the existing `evaluation/results/TEAM.csv` SHA-256.
- That fallback is now staged in this folder. This is packaging of existing work, not new model training or improved accuracy. Its parameters are documented engineering defaults, not externally tuned settings.
- Local tactical assets: video about 5.22 GB, tracking about 196 MB, metadata, tags and homography. Broadcast video about 13.96 GB and its associated assets also exist. The suffixed video filenames are supported by the fallback and do not affect tracking-only inference.
- Python 3.11.9, numpy 2.2.5, pandas 2.2.3 and scikit-learn 1.6.1 were found. A torch import did not expose a usable normal package version; do not assume a working PyTorch environment. Existing `.venv` inherits system packages and is not proof of clean installation.
- The public scoring notebook includes a smoothing sweep. Do not execute that sweep against the competition labels. Existing score reports are not a basis for choosing this sprint's model.
- The signed registration terms and current submission-form email were not available in this audit. The team must check them before final upload.

## Rules that govern all four workstreams

The supplied PDF contains an organisers' email dated 3 November 2026, explicitly superseding earlier instructions. Its key operational consequences are:

| Allowed | Forbidden |
|---|---|
| Frozen inference using supplied automatic tracking, tags or video | Training, self-supervised fitting, pseudo-label training or calibration on this match |
| Automatic input integrity, format and reproduction checks | Comparing output with the supplied video, including transition overlays |
| Training and tuning on external data with documented rights | Any manual labels, tracking repair, output repair or frame-specific exceptions for this match |
| Local inspection of inputs to understand possession, without output checking | Uploading competition data or extracts to AI services, including data-bearing tool output |
| Providing intermediate files through authorised channels | Public redistribution of competition assets or reconstructable derivatives |
| Artificial examples for software tests | Public five-minute ground-truth model selection or parameter search |

All parameter choices requiring tuning use external validation only, including decoder penalties, confidence thresholds and rule parameters. Keep fitting routines separate from prediction. Never pass label-bearing columns into model features. No online fitting, target-match batch-statistic adaptation, or target-match pseudo-labels.

The email does not explicitly settle every diagnostic use of the public labels. This sprint avoids further competition possession scoring entirely; format validation and external evaluation are sufficient. This is a conservative workflow choice, not a claim that every diagnostic score is categorically banned.

Generic code assistance and public documentation research are useful. Do not paste restricted rows, videos, screenshots, generated per-frame features or prediction extracts into hosted AI prompts. Run those computations locally and keep the results local. The email PDF itself contains personal correspondence; do not publish it.

## External data choice and access gate

Primary source: **IDSSE / Sportec-DFL open data**. The authors describe seven full professional matches at 25 Hz, with frame-level ball control and live/dead status. The source is released with DFL permission under CC BY 4.0. This is substantially better aligned with the task than event-only datasets requiring new possession annotation.

Sources:

- Dataset: https://springernature.figshare.com/articles/dataset/An_integrated_dataset_of_spatiotemporal_and_event_data_in_elite_soccer/28196177
- Paper and field definitions: https://www.nature.com/articles/s41597-025-04505-y
- Author code: https://github.com/spoho-datascience/idsse-data
- Reference parser and numeric mappings: https://floodlight.readthedocs.io/en/latest/_modules/floodlight/io/dfl.html
- File catalogue: https://api.figshare.com/v2/articles/28196177/versions/1

The audit read the live Figshare catalogue: seven position XML files total 2,622,603,272 bytes; each is about 349-419 MB. Metadata files are roughly 12 KB each. Download position and match-information files only; event files are unnecessary for the first model. Process one match at a time, retain compact features, and remove only the external raw cache if storage is tight. No full-match MP4 or cloud GPU is needed.

The paper, parser and catalogue were checked, but the full raw corpus was not downloaded or profiled during planning. Actual parsing and label coverage are the first implementation gate. Prefer the original catalogue over a mirror's example match IDs: the official release inspected here contains WMX, WN1, WOH, WOY, WPY, WQQ and WR9, all with prefix `J03`.

Label conversion:

- `BallStatus=0` -> D, regardless of possession team.
- `BallStatus=1, BallPossession=1` -> H.
- `BallStatus=1, BallPossession=2` -> A.
- Unrecognised or missing status/ownership -> unknown external label; exclude from fitting and scoring, never silently map to D.

These are provider control labels, not the private competition ground truth. Definitions and observation quality may differ. Inspect external label transitions against the external tracking and documented events as needed; do not use competition video to reconcile definitions.

Lock the following match split before any results:

| Use | Matches |
|---|---|
| Train | J03WMX, J03WN1, J03WOH, J03WOY |
| Validation/model choice | J03WPY, J03WQQ |
| Final external report only | J03WR9 |

Both halves of a match stay in the same split. Do not split shuffled frames. Do not use the held-out report match to choose another variant or retry training. Seven matches still provide limited evidence of generalisation.

Record version, source file IDs/URLs, expected checksums, fetched SHA-256 hashes, attribution, label mapping, coordinate conversion and split. Verify the downloaded checksums. Retain provider licence/attribution; provide a retrieval script so organisers can obtain the same data.

**Access cutoff:** within Jilla's first two working hours, there must be at least one successfully parsed external half with validated labels and a working path to the remaining matches. Record the result in HANDOFF.md so Ashwin can start without a synchronous meeting. If this gate fails, stop new ML work and use the packaged fallback. Do not pivot to another multi-gigabyte dataset search.

## Smallest useful ML implementation

Use `HistGradientBoostingClassifier` from scikit-learn with explicit temporal features, followed by a three-state sequence decoder. This is trained ML: the classifier learns combinations of measurements from external labels. It is not a pretrained video understanding model. The scope is tracking-to-label inference, not arbitrary MP4-to-label inference.

Reference: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingClassifier.html

### Shared interface agreed before coding

One match adapter returns separate halves with: ordered frame IDs, timestamps, team-specific player x/y arrays, ball x/y, observation masks and pitch dimensions. External labels are in a separate array that is never accepted by feature extraction. Stable player IDs can be used by the external loader to group records, but are not model features.

Each half produces `X_features` (float32 matrix), `feature_names`, `frame_ids`, `fps=25`, `match_id`, plus a separate external `y_labels` only for training/evaluation. Share a tiny invented fixture immediately so the model teammate can work while the data loader is built. Lock feature order in a versioned schema; reject a model/feature mismatch.

Preserve all frame IDs. Align DFL object records by frame number, not array position. Translate centred metric DFL coordinates into a common pitch convention using that match's dimensions. Competition coordinates are normalised and must be converted with 105.3 x 68 m. Compute speed from positions and time consistently; DFL's native speed field is km/h, not m/s. Exclude ball height, provider event fields, identities, absolute match minute, possession and live/dead flags from the prediction features because equivalent information is unavailable or label-derived in the competition input.

### Measurements and time context

Use a small fixed set: nearest three player distances for each team; difference between nearest home/away distances; ball speed and change in speed; signed distance to pitch boundaries; observed player counts; ball-observed flag; time since/until a ball observation; and validity flags for each measurement. Missing values remain NaN with explicit masks, not zero distances.

For these measurements add past/future values and summaries over fixed 1-second and 3-second contexts. Use seconds converted to 25-Hz frames. Compute within each half only. At edges use available context plus a context-length mask; never wrap across halftime. Keep every source frame for prediction and external evaluation even if training samples are thinned.

No Smart Tagging input in the first learned model: the external dataset does not offer the equivalent supplied automatic tags. Using an external possession label as a fake tag feature would leak the answer and create an unrealistic evaluation. The existing fallback retains its original tag handling. Do not add an unvalidated late fusion of tags and ML predictions.

### Training and sequence decoding

Starting implementation: `learning_rate=0.1`, `max_iter=100`, `max_leaf_nodes=15`, `min_samples_leaf=20`, `l2_regularization=1`, `early_stopping=False`, `random_state=2026`. These are limited engineering defaults, not claimed optimal. Use the already available scikit-learn 1.6.1, then pin the tested dependency set including scipy/joblib/threadpoolctl.

For speed, compute context at full resolution, then train using every fifth labelled frame from training halves. Do not downsample validation predictions or move annotated transitions. Train one model initially; do not launch an AutoML search.

Address the clean-external-versus-noisy-competition mismatch using a deterministic extra copy of training features derived after hiding external ball observations in random 0.2-3-second bursts, covering approximately 30% of each half. Select burst locations from a fixed seed without consulting labels or competition outputs. Recompute all dependent features after masking, so future windows cannot retain supposedly hidden observations. Keep original external labels as targets. Include home/away-swapped training examples to reduce arbitrary team-side bias.

For each frame the model supplies P(H), P(A), P(D). Decode the best whole-half sequence using Viterbi-style dynamic programming on:

`sum(log(frame probability)) + lambda * sum(log(transition probability))`.

Estimate the 3x3 transition table from consecutive valid training labels only, with add-one smoothing; never count across missing labels or half boundaries. This is a sequence score using classifier probabilities, not a claim of an exact generative likelihood. Test only lambda in `[0, 0.25, 1, 2]` on external validation. Lambda 0 is the unsmoothed learned prediction and guards against assuming more smoothing is always better.

The backtracking step uses later evidence to decide earlier ambiguous frames. A deflection followed by home control can remain H; an established away sequence can support a turnover at the actual control transition. There is no fixed minimum possession duration, and D must remain able to separate H-D-H. Entirely unobservable halves can return X; otherwise initially predict H/A/D on graded frames. Do not add an uncalibrated confidence threshold that creates excessive X.

Runtime estimate must be measured, not promised. Cache features once; repeated fitting should not reparse raw XML. Cap model-fitting/validation work within the assigned time; if the first small run cannot complete on the available CPU, use the fallback.

## How to compare models legally and use both metrics

Adapt the official `evaluation/possession_metrics.py` to external arrays via a thin wrapper, without editing the metric definitions. It accepts arrays of equal length; external evaluation does not need 199,319 rows. Process each external half separately, so no transition crosses a half boundary. Unknown external ground truth is X and creates an unscored gap.

Compute spellF1 and macroF1 for each validation match and average matches equally. Also report H/A/D per-class F1, missed/extra transitions and very short possessions. Re-run on one fixed, externally masked validation copy to reveal sensitivity to missing ball observations. Keep the mask seed and recipe fixed; never inspect the competition output to decide how to perturb external data.

Reference comparator: the organiser's nearest-player baseline with its documented +/-50-frame window, run on the same external features. Do not assume its competition score applies to these games. Add this MIT source to the package only if used, retaining attribution.

Predeclare the adoption gate: a deployable ML candidate must beat that external baseline on match-mean spellF1 and be no worse on match-mean macroF1, on both clean and masked validation. Choose among qualifying lambdas by higher masked spellF1, then masked macroF1, then lower lambda. This is a conservative team decision, not a competition requirement or a statistical guarantee. If none qualifies, retain the frozen fallback. This comparison does not prove superiority over the earlier tag-assisted fallback, whose inputs are different.

After choosing on validation, score the held-out external match once and report it honestly. Do not use its score to choose another variant. If the holdout exposes a software defect, repair it with an independent regression test and record that the holdout was consulted; do not claim it remained untouched. Freeze the selected model/configuration before running final competition inference.

The public five-minute score is not part of this decision. The private baseline spellF1 of 0.2433 is a published benchmark, not a threshold for your scores on unrelated external matches.

## Work allocation: 28 core person-hours, up to 40 available

Use the following ownership as the default. Each person has seven hours of necessary work and up to three optional hours. Everyone's 30-minute kickoff/interface review is included, and may be asynchronous. A fourth member provides an independent verification/release workstream rather than expanding model scope.

| Owner | Location | Seven-hour core allocation | Handoff |
|---|---|---|---|
| Pranav | Brisbane | 0.5 h interface review; 1 h fallback/source package; 2 h competition adapter; 1.5 h adapter/inference integration tests; 1 h repository preparation; 1 h integration handoffs and defect fixes | Working tactical inference, fallback hash, tested commands and prepared repository |
| Jilla | Sydney | 0.5 h interface review; 1 h licence/manifest/download gate; 3 h external adapter and shared feature extraction; 1.5 h label/units/split checks; 1 h data handoff and fixes | External feature caches, schema, retrieval manifest and verified labels |
| Ashwin | USA | 0.5 h interface review; 1.5 h classifier and decoder against fixtures; 2 h training and masking; 1.5 h external validation and adoption gate; 1 h holdout report; 0.5 h frozen-artifact handoff | Frozen model/configuration, hashes, validation decision and method notes |
| Sriva | USA | 0.5 h interface review; 1 h external metric wrapper and regression checks; 2 h isolated installation/reproduction and artifact QA; 1.5 h technical document/licence review; 1.5 h final repository review, publishing and form submission; 0.5 h release handoff | Independent checks, final document, public URL and submission confirmation |

Totals: 7 h each, 28 h core. Suggested local split is 4 h Saturday plus 3 h Sunday for Pranav, Jilla and Ashwin; Sriva can use 3 h Saturday plus 4 h Sunday to protect the release block. Downloads and unattended jobs add elapsed time; start them early. Do not assume all 28 hours are concurrent or that everyone will be available for a call.

Optional extra three hours per person, only if available:

- Pranav: integration defects, additional reproduction and release backup.
- Jilla: external label/coordinate QA and adapter hardening.
- Ashwin: runtime problems and the already planned missing-observation validation, not a larger parameter search.
- Sriva: a second independent reproduction, document review and submission-access problems.

### Working agreement and file ownership

- Pranav owns the tactical adapter, current fallback and inference entry point; Jilla owns the external reader and shared feature schema/extractor; Ashwin owns fitting, saved models and sequence decoding; Sriva owns evaluation wrappers, release checks and final technical document. Pranav can create the initial package skeleton, then hand document ownership to Sriva.
- Agree on one feature schema before coding. Jilla publishes a tiny invented fixture immediately; Ashwin and Sriva can develop against it while downloads/parsing run. Pranav maps tactical inputs into that same schema.
- Use separate branches or agreed file ownership, then small reviewed commits. Do not have multiple people edit the shared feature extractor independently. Keep HANDOFF.md current at the end of each work block.
- Share source, external retrieval commands, dependency pins, approved external artifacts and hashes. Competition data and data-derived caches stay on authorised local machines; team members needing assets obtain them through the organisers' permitted access process. No competition material goes into hosted AI prompts or public Git.
- Sriva needs an authorised local participant-data copy, a working Python environment, repository write access and the submission-form access early. Check those during his first work block. If he cannot access the participant data in time, choose and generate the final candidate while Pranav is still online on Sunday; US-side model changes after that point are not deployable unless an authorised runner can regenerate and verify them.
- Pranav supplies the registered team name and form URL before going offline. Sriva is the designated final submitter; the others review the same response rather than creating additional responses. If form ownership requires Pranav, arrange an explicit available upload window before the weekend ends; do not assume Monday availability.

### Australia-USA handoff schedule

Ashwin's and Sriva's US timezones are not yet specified. The Eastern/Pacific columns below are examples, not an assumption about where either person lives. Times were checked using timezone data for these dates. Use the UTC timestamp as the shared reference and shift optional calls to actual availability.

| Checkpoint | UTC | Brisbane | Sydney | US Eastern example | US Pacific example |
|---|---|---|---|---|---|
| First proposed cross-region checkpoint | Sat 14 Nov 22:00 | Sun 15 Nov 08:00 | Sun 15 Nov 09:00 | Sat 14 Nov 17:00 | Sat 14 Nov 14:00 |
| Final model/integration handoff cutoff | Sun 15 Nov 22:00 | Mon 16 Nov 08:00 | Mon 16 Nov 09:00 | Sun 15 Nov 17:00 | Sun 15 Nov 14:00 |
| Target submission completed | Mon 16 Nov 02:00 | Mon 16 Nov 12:00 | Mon 16 Nov 13:00 | Sun 15 Nov 21:00 | Sun 15 Nov 18:00 |

The Monday Australian checkpoint is an asynchronous status deadline, not a required Monday meeting. Pranav and Jilla finish their core work by their Sunday evening. Sriva runs the final release from the USA weekend. The final block is three to four hours of his seven-hour budget, not additional unbudgeted work.

### Day 1 in each person's local weekend

- Start the interface/rules review as soon as each person begins. Pranav and Jilla can agree in their daytime; Ashwin and Sriva review the recorded contract when their work block starts.
- Pranav confirms the fallback and begins the tactical adapter. Jilla publishes the fixture/schema, passes the data-access gate and builds external features.
- Ashwin develops model/decoder code against the fixture, then trains once actual external features arrive. Sriva builds the external metric wrapper and prepares a clean environment and submission-access checks.
- By the first proposed checkpoint, record the data gate result, source commits, completed tests and remaining dependencies. The fallback must be available even if ML has not completed. If a participant cannot attend, the written handoff is sufficient.

### Day 2 in each person's local weekend

- Australia Sunday: Pranav completes tactical integration, verifies the fallback, prepares the new public-repository contents and leaves tested commands before going offline. Jilla completes data QA, caches and provenance, then records any unresolved issues. They use their remaining weekend hours rather than waiting for a Monday call.
- USA Sunday: Ashwin finishes the limited validation trials, applies the adoption gate and delivers the frozen artifact and report to Sriva. Sriva independently installs and reproduces the chosen candidate using the prepared entry point and authorised local assets.
- **ML freeze cutoff:** at Sun 15 Nov 22:00 UTC, a deployable ML candidate must have a checkpoint, feature/configuration hashes, external validation report and passing integration checks. Otherwise Sriva uses the already verified fallback. If adoption is technically ready, score the final external holdout once for reporting without retuning. Any late software defect that prevents reliable reproduction triggers the fallback.
- Protect Sriva's final three hours for the chosen-method document, exact CSV/hash validation, repository audit/publication and form submission. Ashwin supports artifact defects while still within his budget. Pranav is a backup only if he explicitly has remaining availability.
- Target submission by Mon 16 Nov 02:00 UTC. Later on November 16 is contingency if someone is available; November 17 remains the documented deadline, whose exact time/timezone must be confirmed. Do not assume an additional weekday work session in the core plan.

## Portable repository contract

Current files in this folder run the frozen fallback. If ML passes the gate, extend it with `training/` for external adapters and fitting, `models/` for the frozen estimator plus transition table, and `configs/ml.json`. Preserve one unambiguous final reproduction command; do not require retraining to reproduce a submission.

Recommended final layout:

```text
submission_package/                 -> contents become new repository root
  README.md                        installation and one final prediction command
  TEAM.md                          rename to registered team name for upload
  LICENSE, CITATION.cff             retained notices for reused code
  THIRD_PARTY_NOTICES.md            add if external data/ML is used
  requirements-submission.txt       exact tested inference dependencies
  requirements-training.txt        exact training dependencies, if ML is used
  games.py                         supplied public match/frame metadata
  possession/                      inference; never imports training labels
  configs/                         frozen chosen settings
  models/                          ML artifact and model manifest, if selected
  training/                        external download/features/fit commands
  evaluation/                      official metrics and format validator
  tests/                           invented fixtures and invariants
  .gitignore                       keep when copying
  artifacts/                       LOCAL ONLY, ignored outputs and diagnostics
  external_data/                   LOCAL ONLY, ignored downloaded data/cache
```

Provide data using `--data-dir`; use no absolute developer paths in code and no imports from the parent workspace. Separate training and inference requirements so organisers can regenerate the CSV without downloading external training matches. Training retrieval should remain reproducible and documented for audit.

The public repository must include any selected model weights and a manifest with model hash, data version/split, feature schema, random seeds, package versions and training command. Record the inference code commit, configuration hash, competition input hashes and final CSV hash locally. Do not accidentally place competition-derived arrays in the model artifact.

## Required checks and submission steps

1. Unit tests: frame 1 -> row 0; coordinate units; home/away mapping; same-team slot permutation invariance; missing values; unknown external label exclusion; duplicate/out-of-order frame rejection; halftime reset; no labels available to the feature function; checkpoint save/load predictions unchanged.
2. Temporal tests on invented or labelled external sequences: same-team pass, deflection, genuine turnover, short real possession, D between two possessions of the same team, missing ball and restart. Fix demonstrated code defects; do not tune using competition output observations.
3. Output contract: exact `frame,label`; 199,319 rows; frames 0..199318; H/A/D/X only. Use X outside the published graded ranges and preserve second-half pre-kickoff D from public metadata. Do not use historical corrected-tracking offsets on participant ATD.
4. Run the included official validator on the exact upload file. It checks format, not accuracy. Do not follow its inherited suggestion to score public GT for model choice.
5. Create a genuinely isolated environment without `--system-site-packages`, preferably on a teammate's machine. Copy only the package source and selected model; point at the local participant data path. Install pinned dependencies, run tests, regenerate the CSV and compare SHA-256 hashes. Do not reuse leftover pyc files, old predictions or parent imports.
6. Create the public submission repository from this folder's reviewed contents, not the parent repository history. Include `.gitignore`. Review `git status --ignored`, `git ls-files`, and all new-repository commits. Exclude match assets, input-derived feature caches, email PDF, tokens, venv, logs and generated CSVs from public commits. Keep required model weights available.
7. Check the public URL without relying on a logged-in collaborator session. Verify required model artifacts are downloadable.
8. Rewrite the technical document around the final chosen method, assets, external labels/rights if any, control/stoppage interpretation, missingness, validation, limitations and reproduction. Do not describe a dropped ML experiment as the submitted method. The existing TEAM.md is only the fallback document.
9. Obtain the registered team name and emailed Google Form URL. Verify the exact deadline time/timezone, Google-account upload access and signed registration terms. Name outputs after the registered team; Markdown is allowed for the technical document.
10. Submit the CSV, public repository URL and technical document through one team response. Save confirmation, code commit and output hash; check that attachments are the exact validated versions. The form permits edits before the deadline; avoid multiple independent team responses.

## Explicit exclusions and uncertainty

This sprint does not deliver arbitrary-video inference, broadcast replay alignment, model training on the Barcelona match, a guaranteed competition score, or a legal certification. Passing the format validator and artificial tests is necessary but not proof of possession accuracy. Clean external tracking is easier than the supplied automatic data; masked external evaluation helps detect fragility but cannot remove that domain difference.

Source research alternatives: SkillCorner has possession-related open tracking but uses different temporal sampling and annotation semantics; SoccerTrack v2 is CC BY 4.0 but gated and its ball track is event-derived; SoccerNet videos have research/access restrictions; Metrica sample-data rights wording is less explicit. PathCRF provides an interesting trained sequence approach but integrating its player-identity assumptions, dependencies and licence/weight provenance is a poor two-day risk. See DATA_SOURCES.md. None is an automatic substitute for the verified primary data route.
