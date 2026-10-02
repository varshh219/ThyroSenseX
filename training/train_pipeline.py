"""ThyroSenseX training pipeline: RF + XGBoost + 1D-CNN with probability fusion.

    python training/train_pipeline.py --data data/upgraded_full_dataset.csv

Steps: clean (drop constant columns, drop duplicate rows) -> stratified
hold-out split -> 5-fold CV on the development set -> train final models ->
tune fusion weights on a validation split -> evaluate once on the test set ->
modality ablation -> write model/model.pkl and model/report/metrics.json.

The CNN is a 1D CNN over the standardised feature vector (features are ordered
demographics, face, voice, thermal so neighbouring features are related). It is
NOT an image CNN: the repo has no image data.
"""

import argparse
import itertools
import json
import os
import random
import sys
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import (GroupShuffleSplit, StratifiedGroupKFold,
                                     StratifiedKFold, train_test_split)
from xgboost import XGBClassifier

SEED = 42
CLASS_NAMES = ["Normal", "Hypothyroidism", "Hyperthyroidism"]
TARGET = "classification"

GROUPS = {
    "demographics": ["age", "gender", "weight"],
    "face": ["has_dark_circle", "facial_swelling", "puffy_eyes", "dry_skin_visible",
             "goiter_visible", "coarse_facial_features", "tired_expression",
             "hair_loss", "weight_gain", "pale_skin"],
    "voice": ["pitch_mean", "pitch_std", "pitch_min", "pitch_max", "energy_mean",
              "energy_std", "zcr_mean", "mfcc_mean_1", "mfcc_mean_2", "mfcc_mean_3"],
    "thermal": ["thermal_mean", "thermal_std", "thermal_max", "thermal_min",
                "thermal_range", "thermal_forehead", "thermal_mid",
                "thermal_chin_neck", "thermal_left_mean", "thermal_right_mean",
                "thermal_lr_asymmetry", "thermal_centre", "thermal_hot_ratio",
                "thermal_grad_v", "thermal_grad_h"],
}

RF_PARAMS = dict(n_estimators=400, max_depth=14, min_samples_split=4,
                 class_weight="balanced", n_jobs=-1, random_state=SEED)
XGB_PARAMS = dict(n_estimators=400, max_depth=6, learning_rate=0.03,
                  subsample=0.8, colsample_bytree=0.8, objective="multi:softprob",
                  eval_metric="mlogloss", n_jobs=-1, random_state=SEED)
CNN_PARAMS = dict(channels=(32, 64, 64), kernel=3, fc=64, dropout=0.3, lr=1e-3,
                  weight_decay=1e-4, batch_size=64, max_epochs=300, patience=25)


