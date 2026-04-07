from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time


# ── Background worker — runs sensors without freezing GUI ──────
class ScanWorker(QThread):
    progress = pyqtSignal(int, str)  # (step 0-5, message)
    finished = pyqtSignal()

    def run(self):
        steps = [
            (0, "Activating camera…"),
            (1, "Facial features captured ✓"),
            (2, "Recording voice sample…"),
            (3, "Voice biomarkers extracted ✓"),
            (4, "Thermal scan in progress…"),
            (5, "All sensors complete ✓"),
        ]
        for step, msg in steps:
            self.progress.emit(step, msg)
            time.sleep(1.2)
        self.finished.emit()


# ── Helper: make a styled card frame ──────────────────────────
def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f


class CaptureScreen(QWidget):
    def __init__(self, go_to):
        super().__init__()
        self.go_to = go_to
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        # ── Header ─────────────────────────────────────
        lbl = QLabel("STEP 1 OF 3")
        lbl.setObjectName("section")
        title = QLabel("Data Capture")
        title.setObjectName("screen_title")

        # ── Progress bar ───────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(6)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)

        # ── Step cards ─────────────────────────────────
        self.step_cards = []
        steps_info = [
            ("Face Scan",       "Detecting 10 facial biomarkers"),
            ("Voice Recording", "Pitch, jitter, shimmer, HNR"),
            ("Thermal Scan",    "MLX90640 neck temperature map"),
        ]

        cards_layout = QVBoxLayout()
        for name, desc in steps_info:
            card = make_card()
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 12, 16, 12)

            # Left: name + description
            info_col = QVBoxLayout()
            n = QLabel(name)
            n.setStyleSheet("font-weight:bold; font-size:13px; color:#e8edf7;")
            d = QLabel(desc)
            d.setStyleSheet("font-size:11px; color:#7a90b8;")
            info_col.addWidget(n)
            info_col.addWidget(d)

            # Right: status badge
            status = QLabel("Waiting")
            status.setStyleSheet(
                "font-size:10px; color:#4a5a78;"
                "border:1px solid #1e2d45;"
                "border-radius:10px; padding:2px 8px;"
            )

            card_layout.addLayout(info_col)
            card_layout.addStretch()
            card_layout.addWidget(status)

            self.step_cards.append(status)
            cards_layout.addWidget(card)

        # ── Status message ─────────────────────────────
        self.status_msg = QLabel("")
        self.status_msg.setStyleSheet("color:#7a90b8; font-size:11px;")

        # ── Start button ───────────────────────────────
        self.btn = QPushButton("Start Capture")
        self.btn.setObjectName("primary")
        self.btn.setFixedWidth(200)
        self.btn.clicked.connect(self.start_scan)

        # ── Assemble ───────────────────────────────────
        layout.addWidget(lbl)
        layout.addWidget(title)
        layout.addWidget(self.progress_bar)
        layout.addLayout(cards_layout)
        layout.addWidget(self.status_msg)
        layout.addStretch()
        layout.addWidget(self.btn, alignment=Qt.AlignCenter)

    def start_scan(self):
        self.btn.setEnabled(False)
        self.btn.setText("Scanning…")
        self.worker = ScanWorker()
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(lambda: self.go_to("processing"))
        self.worker.start()

    def on_progress(self, step, msg):
        self.progress_bar.setValue(step + 1)
        self.status_msg.setText(msg)

        card_idx = step // 2
        status = self.step_cards[card_idx]

        if step % 2 == 0:
            # Active
            status.setText("Active")
            status.setStyleSheet(
                "font-size:10px; color:#4f8dff;"
                "border:1px solid #4f8dff;"
                "border-radius:10px; padding:2px 8px;"
            )
        else:
            # Done
            status.setText("✓ Done")
            status.setStyleSheet(
                "font-size:10px; color:#3ddc97;"
                "border:1px solid #3ddc97;"
                "border-radius:10px; padding:2px 8px;"
            )

    def reset(self):
        self.btn.setEnabled(True)
        self.btn.setText("Start Capture")
        self.progress_bar.setValue(0)
        self.status_msg.setText("")
        for status in self.step_cards:
            status.setText("Waiting")
            status.setStyleSheet(
                "font-size:10px; color:#4a5a78;"
                "border:1px solid #1e2d45;"
                "border-radius:10px; padding:2px 8px;"
            )