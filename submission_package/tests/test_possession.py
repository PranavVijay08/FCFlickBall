"""Synthetic examples; never uses labels or assets from the competition match."""

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

from possession.config import load as load_config
from possession.decoder import decode, decode_half
from possession.features import _arrays, add_smart_tags, read_tracking


CONFIG = load_config(Path(__file__).resolve().parents[1] / "configs" / "default.json")


def scene(n=240):
    features = _arrays(n)
    features["observed"][:] = True
    features["ball_x"][:] = 40
    features["ball_y"][:] = 30
    features["strong"][:] = 0
    return features


class DecoderTests(unittest.TestCase):
    def test_pass_deflection_turnover_stoppage_and_restart(self):
        f = scene()
        f["observed"][60:75] = False
        f["strong"][60:75] = -1
        f["strong"][75:78] = 1  # isolated opponent contact
        f["strong"][100:115] = 1  # sustained opponent control
        f["strong"][115:] = 1
        f["outside"][120:150] = True
        f["strong"][120:150] = -1
        f["observed"][125:150] = False
        f["outside"][125:150] = False
        f["strong"][150:] = 0
        f["speed"][150:160] = 2
        labels, transitions = decode_half(f, 0, 240, 0, CONFIG)
        self.assertTrue(np.all(labels[:100] == "H"))
        self.assertTrue(np.all(labels[100:120] == "A"))
        self.assertTrue(np.all(labels[120:150] == "D"))
        self.assertTrue(np.all(labels[150:] == "H"))
        self.assertIn((100, "H", "A", "confirmed_geometry"), transitions)

    def test_missing_ball_does_not_mean_dead(self):
        f = scene(80)
        f["observed"][20:70] = False
        f["strong"][20:70] = -1
        labels, _ = decode_half(f, 0, 80, 0, CONFIG)
        self.assertTrue(np.all(labels == "H"))

    def test_second_half_waits_for_kickoff_and_resets_state(self):
        f = scene(80)
        f["strong"][40:] = 1
        labels, _ = decode(f, 80, [(1, 0, 30), (2, 40, 80)], {1: 0, 2: 60}, CONFIG)
        self.assertTrue(np.all(labels[:30] == "H"))
        self.assertTrue(np.all(labels[30:40] == "X"))
        self.assertTrue(np.all(labels[40:60] == "D"))
        self.assertTrue(np.all(labels[60:] == "A"))

    def test_stationary_set_piece_and_tag_only_recovery(self):
        f = scene(130)
        f["strong"][30:] = -1
        f["set_piece"][30:90] = True
        f["tag_team"][90:] = 1
        labels, transitions = decode_half(f, 0, 130, 0, CONFIG)
        self.assertTrue(np.all(labels[30:90] == "D"))
        self.assertTrue(np.all(labels[90:] == "A"))
        self.assertIn((30, "H", "D", "stationary_set_piece"), transitions)

    def test_short_real_possession_is_allowed(self):
        config = replace(CONFIG, turnover_window_frames=3, turnover_support_frames=2)
        f = scene(30)
        f["strong"][10:14] = 1
        labels, _ = decode_half(f, 0, 30, 0, config)
        self.assertTrue(np.all(labels[10:14] == "A"))
        self.assertTrue(np.all(labels[14:] == "H"))

    def test_opposing_tag_can_resolve_missing_geometry(self):
        f = scene(80)
        f["observed"][20:] = False
        f["strong"][20:] = -1
        f["tag_team"][20:] = 1
        labels, transitions = decode_half(f, 0, 80, 0, CONFIG)
        self.assertTrue(np.all(labels[:20] == "H"))
        self.assertTrue(np.all(labels[20:] == "A"))
        self.assertIn((20, "H", "A", "sustained_phase_tag"), transitions)

    def test_opposing_tag_does_not_override_observed_contest(self):
        f = scene(80)
        f["strong"][20:] = -1
        f["distance_home"][20:] = 3
        f["distance_away"][20:] = 4
        f["tag_team"][20:] = 1
        labels, _ = decode_half(f, 0, 80, 0, CONFIG)
        self.assertTrue(np.all(labels == "H"))


class FeatureTests(unittest.TestCase):
    def test_parser_alignment_team_geometry_and_interpolation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            meta = root / "meta.xml"
            raw = root / "raw.txt"
            meta.write_text(
                '<root><Team id="home"/><Team id="away"/>'
                '<Player teamId="home"/><Player teamId="away"/></root>', encoding="utf-8")
            raw.write_text(
                "1:0.5,0.5,0;0.9,0.9,0:0.5,0.5,0\n"
                "2:0.5,0.5,0;0.9,0.9,0:NaN,NaN,NaN\n"
                "3:0.5,0.5,0;0.9,0.9,0:0.5,0.5,0\n", encoding="utf-8")
            f = read_tracking(raw, meta, 3, CONFIG, [(0, 3)])
            self.assertEqual(list(f["strong"]), [0, -1, 0])
            self.assertTrue(f["interpolated"][1])
            self.assertFalse(f["observed"][1])
            raw.write_text(raw.read_text(encoding="utf-8").replace("2:", "3:", 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "wrong frame ID"):
                read_tracking(raw, meta, 3, CONFIG, [(0, 3)])

    def test_interpolation_never_crosses_halves(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            meta = root / "meta.xml"
            raw = root / "raw.txt"
            meta.write_text(
                '<root><Team id="home"/><Team id="away"/>'
                '<Player teamId="home"/><Player teamId="away"/></root>', encoding="utf-8")
            raw.write_text(
                "1:0.5,0.5,0;0.9,0.9,0:0.5,0.5,0\n"
                "2:0.5,0.5,0;0.9,0.9,0:NaN,NaN,NaN\n"
                "3:0.5,0.5,0;0.9,0.9,0:NaN,NaN,NaN\n"
                "4:0.5,0.5,0;0.9,0.9,0:0.5,0.5,0\n", encoding="utf-8")
            f = read_tracking(raw, meta, 4, CONFIG, [(0, 2), (2, 4)])
            self.assertFalse(np.any(f["interpolated"]))

    def test_conflicting_tags_are_neutral_and_set_piece_is_separate(self):
        f = _arrays(20)
        events = [
            {"start_frame": 0, "end_frame": 10, "code": "BUILD UP", "tags": {"Team": "Barcelona"}},
            {"start_frame": 5, "end_frame": 15, "code": "PROGRESSION", "tags": {"Team": "Atletic Club"}},
            {"start_frame": 10, "end_frame": 20, "code": "SET PIECES", "tags": {"Team": "N/A"}},
        ]
        add_smart_tags(f, events, 20)
        self.assertEqual(list(f["tag_team"][[0, 7, 12, 17]]), [0, -1, 1, -1])
        self.assertTrue(np.all(f["set_piece"][10:]))


if __name__ == "__main__":
    unittest.main()
