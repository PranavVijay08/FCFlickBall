"""Read the supplied, automatic tactical assets without loading the video."""

import math
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np


ATTACK_CODES = frozenset((
    "BUILD UP", "PROGRESSION", "CREATING CHANCES", "ATTACKING TRANSITION",
    "LONG BALL", "BALL IN FINAL THIRD", "BALL IN THE BOX", "PLAYERS IN THE BOX",
))
DEFENCE_CODES = frozenset((
    "DEFENDING IN ATTACKING THIRD", "DEFENDING IN MIDDLE THIRD",
    "DEFENDING IN DEFENSIVE THIRD", "DEFENSIVE TRANSITION",
))


def _xy(group, pitch):
    values = group.split(",", 2)
    if len(values) < 2:
        raise ValueError("tracking coordinate group has fewer than two fields")
    x, y = float(values[0]), float(values[1])
    if not (math.isfinite(x) and math.isfinite(y)):
        return None
    return x * pitch[0], y * pitch[1]


def read_team_slots(path):
    root = ET.parse(path).getroot()
    teams = [team.get("id") for team in root.iter("Team")]
    if len(teams) != 2 or not all(teams):
        raise ValueError("ATD metadata must name exactly two teams")
    slots = [player.get("teamId") for player in root.iter("Player")]
    if not slots or any(team_id not in teams for team_id in slots):
        raise ValueError("ATD player slots have an unknown team")
    return np.asarray([0 if team_id == teams[0] else 1 for team_id in slots], dtype=np.int8)


def _arrays(n):
    return {
        "observed": np.zeros(n, dtype=bool),
        "interpolated": np.zeros(n, dtype=bool),
        "ball_x": np.full(n, np.nan, dtype=np.float32),
        "ball_y": np.full(n, np.nan, dtype=np.float32),
        "distance_home": np.full(n, np.inf, dtype=np.float32),
        "distance_away": np.full(n, np.inf, dtype=np.float32),
        "strong": np.full(n, -1, dtype=np.int8),
        "outside": np.zeros(n, dtype=bool),
        "speed": np.full(n, np.nan, dtype=np.float32),
        "tag_team": np.full(n, -1, dtype=np.int8),
        "set_piece": np.zeros(n, dtype=bool),
    }


def read_tracking(raw_path, metadata_path, n_frames, config, blocks):
    """Strictly enforce one raw record for each video frame, in order."""
    slots = read_team_slots(metadata_path)
    result = _arrays(n_frames)
    pitch = (config.pitch_length_m, config.pitch_width_m)
    count = 0
    with Path(raw_path).open(encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            count += 1
            if index >= n_frames:
                raise ValueError("ATD contains more frames than the tactical video")
            fields = line.rstrip("\r\n").split(":")
            if len(fields) != 3:
                raise ValueError("ATD record {} has an invalid field count".format(index + 1))
            if int(fields[0]) != index + 1:
                raise ValueError("ATD record at row {} has wrong frame ID".format(index + 1))
            groups = fields[1].split(";")
            if len(groups) != len(slots):
                raise ValueError("ATD row {} has {} tracks; metadata expects {}".format(
                    index + 1, len(groups), len(slots)))
            ball = _xy(fields[2], pitch)
            if ball is None:
                continue
            bx, by = ball
            result["observed"][index] = True
            result["ball_x"][index] = bx
            result["ball_y"][index] = by
            margin = config.outside_margin_m
            result["outside"][index] = (
                bx < -margin or bx > pitch[0] + margin or
                by < -margin or by > pitch[1] + margin)
            nearest = [math.inf, math.inf]
            for slot, group in enumerate(groups):
                point = _xy(group, pitch)
                if point is None:
                    continue
                distance = math.hypot(point[0] - bx, point[1] - by)
                team = int(slots[slot])
                if distance < nearest[team]:
                    nearest[team] = distance
            result["distance_home"][index] = nearest[0]
            result["distance_away"][index] = nearest[1]
            if not result["outside"][index]:
                if (nearest[0] <= config.control_distance_m and
                        nearest[1] - nearest[0] >= config.control_margin_m):
                    result["strong"][index] = 0
                elif (nearest[1] <= config.control_distance_m and
                      nearest[0] - nearest[1] >= config.control_margin_m):
                    result["strong"][index] = 1
        if count != n_frames:
            raise ValueError("ATD contains {} rows; expected {}".format(count, n_frames))
    for start, stop in blocks:
        previous = None
        for index in range(start, stop):
            if result["observed"][index]:
                if previous is not None and index == previous + 1:
                    result["speed"][index] = math.hypot(
                        float(result["ball_x"][index] - result["ball_x"][previous]),
                        float(result["ball_y"][index] - result["ball_y"][previous])) * 25
                previous = index
        observed = np.flatnonzero(result["observed"][start:stop]) + start
        for left, right in zip(observed[:-1], observed[1:]):
            gap = int(right - left - 1)
            if 0 < gap <= config.max_interpolation_gap_frames:
                for index in range(int(left) + 1, int(right)):
                    fraction = (index - left) / (right - left)
                    result["ball_x"][index] = (
                        result["ball_x"][left] * (1 - fraction) +
                        result["ball_x"][right] * fraction)
                    result["ball_y"][index] = (
                        result["ball_y"][left] * (1 - fraction) +
                        result["ball_y"][right] * fraction)
                    result["interpolated"][index] = True
    return result


def add_smart_tags(features, events, n_frames):
    """Collapse all overlapping phase tags to at most one team clue per frame."""
    home_votes = np.zeros(n_frames + 1, dtype=np.int16)
    away_votes = np.zeros(n_frames + 1, dtype=np.int16)
    set_piece = np.zeros(n_frames + 1, dtype=np.int16)
    for event in events:
        start = max(0, min(n_frames, int(event["start_frame"])))
        stop = max(0, min(n_frames, int(event["end_frame"])))
        if start >= stop:
            continue
        code = (event["code"] or "").strip().upper()
        if code == "SET PIECES":
            set_piece[start] += 1
            set_piece[stop] -= 1
            continue
        team_name = (event["tags"].get("Team") or "").strip().casefold()
        if team_name == "barcelona":
            team = 0
        elif team_name in ("atletic club", "athletic club"):
            team = 1
        else:
            continue
        if code in DEFENCE_CODES:
            team = 1 - team
        elif code not in ATTACK_CODES:
            continue
        votes = home_votes if team == 0 else away_votes
        votes[start] += 1
        votes[stop] -= 1
    home = np.cumsum(home_votes[:-1]) > 0
    away = np.cumsum(away_votes[:-1]) > 0
    features["tag_team"][home & ~away] = 0
    features["tag_team"][away & ~home] = 1
    features["set_piece"][:] = np.cumsum(set_piece[:-1]) > 0
    return features
