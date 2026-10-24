"""Read a fixed, reviewable configuration. No values are learned from ground truth."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    pitch_length_m: float
    pitch_width_m: float
    max_interpolation_gap_frames: int
    control_distance_m: float
    control_margin_m: float
    turnover_window_frames: int
    turnover_support_frames: int
    tag_change_frames: int
    outside_margin_m: float
    outside_confirm_frames: int
    stationary_radius_m: float
    stationary_confirm_frames: int
    set_piece_missing_confirm_frames: int
    restart_speed_mps: float
    restart_motion_confirm_frames: int
    live_tag_confirm_frames: int


def load(path):
    with Path(path).open(encoding="utf-8") as handle:
        values = json.load(handle)
    expected = set(Config.__dataclass_fields__)
    if set(values) != expected:
        raise ValueError("configuration keys differ: missing={}, extra={}".format(
            sorted(expected - set(values)), sorted(set(values) - expected)))
    config = Config(**values)
    for name, value in values.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            raise ValueError("{} must be a positive number".format(name))
        if name.endswith("_frames") and (not isinstance(value, int)):
            raise ValueError("{} must be an integer".format(name))
    if config.turnover_support_frames > config.turnover_window_frames:
        raise ValueError("turnover support exceeds window")
    return config
