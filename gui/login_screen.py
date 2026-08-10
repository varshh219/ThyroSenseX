from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from database.database import (
    get_all_patients,
    get_last_scan
)


def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f


class LoginScreen(QWidget):

    def __init__(self, go_to, on_patient_selected):
        super().__init__()

        self.go_to = go_to
        self.on_patient_selected = on_patient_selected

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(14)

        # ─────────────────────────────
        # Banner
        # ─────────────────────────────

        banner = QLabel()

        banner.setPixmap(
            QPixmap(
                "gui/resources/banners/welcome_banner.png"
            )
        )

        banner.setScaledContents(True)
        banner.setFixedHeight(140)

        layout.addWidget(banner)

        # ─────────────────────────────
        # Header
        # ─────────────────────────────

        title_row = QHBoxLayout()

        logo = QLabel()

        logo.setPixmap(
            QPixmap(
                "gui/resources/logos/thyroid_logo.png"
            ).scaled(
                60,
                60,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        title = QLabel(
            '<span style="color:#1e3a8a;">Thyro</span>'
            '<span style="color:#2563eb;">Sense</span>'
            '<span style="color:#1e3a8a;">X</span>'
        )

        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)

        title_row.addWidget(logo)
        title_row.addSpacing(10)
        title_row.addWidget(title)
        title_row.addStretch()

        tag = QLabel(
            "PATIENT MANAGEMENT PORTAL"
        )

        tag.setObjectName("section")

        # ─────────────────────────────
        # Search
        # ─────────────────────────────

        search_row = QHBoxLayout()

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "🔍 Search patient by name..."
        )

        self.search_input.textChanged.connect(
            self._search
        )

        btn_new = QPushButton(
            "➕ New Patient"
        )

        btn_new.setObjectName(
            "primary"
        )

        btn_new.setFixedWidth(150)

        btn_new.clicked.connect(
            lambda: self.go_to(
                "patient_register"
            )
        )

        search_row.addWidget(
            self.search_input
        )

        search_row.addWidget(
            btn_new
        )

        # ─────────────────────────────
        # Patient List
        # ─────────────────────────────

        lbl = QLabel(
            "SELECT PATIENT"
        )

        lbl.setObjectName(
            "section"
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        self.list_widget = QWidget()

        self.list_layout = QVBoxLayout(
            self.list_widget
        )

        self.list_layout.setSpacing(10)

        self.list_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.list_layout.addStretch()

        scroll.setWidget(
            self.list_widget
        )

        # ─────────────────────────────
        # Layout
        # ─────────────────────────────

        layout.addLayout(
            title_row
        )

        layout.addWidget(
            tag
        )

        layout.addLayout(
            search_row
        )

        layout.addWidget(
            lbl
        )

        layout.addWidget(
            scroll
        )

    # ─────────────────────────────
    # Refresh
    # ─────────────────────────────

    def refresh(self):

        self.search_input.clear()

        self._load_patients()

    # ─────────────────────────────
    # Load Patients
    # ─────────────────────────────

    def _load_patients(self, query=""):

        try:

            while self.list_layout.count() > 1:

                item = self.list_layout.takeAt(0)

                if item.widget():

                    item.widget().deleteLater()

            patients = get_all_patients()

            if query.strip():

                patients = [

                    p for p in patients

                    if query.lower()
                    in p["name"].lower()

                ]

            if not patients:

                empty = QLabel(
                    "🩺 No patients found\n\nClick 'New Patient' to register."
                )

                empty.setAlignment(
                    Qt.AlignCenter
                )

                self.list_layout.insertWidget(
                    0,
                    empty
                )

                return

            for patient in reversed(
                patients
            ):

                card = self._make_patient_card(
                    patient
                )

                self.list_layout.insertWidget(
                    0,
                    card
                )

        except Exception as e:

            print(
                "[LoginScreen] Load error:",
                e
            )

    # ─────────────────────────────
    # Patient Card
    # ─────────────────────────────

    def _make_patient_card(
        self,
        patient
    ):

        card = make_card()

        card_layout = QHBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            14,
            12,
            14,
            12
        )

        name_text = patient.get(
            "name",
            "Unknown"
        )

        initials = "".join(
            w[0].upper()
            for w in name_text.split()[:2]
        )

        avatar = QLabel(
            initials
        )

        avatar.setFixedSize(
            44,
            44
        )

        avatar.setAlignment(
            Qt.AlignCenter
        )

        avatar.setStyleSheet("""
            background:#2563eb;
            color:white;
            border-radius:22px;
            font-weight:bold;
            font-size:14px;
        """)

        info = QVBoxLayout()

        name = QLabel(
            name_text
        )

        name.setStyleSheet("""
            font-weight:bold;
            font-size:14px;
        """)

        pid = patient.get(
            "id",
            "N/A"
        )

        age = patient.get(
            "age",
            "--"
        )

        gender = patient.get(
            "gender",
            "--"
        )

        details = QLabel(
            f"ID: {pid} · {age} yrs · {gender}"
        )

        last = get_last_scan(
            pid
        )

        if last:

            last_scan = QLabel(
                f"Last: {last['date']} — {last['prediction']}"
            )

        else:

            last_scan = QLabel(
                "No scans yet"
            )

        info.addWidget(
            name
        )

        info.addWidget(
            details
        )

        info.addWidget(
            last_scan
        )

        btn = QPushButton(
            "🩺 Select"
        )

        btn.setObjectName(
            "primary"
        )

        btn.setFixedWidth(
            110
        )

        btn.clicked.connect(
            lambda _, p=patient:
            self._select_patient(p)
        )

        card_layout.addWidget(
            avatar
        )

        card_layout.addLayout(
            info
        )

        card_layout.addStretch()

        card_layout.addWidget(
            btn
        )

        return card

    # ─────────────────────────────
    # Search
    # ─────────────────────────────

    def _search(self, query):

        self._load_patients(
            query
        )

    # ─────────────────────────────
    # Select Patient
    # ─────────────────────────────

    def _select_patient(
        self,
        patient
    ):

        print(
            f"[PATIENT] Selected: "
            f"{patient.get('name')}"
        )

        self.on_patient_selected(
            patient
        )

        self.go_to(
            "welcome"
        )