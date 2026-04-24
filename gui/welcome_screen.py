from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt


def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f


class WelcomeScreen(QWidget):
    def __init__(self, go_to):
        super().__init__()
        self.go_to = go_to
        self._current_patient = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(40, 40, 40, 40)

        # ── Title ─────────────────────────
        title_row = QHBoxLayout()
        title_row.setAlignment(Qt.AlignCenter)

        title = QLabel(
            '<span style="color:#e6edf3;">Thyro</span>'
            '<span style="color:#58a6ff;">Sense</span>'
            '<span style="color:#e6edf3;">X</span>'
        )
        title.setStyleSheet("font-size:30px; font-weight:bold;")
        title_row.addWidget(title)

        # ── Patient Card ───────────────────
        self.patient_card = make_card()
        pc_layout = QVBoxLayout(self.patient_card)

        self.tag = QLabel("NO PATIENT SELECTED")
        self.tag.setAlignment(Qt.AlignCenter)
        self.tag.setStyleSheet(
            "font-size:13px; color:#ff4f5e; font-weight:bold;"
        )

        pc_layout.addWidget(self.tag)

        # ── Description ────────────────────
        desc = QLabel(
            "Non-invasive thyroid screening using multimodal AI.\n"
            "Ensure proper lighting and face the device directly."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(
            "color:#8b949e; font-size:12px;"
        )

        # ── Badges ─────────────────────────
        badges = QHBoxLayout()
        badges.setAlignment(Qt.AlignCenter)

        for text in ["Facial", "Voice", "Thermal"]:
            b = QLabel(text)
            b.setStyleSheet(
                "background:#1e2d45; border-radius:14px;"
                "padding:5px 14px; font-size:11px;"
            )
            badges.addWidget(b)

        # ── Button ─────────────────────────
        self.btn_start = QPushButton("Begin Scan")
        self.btn_start.setObjectName("primary")
        self.btn_start.setFixedWidth(220)
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self._start_scan)

        # ── Hint ───────────────────────────
        hint = QLabel("⏱ ~45 sec · No contact required")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color:#6e7681; font-size:10px;")

        # ── Layout ─────────────────────────
        layout.addStretch()
        layout.addLayout(title_row)
        layout.addWidget(self.patient_card)
        layout.addWidget(desc)
        layout.addLayout(badges)
        layout.addSpacing(20)
        layout.addWidget(self.btn_start, alignment=Qt.AlignCenter)
        layout.addWidget(hint)
        layout.addStretch()

    # ── SET PATIENT ───────────────────────
    def set_patient(self, patient):
        self._current_patient = patient

        if not patient:
            self.tag.setText("NO PATIENT SELECTED")
            self.btn_start.setEnabled(False)
            return

        pid = patient.get("patient_id", patient.get("id", "—"))

        self.tag.setText(
            f"{patient.get('name','').upper()}  ·  {pid}"
        )

        # Enable scan
        self.btn_start.setEnabled(True)

    # ── START SCAN ────────────────────────
    def _start_scan(self):
        if not self._current_patient:
            return

        print(f"[SCAN] Starting for {self._current_patient.get('name')}")

        # Go to capture screen
        self.go_to("capture")