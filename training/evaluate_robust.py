"""Patient-level and external-site evaluation on a dataset with subject_id/site.

    python training/evaluate_robust.py --data data/synthetic_hard.csv

Reports (1) row-level CV (optimistic, for comparison), (2) patient-level CV
where no subject appears in both train and test, and (3) leave-one-site-out
external validation. Does not write model files.
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import (GroupShuffleSplit, StratifiedGroupKFold,
                                     StratifiedKFold)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_pipeline import (GROUPS, SEED, TARGET, cnn_proba_torch, fit_cnn,  # noqa: E402
                            fit_rf, fit_xgb, metrics, seed_everything)

FEATURES = [c for g in GROUPS.values() for c in g]


def run(x, y, groups, tr, te):
    # group-aware inner split so CNN early stopping never sees test subjects
    gss = GroupShuffleSplit(1, test_size=0.15, random_state=SEED)
    a, b = next(gss.split(x[tr], y[tr], groups[tr]))
    xa, ya, xb, yb = x[tr][a], y[tr][a], x[tr][b], y[tr][b]
    p = {"rf": fit_rf(x[tr], y[tr]).predict_proba(x[te]),
         "xgb": fit_xgb(x[tr], y[tr]).predict_proba(x[te]),
         "cnn": cnn_proba_torch(fit_cnn(xa, ya, xb, yb), x[te])}
    p["fusion_equal"] = (p["rf"] + p["xgb"] + p["cnn"]) / 3
    return p


def summarise(results):
    return {k: {"accuracy": [round(float(np.mean([m[k]["accuracy"] for m in results])), 4),
                             round(float(np.std([m[k]["accuracy"] for m in results])), 4)],
                "f1_macro": [round(float(np.mean([m[k]["f1_macro"] for m in results])), 4),
                             round(float(np.std([m[k]["f1_macro"] for m in results])), 4)],
                "auc": round(float(np.mean([m[k]["auc_ovr_macro"] for m in results])), 4)}
            for k in results[0]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/synthetic_hard.csv")
    ap.add_argument("--out", default="model/report/robust_eval.json")
    a = ap.parse_args()
    seed_everything()
    df = pd.read_csv(a.data)
    active = [c for c in FEATURES if df[c].nunique() > 1]
    x = df[active].values.astype(np.float32)
    y = df[TARGET].values
    g = df["subject_id"].values
    print(f"{len(df)} rows, {df.subject_id.nunique()} subjects, {len(active)} features, "
          f"sites {df.site.value_counts().to_dict()}")
    out = {"data": a.data, "rows": len(df), "subjects": int(df.subject_id.nunique())}

    print("Row-level CV (subjects leak across folds) ...")
    res = [{k: metrics(y[te], v) for k, v in run(x, y, g, tr, te).items()}
           for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED).split(x, y)]
    out["row_level_cv5"] = summarise(res)

    print("Patient-level CV (grouped by subject) ...")
    res = [{k: metrics(y[te], v) for k, v in run(x, y, g, tr, te).items()}
           for tr, te in StratifiedGroupKFold(5, shuffle=True, random_state=SEED).split(x, y, g)]
    out["patient_level_cv5"] = summarise(res)

    print("Leave-one-site-out external validation ...")
    out["leave_one_site_out"] = {}
    for s in sorted(df.site.unique()):
        te = np.where(df.site.values == s)[0]
        tr = np.where(df.site.values != s)[0]
        p = run(x, y, g, tr, te)
        out["leave_one_site_out"][s] = {
            "n_test": len(te),
            **{k: {"accuracy": round(accuracy_score(y[te], v.argmax(1)), 4),
                   "f1_macro": round(f1_score(y[te], v.argmax(1), average="macro"), 4)}
               for k, v in p.items()}}

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=2)
    for sect in ("row_level_cv5", "patient_level_cv5"):
        print(sect)
        for k, v in out[sect].items():
            print(f"  {k:13s} acc {v['accuracy'][0]:.3f}±{v['accuracy'][1]:.3f}  f1 {v['f1_macro'][0]:.3f}  auc {v['auc']:.3f}")
    print("leave_one_site_out")
    for s, v in out["leave_one_site_out"].items():
        print(f"  site {s} (n={v['n_test']}): " + "  ".join(f"{k} {v[k]['accuracy']:.3f}" for k in ("rf", "xgb", "cnn", "fusion_equal")))


if __name__ == "__main__":
    main()
