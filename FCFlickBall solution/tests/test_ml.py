import tempfile
import unittest
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from threadpoolctl import threadpool_limits
from possession.ml_features import Observations, SCHEMA, extract, mask_ball
from possession.ml_model import viterbi, probabilities
from training.idsse import load_match


def fixture(n=120):
    ball = np.column_stack((np.arange(n)/10+30, np.full(n, 30))).astype(np.float32)
    home = np.stack((ball+[.5, 0], ball+[10, 3], ball+[20, -4]), axis=1)
    away = home+[5, 0]
    return Observations(np.arange(n), ball, home, away, (105., 68.))


class FeatureTests(unittest.TestCase):
    def test_slot_permutation_and_own_labels_unavailable(self):
        a = fixture()
        b = Observations(a.frames, a.ball, a.home[:, ::-1], a.away[:, ::-1], a.pitch)
        x, names = extract(a)
        np.testing.assert_allclose(x, extract(b)[0], equal_nan=True)
        self.assertFalse(hasattr(a, "labels"))
        self.assertEqual(x.shape[1], len(names))

    def test_masking_recomputes_geometry(self):
        a = mask_ball(fixture(), 2026)
        x, names = extract(a)
        missing = ~np.isfinite(a.ball).all(axis=1)
        self.assertTrue(missing.any())
        self.assertTrue(np.isnan(x[missing, names.index("home_distance_1")]).all())
        self.assertTrue((x[missing, names.index("ball_observed")] == 0).all())

    def test_half_edge_does_not_wrap(self):
        x, names = extract(fixture())
        self.assertTrue(np.isnan(x[0, names.index("home_distance_1_offset_-25")]))
        self.assertTrue(np.isnan(x[-1, names.index("home_distance_1_offset_25")]))
        a = fixture()
        a.frames[4] = a.frames[3]
        with self.assertRaises(ValueError):
            extract(a)


class DecoderTests(unittest.TestCase):
    def test_future_evidence_deflection_and_short_possession(self):
        transitions = np.full((3, 3), .01)
        np.fill_diagonal(transitions, .98)
        p = np.tile([.98, .01, .01], (60, 1))
        p[20] = [.4, .59, .01]  # A brief opposing contact.
        pred = viterbi(p, transitions, 1.)
        self.assertTrue((pred == 0).all())
        p[30:36] = [.001, .998, .001]  # A short, strong opposing possession.
        pred = viterbi(p, transitions, 1.)
        self.assertTrue((pred[30:36] == 1).all())

    def test_same_team_restart_is_two_possessions(self):
        p = np.tile([.999, .0005, .0005], (30, 1))
        p[10:15] = [.0005, .0005, .999]
        pred = viterbi(p, np.full((3, 3), 1/3), 1.)
        np.testing.assert_array_equal(pred[10:15], 2)
        self.assertEqual(pred[9], pred[15])
        np.testing.assert_array_equal(viterbi(p, np.full((3, 3), 1/3), 0), p.argmax(axis=1))

    def test_saved_model_predictions_and_feature_schema(self):
        obs = fixture()
        x, names = extract(obs)
        y = np.arange(len(x)) % 3
        with threadpool_limits(limits=2):
            model = HistGradientBoostingClassifier(max_iter=2, min_samples_leaf=5, random_state=1).fit(x, y)
        bundle = dict(estimator=model, schema=SCHEMA, feature_names=names)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"model.joblib"
            joblib.dump(bundle, path)
            np.testing.assert_array_equal(probabilities(bundle, obs), probabilities(joblib.load(path), obs))
        bundle["schema"] = "bad"
        with self.assertRaises(ValueError):
            probabilities(bundle, obs)


class ExternalAdapterTests(unittest.TestCase):
    def test_label_mapping_frame_alignment_and_units(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            root.joinpath("matchinformation_TEST.xml").write_text(
                '<Root><General HomeTeamId="h" GuestTeamId="a"/><Environment PitchX="100" PitchY="60"/></Root>')
            xml = ['<Root>']
            for half in ("firstHalf", "secondHalf"):
                for team, x in (("ball", 0), ("h", 1), ("a", 5)):
                    xml.append(f'<FrameSet GameSection="{half}" TeamId="{team}" PersonId="{team}">')
                    for n, status, owner in ((10001, 1, 1), (10002, 1, 2), (10003, 0, 1), (10004, 1, 9)):
                        xml.append(f'<Frame N="{n}" X="{x}" Y="0" BallStatus="{status}" BallPossession="{owner}"/>')
                    xml.append('</FrameSet>')
            xml.append('</Root>')
            root.joinpath("positions_raw_TEST.xml").write_text(''.join(xml))
            halves = load_match(root, "TEST")
            self.assertEqual(len(halves), 2)
            for _, obs, y in halves:
                np.testing.assert_array_equal(y, [0, 1, 2, 3])
                np.testing.assert_array_equal(obs.frames, np.arange(10001, 10005))
                np.testing.assert_allclose(obs.ball[0], [50, 30])
                np.testing.assert_allclose(obs.home[0, 0], [51, 30])


if __name__ == "__main__":
    unittest.main()
