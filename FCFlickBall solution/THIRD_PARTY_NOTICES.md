# Sources and third-party notices

## Organiser source

The match metadata helpers and official metric/validation functions originate from Metrica Sports' [More than a Hack 2027 repository](https://github.com/metrica-sports/more-than-a-hack-2027). Their original MIT notice is retained in LICENSE, and CITATION.cff describes that upstream benchmark, not a newly published dataset. No benchmark labels or match assets are bundled here. The licence does not grant rights to redistribute the competition assets.

## External training data and model

Manuel Bassek, Robert Rein, Hendrik Weber and Daniel Memmert (2025), *An integrated dataset of spatiotemporal and event data in elite soccer*, Scientific Data 12, 195.

- Paper: https://doi.org/10.1038/s41597-025-04505-y
- Dataset, pinned version 1: https://doi.org/10.6084/m9.figshare.28196177.v1
- Dataset licence: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
- Original data provider: Deutsche Fussball Liga / Sportec Solutions; the publication describes provider permission.

The external raw data are not bundled. training/idsse_manifest.json records the release, provider file identifiers, checksums and splits. Our transformations align frames, translate coordinates, map provider BallStatus/BallPossession fields to targets, extract features and create missing-ball and team-swap augmentation. The bundled model and transitions were fitted on the declared external training split. Decoder selection used the external validation split. These transformations and model are this project's work, not original provider annotations or an endorsed IDSSE model. Preserve this attribution when distributing the model.

## Dependencies

NumPy, pandas, scikit-learn, SciPy, joblib, threadpoolctl, python-dateutil, pytz and tzdata retain their upstream licences. They are installed from their distributions; their source is not bundled or relicensed here.
