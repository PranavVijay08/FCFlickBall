"""One final reproduction command, controlled by the reviewed frozen selection file."""
import argparse
import json
from pathlib import Path
from possession.cli import ROOT, _digest


def run(data_dir, output):
    selection = json.loads((ROOT / "configs" / "selected.json").read_text(encoding="utf-8"))
    if selection["method"] == "ml":
        model = ROOT / selection["model"]
        if _digest(model) != selection["model_sha256"]:
            raise ValueError("Frozen model hash mismatch")
        from possession.ml_cli import run as predict
        predict(data_dir, model, output)
    elif selection["method"] == "fallback":
        config = ROOT / "configs" / "default.json"
        if _digest(config) != selection["config_sha256"]:
            raise ValueError("Frozen fallback configuration hash mismatch")
        from possession.cli import run as predict
        predict(data_dir, config, output)
    else:
        raise ValueError("Unknown final method")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", required=True)
    p.add_argument("--output", default=str(ROOT / "artifacts" / "TEAM.csv"))
    args = p.parse_args()
    run(args.data_dir, args.output)
