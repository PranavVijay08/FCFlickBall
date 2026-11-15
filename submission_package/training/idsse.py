"""Streaming external DFL XML adapter; labels are kept outside observation objects."""
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from possession.ml_features import Observations
from training.download_idsse import SPLITS


def load_match(folder, match):
    folder = Path(folder)
    meta = next(folder.glob("*matchinformation*" + match + ".xml"))
    raw = next(folder.glob("*positions_raw*" + match + ".xml"))
    r = ET.parse(meta).getroot()
    general, environment = r.find(".//General"), r.find(".//Environment")
    teams = [general.get("HomeTeamId"), general.get("GuestTeamId")]
    pitch = (float(environment.get("PitchX")), float(environment.get("PitchY")))
    records = {}
    current, rows = None, None
    root = None
    for event, element in ET.iterparse(raw, events=("start", "end")):
        if root is None:
            root = element
        if event == "start" and element.tag == "FrameSet":
            current = dict(element.attrib)
            rows = []
        elif event == "end" and element.tag == "Frame" and current is not None:
            team = current["TeamId"]
            if team in teams or team.lower() == "ball":
                a = element.attrib
                rows.append((int(a["N"]), float(a["X"]), float(a["Y"]),
                             float(a.get("BallStatus", "nan")), float(a.get("BallPossession", "nan"))))
            element.clear()
        elif event == "end" and element.tag == "FrameSet":
            team = current["TeamId"]
            if rows:
                half = current["GameSection"]
                records.setdefault(half, []).append((team, current.get("PersonId"), np.asarray(rows)))
            current, rows = None, None
            element.clear()
            root.clear()
    result = []
    for half in ("firstHalf", "secondHalf"):
        items = records[half]
        balls = [a for team, _, a in items if team.lower() == "ball"]
        if len(balls) != 1:
            raise ValueError("Expected one ball series per half")
        ball = balls[0]
        frames = ball[:, 0].astype(np.int64)
        if not np.all(np.diff(frames) == 1):
            raise ValueError("External ball frames must be consecutive")
        team_arrays = []
        for team in teams:
            tracks = [a for tid, _, a in items if tid == team]
            values = np.full((len(frames), len(tracks), 2), np.nan, np.float32)
            for j, track in enumerate(tracks):
                indices = track[:, 0].astype(np.int64) - frames[0]
                if len(np.unique(indices)) != len(indices) or np.any(np.diff(indices) <= 0):
                    raise ValueError("Duplicate or unordered external player frames")
                if np.any(indices < 0) or np.any(indices >= len(frames)):
                    raise ValueError("Player series outside external half")
                values[indices, j] = track[:, 1:3] + np.array(pitch)/2
            team_arrays.append(values)
        labels = np.full(len(frames), 3, np.int8)
        status, owner = ball[:, 3], ball[:, 4]
        labels[status == 0] = 2
        labels[(status == 1) & (owner == 1)] = 0
        labels[(status == 1) & (owner == 2)] = 1
        obs = Observations(frames, (ball[:, 1:3] + np.array(pitch)/2).astype(np.float32),
                           *team_arrays, pitch)
        obs.validate()
        result.append((half, obs, labels))
    return result


def save_half(path, obs, labels):
    np.savez_compressed(path, frames=obs.frames, ball=obs.ball, home=obs.home, away=obs.away,
                        pitch=obs.pitch, labels=labels)


def read_half(path):
    with np.load(path, allow_pickle=False) as data:
        obs = Observations(data["frames"], data["ball"], data["home"], data["away"], tuple(data["pitch"]))
        labels = data["labels"]
    obs.validate()
    return obs, labels


def prepare(folder, dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    summary = []
    for split, matches in SPLITS.items():
        for match in matches:
            paths = [dest / (match + "_" + half + ".npz") for half in ("firstHalf", "secondHalf")]
            if not all(p.exists() for p in paths):
                print("Parsing external", match, flush=True)
                for (half, obs, labels), path in zip(load_match(folder, match), paths):
                    save_half(path, obs, labels)
            for path in paths:
                obs, labels = read_half(path)
                row = {"match": match, "split": split, "half": path.stem.split("_")[1],
                       "frames": len(labels), "label_counts": np.bincount(labels, minlength=4).tolist(),
                       "ball_observed_fraction": float(np.isfinite(obs.ball).all(axis=1).mean())}
                summary.append(row)
                print(json.dumps(row), flush=True)
    (dest / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="external_data/idsse")
    parser.add_argument("--dest", default="external_data/prepared")
    args = parser.parse_args()
    prepare(args.source, args.dest)
