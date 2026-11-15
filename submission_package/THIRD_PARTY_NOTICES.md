# Sources and third-party notices

## Organiser source

The baseline possession pipeline, public match metadata, tag loader and official metrics/validator reuse source from Metrica Sports' More than a Hack 2027 repository under its MIT licence. Retain `LICENSE` and `CITATION.cff`. Competition videos, tracking, tags and homography are separately restricted and are not distributed in this package.

## External training data: IDSSE, version 1

Manuel Bassek, Robert Rein, Hendrik Weber and Daniel Memmert (2025), *An integrated dataset of spatiotemporal and event data in elite soccer*, Scientific Data 12, 195.

- Paper: https://doi.org/10.1038/s41597-025-04505-y
- Dataset: https://doi.org/10.6084/m9.figshare.28196177.v1
- Licence: Creative Commons Attribution 4.0 International, https://creativecommons.org/licenses/by/4.0/
- Original data provider: Deutsche Fussball Liga / Sportec Solutions; publication permission is documented in the authors' paper.

The external raw data are not bundled. `training.download_idsse` retrieves the pinned release, verifies provider MD5 checksums and records SHA-256 hashes. Our transformations translate coordinates, align records by frame, extract team-level time-context features, create deterministic missing-ball augmentations and map native BallPossession/BallStatus fields to H/A/D training labels. The estimator and transition probabilities are fitted only on the declared training matches. Model/decoder selection uses only the separate declared validation matches.

These transformations and the learned model are produced by this project; they are not original provider annotations or an official IDSSE model. See the saved validation/training record for the actual selected method. Raw competition-match data never enter training.

## Libraries

The pinned environment uses numpy, pandas, scikit-learn, scipy, joblib and threadpoolctl. These remain under their respective upstream licences. This repository does not relicense them. Dependencies are installed from their published distributions; no dependency source is bundled.
