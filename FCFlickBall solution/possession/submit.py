"""Reproduce the final submission with the frozen external-data model."""
import argparse
import json
from possession.common import ROOT, _digest


def run(data_dir, output):
    selection = json.loads((ROOT / "configs" / "selected.json").read_text(encoding="utf-8"))
    if selection["method"] != "ml":
        raise ValueError("This submission package supports only the frozen ML method")
    model = ROOT / selection["model"]
    if _digest(model) != selection["model_sha256"]:
        raise ValueError("Frozen model hash mismatch")
    from possession.ml_cli import run as predict
    predict(data_dir, model, output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--output", default=str(ROOT / "submission_files" / "FCFlickBall.csv"))
    args = parser.parse_args()
    run(args.data_dir, args.output)
