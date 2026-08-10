from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
    QApplication
)

from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtGui import (
    QPixmap,
    QImage,
    QIcon
)

import cv2
import numpy as np

from api.client import (
    get_camera_frame,
    get_thermal_data,
    capture_image,
    record_audio
)


# ══════════════════════════════════════════════════════
# CARD STYLE
# ══════════════════════════════════════════════════════

def make_card():

    f = QFrame()

    f.setObjectName("card")

    return f


# ══════════════════════════════════════════════════════
# CAPTURE SCREEN
# ══════════════════════════════════════════════════════

class CaptureScreen(QWidget):

    def __init__(self, go_to):

        super().__init__()

        self.go_to = go_to

        self._timer = QTimer()

        self._timer.timeout.connect(
            self._update_preview
        )

        # ── DATA STORAGE ─────────────────
        self.image_bytes = None
        self.thermal_bytes = None
        self.audio_bytes = None

        self.audio_ok = False

        # ── CAPTURE FLAGS ───────────────
        self.cam_captured = False
        self.thm_captured = False

        self._build_ui()

    # ════════════════════════════════════
    # UI
    # ════════════════════════════════════

    def _build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            24, 24, 24, 24
        )

        layout.setSpacing(18)
        
        logo = QLabel()

        logo.setPixmap(
            QPixmap(
                "gui/resources/logos/thyroid_logo.png"
            ).scaled(
                70,
                70,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        logo.setAlignment(Qt.AlignCenter)

        layout.addWidget(logo)
        # ─────────────────────────────────
        # TITLE
        # ─────────────────────────────────

        title = QLabel(
            "Thyroid Data Acquisition"
        )

        title.setObjectName(
            "screen_title"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(title)

        # ─────────────────────────────────
        # PREVIEW ROW
        # ─────────────────────────────────

        preview_row = QHBoxLayout()

        preview_row.setSpacing(20)

        # ───────────────── CAMERA CARD ──

        cam_card = make_card()

        cam_layout = QVBoxLayout(cam_card)

        cam_title = QLabel(
            "📷 Camera Preview"
        )

        cam_title.setAlignment(
            Qt.AlignCenter
        )

        self.cam_label = QLabel()

        self.cam_label.setMinimumSize(
            640,
            480
        )

        self.cam_label.setAlignment(
            Qt.AlignCenter
        )

        self.cam_label.setScaledContents(
            True
        )

        self.cam_label.setStyleSheet("""
            QLabel {
                border: 2px solid #3ddc97;
                border-radius: 14px;
                background-color: black;
                color: white;
                font-size: 18px;
            }
        """)

        self.cam_label.setText(
            "Camera Preview"
        )

        cam_layout.addWidget(cam_title)

        cam_layout.addWidget(
            self.cam_label
        )

        # ───────────────── THERMAL CARD ─

        thm_card = make_card()

        thm_layout = QVBoxLayout(thm_card)

        thm_title = QLabel(
            "🌡 Thermal Preview"
        )

        thm_title.setAlignment(
            Qt.AlignCenter
        )

        self.thm_label = QLabel()

        self.thm_label.setMinimumSize(
            420,
            420
        )

        self.thm_label.setAlignment(
            Qt.AlignCenter
        )

        self.thm_label.setScaledContents(
            True
        )

        self.thm_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ff7849;
                border-radius: 14px;
                background-color: black;
                color: white;
                font-size: 18px;
            }
        """)

        self.thm_label.setText(
            "Thermal Preview"
        )

        thm_layout.addWidget(thm_title)

        thm_layout.addWidget(
            self.thm_label
        )

        preview_row.addWidget(
            cam_card,
            2
        )

        preview_row.addWidget(
            thm_card,
            1
        )

        layout.addLayout(preview_row)

        # ─────────────────────────────────
        # BUTTONS
        # ─────────────────────────────────

        btn_row = QHBoxLayout()

        btn_row.setSpacing(16)

        # Camera Button

        self.btn_cam = QPushButton(
            "📸 Capture Image"
        )

        self.btn_cam.setIcon(
            QIcon(
                "gui/resources/icons/camera.png"
            )
        )

        self.btn_cam.setMinimumHeight(55)

        self.btn_cam.clicked.connect(
            self.capture_image
        )

        # Thermal Button

        self.btn_thm = QPushButton(
            "🌡 Capture Thermal"
        )

        self.btn_thm.setIcon(
            QIcon(
                "gui/resources/icons/thermal.png"
            )
        )

        self.btn_thm.setMinimumHeight(55)

        self.btn_thm.clicked.connect(
            self.capture_thermal
        )

        # Audio Button

        self.btn_audio = QPushButton(
            "🎤 Record Audio"
        )

        self.btn_audio.setIcon(
            QIcon(
                "gui/resources/icons/mic.png"
            )
        )

        self.btn_audio.setMinimumHeight(55)

        self.btn_audio.clicked.connect(
            self.record_audio
        )

        btn_row.addWidget(self.btn_cam)
        btn_row.addWidget(self.btn_thm)
        btn_row.addWidget(self.btn_audio)
        layout.addLayout(btn_row)

        # ─────────────────────────────────
        # STATUS
        # ─────────────────────────────────

        self.status = QLabel(
            "Ready for Capture"
        )

        self.status.setAlignment(
            Qt.AlignCenter
        )

        self.status.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
            color:#58a6ff;
        """)

        layout.addWidget(
            self.status
        )
        # ─────────────────────────────────
        # START SCAN
        # ─────────────────────────────────

        self.btn_scan = QPushButton(
            "🧠 Run AI Analysis"
        )

        self.btn_scan.setObjectName(
            "primary"
        )

        self.btn_scan.setMinimumHeight(
            55
        )

        self.btn_scan.clicked.connect(
            self.start_scan
        )

        layout.addStretch()

        layout.addWidget(
            self.btn_scan,
            alignment=Qt.AlignCenter
        )

    # ════════════════════════════════════
    # PREVIEW
    # ════════════════════════════════════

    def start_preview(self):

        self._timer.start(30)

    def stop_preview(self):

        self._timer.stop()

    def _update_preview(self):

        # ── LIVE CAMERA ─────────────────
        if not self.cam_captured:

            try:

                cam_bytes = get_camera_frame()

                if cam_bytes:

                    self._show(
                        self.cam_label,
                        cam_bytes
                    )

            except Exception as e:

                print(
                    "[LIVE CAMERA ERROR]",
                    e
                )

        # ── LIVE THERMAL ────────────────
        if not self.thm_captured:

            try:

                thm_bytes = get_thermal_data()

                if thm_bytes:

                    self._show(
                        self.thm_label,
                        thm_bytes
                    )

            except Exception as e:

                print(
                    "[LIVE THERMAL ERROR]",
                    e
                )

    # ════════════════════════════════════
    # SHOW IMAGE
    # ════════════════════════════════════

    def _show(self, label, jpeg_bytes):

        arr = np.frombuffer(
            jpeg_bytes,
            np.uint8
        )

        frame = cv2.imdecode(
            arr,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            return

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        h, w, ch = rgb.shape

        img = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        pix = QPixmap.fromImage(img)

        pix = pix.scaled(
            label.width(),
            label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        label.setPixmap(pix)

    # ════════════════════════════════════
    # CAPTURE IMAGE
    # ════════════════════════════════════

    def capture_image(self):

        try:

            capture_image()

            frame = get_camera_frame()

            if frame:

                self.image_bytes = frame

                self.cam_captured = True

                self._show(
                    self.cam_label,
                    frame
                )

                self.status.setText(
                    "✅ Image captured"
                )

                print(
                    "[SCAN] Image captured"
                )

        except Exception as e:

            print(e)

            self.status.setText(
                "❌ Image failed"
            )

    # ════════════════════════════════════
    # CAPTURE THERMAL
    # ════════════════════════════════════

    def capture_thermal(self):

        try:

            frame = get_thermal_data()

            if frame:

                self.thermal_bytes = frame

                self.thm_captured = True

                self._show(
                    self.thm_label,
                    frame
                )

                self.status.setText(
                    "✅ Thermal captured"
                )

                print(
                    "[SCAN] Thermal captured"
                )

            else:

                self.status.setText(
                    "❌ Thermal failed"
                )

        except Exception as e:

            print(e)

            self.status.setText(
                "❌ Thermal error"
            )

    # ════════════════════════════════════
    # RECORD AUDIO
    # ════════════════════════════════════

    def record_audio(self):

        try:

            self.status.setText(
                "🎤 Recording audio..."
            )

            QApplication.processEvents()

            print(
                "[AUDIO] Recording started"
            )

            data = record_audio()

            print(
                "[AUDIO] Response =",
                data
            )

            self.audio_ok = data.get(
                "ok",
                False
            )

            self.audio_bytes = data.get(
                "file"
            )

            if self.audio_ok:

                self.status.setText(
                    "✅ Audio recorded successfully"
                )

                print(
                    "[SCAN] Audio recorded"
                )

            else:

                self.status.setText(
                    "❌ Audio recording failed"
                )

        except Exception as e:

            print(
                "[AUDIO ERROR]",
                e
            )

            self.status.setText(
                "❌ Audio failed"
            )

    # ════════════════════════════════════
    # START SCAN
    # ════════════════════════════════════

    def start_scan(self):

        if not self.image_bytes:

            self.status.setText(
                "⚠ Capture image first"
            )

            return

        if not self.thermal_bytes:

            self.status.setText(
                "⚠ Capture thermal first"
            )

            return

        if not self.audio_ok:

            self.status.setText(
                "⚠ Record audio first"
            )

            return

        self.stop_preview()

        print(
            "[SCAN] Starting processing"
        )

        self.go_to("processing")

    # ════════════════════════════════════
    # RESET
    # ════════════════════════════════════

    def reset(self):

        self.image_bytes = None

        self.thermal_bytes = None

        self.audio_bytes = None

        self.audio_ok = False

        self.cam_captured = False

        self.thm_captured = False

        self.status.setText("Ready for capture")

        self.cam_label.setText(
                "📷 Camera Preview"
            )

        self.thm_label.setText(
                "🌡 Thermal Preview"
            )

        self.start_preview()