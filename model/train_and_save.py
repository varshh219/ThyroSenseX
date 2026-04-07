import pandas as pd
import numpy as np
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing   import StandardScaler, LabelEncoder
from sklearn.ensemble        import RandomForestClassifier
from sklearn.metrics         import accuracy_score, classification_report


def train_and_save(csv_path, model_dir="model"):
    print("═══ ThyroSenseX Model Training ═══\n")

    # ── Load dataset ───────────────────────────────────
    print("Loading dataset...")
    data = pd.read_csv(csv_path)
    print(f"Dataset shape: {data.shape}")

    # ── Encode gender if string ────────────────────────
    if data['gender'].dtype == object:
        le = LabelEncoder()
        data['gender'] = le.fit_transform(data['gender'])

    # ── Features and target ────────────────────────────
    X = data.drop('Classification', axis=1)
    y = data['Classification']

    print(f"Features : {list(X.columns)}")
    print(f"Classes  : {y.unique()}\n")

    # ── Train / test split ─────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ── Scale features ─────────────────────────────────
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    # ── Train Random Forest ────────────────────────────
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=200, random_state=42)
    rf.fit(X_train_scaled, y_train)

    y_pred = rf.predict(X_test_scaled)
    acc    = accuracy_score(y_test, y_pred)
    print(f"Accuracy : {acc * 100:.2f}%\n")
    print(classification_report(
        y_test, y_pred,
        target_names=["Normal", "Hypothyroid", "Hyperthyroid"]
    ))

    # ── Save model and scaler ──────────────────────────
    os.makedirs(model_dir, exist_ok=True)

    model_path   = os.path.join(model_dir, "thyroid_model.pkl")
    scaler_path  = os.path.join(model_dir, "scaler.pkl")
    columns_path = os.path.join(model_dir, "feature_columns.pkl")

    with open(model_path,   "wb") as f: pickle.dump(rf,              f)
    with open(scaler_path,  "wb") as f: pickle.dump(scaler,          f)
    with open(columns_path, "wb") as f: pickle.dump(list(X.columns), f)

    print(f"✓ Model   saved → {model_path}")
    print(f"✓ Scaler  saved → {scaler_path}")
    print(f"✓ Columns saved → {columns_path}")

    return acc


if __name__ == "__main__":
    CSV_PATH = "major.csv"
    train_and_save(CSV_PATH)