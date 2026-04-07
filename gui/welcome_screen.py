from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton
)
from PyQt5.QtCore import Qt


class WelcomeScreen(QWidget):
    def __init__(self, go_to):
        super().__init__()
        self.go_to = go_to
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(40, 40, 40, 40)

        # ── Title ──────────────────────────────────────
        title_row = QHBoxLayout()
        title_row.setAlignment(Qt.AlignCenter)

        t1 = QLabel("Thyro")
        t1.setStyleSheet("font-size:28px; font-weight:bold; color:#e8edf7;")

        t2 = QLabel("Sense")
        t2.setStyleSheet("font-size:28px; font-weight:bold; color:#4f8dff;")

        t3 = QLabel("X")
        t3.setStyleSheet("font-size:28px; font-weight:bold; color:#e8edf7;")

        title_row.addWidget(t1)
        title_row.addWidget(t2)
        title_row.addWidget(t3)

        # ── Tagline ────────────────────────────────────
        self.tag = QLabel("AI · IoT THYROID DETECTION SYSTEM")
        self.tag.setObjectName("section")
        self.tag.setAlignment(Qt.AlignCenter)

        # ── Description ────────────────────────────────
        desc = QLabel(
            "Non-invasive thyroid screening using multimodal AI.\n"
            "Position yourself in front of the device to begin."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color:#4a5a78; font-size:12px; line-height:1.6;")

        # ── Badges ─────────────────────────────────────
        badges = QHBoxLayout()
        badges.setAlignment(Qt.AlignCenter)
        for text, color in [
            ("Facial Analysis",  "#1a2a4a"),
            ("Voice Biomarkers", "#0d2e28"),
            ("Thermal Imaging",  "#2e1f0a"),
        ]:
            b = QLabel(text)
            b.setStyleSheet(
                f"background:{color}; border-radius:12px;"
                f"padding:4px 12px; font-size:11px; color:#7a90b8;"
            )
            badges.addWidget(b)

        # ── Button ─────────────────────────────────────
        btn = QPushButton("Begin Scan")
        btn.setObjectName("primary")
        btn.setFixedWidth(200)
        btn.clicked.connect(lambda: self.go_to("capture"))

        # ── Hint ───────────────────────────────────────
        hint = QLabel("Est. scan time: ~45 seconds  ·  No physical contact required")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color:#4a5a78; font-size:10px;")

        # ── Assemble ───────────────────────────────────
        layout.addStretch()
        layout.addLayout(title_row)
        layout.addWidget(self.tag)      # ← fixed
        layout.addSpacing(12)
        layout.addWidget(desc)
        layout.addSpacing(8)
        layout.addLayout(badges)
        layout.addSpacing(20)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        layout.addSpacing(6)
        layout.addWidget(hint)
        layout.addStretch()

    def set_patient(self, patient):
        """Show patient name on welcome screen."""
        self.tag.setText(
            f"PATIENT: {patient['name'].upper()}  ·  {patient['id']}"
        )