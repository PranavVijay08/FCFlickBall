"""Generate one deterministic full-match possession CSV from provided tactical assets."""

import argparse
import csv
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from games import GAME, GAMES, asset_paths, half_video_blocks
from starter.load_smart_tagging import load as load_smart_tagging
from evaluation import possession_metrics as pm
from possession.config import load as load_config
from possession.decoder import decode
from possession.features import add_smart_tags, read_tracking


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "default.json"
DEFAULT_OUTPUT = ROOT / "evaluation" / "results" / "TEAM.csv"
KICKOFFS = {1: 11185, 2: 113742}  # Published in DATA.md / FAQ.md.


def _digest(path):
    hash_value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hash_value.update(chunk)
    return hash_value.hexdigest()


def _video_path(data_dir, override):
    if override:
        path = Path(override)
        if not path.is_file():
            raise FileNotFoundError("configured tactical video does not exist")
        return path
    expected = Path(asset_paths(data_dir=str(data_dir))["video"])
    if expected.is_file():
        return expected
    candidates = sorted(expected.parent.glob(expected.stem + "-*.mp4"))
    return candidates[0] if len(candidates) == 1 else None


def _git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL,
            text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def run(data_dir, config_path, output, tactical_video=None, diagnostics=None):
    data_dir = Path(data_dir).resolve()
    config_path = Path(config_path).resolve()
    output = Path(output).resolve()
    config = load_config(config_path)
    paths = asset_paths(data_dir=str(data_dir))
    required = ("atd_meta", "atd_raw", "smart_tagging")
    missing = [name for name in required if not Path(paths[name]).is_file()]
    if missing:
        raise FileNotFoundError("missing tactical assets: {}".format(", ".join(missing)))
    video = _video_path(data_dir, tactical_video)
    blocks = [(start, last + 1) for _, start, last in half_video_blocks(GAME)]
    named_blocks = [(half, start, last + 1) for half, start, last in half_video_blocks(GAME)]
    n_frames = GAMES[GAME]["n_video_frames"]
    features = read_tracking(paths["atd_raw"], paths["atd_meta"], n_frames, config, blocks)
    events = load_smart_tagging(data_dir=str(data_dir))
    add_smart_tags(features, events, n_frames)
    labels, transitions = decode(features, n_frames, named_blocks, KICKOFFS, config)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("frame", "label"))
        writer.writerows(enumerate(labels))
    table = pm.read_label_csv(output)
    problem = pm.validate_submission(table, n_frames)
    if problem:
        raise ValueError("generated file failed the official format check: " + problem)
    if diagnostics:
        path = Path(diagnostics).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(("frame", "from", "to", "reason"))
            writer.writerows(transitions)
    manifest = {
        "method": "deterministic_tactical_tracking_and_smart_tagging",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "git_commit": _git_commit(),
        "config_sha256": _digest(config_path),
        "source_sha256": {
            str(path.relative_to(ROOT)): _digest(path)
            for path in sorted((ROOT / "possession").glob("*.py")) + [
                ROOT / "games.py",
                ROOT / "starter" / "load_smart_tagging.py",
                ROOT / "evaluation" / "possession_metrics.py",
            ]
        },
        "input_sha256": {name: _digest(paths[name]) for name in required},
        "output_sha256": _digest(output),
        "video_path_resolved": video is not None,
    }
    manifest_path = output.with_suffix(".run.json")
    with manifest_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("VALID {} frames; output SHA-256 {}".format(n_frames, manifest["output_sha256"]))
    print("Local run manifest: {}".format(manifest_path))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(ROOT / "data"))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--tactical-video", help="optional video path override for the delivered filename")
    parser.add_argument("--diagnostics", help="optional local, restricted transition log")
    args = parser.parse_args()
    run(args.data_dir, args.config, args.output, args.tactical_video, args.diagnostics)


if __name__ == "__main__":
    main()
