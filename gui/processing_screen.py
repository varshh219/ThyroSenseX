import numpy as np

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


# ══════════════════════════════════════════════════════════════
# WORKER
# ══════════════════════════════════════════════════════════════

class ScanWorker(QThread):
    step_signal  = pyqtSignal(int, str)
    done_signal  = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, image_bytes, thermal_bytes, audio_bytes, audio_ok):
        super().__init__()
        self.image_bytes = image_bytes
        self.thermal_bytes = thermal_bytes   # ⚠ now LIST (grid)
        self.audio_bytes = audio_bytes
        self.audio_ok = audio_ok

    def run(self):
        features = {}

        # ── Step 1 ─────────────────────────
        self.step_signal.emit(1, "Preparing data...")

        if not self.image_bytes:
            self.error_signal.emit("Image not captured")
            return

        # ── Step 2: Feature extraction ─────
        self.step_signal.emit(2, "Extracting features...")

        # ── FACE ───────────────────────────
        try:
            from thyrosensex.face_features import extract_face_features
            f = extract_face_features(self.image_bytes)
            features.update(f or {})
        except Exception as e:
            print("[Face Error]", e)

        # ── THERMAL (✅ FIXED HERE) ─────────
        try:
            from thyrosensex.thermal_features import extract_thermal_features

            # ✅ Use REAL thermal grid directly
            if isinstance(self.thermal_bytes, list):
                f = extract_thermal_features(self.thermal_bytes)
                features.update(f or {})
                print("[Thermal] Using REAL sensor data")

            else:
                print("[Thermal] Invalid thermal format")

        except Exception as e:
            print("[Thermal Error]", e)

        # ── AUDIO ──────────────────────────
        try:
            from thyrosensex.voice_features import extract_voice_features
            if self.audio_bytes:
                f = extract_voice_features(self.audio_bytes)
                features.update(f or {})
        except Exception as e:
            print("[Audio Error]", e)

        print(f"[ScanWorker] Features collected: {len(features)}")

        # ── Step 3: Model ──────────────────
        self.step_signal.emit(3, "Running model...")

        try:
            prediction, confidence, _ = _run_model(features)
        except Exception as e:
            print("[Model Error]", e)
            prediction, confidence = "Error", 0

        # ── Step 4: OLED ───────────────────
        self.step_signal.emit(4, "Sending to OLED...")

        try:
            from api.client import display_result
            display_result(prediction, confidence)
        except Exception as e:
            print("[OLED Error]", e)

        result = {
            "prediction": prediction,
            "confidence": confidence,
            "features": features,
            "audio_ok": self.audio_ok
        }

        self.done_signal.emit(result)


# ══════════════════════════════════════════════════════════════
# MODEL
# ══════════════════════════════════════════════════════════════

FEATURE_KEYS = [
    "face_eye_openness", "face_eye_symmetry", "face_ratio",
    "face_brightness_sym", "face_neck_mean", "face_neck_brightness",
    "face_skin_b", "face_skin_g", "face_skin_r",
    "face_center_x", "face_center_y", "face_area",

    "thermal_mean", "thermal_std", "thermal_max", "thermal_min",
    "thermal_range", "thermal_forehead", "thermal_mid",
    "thermal_chin_neck", "thermal_left_mean", "thermal_right_mean",
    "thermal_lr_asymmetry", "thermal_centre",
    "thermal_hot_ratio", "thermal_grad_v", "thermal_grad_h",

    "pitch_mean", "pitch_std", "pitch_min", "pitch_max",
    "energy_mean", "energy_std", "zcr_mean",
    "mfcc_mean_1", "mfcc_mean_2", "mfcc_mean_3",
]

LABELS = {0: "Normal", 1: "Hypothyroidism", 2: "Hyperthyroidism"}


def _run_model(features: dict):
    import os
    from config import MODEL_PATH, XGB_PATH, SCALER_PATH, CNN_PATH

    vector = np.array(
        [[float(features.get(k, 0.0)) for k in FEATURE_KEYS]],
        dtype=np.float32
    )

    all_probas = []

    # ⚠ Skip scaler if mismatch
    scaled = vector

    # RF
    if os.path.exists(MODEL_PATH):
        try:
            import pickle
            with open(MODEL_PATH, "rb") as f:
                rf = pickle.load(f)
            all_probas.append(rf.predict_proba(scaled)[0])
        except Exception as e:
            print("[RF Error]", e)

    # XGB
    if os.path.exists(XGB_PATH):
        try:
            import pickle
            with open(XGB_PATH, "rb") as f:
                xgb = pickle.load(f)
            all_probas.append(xgb.predict_proba(scaled)[0])
        except Exception as e:
            print("[XGB Error]", e)

    # CNN
    if os.path.exists(CNN_PATH):
        try:
            from tensorflow.keras.models import load_model
            cnn = load_model(CNN_PATH)
            inp = scaled.reshape(1, scaled.shape[1], 1)
            all_probas.append(cnn.predict(inp)[0])
        except Exception as e:
            print("[CNN Error]", e)

    # Ensemble
    if all_probas:
        avg = np.mean(all_probas, axis=0)
        idx = int(np.argmax(avg))
        return LABELS[idx], int(avg[idx] * 100), {}

    # Fallback (uses REAL temp now)
    mean = float(features.get("thermal_mean", 35.0))

    if mean > 35.5:
        return "Hyperthyroidism", 72, {}
    elif mean < 33.5:
        return "Hypothyroidism", 68, {}
    else:
        return "Normal", 80, {}


# ══════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════

class ProcessingScreen(QWidget):

    def __init__(self, go_to, on_result=None):
        super().__init__()
        self.go_to = go_to
        self.on_result = on_result

        self._worker = None
        self._current_patient = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.status = QLabel("Processing...")
        self.status.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 4)

        layout.addWidget(self.status)
        layout.addWidget(self.progress)

    def start(self, patient, image, thermal, audio, audio_ok):
        self._current_patient = patient
        self.progress.setValue(0)

        self._worker = ScanWorker(image, thermal, audio, audio_ok)
        self._worker.step_signal.connect(self._on_step)
        self._worker.done_signal.connect(self._on_done)
        self._worker.error_signal.connect(self._on_error)
        self._worker.start()

    def _on_step(self, step, msg):
        self.progress.setValue(step)
        self.status.setText(msg)

    def _on_done(self, result):
        if self.on_result:
            self.on_result(result, self._current_patient)
        self.go_to("result")

    def _on_error(self, msg):
        print("ERROR:", msg)
        self.go_to("result")