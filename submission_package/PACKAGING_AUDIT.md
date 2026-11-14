# Packaging audit - 14 November 2026

This is a packaging and software-integrity record, not a claim of competitive accuracy or organiser approval.

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
