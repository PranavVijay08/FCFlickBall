"""Train/select on licensed external data; test split is evaluated only by --holdout."""
import argparse
import hashlib
import json
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from threadpoolctl import threadpool_limits
from possession.ml_features import SCHEMA, extract, mask_ball, swapped
from possession.ml_model import probabilities, viterbi
from training.idsse import read_half
from training.download_idsse import SPLITS, digest
from evaluation import possession_metrics as pm

SETTINGS = dict(learning_rate=.1, max_iter=100, max_leaf_nodes=15, min_samples_leaf=20,
                l2_regularization=1., early_stopping=False, random_state=2026)
LAMBDAS = [0., .25, 1., 2.]


def seed_for(match, half):
    return int(hashlib.sha256((match+half).encode()).hexdigest()[:8], 16)


def halves(folder, split):
    for match in SPLITS[split]:
        for half in ("firstHalf", "secondHalf"):
            path = Path(folder) / (match + "_" + half + ".npz")
            yield match, half, path, *read_half(path)


def baseline(obs):
    distances = []
    for players in (obs.home, obs.away):
        d = np.linalg.norm(players-obs.ball[:, None], axis=2)
        d[~np.isfinite(d)] = np.inf
        distances.append(np.min(d, axis=1) if d.shape[1] else np.full(len(obs.frames), np.inf))
    h, a = distances
    codes = np.where(np.isfinite(np.minimum(h, a)), np.where(h <= a, 0, 1), 2)
    sums = [np.concatenate(([0], np.cumsum(codes == side))) for side in (0, 1)]
    t = np.arange(len(codes))
    lo, hi = np.maximum(0, t-50), np.minimum(len(codes), t+51)
    home, away = [s[hi]-s[lo] for s in sums]
    return np.where(home+away > 0, np.where(home >= away, 0, 1), 2).astype(np.int8)


def metrics(y, pred):
    r = pm.evaluate(y, pred, bootstrap_n=0)
    return {"macro_f1": r["macro_f1"], "spell_f1": r["spell_f1_mean"],
            "spells_predicted": r["n_pred_spells"], "spells_true": r["n_gt_spells"],
            "per_class": r["per_class"]}


def aggregate(rows):
    # Average halves within matches, then matches equally.
    result = {}
    for condition in ("clean", "masked"):
        group = [r for r in rows if r["condition"] == condition]
        result[condition] = {}
        for key in ("macro_f1", "spell_f1"):
            by_match = [np.mean([r[key] for r in group if r["match"] == m])
                        for m in sorted({r["match"] for r in group})]
            result[condition][key] = float(np.mean(by_match))
    return result


def evaluate_bundle(bundle, folder, split, lambdas):
    rows = {str(value): [] for value in lambdas}
    reference = []
    for match, half, _, obs, labels in halves(folder, split):
        for condition, inputs in (("clean", obs), ("masked", mask_ball(obs, seed_for(match, half)))):
            print("Evaluating external", split, match, half, condition, flush=True)
            p = probabilities(bundle, inputs)
            reference.append(dict(match=match, half=half, condition=condition, **metrics(labels, baseline(inputs))))
            for value in lambdas:
                pred = viterbi(p, bundle["transitions"], value)
                rows[str(value)].append(dict(match=match, half=half, condition=condition, **metrics(labels, pred)))
    return {k: {"aggregate": aggregate(v), "halves": v} for k, v in rows.items()}, {
        "aggregate": aggregate(reference), "halves": reference}


