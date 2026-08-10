import numpy as np
import joblib
import os

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QProgressBar
)

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal


# ============================================================
# LOAD MODEL
# ============================================================

MODEL_PATH = os.path.join("model", "model.pkl")

model_pack = joblib.load(MODEL_PATH)

rf_model = model_pack["rf_model"]
xgb_model = model_pack["xgb_model"]
feature_columns = model_pack["feature_columns"]
class_names = model_pack["class_names"]

print("[MODEL] Loaded successfully")
print("[MODEL] Features:", len(feature_columns))
print("[MODEL] Classes:", class_names)


# ============================================================
# WORKER
# ============================================================

class ScanWorker(QThread):

    step_signal = pyqtSignal(int, str)
    done_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(
        self,
        patient,
        image_bytes,
        thermal_bytes,
        audio_bytes,
        audio_ok
    ):
        super().__init__()

        self.patient = patient
        self.image_bytes = image_bytes
        self.thermal_bytes = thermal_bytes
        self.audio_bytes = audio_bytes
        self.audio_ok = audio_ok

    def run(self):

        features = {}

        # ----------------------------------------------------
        # STEP 1 - PREPARE DATA
        # ----------------------------------------------------

        self.step_signal.emit(
            1,
            "Preparing data..."
        )

        if not self.image_bytes:

            self.error_signal.emit(
                "Image not captured"
            )

            return

        # ----------------------------------------------------
        # STEP 2 - FEATURE EXTRACTION
        # ----------------------------------------------------

        self.step_signal.emit(
            2,
            "Extracting features..."
        )

        # FACE
        try:

            from thyrosensex.face_features import (
                extract_face_features
            )

            face_features = extract_face_features(
                self.image_bytes
            )

            if face_features:

                features.update(
                    face_features
                )

            print(
                "[FACE] Features:",
                face_features
            )

        except Exception as e:

            print(
                "[Face Error]",
                e
            )

        # THERMAL
        try:

            from thyrosensex.thermal_features import (
                extract_thermal_features
            )

            if isinstance(
                self.thermal_bytes,
                list
            ):

                thermal_features = (
                    extract_thermal_features(
                        self.thermal_bytes
                    )
                )

                if thermal_features:

                    features.update(
                        thermal_features
                    )

                print(
                    "[THERMAL] Features:",
                    thermal_features
                )

        except Exception as e:

            print(
                "[Thermal Error]",
                e
            )

        # AUDIO
        try:

            from thyrosensex.voice_features import (
                extract_voice_features
            )

            if self.audio_bytes:

                audio_features = (
                    extract_voice_features(
                        self.audio_bytes
                    )
                )

                if audio_features:

                    features.update(
                        audio_features
                    )

                print(
                    "[AUDIO] Features:",
                    audio_features
                )

        except Exception as e:

            print(
                "[Audio Error]",
                e
            )

        # ----------------------------------------------------
        # PATIENT FEATURES
        # ----------------------------------------------------

        try:

            features["age"] = float(
                self.patient.get(
                    "age",
                    0
                )
            )

            features["weight"] = float(
                self.patient.get(
                    "weight",
                    0
                )
            )

            gender = self.patient.get(
                "gender",
                "Female"
            )

            features["gender"] = (
                1
                if str(gender).lower() == "male"
                else 0
            )

        except Exception as e:

            print(
                "[Patient Feature Error]",
                e
            )

        print(
            "[ScanWorker] Features collected:",
            len(features)
        )

        # ----------------------------------------------------
        # STEP 3 - RUN ACTUAL MODEL
        # ----------------------------------------------------

        self.step_signal.emit(
            3,
            "Running AI model..."
        )

        try:

            prediction, confidence = _run_model(
                features
            )

        except Exception as e:

            print(
                "[Model Error]",
                e
            )

            prediction = "Error"
            confidence = 0

        # ----------------------------------------------------
        # STEP 4 - SEND RESULT TO OLED
        # ----------------------------------------------------

        self.step_signal.emit(
            4,
            "Sending result to OLED..."
        )

        try:

            from api.client import display_result

            display_result(
                prediction,
                confidence
            )

        except Exception as e:

            print(
                "[OLED Error]",
                e
            )

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        result = {

            "prediction": prediction,

            "confidence": confidence,

            "features": features,

            "patient": self.patient,

            "image": (
                "Captured"
                if self.image_bytes
                else "—"
            ),

            "audio": (
                "Recorded"
                if self.audio_ok
                else "Not captured"
            )
        }

        self.done_signal.emit(
            result
        )


# ============================================================
# MODEL PREDICTION
# ============================================================

