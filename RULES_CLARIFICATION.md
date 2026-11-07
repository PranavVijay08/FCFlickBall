# Initial Challenge: organisers' rules clarification

Recorded on November 7, 2026 from the organisers' email supplied by the team. The email's send date was not supplied. Keep the original email as the authoritative record.

**This clarification takes precedence over conflicting repository documentation, earlier emails, and individual answers.** The original competition documents remain in this fork for reference; follow this clarification wherever they conflict.

## Email text

> There has been some confusion about what is and what is not permitted in the Initial Challenge, so we are sending this clarification to all of you.
>
> Please note that the rules below take precedence over any other information you may have received previously, whether in the documentation, in earlier emails or in answers to individual questions.
>
> **What is not allowed**
> - Checking your output against the video.
> - Hand labels, human-produced data or any other data created manually on the provided game.
> - Uploading the provided data to AI services.
> - Training, fitting or calibrating your algorithm on the ground-truth possession data or on the provided video.
>
> **What is allowed**
> - Running automatic checks using only the provided data.
> - Inspecting the provided data and the video to better understand what counts as possession.
> - Using as input the video, the automatic tracking data, the smart tagging or any other generated data, as long as your algorithm was not trained on the ground truth or on the provided video.
> - Providing files of intermediate steps.
> - Using any dataset you have the rights to use. Please check the license of any dataset before using it.
>
> **Training and tuning**
> If you need to train (or retrain), you MUST use only external data. If your algorithm has parameters that need to be tuned, you MUST tune them on external data, never on the ground-truth possession data or on the provided video.

## Working interpretation for this solution

- Run the fixed algorithm locally on the provided automatic tracking and tags. Automatic format, frame-order, missing-value, and reproducibility checks remain useful.
- Inspect the provided video only to understand the meaning of possession. Do not compare predictions, logged transitions, overlays, or scores against the video, even without manually editing a CSV.
- Do not train, retrain, fit, calibrate, optimise thresholds, or choose model versions using this match. The external-data-only requirement also rules out the previously suggested training on this game's automatic pseudo-labels or self-supervised training on the provided assets.
- Fixed initial rule settings are distinguished from tuning. The current settings are untrained engineering assumptions, not externally validated or optimal values. See `PARAMETER_PROVENANCE.md`.
- Any future parameter search or learned model must use licensed external data, with external validation matches. Record the dataset rights and the exact process.
- Do not send the supplied assets or extracts to AI services. This applies to data-bearing prompts, screenshots, clips, tool outputs, and uploads.
- Intermediate outputs can be provided as permitted by the clarification. Use the organisers' authorised submission channel; this permission does not by itself grant unrestricted public redistribution of the licensed match data.
- Keep the format validator separate from possession scoring. Do not use the public five-minute score for tuning or model selection. Our conservative workflow is to stop further possession-score comparisons on this match unless organisers confirm their diagnostic use under the clarification.

## Existing work

The prediction pipeline has no training step and does not read the provided video or ground-truth labels. Its thresholds were fixed before scoring the candidate on the public five-minute labels. That historical check is recorded, not removed; it did not cause parameter changes. Video metadata was checked automatically, but predictions were not compared against video.

The program and configuration are not changed by this clarification update. Documentation that previously suggested video-based output checks or training on this game's pseudo-labels is superseded. This record explains the development process; it is not an organiser's certification of the entry.
