import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame
from PyQt5.QtCore    import Qt, QTimer, QThread, pyqtSignal
import numpy as np

class PredictionWorker(QThread):
    log      = pyqtSignal(int, str)
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, patient=None):
        super().__init__()
        self.patient = patient

    def run(self):
        import time
        from sensors.camera     import capture_face_image
        from sensors.microphone import record_voice, cleanup_audio
        from sensors.thermal    import read_thermal
        from model.predictor    import ThyroidPredictor
        import config

        # Step 1: Capture
        self.log.emit(0, 'Capturing face image...')
        self.progress.emit(15)
        face_image = capture_face_image(preview_seconds=3)

        self.log.emit(1, 'Recording voice sample...')
        self.progress.emit(30)
        audio_path = record_voice(duration=4)

        self.log.emit(2, 'Reading thermal sensor...')
        self.progress.emit(45)
        thermal    = read_thermal(simulate=config.SIMULATE_THERMAL)

        # Step 2: Feature extraction
        self.log.emit(3, 'Extracting facial features...')
        self.progress.emit(55)
        from thyrosensex.face_features    import extract_face_features
        from thyrosensex.voice_features   import extract_voice_features
        from thyrosensex.thermal_features import extract_thermal_features
        face_feats    = extract_face_features(face_image) if face_image is not None else {}
        voice_feats   = extract_voice_features(audio_path) if audio_path else {}
        thermal_feats = extract_thermal_features(thermal)
        cleanup_audio(audio_path)

        # Step 3: Fuse features
        self.log.emit(4, 'Running feature fusion...')
        self.progress.emit(70)
        patient = self.patient or {}
        all_features = {
            'age':    patient.get('age', 30),
            'gender': 1 if patient.get('gender','Female')=='Female' else 0,
            'weight': 65,
            'has_thyroid': 1,
            **face_feats, **voice_feats, **thermal_feats
        }

        # Step 4: Predict
        self.log.emit(5, 'Running AI inference...')
        self.progress.emit(85)
        predictor = ThyroidPredictor()
        result    = predictor.predict(all_features)

        # Add raw features to result for PDF
        result['features'] = {
            'Pitch':        voice_feats.get('pitch_hz', 0),
            'Jitter':       voice_feats.get('jitter', 0),
            'Shimmer':      voice_feats.get('shimmer', 0),
            'HNR':          voice_feats.get('hnr', 0),
            'Thermal Mean': thermal_feats.get('mean_temp', 0),
            'Thermal Max':  thermal_feats.get('max_temp', 0),
            'Facial Flags': f"{sum(1 for v in face_feats.values() if v > 0.5)}/10",
        }

        self.log.emit(6, 'Prediction generated!')
        self.progress.emit(100)
        self.finished.emit(result)

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt

class ProcessingScreen(QWidget):
    def __init__(self, go_to, on_result=None):
        super().__init__()
        self.go_to = go_to
        self.on_result = on_result
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.label = QLabel("Processing...")
        self.label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setValue(0)

        layout.addStretch()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addStretch()

    def start(self, patient):
        from gui.processing_screen import PredictionWorker

        self.worker = PredictionWorker(patient)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, result):
        if self.on_result:
            self.on_result(result)
        self.go_to('result')