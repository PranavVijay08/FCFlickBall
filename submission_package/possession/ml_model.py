"""Frozen model inference and whole-half sequence decoding; no fitting here."""
import numpy as np
from threadpoolctl import threadpool_limits
from possession.ml_features import SCHEMA, extract


def viterbi(probabilities, transitions, strength):
    if probabilities.ndim != 2 or probabilities.shape[1] != 3 or not len(probabilities):
        raise ValueError("Expected nonempty H/A/D probabilities")
    if not np.isfinite(probabilities).all() or np.any(probabilities < 0):
        raise ValueError("Invalid prediction probabilities")
    emission = np.log(np.maximum(probabilities, 1e-12))
    links = strength * np.log(np.maximum(transitions, 1e-12))
    pointers = np.zeros((len(emission), 3), np.int8)
    scores = emission[0]
    for t in range(1, len(emission)):
        candidates = scores[:, None] + links
        pointers[t] = np.argmax(candidates, axis=0)
        scores = candidates[pointers[t], np.arange(3)] + emission[t]
    labels = np.empty(len(emission), np.int8)
    labels[-1] = int(np.argmax(scores))
    for t in range(len(labels)-1, 0, -1):
        labels[t-1] = pointers[t, labels[t]]
    return labels


def probabilities(bundle, obs):
    if bundle["schema"] != SCHEMA:
        raise ValueError("Unsupported model feature schema")
    features, names = extract(obs)
    if names != bundle["feature_names"]:
        raise ValueError("Model/feature order mismatch")
    if list(bundle["estimator"].classes_) != [0, 1, 2]:
        raise ValueError("Model must predict H/A/D in the declared order")
    with threadpool_limits(limits=4):
        return bundle["estimator"].predict_proba(features)


def predict(bundle, obs):
    p = probabilities(bundle, obs)
    return viterbi(p, bundle["transitions"], bundle["lambda"])