def seed_everything(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.use_deterministic_algorithms(True)
    except ImportError:
        pass


# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------
def load_and_clean(path, group_col=None):
    df = pd.read_csv(path)
    raw = df
    info = {"rows_raw": len(df)}
    missing = [c for g in GROUPS.values() for c in g if c not in df.columns]
    if missing:
        sys.exit(f"dataset is missing expected columns: {missing}")
    feature_columns = [c for g in GROUPS.values() for c in g]  # fixed order
    df = df[feature_columns + [TARGET]]
    n_dup = int(df.duplicated().sum())
    if group_col:
        df[group_col] = raw[group_col].values  # keep subject ids for grouped splits
        n_dup = 0  # repeated sessions are legitimate, not duplicates
    else:
        df = df.drop_duplicates().reset_index(drop=True)
    info.update(duplicates_removed=n_dup, rows_clean=len(df),
                class_counts={CLASS_NAMES[k]: int(v)
                              for k, v in df[TARGET].value_counts().sort_index().items()})
    active = [c for c in feature_columns if df[c].nunique() > 1]
    info["constant_columns_dropped"] = [c for c in feature_columns if c not in active]
    info["active_columns"] = active
    return df, feature_columns, active, info


# --------------------------------------------------------------------------
# models
# --------------------------------------------------------------------------
def fit_rf(x, y):
    return RandomForestClassifier(**RF_PARAMS).fit(x, y)


def fit_xgb(x, y):
    return XGBClassifier(**XGB_PARAMS).fit(x, y)


def build_cnn(n_features, n_classes, p=CNN_PARAMS):
    import torch.nn as nn

    layers, cin = [], 1
    for i, cout in enumerate(p["channels"]):
        layers += [nn.Conv1d(cin, cout, p["kernel"], padding=p["kernel"] // 2),
                   nn.BatchNorm1d(cout), nn.ReLU()]
        if i == 1:
            layers.append(nn.MaxPool1d(2))
        cin = cout
    return nn.Sequential(*layers, nn.AdaptiveAvgPool1d(1), nn.Flatten(),
                         nn.Linear(cin, p["fc"]), nn.ReLU(), nn.Dropout(p["dropout"]),
                         nn.Linear(p["fc"], n_classes))


def fit_cnn(x_tr, y_tr, x_val, y_val, n_classes=3, verbose=False):
    """Returns dict with standardiser stats, torch model and training history."""
    import torch
    import torch.nn as nn

    p = CNN_PARAMS
    mean = x_tr.mean(axis=0)
    std = x_tr.std(axis=0)
    std[std == 0] = 1.0

    def prep(a):
        return torch.tensor(((a - mean) / std)[:, None, :], dtype=torch.float32)

    xt, xv = prep(x_tr), prep(x_val)
    yt = torch.tensor(np.asarray(y_tr), dtype=torch.long)
    yv = torch.tensor(np.asarray(y_val), dtype=torch.long)
    model = build_cnn(x_tr.shape[1], n_classes)
    opt = torch.optim.Adam(model.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
    lossf = nn.CrossEntropyLoss()
    gen = torch.Generator().manual_seed(SEED)
    best, best_state, bad, hist = float("inf"), None, 0, []
    for epoch in range(p["max_epochs"]):
        model.train()
        perm = torch.randperm(len(xt), generator=gen)
        for i in range(0, len(xt), p["batch_size"]):
            idx = perm[i:i + p["batch_size"]]
            if len(idx) < 2:
                continue
            opt.zero_grad()
            lossf(model(xt[idx]), yt[idx]).backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            vloss = lossf(model(xv), yv).item()
        hist.append(vloss)
        if vloss < best - 1e-4:
            best, bad = vloss, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= p["patience"]:
                break
    model.load_state_dict(best_state)
    model.eval()
    if verbose:
        print(f"    CNN stopped at epoch {len(hist)}, best val loss {best:.4f}")
    return {"torch": model, "mean": mean, "std": std, "epochs": len(hist),
            "best_val_loss": best}


def cnn_proba_torch(c, x):
    import torch
    with torch.no_grad():
        t = torch.tensor(((x - c["mean"]) / c["std"])[:, None, :], dtype=torch.float32)
        return torch.softmax(c["torch"](t), dim=1).numpy()


def export_cnn(c):
    """Fold BatchNorm into the convs and return plain numpy arrays."""
    import torch.nn as nn

    mods = list(c["torch"])
    convs, i = [], 0
    while i < len(mods):
        m = mods[i]
        if isinstance(m, nn.Conv1d):
            bn = mods[i + 1]
            s = (bn.weight / (bn.running_var + bn.eps).sqrt()).detach().numpy()
            w = m.weight.detach().numpy() * s[:, None, None]
            b = (m.bias.detach().numpy() - bn.running_mean.numpy()) * s + bn.bias.detach().numpy()
            pool = isinstance(mods[i + 3], nn.MaxPool1d) if i + 3 < len(mods) else False
            convs.append({"w": w.astype(np.float32), "b": b.astype(np.float32), "pool": pool})
            i += 4 if pool else 3
        else:
            i += 1
    lins = [m for m in mods if isinstance(m, nn.Linear)]
    return {
        "mean": c["mean"].astype(np.float32), "std": c["std"].astype(np.float32),
        "convs": convs,
        "fc1_w": lins[0].weight.detach().numpy(), "fc1_b": lins[0].bias.detach().numpy(),
        "fc2_w": lins[1].weight.detach().numpy(), "fc2_b": lins[1].bias.detach().numpy(),
    }


# --------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------
def metrics(y_true, proba):
    y_true = np.asarray(y_true)
    pred = proba.argmax(axis=1)
    cm = confusion_matrix(y_true, pred, labels=[0, 1, 2])
    sens, spec = {}, {}
    for k, name in enumerate(CLASS_NAMES):
        tp = cm[k, k]
        fn = cm[k].sum() - tp
        fp = cm[:, k].sum() - tp
        tn = cm.sum() - tp - fn - fp
        sens[name] = round(tp / (tp + fn), 4) if tp + fn else None
        spec[name] = round(tn / (tn + fp), 4) if tn + fp else None
    return {
        "accuracy": round(accuracy_score(y_true, pred), 4),
        "precision_macro": round(precision_score(y_true, pred, average="macro", zero_division=0), 4),
        "recall_macro": round(recall_score(y_true, pred, average="macro", zero_division=0), 4),
        "f1_macro": round(f1_score(y_true, pred, average="macro", zero_division=0), 4),
        "auc_ovr_macro": round(roc_auc_score(y_true, proba, multi_class="ovr", average="macro"), 4),
        "sensitivity": sens, "specificity": spec, "confusion_matrix": cm.tolist(),
    }


def bootstrap_ci(y_true, proba, n=1000):
    rng = np.random.default_rng(SEED)
    y_true = np.asarray(y_true)
    acc, f1 = [], []
    for _ in range(n):
        i = rng.integers(0, len(y_true), len(y_true))
        pred = proba[i].argmax(axis=1)
        acc.append(accuracy_score(y_true[i], pred))
        f1.append(f1_score(y_true[i], pred, average="macro", zero_division=0))
    q = lambda a: [round(float(np.percentile(a, 2.5)), 4), round(float(np.percentile(a, 97.5)), 4)]
    return {"accuracy_95ci": q(acc), "f1_macro_95ci": q(f1)}


def mcnemar_p(y_true, pa, pb):
    """Exact two-sided McNemar test on the two models' correctness."""
    from scipy.stats import binomtest
    ca = pa.argmax(1) == y_true
    cb = pb.argmax(1) == y_true
    b, c = int((ca & ~cb).sum()), int((~ca & cb).sum())
    return 1.0 if b + c == 0 else round(float(binomtest(b, b + c, 0.5).pvalue), 6)


def fusion(probs, w):
    return sum(w[k] * probs[k] for k in ("rf", "xgb", "cnn"))


def tune_weights(y_val, probs):
    best, best_w = float("inf"), None
    grid = np.arange(0, 1.01, 0.1)
    for a, b in itertools.product(grid, grid):
        if a + b > 1.0 + 1e-9:
            continue
        w = {"rf": a, "xgb": b, "cnn": max(0.0, 1.0 - a - b)}
        p = np.clip(fusion(probs, w), 1e-9, 1)
        loss = -np.mean(np.log(p[np.arange(len(y_val)), y_val]))
        if loss < best:
            best, best_w = loss, w
    return {k: round(float(v), 2) + 0.0 for k, v in best_w.items()}


# --------------------------------------------------------------------------
# experiments
# --------------------------------------------------------------------------
def inner_split(x, y, groups=None):
    if groups is None:
        return train_test_split(x, y, test_size=0.15, stratify=y, random_state=SEED)
    a, b = next(GroupShuffleSplit(1, test_size=0.15, random_state=SEED).split(x, y, groups))
    return x[a], x[b], y[a], y[b]


def cross_validate(x, y, folds=5, groups=None):
    if groups is None:
        skf = StratifiedKFold(folds, shuffle=True, random_state=SEED)
        splits = skf.split(x, y)
    else:
        splits = StratifiedGroupKFold(folds, shuffle=True, random_state=SEED).split(x, y, groups)
    res = {k: [] for k in ("rf", "xgb", "cnn", "fusion_equal")}
    for f, (tr, te) in enumerate(splits, 1):
        print(f"  fold {f}/{folds}")
        xtr, ytr, xte, yte = x[tr], y[tr], x[te], y[te]
        xa, xb, ya, yb = inner_split(xtr, ytr, None if groups is None else groups[tr])
        probs = {"rf": fit_rf(xtr, ytr).predict_proba(xte),
                 "xgb": fit_xgb(xtr, ytr).predict_proba(xte),
                 "cnn": cnn_proba_torch(fit_cnn(xa, ya, xb, yb), xte)}
        probs["fusion_equal"] = (probs["rf"] + probs["xgb"] + probs["cnn"]) / 3
        for k in res:
            res[k].append(metrics(yte, probs[k]))
    summary = {}
    for k, runs in res.items():
        summary[k] = {m: [round(float(np.mean([r[m] for r in runs])), 4),
                          round(float(np.std([r[m] for r in runs])), 4)]
                      for m in ("accuracy", "precision_macro", "recall_macro",
                                "f1_macro", "auc_ovr_macro")}
    return summary


def _splits(x, y, g, folds):
    if g is None:
        return StratifiedKFold(folds, shuffle=True, random_state=SEED).split(x, y)
    return StratifiedGroupKFold(folds, shuffle=True, random_state=SEED).split(x, y, g)


def ablation(df, active, dev_idx, folds=5, groups=None):
    mods = ["face", "voice", "thermal"]
    out = {}
    for r in range(0, len(mods) + 1):
        for combo in itertools.combinations(mods, r):
            cols = [c for c in GROUPS["demographics"] + sum((GROUPS[m] for m in combo), [])
                    if c in active]
            name = "demographics" + "".join(f"+{m}" for m in combo)
            x = df.loc[dev_idx, cols].values.astype(np.float32)
            y = df.loc[dev_idx, TARGET].values
            accs, f1s = [], []
            for tr, te in _splits(x, y, groups, folds):
                p = fit_xgb(x[tr], y[tr]).predict_proba(x[te])
                accs.append(accuracy_score(y[te], p.argmax(1)))
                f1s.append(f1_score(y[te], p.argmax(1), average="macro"))
            out[name] = {"n_features": len(cols),
                         "accuracy": [round(float(np.mean(accs)), 4), round(float(np.std(accs)), 4)],
                         "f1_macro": [round(float(np.mean(f1s)), 4), round(float(np.std(f1s)), 4)]}
            print(f"  {name:40s} acc={out[name]['accuracy'][0]:.3f}")
    # modality-only (no demographics) to isolate each sensor's own signal
    for m in mods:
        cols = [c for c in GROUPS[m] if c in active]
        if not cols:
            continue
        x = df.loc[dev_idx, cols].values.astype(np.float32)
        y = df.loc[dev_idx, TARGET].values
        accs = []
        for tr, te in _splits(x, y, groups, folds):
            accs.append(accuracy_score(y[te], fit_xgb(x[tr], y[tr]).predict(x[te])))
        out[f"{m}_only"] = {"n_features": len(cols),
                            "accuracy": [round(float(np.mean(accs)), 4), round(float(np.std(accs)), 4)]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/upgraded_full_dataset.csv")
    ap.add_argument("--out", default="model/model.pkl")
    ap.add_argument("--report", default="model/report/metrics.json")
    ap.add_argument("--group-col", default=None, help="subject id column for patient-level splits")
    ap.add_argument("--skip-cv", action="store_true")
    ap.add_argument("--skip-ablation", action="store_true")
    a = ap.parse_args()

    seed_everything()
    t0 = time.time()
    df, feature_columns, active, info = load_and_clean(a.data, a.group_col)
    print(f"Clean data: {info['rows_raw']} -> {info['rows_clean']} rows "
          f"({info['duplicates_removed']} duplicates removed), "
          f"{len(active)}/{len(feature_columns)} active features")
    print("Dropped constant columns:", info["constant_columns_dropped"])

    idx = np.arange(len(df))
    grp = df[a.group_col].values if a.group_col else None
    if grp is None:
        dev_idx, test_idx = train_test_split(idx, test_size=0.2, stratify=df[TARGET],
                                             random_state=SEED)
    else:
        sgkf = StratifiedGroupKFold(5, shuffle=True, random_state=SEED)
        dev_idx, test_idx = next(sgkf.split(idx, df[TARGET], grp))
        assert not set(grp[dev_idx]) & set(grp[test_idx])
    x_all = df[active].values.astype(np.float32)
    y_all = df[TARGET].values
    x_dev, y_dev = x_all[dev_idx], y_all[dev_idx]
    x_test, y_test = x_all[test_idx], y_all[test_idx]
    print(f"Dev {len(dev_idx)} / test {len(test_idx)} ({'subject-level' if grp is not None else 'row-level'}, seed {SEED})")

    report = {"data": info, "split": {"dev": len(dev_idx), "test": len(test_idx), "seed": SEED},
              "hyperparameters": {"rf": RF_PARAMS, "xgb": XGB_PARAMS, "cnn": CNN_PARAMS},
              "caveat": (("Splits are subject-level. " if grp is not None else
                         "Rows have no subject ID, so splits are row-level, not patient-level. ")
                        + "The training data is synthetic/simulated; results are not "
                        "clinical performance.")}

    if not a.skip_cv:
        print("5-fold CV on development set ...")
        report["cv_5fold_dev"] = cross_validate(
            x_dev, y_dev, groups=None if grp is None else grp[dev_idx])

    print("Training final models ...")
    x_tr, x_val, y_tr, y_val = inner_split(x_dev, y_dev, None if grp is None else grp[dev_idx])
    rf = fit_rf(x_tr, y_tr)
    xgb = fit_xgb(x_tr, y_tr)
    cnn = fit_cnn(x_tr, y_tr, x_val, y_val, verbose=True)
    val_probs = {"rf": rf.predict_proba(x_val), "xgb": xgb.predict_proba(x_val),
                 "cnn": cnn_proba_torch(cnn, x_val)}
    weights = tune_weights(y_val, val_probs)
    print("Fusion weights (tuned on validation log-loss):", weights)

    probs = {"rf": rf.predict_proba(x_test), "xgb": xgb.predict_proba(x_test),
             "cnn": cnn_proba_torch(cnn, x_test)}
    probs["fusion"] = fusion(probs, weights)
    report["test"] = {k: {**metrics(y_test, p), **bootstrap_ci(y_test, p)}
                      for k, p in probs.items()}
    report["fusion_weights"] = weights
    report["cnn_training"] = {"epochs_run": cnn["epochs"], "best_val_loss": round(cnn["best_val_loss"], 4)}
    report["mcnemar_p_fusion_vs"] = {k: mcnemar_p(y_test, probs["fusion"], probs[k])
                                     for k in ("rf", "xgb", "cnn")}
    for k, m in report["test"].items():
        print(f"  {k:7s} acc={m['accuracy']:.4f} f1={m['f1_macro']:.4f} auc={m['auc_ovr_macro']:.4f}")

    if not a.skip_ablation:
        print("Modality ablation (XGBoost, 5-fold CV on dev) ...")
        report["ablation_xgb_cv5_dev"] = ablation(df, active, dev_idx, groups=None if grp is None else grp[dev_idx])

    # ---- save the model pack ------------------------------------------------
    pack = {
        "feature_columns": feature_columns,
        "active_columns": active,
        "active_idx": [feature_columns.index(c) for c in active],
        "class_names": CLASS_NAMES,
        "rf_model": rf,
        "xgb_raw_json": bytes(xgb.get_booster().save_raw("json")),
        "cnn": export_cnn(cnn),
        "fusion_weights": weights,
        "metadata": {"trained": time.strftime("%Y-%m-%d %H:%M:%S"), "seed": SEED,
                     "data": os.path.basename(a.data), "rows": info["rows_clean"]},
    }
    # parity check: exported numpy CNN must match the torch model
    from model.ensemble import ThyroidEnsemble, cnn_predict_proba
    diff = np.abs(cnn_predict_proba(pack["cnn"], x_test) - probs["cnn"]).max()
    assert diff < 1e-4, f"numpy CNN export mismatch: {diff}"
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    joblib.dump(pack, a.out)
    ens = ThyroidEnsemble.load(a.out)
    full = np.zeros((len(x_test), len(feature_columns)), dtype=np.float32)
    full[:, pack["active_idx"]] = x_test
    assert np.allclose(ens.predict_all(full)["fusion"], probs["fusion"], atol=1e-4)
    print(f"Saved {a.out} (numpy CNN parity max diff {diff:.2e}; reload verified)")

    os.makedirs(os.path.dirname(a.report), exist_ok=True)
    with open(a.report, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Saved {a.report}  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
