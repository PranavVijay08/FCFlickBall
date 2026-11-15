"""Read participant observations locally, with no labels or video access."""
from pathlib import Path
import numpy as np
from possession.features import read_team_slots
from possession.ml_features import Observations
from games import GAME, asset_paths, half_video_blocks, source_frames


def load_halves(data_dir):
    paths = asset_paths(data_dir=str(data_dir))
    slots = read_team_slots(paths["atd_meta"])
    n = source_frames()
    ball = np.full((n, 2), np.nan, np.float32)
    players = np.full((n, len(slots), 2), np.nan, np.float32)
    pitch = (105.3, 68.)
    count = 0
    with Path(paths["atd_raw"]).open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            count += 1
            fields = line.rstrip().split(":")
            if i >= n or len(fields) != 3 or int(fields[0]) != i+1:
                raise ValueError("Invalid tactical record order/format")
            groups = fields[1].split(";")
            if len(groups) != len(slots):
                raise ValueError("Tactical slot count mismatch")
            ball[i] = [float(v) for v in fields[2].split(",")[:2]]
            for j, group in enumerate(groups):
                players[i, j] = [float(v) for v in group.split(",")[:2]]
    if count != n:
        raise ValueError("Incorrect tactical frame count")
    ball *= pitch
    players *= pitch
    halves = []
    for half, first, last in half_video_blocks(GAME):
        section = slice(first, last+1)
        obs = Observations(np.arange(first, last+1), ball[section],
                           players[section][:, slots == 0], players[section][:, slots == 1], pitch)
        obs.validate()
        halves.append((half, obs))
    return halves
