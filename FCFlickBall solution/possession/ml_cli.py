"""Frozen, local ML inference. Requires no external dataset, training labels or network."""
import argparse
import csv
import json
import importlib.metadata
import platform
from pathlib import Path
import joblib
import numpy as np
from games import source_frames, asset_paths
from evaluation import possession_metrics as pm
from possession.common import _digest, _git_commit
from possession.ml_features import SCHEMA
from possession.ml_model import predict
from possession.tactical import load_halves


def run(data_dir, model, output):
    bundle = joblib.load(model)  # Trusted local artifact only; joblib files can execute code.
    if not bundle.get("adopt_ml"):
        raise ValueError("This model did not pass the external adoption gate; use the frozen fallback")
    before = _digest(model)
    labels = np.full(source_frames(), "X", dtype="U1")
    for half, obs in load_halves(data_dir):
        if not np.isfinite(obs.ball).any() and not np.isfinite(obs.home).any() and not np.isfinite(obs.away).any():
            continue
        codes = predict(bundle, obs)
        labels[obs.frames] = np.array(["H", "A", "D"])[codes]
        if half == 2:
            labels[obs.frames[obs.frames < 113742]] = "D"  # Published kickoff, not inferred/tuned.
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(("frame", "label"))
        writer.writerows(enumerate(labels))
    reason = pm.validate_submission(pm.read_label_csv(output), source_frames())
    if reason:
        raise ValueError(reason)
    if _digest(model) != before:
        raise RuntimeError("Frozen model was modified during inference")
    manifest = {"method": "external_idsse_hgb_sequence", "schema": SCHEMA,
                "model_sha256": before, "output_sha256": _digest(output), "git_commit": _git_commit(),
                "python": platform.python_version(),
                "packages": {name: importlib.metadata.version(name) for name in
                             ("numpy", "pandas", "scikit-learn", "scipy", "joblib", "threadpoolctl")},
                "input_sha256": {name: _digest(path) for name, path in asset_paths(data_dir=str(data_dir)).items()
                                 if name in ("atd_meta", "atd_raw")},
                "source_sha256": {str(p.relative_to(Path(__file__).resolve().parents[1])): _digest(p)
                                  for p in sorted(Path(__file__).parent.glob("*.py"))}}
    output.with_suffix(".run.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("VALID", len(labels), "frames; SHA-256", manifest["output_sha256"])


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", required=True)
    p.add_argument("--model", default="models/idsse_hgb.joblib")
    p.add_argument("--output", default="artifacts/FCFlickBall.csv")
    args = p.parse_args()
    run(args.data_dir, args.model, args.output)