def train(folder, model_path, report_path):
    matrices, targets, sources = [], [], []
    transitions = np.ones((3, 3), np.float64)
    feature_names = None
    for match, half, path, obs, labels in halves(folder, "train"):
        print("Preparing external training", match, half, flush=True)
        sources.append({"path": path.name, "sha256": digest(path)})
        valid_pairs = (labels[:-1] < 3) & (labels[1:] < 3)
        for y in (labels, np.where(labels == 0, 1, np.where(labels == 1, 0, labels))):
            np.add.at(transitions, (y[:-1][valid_pairs], y[1:][valid_pairs]), 1)
        for inputs in (obs, mask_ball(obs, seed_for(match, half))):
            for team_swap in (False, True):
                x, names = extract(swapped(inputs) if team_swap else inputs)
                if feature_names is not None and feature_names != names:
                    raise ValueError("Inconsistent feature order")
                feature_names = names
                y = np.where(labels == 0, 1, np.where(labels == 1, 0, labels)) if team_swap else labels
                idx = np.arange(0, len(y), 5)
                idx = idx[y[idx] < 3]
                matrices.append(x[idx])
                targets.append(y[idx])
    x, y = np.concatenate(matrices), np.concatenate(targets)
    del matrices, targets
    if set(np.unique(y)) != {0, 1, 2}:
        raise ValueError("Training data must contain all three classes")
    print("Training", len(y), "external samples;", x.shape[1], "features", flush=True)
    estimator = HistGradientBoostingClassifier(**SETTINGS)
    with threadpool_limits(limits=4):
        estimator.fit(x, y)
    del x, y
    transitions /= transitions.sum(axis=1, keepdims=True)
    bundle = {"schema": SCHEMA, "feature_names": feature_names, "estimator": estimator,
              "transitions": transitions, "lambda": 0., "training_settings": SETTINGS,
              "training_source": "IDSSE version 1, external matches only", "splits": SPLITS}
    candidates, reference = evaluate_bundle(bundle, folder, "validation", LAMBDAS)
    eligible = []
    for key, result in candidates.items():
        scores, ref = result["aggregate"], reference["aggregate"]
        passed = all(scores[c]["spell_f1"] > ref[c]["spell_f1"] and
                     scores[c]["macro_f1"] >= ref[c]["macro_f1"] for c in ("clean", "masked"))
        result["passes_adoption_gate"] = passed
        if passed:
            eligible.append(float(key))
    # Retain the strongest external candidate for review even if it does not qualify for deployment.
    pool = eligible or LAMBDAS
    selected = max(pool, key=lambda v: (candidates[str(v)]["aggregate"]["masked"]["spell_f1"],
                                      candidates[str(v)]["aggregate"]["masked"]["macro_f1"], -v))
    bundle["lambda"] = selected
    bundle["adopt_ml"] = bool(eligible)
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path, compress=3)
    report = {"decision": "ml" if eligible else "fallback", "selected_lambda": selected,
              "model_sha256": digest(model_path), "training_sources": sources,
              "settings": SETTINGS, "splits": SPLITS, "validation": candidates,
              "baseline": reference, "test_consulted": False}
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("ADOPTION DECISION", report["decision"], "lambda", selected, flush=True)
    print(json.dumps({"model": candidates[str(selected)]["aggregate"], "baseline": reference["aggregate"]}), flush=True)


def holdout(folder, model_path, output):
    if Path(output).exists():
        raise FileExistsError("Holdout report exists; refusing accidental repeated test evaluation")
    bundle = joblib.load(model_path)  # Only load the trusted artifact generated by this repository.
    candidate, reference = evaluate_bundle(bundle, folder, "test", [bundle["lambda"]])
    report = {"model_sha256": digest(model_path), "candidate": candidate, "baseline": reference,
              "purpose": "Final reporting only; no further model selection"}
    Path(output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Holdout report saved; model/configuration unchanged", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", default="external_data/prepared")
    parser.add_argument("--model", default="models/idsse_hgb.joblib")
    parser.add_argument("--report", default="artifacts/external_validation.json")
    parser.add_argument("--holdout", action="store_true")
    args = parser.parse_args()
    if args.holdout:
        holdout(args.prepared, args.model, args.report)
    else:
        train(args.prepared, args.model, args.report)
