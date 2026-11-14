"""Decode possession with evidence that persists over time, independently per half."""

from collections import deque

import math
import numpy as np


TEAM_LABELS = ("H", "A")


def _restart_team(features, start, stop):
    strong = set(int(value) for value in features["strong"][start:stop] if value >= 0)
    if len(strong) == 1:
        return strong.pop()
    tags = set(int(value) for value in features["tag_team"][start:stop] if value >= 0)
    if not strong and len(tags) == 1:
        return tags.pop()
    return -1


def decode_half(features, start, stop, kickoff, config):
    """Return labels and local transition reasons for [start, stop)."""
    labels = np.full(stop - start, "X", dtype="<U1")
    transitions = []
    if not start <= kickoff < stop:
        raise ValueError("kickoff is outside the supplied half")
    labels[:kickoff - start] = "D"
    state = -1  # -1 unresolved; 0 home; 1 away; 2 dead
    window = deque(maxlen=config.turnover_window_frames)
    tag_change = 0
    tag_initial = 0
    live_tag = 0
    outside_count = 0
    stationary_count = 0
    stationary_anchor = None
    set_piece_missing = 0
    restart_motion = 0

    for frame in range(kickoff, stop):
        local = frame - start
        strong = int(features["strong"][frame])
        tag = int(features["tag_team"][frame])
        seen = bool(features["observed"][frame])
        outside = seen and bool(features["outside"][frame])
        set_piece = bool(features["set_piece"][frame])
        speed = float(features["speed"][frame])

        outside_count = outside_count + 1 if outside else 0
        if seen and set_piece and not outside:
            point = (float(features["ball_x"][frame]), float(features["ball_y"][frame]))
            if stationary_anchor is None or math.dist(point, stationary_anchor) > config.stationary_radius_m:
                stationary_anchor = point
                stationary_count = 1
            else:
                stationary_count += 1
        else:
            stationary_anchor = None
            stationary_count = 0
        set_piece_missing = set_piece_missing + 1 if set_piece and not seen else 0

        if state != 2:
            stop_reason = None
            onset = None
            if outside_count >= config.outside_confirm_frames:
                stop_reason = "observed_outside_pitch"
                onset = frame - outside_count + 1
            elif stationary_count >= config.stationary_confirm_frames:
                stop_reason = "stationary_set_piece"
                onset = frame - stationary_count + 1
            elif set_piece_missing >= config.set_piece_missing_confirm_frames:
                stop_reason = "missing_ball_set_piece"
                onset = frame - set_piece_missing + 1
            if stop_reason is not None:
                previous = labels[onset - start - 1] if onset > start else "X"
                labels[onset - start:local + 1] = "D"
                transitions = [event for event in transitions if event[0] < onset]
                transitions.append((onset, previous, "D", stop_reason))
                state = 2
                window.clear()
                tag_change = tag_initial = live_tag = 0
                restart_motion = 0
                continue

        if state == 2:
            moving = seen and not outside and math.isfinite(speed) and speed > config.restart_speed_mps
            restart_motion = restart_motion + 1 if moving else 0
            live_tag = live_tag + 1 if tag >= 0 and not set_piece else 0
            onset = None
            reason = None
            if restart_motion >= config.restart_motion_confirm_frames:
                onset = frame - restart_motion + 1
                reason = "observed_restart_motion"
            elif live_tag >= config.live_tag_confirm_frames:
                onset = frame - live_tag + 1
                reason = "sustained_live_phase"
            if onset is None:
                labels[local] = "D"
                continue
            team = _restart_team(features, onset, frame + 1)
            state = team
            label = TEAM_LABELS[team] if team >= 0 else "X"
            labels[onset - start:local + 1] = label
            transitions.append((onset, "D", label, reason))
            window.clear()
            tag_change = tag_initial = 0
            outside_count = stationary_count = set_piece_missing = 0
            stationary_anchor = None
            continue

        if state == -1:
            if strong >= 0:
                state = strong
                labels[local] = TEAM_LABELS[strong]
                transitions.append((frame, "X", TEAM_LABELS[strong], "initial_geometry"))
                tag_initial = 0
            elif tag >= 0:
                tag_initial = tag_initial + 1 if tag_initial and tag == int(features["tag_team"][frame - 1]) else 1
                if tag_initial >= config.tag_change_frames:
                    onset = frame - tag_initial + 1
                    state = tag
                    labels[onset - start:local + 1] = TEAM_LABELS[tag]
                    transitions.append((onset, "X", TEAM_LABELS[tag], "initial_phase_tag"))
                else:
                    labels[local] = "X"
            else:
                tag_initial = 0
                labels[local] = "X"
            continue

        labels[local] = TEAM_LABELS[state]
        window.append((frame, strong))
        opponent = 1 - state
        if strong == opponent:
            supporters = [index for index, value in window if value == opponent]
            if len(supporters) >= config.turnover_support_frames:
                onset = supporters[0]
                labels[onset - start:local + 1] = TEAM_LABELS[opponent]
                transitions.append((onset, TEAM_LABELS[state], TEAM_LABELS[opponent], "confirmed_geometry"))
                state = opponent
                window.clear()
                tag_change = 0
                continue
        geometry_unavailable = (not seen or (
            math.isinf(float(features["distance_home"][frame])) and
            math.isinf(float(features["distance_away"][frame]))))
        if tag == opponent and strong == -1 and geometry_unavailable:
            tag_change += 1
            if tag_change >= config.tag_change_frames:
                onset = frame - tag_change + 1
                labels[onset - start:local + 1] = TEAM_LABELS[opponent]
                transitions.append((onset, TEAM_LABELS[state], TEAM_LABELS[opponent], "sustained_phase_tag"))
                state = opponent
                window.clear()
                tag_change = 0
        else:
            tag_change = 0
    return labels, transitions


def decode(features, n_frames, blocks, kickoffs, config):
    result = np.full(n_frames, "X", dtype="<U1")
    transitions = []
    for half, start, stop in blocks:
        labels, part = decode_half(features, start, stop, kickoffs[half], config)
        result[start:stop] = labels
        transitions.extend(part)
    return result, transitions
