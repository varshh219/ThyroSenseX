"""Inference for the ThyroSenseX RF + XGBoost + 1D-CNN fusion ensemble.

Pure numpy / sklearn / xgboost so it runs on the Raspberry Pi without torch.
The 1D CNN is trained with torch (training/train_pipeline.py) and exported as
plain numpy arrays inside the model pack, with BatchNorm already folded away.
"""

import numpy as np
import joblib


def _softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def _conv1d_same(x, w, b):
    """x: (N, Cin, L), w: (Cout, Cin, K) with odd K, zero 'same' padding."""
    n, _, length = x.shape
    cout, _, k = w.shape
    pad = k // 2
    xp = np.pad(x, ((0, 0), (0, 0), (pad, pad)))
    out = np.zeros((n, cout, length), dtype=np.float32)
    for i in range(k):
        out += np.einsum("oc,ncl->nol", w[:, :, i], xp[:, :, i:i + length])
    return out + b[None, :, None]


def _maxpool2(x):
    n, c, length = x.shape
    length2 = length // 2
    return x[:, :, :length2 * 2].reshape(n, c, length2, 2).max(axis=3)


def cnn_predict_proba(cnn, x):
    """x: (N, n_active) raw (unscaled) features in `active_columns` order."""
    x = (x - cnn["mean"]) / cnn["std"]
    h = x[:, None, :].astype(np.float32)
    for layer in cnn["convs"]:
        h = np.maximum(_conv1d_same(h, layer["w"], layer["b"]), 0.0)
        if layer["pool"]:
            h = _maxpool2(h)
    h = h.mean(axis=2)
    h = np.maximum(h @ cnn["fc1_w"].T + cnn["fc1_b"], 0.0)
    return _softmax(h @ cnn["fc2_w"].T + cnn["fc2_b"])


class ThyroidEnsemble:
    def __init__(self, pack):
        from xgboost import XGBClassifier

        self.pack = pack
        self.feature_columns = pack["feature_columns"]
        self.class_names = pack["class_names"]
        self.active_idx = np.asarray(pack["active_idx"])
        self.weights = pack["fusion_weights"]
        self.rf = pack["rf_model"]
        self.xgb = XGBClassifier()
        self.xgb.load_model(bytearray(pack["xgb_raw_json"]))
        self.cnn = pack["cnn"]

    @classmethod
    def load(cls, path):
        return cls(joblib.load(path))

    def vector(self, features: dict):
        return np.array(
            [[float(features.get(c, 0.0)) for c in self.feature_columns]],
            dtype=np.float32,
        )

    def predict_all(self, x_full):
        """x_full: (N, len(feature_columns)). Returns dict of per-model probs."""
        x = np.asarray(x_full, dtype=np.float32)[:, self.active_idx]
        probs = {
            "rf": self.rf.predict_proba(x),
            "xgb": self.xgb.predict_proba(x),
            "cnn": cnn_predict_proba(self.cnn, x),
        }
        probs["fusion"] = sum(self.weights[k] * probs[k] for k in ("rf", "xgb", "cnn"))
        return probs

    def predict(self, features: dict):
        """Returns (class_name, confidence_percent, per_model_probs)."""
        probs = self.predict_all(self.vector(features))
        fused = probs["fusion"][0]
        idx = int(np.argmax(fused))
        return self.class_names[idx], round(float(fused[idx]) * 100, 2), probs
