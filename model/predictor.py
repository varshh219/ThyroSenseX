import pickle
import numpy as np
import os
import pandas as pd

class ThyroidPredictor:
    """
    Loads the trained model and runs predictions.
    Used by the GUI processing screen.
    """

    CLASS_NAMES = {
        0: "Normal",
        1: "Hypothyroidism",
        2: "Hyperthyroidism"
    }

    def __init__(self, model_dir="model"):
        self.model   = None
        self.scaler  = None
        self.columns = None
        self._load(model_dir)

    def _load(self, model_dir):
        model_path   = os.path.join(model_dir, "thyroid_model.pkl")
        scaler_path  = os.path.join(model_dir, "scaler.pkl")
        columns_path = os.path.join(model_dir, "feature_columns.pkl")

        with open(model_path,   "rb") as f: self.model   = pickle.load(f)
        with open(scaler_path,  "rb") as f: self.scaler  = pickle.load(f)
        with open(columns_path, "rb") as f: self.columns = pickle.load(f)

        print(f"✓ Model loaded — {len(self.columns)} features expected")

    def predict(self, feature_dict: dict) -> dict:
        """
        Takes a dict of features and returns prediction.

        Args:
            feature_dict: dict with keys matching training columns

        Returns:
            {
              'prediction'   : 'Normal' / 'Hypothyroidism' / 'Hyperthyroidism'
              'class_id'     : 0 / 1 / 2
              'confidence'   : float (0-100)
              'probabilities': {'Normal': x, 'Hypothyroidism': y, 'Hyperthyroidism': z}
            }
        """

        # Build feature vector in correct column order
        row = []
        for col in self.columns:
            val = feature_dict.get(col, 0.0)
            row.append(val)

        X = np.array([row])

        # Scale

        X_df     = pd.DataFrame(X, columns=self.columns)
        X_scaled = self.scaler.transform(X_df)

        # Predict
        class_id     = int(self.model.predict(X_scaled)[0])
        probabilities = self.model.predict_proba(X_scaled)[0]

        prediction  = self.CLASS_NAMES[class_id]
        confidence  = float(probabilities[class_id]) * 100

        return {
            "prediction": prediction,
            "class_id":   class_id,
            "confidence": round(confidence, 2),
            "probabilities": {
                "Normal":          round(float(probabilities[0]) * 100, 2),
                "Hypothyroidism":  round(float(probabilities[1]) * 100, 2),
                "Hyperthyroidism": round(float(probabilities[2]) * 100, 2),
            }
        }


# Quick test
if __name__ == "__main__":
    predictor = ThyroidPredictor()

    # Sample feature dict — simulating a patient
    sample = {
        "age":                          45,
        "gender":                        1,
        "weight":                       70,
        "has_dark_circle":               1,
        "facial_swelling":               1,
        "puffy_eyes":                    1,
        "dry_skin_visible":              1,
        "goiter_visible":                0,
        "Coarse facial features":        1,
        "Tired or dull facial expression": 1,
        "Thinning hair or hair loss":    1,
        "Weight gain":                   1,
        "Pale skin":                     1,
        "Pitch(hz)":                   148.0,
        "Frequency":                   106.0,
        "Jitter":                      0.005,
        "Shimmer":                     0.024,
        "hnr":                         12.97,
        "Mean Intensity":              62.0,
        "Max Intensity":               87.0,
        "Min Intensity":               53.0,
        "has_thyroid":                   1,
    }

    result = predictor.predict(sample)

    print("\n═══ Prediction Result ═══")
    print(f"Prediction   : {result['prediction']}")
    print(f"Confidence   : {result['confidence']}%")
    print(f"Probabilities: {result['probabilities']}")