def _run_model(features: dict):

    print("\n================================")
    print("        MODEL PREDICTION")
    print("================================")

    # --------------------------------------------------------
    # DISPLAY FEATURES
    # --------------------------------------------------------

    print("\n=== INPUT FEATURES ===")

    for column in feature_columns:

        print(
            f"{column}:",
            features.get(
                column,
                0.0
            )
        )

    # --------------------------------------------------------
    # CREATE MODEL VECTOR
    # --------------------------------------------------------

    vector = np.array(
        [
            [
                float(
                    features.get(
                        column,
                        0.0
                    )
                )
                for column in feature_columns
            ]
        ],
        dtype=np.float32
    )

    print(
        "\n[MODEL] Feature vector shape:",
        vector.shape
    )

    # --------------------------------------------------------
    # RANDOM FOREST
    # --------------------------------------------------------

    rf_probs = rf_model.predict_proba(
        vector
    )[0]

    rf_prediction_index = np.argmax(
        rf_probs
    )

    rf_confidence = (
        float(
            rf_probs[
                rf_prediction_index
            ]
        ) * 100
    )

    # --------------------------------------------------------
    # XGBOOST
    # --------------------------------------------------------

    xgb_probs = xgb_model.predict_proba(
        vector
    )[0]

    xgb_prediction_index = np.argmax(
        xgb_probs
    )

    xgb_confidence = (
        float(
            xgb_probs[
                xgb_prediction_index
            ]
        ) * 100
    )

    # --------------------------------------------------------
    # PRINT MODEL OUTPUT
    # --------------------------------------------------------

    print("\n=== RANDOM FOREST ===")

    print(
        "Probabilities:",
        rf_probs
    )

    print(
        "Predicted class index:",
        rf_prediction_index
    )

    print(
        "Confidence:",
        rf_confidence
    )

    print("\n=== XGBOOST ===")

    print(
        "Probabilities:",
        xgb_probs
    )

    print(
        "Predicted class index:",
        xgb_prediction_index
    )

    print(
        "Confidence:",
        xgb_confidence
    )

    # --------------------------------------------------------
    # USE XGBOOST AS FINAL MULTI-CLASS MODEL
    # --------------------------------------------------------

    if xgb_prediction_index >= len(
        class_names
    ):

        raise ValueError(
            "Model predicted an invalid class index."
        )

    prediction = class_names[
        xgb_prediction_index
    ]

    confidence = round(
        xgb_confidence,
        2
    )

    # --------------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------------

    print("\n================================")
    print("FINAL AI PREDICTION")
    print("================================")

    print(
        "Prediction:",
        prediction
    )

    print(
        "Confidence:",
        confidence,
        "%"
    )

    print("================================\n")

    return prediction, confidence


# ============================================================
# PROCESSING SCREEN
# ============================================================

class ProcessingScreen(QWidget):

    def __init__(
        self,
        go_to,
        on_result=None
    ):

        super().__init__()

        self.go_to = go_to

        self.on_result = on_result

        self._worker = None

        self._current_patient = None

        self._build_ui()

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def _build_ui(self):

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            60,
            60,
            60,
            60
        )

        layout.setSpacing(
            25
        )

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        logo = QLabel()

        logo.setPixmap(
            QPixmap(
                "gui/resources/logos/thyroid_logo.png"
            ).scaled(
                90,
                90,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        logo.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            logo
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = QLabel(
            "AI Analysis in Progress"
        )

        title.setObjectName(
            "screen_title"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status = QLabel(
            "Preparing scan..."
        )

        self.status.setAlignment(
            Qt.AlignCenter
        )

        self.status.setStyleSheet(
            """
            font-size:18px;
            font-weight:bold;
            color:#2563eb;
            """
        )

        layout.addWidget(
            self.status
        )

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        self.progress = QProgressBar()

        self.progress.setRange(
            0,
            4
        )

        self.progress.setMinimumHeight(
            25
        )

        layout.addWidget(
            self.progress
        )

        # ----------------------------------------------------
        # INFORMATION
        # ----------------------------------------------------

        info = QLabel(
            "Please wait while ThyroSenseX processes\n"
            "facial, thermal and voice biomarkers."
        )

        info.setAlignment(
            Qt.AlignCenter
        )

        info.setStyleSheet(
            """
            color:#8b949e;
            font-size:12px;
            """
        )

        layout.addWidget(
            info
        )

        layout.addStretch()

    # --------------------------------------------------------
    # START SCAN
    # --------------------------------------------------------

    def start(
        self,
        patient,
        image,
        thermal,
        audio,
        audio_ok
    ):

        self._current_patient = patient

        self.progress.setValue(
            0
        )

        self.status.setText(
            "Preparing scan..."
        )

        self._worker = ScanWorker(
            patient,
            image,
            thermal,
            audio,
            audio_ok
        )

        self._worker.step_signal.connect(
            self._on_step
        )

        self._worker.done_signal.connect(
            self._on_done
        )

        self._worker.error_signal.connect(
            self._on_error
        )

        self._worker.start()

    # --------------------------------------------------------
    # STEP UPDATE
    # --------------------------------------------------------

    def _on_step(
        self,
        step,
        msg
    ):

        self.progress.setValue(
            step
        )

        self.status.setText(
            msg
        )

    # --------------------------------------------------------
    # DONE
    # --------------------------------------------------------

    def _on_done(
        self,
        result
    ):

        self.status.setText(
            "Analysis Complete"
        )

        if self.on_result:

            self.on_result(
                result,
                self._current_patient
            )

        self.go_to(
            "result"
        )

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    def _on_error(
        self,
        msg
    ):

        print(
            "ERROR:",
            msg
        )

        self.status.setText(
            "Analysis Failed"
        )

        self.go_to(
            "result"
        )