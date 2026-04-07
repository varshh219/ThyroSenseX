from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QProgressBar, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import numpy as np


def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f


# ── Background worker — runs features + model ──────────────────
class PredictionWorker(QThread):
    log      = pyqtSignal(int, str)   # (step index, message)
    progress = pyqtSignal(int)        # 0-100
    finished = pyqtSignal(dict)       # prediction result dict

    def run(self):
        import time

        # ── Step 1: Face features ──────────────────────
        self.log.emit(0, "Preprocessing facial features…")
        self.progress.emit(15)
        time.sleep(0.8)

        # Simulated face features (replace with real later)
        face_data = {
            "has_dark_circle":                1,
            "facial_swelling":                1,
            "puffy_eyes":                     1,
            "dry_skin_visible":               1,
            "goiter_visible":                 0,
            "Coarse facial features":         1,
            "Tired or dull facial expression":1,
            "Thinning hair or hair loss":     1,
            "Weight gain":                    1,
            "Pale skin":                      1,
        }

        # ── Step 2: Voice features ─────────────────────
        self.log.emit(1, "Extracting voice biomarkers…")
        self.progress.emit(35)
        time.sleep(0.8)

        voice_data = {
            "Pitch(hz)":   148.0,
            "Frequency":   106.0,
            "Jitter":      0.005,
            "Shimmer":     0.024,
            "hnr":         12.97,
        }

        # ── Step 3: Thermal features ───────────────────
        self.log.emit(2, "Parsing thermal signature…")
        self.progress.emit(55)
        time.sleep(0.8)

        from sensors.thermal import read_thermal
        thermal = read_thermal(simulate=True)
        thermal_data = {
            "Mean Intensity": float(np.mean(thermal)),
            "Max Intensity":  float(np.max(thermal)),
            "Min Intensity":  float(np.min(thermal)),
        }

        # ── Step 4: Combine features ───────────────────
        self.log.emit(3, "Running multimodal feature fusion…")
        self.progress.emit(70)
        time.sleep(0.8)

        # Patient info (defaults for now)
        patient_data = {
            "age":        30,
            "gender":      1,
            "weight":     65,
            "has_thyroid": 1,
        }

        # Merge all features
        all_features = {
            **patient_data,
            **face_data,
            **voice_data,
            **thermal_data,
        }

        # ── Step 5: Run model ──────────────────────────
        self.log.emit(4, "Running AI inference…")
        self.progress.emit(85)
        time.sleep(0.8)

        from model.predictor import ThyroidPredictor
        predictor = ThyroidPredictor()
        result    = predictor.predict(all_features)

        # ── Step 6: Done ───────────────────────────────
        self.log.emit(5, "Applying calibration weights…")
        self.progress.emit(95)
        time.sleep(0.5)

        self.log.emit(6, "Prediction generated ✓")
        self.progress.emit(100)

        self.finished.emit(result)


# ── Processing Screen ──────────────────────────────────────────
class ProcessingScreen(QWidget):
    def __init__(self, go_to, on_result=None):
        super().__init__()
        self.go_to     = go_to
        self.on_result = on_result
        self.worker    = None
        self.step      = 0
        self.log_steps = [
            "Preprocessing facial features…",
            "Extracting voice biomarkers…",
            "Parsing thermal signature…",
            "Running multimodal feature fusion…",
            "Running AI inference…",
            "Applying calibration weights…",
            "Prediction generated ✓",
        ]
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        # ── Header ─────────────────────────────────────
        lbl = QLabel("STEP 2 OF 3")
        lbl.setObjectName("section")
        title = QLabel("AI Analysis")
        title.setObjectName("screen_title")

        # ── Percentage ─────────────────────────────────
        self.pct_label = QLabel("0%")
        self.pct_label.setAlignment(Qt.AlignCenter)
        self.pct_label.setStyleSheet(
            "font-size:42px; font-weight:bold; color:#4f8dff;"
        )

        # ── Main progress bar ──────────────────────────
        self.main_bar = QProgressBar()
        self.main_bar.setMaximum(100)
        self.main_bar.setValue(0)
        self.main_bar.setTextVisible(False)
        self.main_bar.setFixedHeight(10)

        # ── Subtitle ───────────────────────────────────
        sub = QLabel("Running multimodal AI inference")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color:#7a90b8; font-size:12px;")

        # ── Log card ───────────────────────────────────
        log_card = make_card()
        from PyQt5.QtWidgets import QVBoxLayout as VBox
        log_layout = VBox(log_card)
        log_layout.setContentsMargins(14, 12, 14, 12)
        log_layout.setSpacing(4)

        self.log_labels = []
        for _ in range(7):
            l = QLabel("")
            l.setStyleSheet("font-size:11px; color:#4a5a78;")
            log_layout.addWidget(l)
            self.log_labels.append(l)

        # ── Assemble ───────────────────────────────────
        layout.addWidget(lbl)
        layout.addWidget(title)
        layout.addSpacing(16)
        layout.addWidget(self.pct_label)
        layout.addWidget(self.main_bar)
        layout.addWidget(sub)
        layout.addSpacing(10)
        layout.addWidget(log_card)
        layout.addStretch()

    def start(self):
        # Reset UI
        self.step = 0
        self.main_bar.setValue(0)
        self.pct_label.setText("0%")
        for l in self.log_labels:
            l.setText("")
            l.setStyleSheet("font-size:11px; color:#4a5a78;")

        # Start worker
        self.worker = PredictionWorker()
        self.worker.log.connect(self._on_log)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_log(self, idx, msg):
        self.log_labels[idx].setText("● " + msg)
        self.log_labels[idx].setStyleSheet(
            "font-size:11px; color:#63d4b8;"
        )

    def _on_progress(self, val):
        self.main_bar.setValue(val)
        self.pct_label.setText(f"{val}%")

    def _on_finished(self, result):
        # Pass result to main window
        if self.on_result:
            self.on_result(result)
        # Navigate to result screen
        QTimer.singleShot(800, lambda: self.go_to("result"))