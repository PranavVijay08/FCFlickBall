# External training source research - 14 November 2026

These findings are recommendations, not claims that every source has been downloaded or used. No external training data has been used by the packaged fallback.

| Source | Evidence and rights | Fit for this sprint |
|---|---|---|
| [IDSSE / Sportec-DFL](https://springernature.figshare.com/articles/dataset/An_integrated_dataset_of_spatiotemporal_and_event_data_in_elite_soccer/28196177) | Official seven-match release, CC BY 4.0, with DFL permission documented in the [paper](https://www.nature.com/articles/s41597-025-04505-y). Frame-level BallPossession and BallStatus are documented. | Primary choice: continuous tracking and labels; no video decoding or manual full-match labelling needed. Provider semantics and data quality still require checks. |
| [SkillCorner Open Data](https://github.com/SkillCorner/opendata) | Repository MIT notice, explicit open-data release and attribution request. README describes 10-Hz tracking possession fields and in-play phases. | Legitimate candidate for later robustness work; a second provider adapter and semantic checks cost time. Do not make this a second simultaneous training project. |
| [SoccerTrack v2](https://huggingface.co/datasets/atomscott/soccertrack-v2) | CC BY 4.0 dataset licence; gated access acceptance. Current card distinguishes event-anchored, linearly interpolated ball tracks from measurements. | Not the first source for this sprint. Raw video is large; existing event labels do not directly supply this challenge's continuous H/A/D truth. Event-derived ball tracks may leak annotation timing into evaluation. |
| [SoccerNet](https://www.soccer-net.org/data) | [FAQ](https://www.soccer-net.org/faq) invites model training for research but restricts commercial use; video access may require an NDA. | Valuable future video work; access, rights and missing continuous possession labels are extra dependencies now. SoccerNet challenge rules are not automatically rules of this Barcelona hackathon. |
| [Metrica sample data](https://github.com/metrica-sports/sample-data) | Synchronized tracking/events; README requests responsible use and acknowledgement but does not give the same explicit dataset licence as IDSSE. | Do not resolve ambiguous rights under deadline when an explicit licensed alternative exists. |
| [PathCRF](https://github.com/hyunsungkim-ds/pathcrf) | Author repository describes pretrained checkpoints, possession-path modelling and external Sportec data. Repository code licence is MPL 2.0; verify coverage/provenance of weights and dependencies before reuse. | Interesting research, not a plug-in H/A/D model for anonymous, fragmented participant track slots. Leave out of the two-day critical path. |

## Verified IDSSE version-1 file manifest

The official Figshare API catalogue was read on 14 November 2026. File sizes below are raw XML bytes, not video sizes. Download URLs have form `https://ndownloader.figshare.com/files/<id>`.

| Match | Split | Positions file ID | Bytes | Catalogue MD5 | Metadata file ID |
|---|---|---:|---:|---|---:|
| J03WMX | train | 51643514 | 418524833 | e4273a2adf5dbd9d4ec42def2f01905c | 51643475 |
| J03WN1 | train | 51643517 | 391722803 | bacb2f609c1d1b0bfc906f6b9d4109f2 | 51643472 |
| J03WOH | train | 51643520 | 348945715 | 3efff25a86a61768e7d253b4bba137a3 | 51643478 |
| J03WOY | train | 51643523 | 362567859 | 4e1063e0a0ae499920cf68ac1aa3ab4e | 51643481 |
| J03WPY | validation | 51643526 | 371688499 | e56ff1336a334f8da51110fbe7cab764 | 51643487 |
| J03WQQ | validation | 51643529 | 356219423 | 9105bad987191d3c3c362c1fce9a4fcd | 51643484 |
| J03WR9 | held-out report | 51643532 | 372934140 | e060bb7d7a5a3bfbd15bbf9bc631024d | 51643490 |

Use the full version-pinned catalogue for exact filenames and metadata checksums. This manifest intentionally uses the official catalogue, not conflicting match-ID examples in a mirror. The complete raw data were not downloaded during the planning audit.

Attribution to retain if used: Manuel Bassek, Robert Rein, Hendrik Weber and Daniel Memmert (2025), *An integrated dataset of spatiotemporal and event data in elite soccer*, Scientific Data 12, 195. Dataset DOI: https://doi.org/10.6084/m9.figshare.28196177. Licence: https://creativecommons.org/licenses/by/4.0/. Identify your transformations and derived features separately from the original dataset.
