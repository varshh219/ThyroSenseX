"""Generate a HARD *synthetic* ThyroSenseX-style dataset for stress-testing.

    python training/make_synthetic_hard.py --out data/synthetic_hard.csv

THIS IS SIMULATED DATA, NOT PATIENT DATA. Never report results on it as
clinical performance. Its purpose is to test the pipeline under conditions the
easy dataset hides: subject IDs with repeated sessions (patient-level splits),
several sites with different device calibration (external validation),
overlapping classes (subclinical cases), confounders (age, sex, weight,
ambient temperature), noisy symptom flags and label noise.

Effect directions follow textbook physiology (hypothyroid: lower temperature,
lower pitch, dry skin, weight gain; hyperthyroid: higher temperature, weight
loss, tremulous/higher voice); magnitudes are deliberately modest.
Classes: 0 Normal, 1 Hypothyroidism, 2 Hyperthyroidism.
"""

import argparse
import json
import os

import numpy as np
import pandas as pd

SITES = {  # name: (device temp offset C, mic gain dB, class prior N/Hypo/Hyper, mean age)
    "A": (0.0, 0.0, (0.55, 0.28, 0.17), 42),
    "B": (0.6, 3.0, (0.45, 0.35, 0.20), 48),
    "C": (-0.5, -4.0, (0.65, 0.20, 0.15), 38),
}


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


LEVELS = {  # label_noise, rater flip, noise multiplier, severity Beta(a, b)
    "hard": dict(label_noise=0.04, flip=0.06, noise=1.0, sev=(1.6, 2.4)),
    "medium": dict(label_noise=0.02, flip=0.03, noise=0.6, sev=(2.5, 1.8)),
    "easy": dict(label_noise=0.0, flip=0.0, noise=0.12, sev=(6.0, 1.0)),
}


