# Packaging audit - 14 November 2026

This is a packaging and software-integrity record, not a claim of competitive accuracy or organiser approval.

## Completed ML implementation (subsequent to the initial packaging below)

- Downloaded all seven external IDSSE version-1 tracking XMLs and metadata with explicit network approval; all provider MD5 checksums matched. Prepared all 14 halves with native external H/A/D targets.
- Implemented the shared 105-feature observation schema, external adapter, CPU classifier, fixed masking/team-swap augmentation, external evaluation, frozen whole-half decoding and strict tactical adapter.
- Trained on four external matches and selected decoder strength 2 using only two validation matches under the predeclared clean/masked adoption gate. Evaluated the reserved external match once after selection; made no subsequent model changes.
- External aggregate results and comparator scores are in reports/. They are not competition scores. The ML method passed the external adoption gate; superiority over the earlier tag-assisted fallback is not established.
- All 17 tests passed in the original environment and a new Python 3.11.9 environment with system-site-packages disabled. Initial sandbox execution blocked a Windows worker pipe; the approved unsandboxed test/training runs passed. The clean environment's pip check passed.
- The selected frozen model is bundled with hash `493eed8a1d3287fea0b3d58468a39b9ed9acc75ceaa4af563dbd407a9408c8ae`. It is approximately 302 KB. Source provenance and exact training package versions are in models/manifest.json.
- Local competition inference and a second run in the isolated environment generated identical CSV bytes: SHA-256 `abda45972282c7d39a2e73d46ad4764c263b098701389e83ec0656d5c89e92c3`, 199,319 data rows, accepted by the official format-validation API.
- The original fallback code/configuration remains available and its previous output hash is recorded below. TEAM.md and README.md now describe the selected ML solution.
- No competition possession scoring, video-based output checks, manual prediction edits, target-match training or uploads of participant assets to AI services were performed for this ML implementation.
- Remaining external actions belong to the user: review/commit, public repository creation/publication, registered naming, terms/form/deadline checks and upload. No commits, pushes or messages to organisers were made by the agent.
- Reproduction checks are on one computer using separate environments; this is not a claim of independent second-computer verification or legal certification.
- A source-only ZIP was built using the tracked/unignored package file list, extracted into a separate ignored folder, and run with the isolated environment and an explicit participant-data path. Its CSV was byte-identical, confirming no dependency on parent-workspace source. The ZIP includes the frozen model and excludes participant inputs, outputs, caches and environments. It is a local review artifact, not a published repository.

## Initial fallback packaging audit (historical)

- Source provenance: `feature/AI_attempt`, commit `7c35045dce2838a79133a38abc75acb285289290`.
- Destination: `submission_package/` in `feature/ML_algo_solution`; original source branch unchanged.
- Prediction source/configuration copied without logic or setting changes. Windows checkout line endings differ from Git blob line endings; a normalised source comparison found no Python changes. Documentation amended to identify package status, the email date and correct local reproduction references.
- Ten artificial unittest cases passed in a temporary source export and in the package.
- Package inference generated 199,319 labels and passed the official format validator.
- The package output SHA-256 equals the earlier candidate CSV and temporary source export output:
  `9db578ab1f2d275f3f4bfca183082d2dfc8fe3e4d1c728016b9cad96d0bce909`.
- No competition ground-truth scoring, video-based output checking, model fitting or threshold changes were performed in this audit.
- Used current Python 3.11.9 with numpy 2.2.5 and pandas 2.2.3. A newly installed isolated environment and second-computer reproduction remain final-team checks.
- Generated predictions, manifests, PDF review images and caches are under ignored paths. The public package contains source, configuration, tests and documentation, not participant assets.
- No external dataset was downloaded in full or used for training. The IDSSE official metadata catalogue was read to verify licensing, file IDs, sizes and published checksums; label definitions were checked against the paper and reference parser.
- Nothing has been committed, pushed or submitted by this packaging step. Registered team name, final technical-document filename, submission form access and exact deadline time/timezone still require team completion.

## Four-member schedule revision

The plan now allocates seven core hours each to Pranav (Brisbane), Jilla (Sydney), Ashwin (USA) and Sriva (USA): 28 hours total, up to 40 if everyone has additional availability. It adds a written handoff template, example timezone conversions and Sriva as the proposed final verifier/submitter during the USA weekend. Monday work from Australia is not assumed. These are documentation and coordination changes; prediction code, parameters, model status and the previously verified output are unchanged.
