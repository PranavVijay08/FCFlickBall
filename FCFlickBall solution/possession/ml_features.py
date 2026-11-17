"""Shared observation-only features. This module cannot read training labels."""
from dataclasses import dataclass
import numpy as np

SCHEMA = "team_geometry_context_v1"


@dataclass
class Observations:
    frames: np.ndarray
    ball: np.ndarray
    home: np.ndarray
    away: np.ndarray
    pitch: tuple
    fps: int = 25

    def validate(self):
        n = len(self.frames)
        if n == 0 or not np.all(np.diff(self.frames) == 1):
            raise ValueError("A half must contain nonempty consecutive ordered frames")
        if self.ball.shape != (n, 2):
            raise ValueError("Invalid ball shape")
        for a in (self.home, self.away):
            if a.ndim != 3 or a.shape[0] != n or a.shape[2] != 2:
                raise ValueError("Invalid team positions shape")
        if self.fps != 25 or any(x <= 0 for x in self.pitch):
            raise ValueError("Expected 25 Hz and positive pitch dimensions")


def mask_ball(obs, seed, fraction=0.30):
    """External augmentation only: fixed-seed bursts, independent of labels."""
    rng = np.random.default_rng(seed)
    n = len(obs.frames)
    mask = np.zeros(n, bool)
    while mask.mean() < fraction:
        start = int(rng.integers(n))
        length = int(rng.integers(5, 76))
        mask[start:min(n, start + length)] = True
    ball = obs.ball.copy()
    ball[mask] = np.nan
    return Observations(obs.frames, ball, obs.home, obs.away, obs.pitch, obs.fps)


def swapped(obs):
    return Observations(obs.frames, obs.ball, obs.away, obs.home, obs.pitch, obs.fps)


def _lag(a, offset):
    result = np.full_like(a, np.nan)
    if offset == 0:
        return a.copy()
    if abs(offset) < len(a):
        if offset > 0:
            result[:-offset] = a[offset:]
        else:
            result[-offset:] = a[:offset]
    return result


def _rolling(a, radius):
    finite = np.isfinite(a)
    sums = np.concatenate(([0.0], np.cumsum(np.where(finite, a, 0), dtype=np.float64)))
    counts = np.concatenate(([0], np.cumsum(finite)))
    t = np.arange(len(a))
    lo, hi = np.maximum(0, t-radius), np.minimum(len(a), t+radius+1)
    count = counts[hi] - counts[lo]
    mean = np.full(len(a), np.nan, np.float32)
    np.divide(sums[hi]-sums[lo], count, out=mean, where=count > 0)
    return mean, count / (hi-lo)


def extract(obs):
    obs.validate()
    n = len(obs.frames)
    seen = np.isfinite(obs.ball).all(axis=1)
    cols, names = [], []

    def add(name, a):
        a = np.asarray(a, np.float32).copy()
        a[~np.isfinite(a)] = np.nan
        names.append(name)
        cols.append(a)

    nearest = []
    for team, players in (("home", obs.home), ("away", obs.away)):
        valid = np.isfinite(players).all(axis=2)
        distances = np.linalg.norm(players - obs.ball[:, None, :], axis=2)
        distances[~np.isfinite(distances)] = np.inf
        distances = np.sort(distances, axis=1)
        for k in range(3):
            add(team + "_distance_" + str(k+1), distances[:, k] if k < distances.shape[1]
                else np.full(n, np.nan))
        nearest.append(cols[-3])
        add(team + "_players_observed", valid.sum(axis=1))
    add("nearest_difference", nearest[0] - nearest[1])
    add("ball_observed", seen)
    speed = np.full(n, np.nan)
    speed[1:] = np.linalg.norm(np.diff(obs.ball, axis=0), axis=1) * obs.fps
    add("ball_speed", speed)
    add("ball_speed_change", np.concatenate(([np.nan], np.diff(speed))) * obs.fps)
    length, width = obs.pitch
    add("ball_x_fraction", obs.ball[:, 0] / length)
    add("ball_y_fraction", obs.ball[:, 1] / width)
    add("boundary_distance", np.min(np.column_stack((obs.ball[:, 0], length-obs.ball[:, 0],
                                                     obs.ball[:, 1], width-obs.ball[:, 1])), axis=1))
    t = np.arange(n)
    previous = np.maximum.accumulate(np.where(seen, t, -n))
    following = np.minimum.accumulate(np.where(seen, t, 2*n)[::-1])[::-1]
    add("since_ball_seconds", np.minimum((t-previous)/obs.fps, 30))
    add("until_ball_seconds", np.minimum((following-t)/obs.fps, 30))
    base_names, base = list(names), np.column_stack(cols)
    result = [base]
    for offset in (-75, -25, 25, 75):
        result.append(_lag(base, offset))
        names.extend([name + "_offset_" + str(offset) for name in base_names])
    for name in ("home_distance_1", "away_distance_1", "nearest_difference", "ball_speed", "ball_observed"):
        for radius in (25, 75):
            mean, coverage = _rolling(base[:, base_names.index(name)], radius)
            result.extend((mean[:, None], coverage[:, None]))
            names.extend((name + "_mean_" + str(radius), name + "_coverage_" + str(radius)))
    return np.concatenate(result, axis=1).astype(np.float32), names
