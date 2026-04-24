from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage

import cv2
import numpy as np
from api.client import get_thermal_frame

from api.client import (
    get_camera_frame,
    get_thermal_frame,
    capture_image,
    record_audio
)


def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f


class CaptureScreen(QWidget):
    def __init__(self, go_to):
        super().__init__()
        self.go_to = go_to

        self._timer = QTimer()
        self._timer.timeout.connect(self._update_preview)

        # ── Data storage ─────────────────────
        self.image_bytes = None
        self.thermal_bytes = None
        self.audio_bytes = None
        self.audio_ok = False

        self._build_ui()

    # ── UI ─────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Step-by-Step Capture")
        title.setObjectName("screen_title")

        # Camera preview
        self.cam_label = QLabel("Camera Preview")
        self.cam_label.setFixedHeight(200)
        self.cam_label.setAlignment(Qt.AlignCenter)

        # Thermal preview
        self.thm_label = QLabel("Thermal Preview")
        self.thm_label.setFixedHeight(200)
        self.thm_label.setAlignment(Qt.AlignCenter)

        # Buttons
        btn_row = QHBoxLayout()

        self.btn_cam = QPushButton("📸 Capture Image")
        self.btn_cam.clicked.connect(self.capture_image)

        self.btn_thm = QPushButton("🌡 Capture Thermal")
        self.btn_thm.clicked.connect(self.capture_thermal)

        self.btn_audio = QPushButton("🎤 Record Audio")
        self.btn_audio.clicked.connect(self.record_audio)

        btn_row.addWidget(self.btn_cam)
        btn_row.addWidget(self.btn_thm)
        btn_row.addWidget(self.btn_audio)

        # Scan button
        self.btn_scan = QPushButton("▶ Start Scan")
        self.btn_scan.setObjectName("primary")
        self.btn_scan.clicked.connect(self.start_scan)

        # Status
        self.status = QLabel("Ready")
        self.status.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(self.cam_label)
        layout.addWidget(self.thm_label)
        layout.addLayout(btn_row)
        layout.addWidget(self.status)
        layout.addStretch()
        layout.addWidget(self.btn_scan, alignment=Qt.AlignCenter)

    # ── Preview ────────────────────────────
    def start_preview(self):
        self._timer.start(200)

    def stop_preview(self):
        self._timer.stop()

    def _update_preview(self):
        # Camera preview (only if not captured)
        if self.image_bytes is None:
            cam_bytes = get_camera_frame()
            if cam_bytes:
                self._show(self.cam_label, cam_bytes)

        # Thermal preview (only if not captured)
        if self.thermal_bytes is None:
            thm_bytes = get_thermal_frame()
            if thm_bytes:
                self._show(self.thm_label, thm_bytes)

    def _show(self, label, jpeg_bytes):
        arr = np.frombuffer(jpeg_bytes, np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(img))

    # ── Capture Image ──────────────────────
    def capture_image(self):
        try:
            capture_image()  # trigger Pi capture

            frame = get_camera_frame()
            if frame:
                self.image_bytes = frame
                self._show(self.cam_label, frame)

                self.status.setText("✅ Image captured")
                print("[SCAN] Image captured")

        except Exception as e:
            print(e)
            self.status.setText("❌ Image failed")

    # ── Capture Thermal ────────────────────
    def capture_thermal(self):
        try:
            from api.client import get_thermal_frame

            frame = get_thermal_frame()

            if frame:
                # ✅ store thermal IMAGE bytes
                self.thermal_bytes = frame

                self.status.setText("✅ Thermal captured")
                print("[SCAN] Thermal captured")

            else:
                self.status.setText("❌ Thermal failed")

        except Exception as e:
            print(e)
            self.status.setText("❌ Thermal error")
    # ── Record Audio ───────────────────────
    def record_audio(self):
        try:
            data = record_audio()

            self.audio_ok = data.get("ok", False)

            if self.audio_ok:
                self.status.setText("✅ Audio recorded")
                print("[SCAN] Audio recorded")
            else:
                self.status.setText("⚠ Audio issue")

        except Exception as e:
            print(e)
            self.status.setText("❌ Audio failed")

    # ── Start Scan ─────────────────────────
    def start_scan(self):
        if not self.image_bytes:
            self.status.setText("⚠ Capture image first")
            return

        if not self.thermal_bytes:
            self.status.setText("⚠ Capture thermal first")
            return

        if not self.audio_ok:
            self.status.setText("⚠ Record audio first")
            return

        self.stop_preview()

        print("[SCAN] Starting processing")
        self.go_to("processing")

    # ── Reset ─────────────────────────────
    def reset(self):
        self.image_bytes = None
        self.thermal_bytes = None
        self.audio_bytes = None
        self.audio_ok = False

        self.status.setText("Ready")

        # Clear UI
        self.cam_label.setText("Camera Preview")
        self.thm_label.setText("Thermal Preview")

        self.start_preview()