def make(n_subjects, seed, level="hard"):
    lv = LEVELS[level]
    label_noise, flip_rate, nz = lv["label_noise"], lv["flip"], lv["noise"]
    rng = np.random.default_rng(seed)
    rows = []
    for sid in range(n_subjects):
        site = rng.choice(list(SITES), p=[0.45, 0.35, 0.20])
        t_off, gain_db, prior, mean_age = SITES[site]
        cls = rng.choice(3, p=prior)
        female = rng.random() < (0.80 if cls == 1 else 0.65 if cls == 2 else 0.5)
        age = float(np.clip(rng.normal(mean_age + (6 if cls == 1 else -4 if cls == 2 else 0), 14), 18, 85))
        bmi = float(np.clip(rng.normal(24.5 + (2.5 if cls == 1 else -2.2 if cls == 2 else 0), 4), 15, 45))
        height = rng.normal(1.60 if female else 1.74, 0.07)
        weight = bmi * height**2
        # disease severity: many subclinical / mild cases overlap with normal
        sev = 0.0 if cls == 0 else float(rng.beta(*lv["sev"]))
        sgn = {0: 0, 1: -1, 2: 1}[cls]
        # per-subject traits stay fixed across sessions
        base_flag = rng.normal(0, 0.6, 10)  # personal tendency for each flag
        pitch_base = rng.normal(205 if female else 120, (22 if female else 16) * nz) - 0.25 * (age - 40)
        thermal_base = rng.normal(34.2, 0.5) + 0.01 * (weight - 70) * -1
        for _ in range(int(rng.integers(1, 5))):  # 1-4 sessions
            ambient = rng.normal(24, 2.5 * nz)  # latent, NOT a feature
            sess_t = thermal_base + 0.12 * (ambient - 24) + t_off + sgn * sev * 0.9 + rng.normal(0, 0.45 * nz)
            # face flags (rater noise + base rates + disease effect)
            eff = np.zeros(10)
            if cls == 1:
                eff = sev * np.array([0.8, 1.6, 1.8, 2.0, 1.0, 1.6, 1.8, 1.4, 1.8, 1.4])
            elif cls == 2:
                eff = sev * np.array([0.6, 0.4, 0.8, -0.8, 1.8, 0.2, 1.2, 0.4, -1.6, 0.2])
            base = np.array([-0.5, -1.4, -0.9, -1.0, -2.2, -1.9, -0.6, -1.5, -1.0, -0.8])
            p = sigmoid(base + eff + base_flag * 0.6 + 0.01 * (age - 40))
            flags = (rng.random(10) < p).astype(int)
            flip = rng.random(10) < flip_rate  # rater / extractor error
            flags = np.where(flip, 1 - flags, flags)
            # voice: strong confounding by sex/age, weak class effect, big session noise
            snr = rng.normal(0, 1)
            pm = pitch_base + sgn * sev * (-14 if sgn < 0 else 9) + rng.normal(0, 9 * nz)
            ps = abs(rng.normal(22 + (8 * sev if cls == 2 else 0), 7))
            pmin = pm - abs(rng.normal(35, 10))
            pmax = pm + abs(rng.normal(45, 14)) + (15 * sev if cls == 2 else 0)
            emean = rng.normal(0.05 + 0.002 * gain_db, 0.015) * (1 - 0.15 * sev * (cls == 1))
            estd = abs(rng.normal(0.03, 0.01))
            zcr = abs(rng.normal(0.09, 0.025)) + 0.01 * snr
            mf = [rng.normal(m, s) + sgn * sev * d + 0.4 * snr * (i == 0)
                  for i, (m, s, d) in enumerate([(-250, 25, 6), (95, 14, -4), (-5, 9, 2)])]
            # thermal field: shared session temperature + region offsets + noise
            tm = sess_t
            reg = lambda off, sd: tm + off + rng.normal(0, sd)
            fore = reg(0.5, 0.25)
            mid = reg(0.0, 0.25)
            neck = reg(-0.3 + sgn * sev * 0.35, 0.3)  # thyroid region carries extra signal
            left, right = reg(0.0, 0.2), reg(0.0, 0.2)
            asym = abs(left - right) + (0.25 * sev if cls != 0 and rng.random() < 0.5 else 0)
            tmax = max(fore, mid, neck, left, right) + abs(rng.normal(0.8, 0.3))
            tmin = min(fore, mid, neck, left, right) - abs(rng.normal(1.6, 0.5))
            lab = cls
            if rng.random() < label_noise:  # diagnostic ambiguity: neighbouring-class label
                lab = int(rng.choice([c for c in range(3) if c != cls]))
            rows.append({
                "subject_id": sid, "site": site,
                "age": round(age), "gender": int(female), "weight": round(weight + rng.normal(0, 0.8)),
                "has_dark_circle": flags[0], "facial_swelling": flags[1], "puffy_eyes": flags[2],
                "dry_skin_visible": flags[3], "goiter_visible": flags[4],
                "coarse_facial_features": flags[5], "tired_expression": flags[6],
                "hair_loss": flags[7], "weight_gain": flags[8], "pale_skin": flags[9],
                "pitch_mean": pm, "pitch_std": ps, "pitch_min": pmin, "pitch_max": pmax,
                "energy_mean": emean, "energy_std": estd, "zcr_mean": zcr,
                "mfcc_mean_1": mf[0], "mfcc_mean_2": mf[1], "mfcc_mean_3": mf[2],
                "thermal_mean": tm, "thermal_std": abs(rng.normal(1.1, 0.3)), "thermal_max": tmax,
                "thermal_min": tmin, "thermal_range": tmax - tmin, "thermal_forehead": fore,
                "thermal_mid": mid, "thermal_chin_neck": neck, "thermal_left_mean": left,
                "thermal_right_mean": right, "thermal_lr_asymmetry": asym,
                "thermal_centre": tm + rng.normal(0, 0.2),
                "thermal_hot_ratio": float(np.clip(rng.normal(0.18 + 0.05 * sgn * sev, 0.06), 0, 1)),
                "thermal_grad_v": rng.normal(0.4 - sgn * sev * 0.1, 0.15),
                "thermal_grad_h": rng.normal(0.1, 0.12),
                "classification": lab,
            })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/synthetic_hard.csv")
    ap.add_argument("--subjects", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--level", choices=list(LEVELS), default="hard")
    a = ap.parse_args()
    df = make(a.subjects, a.seed, a.level)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    df.round(4).to_csv(a.out, index=False)
    meta = {"SYNTHETIC": True, "note": "Simulated data for pipeline stress-testing; not patient data.",
            "level": a.level, "level_params": LEVELS[a.level], "subjects": int(df.subject_id.nunique()), "rows": len(df), "seed": a.seed,
            "class_counts": {int(k): int(v) for k, v in df.classification.value_counts().sort_index().items()},
            "sites": df.site.value_counts().to_dict()}
    with open(a.out.replace(".csv", ".meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
