from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


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
        layout.setContentsMargins(40, 20, 40, 20)

        # ────────────────────────────────
        # BANNER
        # ────────────────────────────────

        banner = QLabel()

        banner.setPixmap(
            QPixmap(
                "gui/resources/banners/welcome_banner.png"
            )
        )

        banner.setScaledContents(True)
        banner.setFixedHeight(220)

        layout.addWidget(banner)

        # ────────────────────────────────
        # LOGO
        # ────────────────────────────────

        logo = QLabel()

        logo.setPixmap(
            QPixmap(
                "gui/resources/logos/thyroid_logo.png"
            )
        )

        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(120, 120)
        logo.setScaledContents(True)

        layout.addWidget(logo)

        # ────────────────────────────────
        # TITLE
        # ────────────────────────────────

        title = QLabel("ThyroSenseX")

        title.setObjectName("screen_title")

        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)

        subtitle = QLabel(
            "AI Powered Thyroid Screening System"
        )

        subtitle.setAlignment(Qt.AlignCenter)

        subtitle.setStyleSheet("""
            font-size:14px;
            color:#64748b;
        """)

        layout.addWidget(subtitle)

        # ────────────────────────────────
        # PATIENT CARD
        # ────────────────────────────────

        self.patient_card = make_card()

        pc_layout = QVBoxLayout(
            self.patient_card
        )

        pc_layout.setSpacing(6)

        self.tag = QLabel(
            "NO PATIENT SELECTED"
        )

        self.tag.setAlignment(
            Qt.AlignCenter
        )

        self.tag.setStyleSheet("""
            font-size:15px;
            font-weight:bold;
            color:#dc2626;
        """)

        self.info = QLabel("")

        self.info.setAlignment(
            Qt.AlignCenter
        )

        self.info.setStyleSheet("""
            font-size:12px;
            color:#64748b;
        """)

        pc_layout.addWidget(self.tag)
        pc_layout.addWidget(self.info)

        layout.addWidget(self.patient_card)

        # ────────────────────────────────
        # DESCRIPTION
        # ────────────────────────────────

        desc = QLabel(
            "Non-invasive thyroid screening using "
            "facial imaging, thermal analysis, and "
            "voice biomarkers."
        )

        desc.setWordWrap(True)

        desc.setAlignment(
            Qt.AlignCenter
        )

        desc.setStyleSheet("""
            color:#475569;
            font-size:13px;
        """)

        layout.addWidget(desc)

        # ────────────────────────────────
        # BADGES
        # ────────────────────────────────

        badges = QHBoxLayout()

        badges.setAlignment(
            Qt.AlignCenter
        )

        for text in [
            "📷 Facial",
            "🌡 Thermal",
            "🎤 Voice"
        ]:

            b = QLabel(text)

            b.setStyleSheet("""
                background:#dbeafe;
                color:#1e40af;
                border-radius:14px;
                padding:6px 14px;
                font-size:11px;
                font-weight:bold;
            """)

            badges.addWidget(b)

        layout.addLayout(badges)

        # ────────────────────────────────
        # BUTTON
        # ────────────────────────────────

        self.btn_start = QPushButton(
            "Begin Scan"
        )

        self.btn_start.setObjectName(
            "primary"
        )

        self.btn_start.setFixedWidth(220)

        self.btn_start.setEnabled(False)

        self.btn_start.clicked.connect(
            self._start_scan
        )

        layout.addSpacing(20)

        layout.addWidget(
            self.btn_start,
            alignment=Qt.AlignCenter
        )

        # ────────────────────────────────
        # HINT
        # ────────────────────────────────

        hint = QLabel(
            "⏱ ~45 sec • No contact required"
        )

        hint.setAlignment(
            Qt.AlignCenter
        )

        hint.setStyleSheet("""
            color:#64748b;
            font-size:11px;
        """)

        layout.addWidget(hint)

        layout.addStretch()

    # ────────────────────────────────
    # SET PATIENT
    # ────────────────────────────────

    def set_patient(self, patient):

        self._current_patient = patient

        if not patient:

            self.tag.setText(
                "NO PATIENT SELECTED"
            )

            self.info.setText("")

            self.btn_start.setEnabled(False)

            return

        pid = patient.get(
            "patient_id",
            patient.get("id", "—")
        )

        age = patient.get(
            "age",
            "—"
        )

        gender = patient.get(
            "gender",
            "—"
        )

        weight = patient.get(
            "weight",
            "—"
        )

        self.tag.setText(
            f"{patient.get('name', '').upper()} • {pid}"
        )

        self.info.setText(
            f"{age} yrs • {gender} • {weight} kg"
        )

        self.btn_start.setEnabled(True)

    # ────────────────────────────────
    # START SCAN
    # ────────────────────────────────

    def _start_scan(self):

        if not self._current_patient:
            return

        print(
            f"[SCAN] Starting for "
            f"{self._current_patient.get('name')}"
        )

        self.go_to("capture")