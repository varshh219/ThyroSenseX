from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QFrame, QComboBox
)
from PyQt5.QtCore import Qt


def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f


class PatientRegisterScreen(QWidget):
    def __init__(self, go_to):
        super().__init__()
        self.go_to = go_to
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        # ── Header ─────────────────────────────────────
        lbl = QLabel("PATIENT REGISTRATION")
        lbl.setObjectName("section")
        title = QLabel("New Patient")
        title.setObjectName("screen_title")

        # ── Form card ──────────────────────────────────
        card = make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(12)

        # Input style
        input_style = (
            "background:#0a0e14; border:1px solid #1e2d45;"
            "border-radius:8px; padding:10px 14px;"
            "font-size:12px; color:#e8edf7;"
        )
        label_style = "font-size:11px; color:#7a90b8;"

        # ── Name ───────────────────────────────────────
        card_layout.addWidget(QLabel("Full Name").also(
            lambda l: l.setStyleSheet(label_style)
        ) if False else self._label("Full Name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Varshitha S")
        self.name_input.setStyleSheet(input_style)
        card_layout.addWidget(self.name_input)

        # ── Age + Gender row ───────────────────────────
        ag_row = QHBoxLayout()
        ag_row.setSpacing(10)

        age_col = QVBoxLayout()
        age_col.addWidget(self._label("Age"))
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("e.g. 25")
        self.age_input.setStyleSheet(input_style)
        age_col.addWidget(self.age_input)

        gender_col = QVBoxLayout()
        gender_col.addWidget(self._label("Gender"))
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Female", "Male", "Other"])
        self.gender_input.setStyleSheet(
            "background:#0a0e14; border:1px solid #1e2d45;"
            "border-radius:8px; padding:8px 14px;"
            "font-size:12px; color:#e8edf7;"
        )
        gender_col.addWidget(self.gender_input)

        ag_row.addLayout(age_col)
        ag_row.addLayout(gender_col)
        card_layout.addLayout(ag_row)

        # ── Phone ──────────────────────────────────────
        card_layout.addWidget(self._label("Phone Number"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("e.g. 9876543210")
        self.phone_input.setStyleSheet(input_style)
        card_layout.addWidget(self.phone_input)

        # ── Address ────────────────────────────────────
        card_layout.addWidget(self._label("Address"))
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("e.g. Bangalore, Karnataka")
        self.address_input.setStyleSheet(input_style)
        card_layout.addWidget(self.address_input)

        # ── Error message ──────────────────────────────
        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet("color:#ff4f5e; font-size:11px;")
        self.error_lbl.setAlignment(Qt.AlignCenter)

        # ── Buttons ────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_register = QPushButton("Register Patient")
        btn_register.setObjectName("primary")
        btn_register.clicked.connect(self._register)

        btn_back = QPushButton("Back")
        btn_back.setObjectName("secondary")
        btn_back.clicked.connect(lambda: self.go_to("login"))

        btn_row.addWidget(btn_register)
        btn_row.addWidget(btn_back)

        # ── Assemble ───────────────────────────────────
        layout.addWidget(lbl)
        layout.addWidget(title)
        layout.addWidget(card)
        layout.addWidget(self.error_lbl)
        layout.addStretch()
        layout.addLayout(btn_row)

    def _label(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-size:11px; color:#7a90b8;")
        return l

    def _register(self):
        """Validate and register new patient."""
        name    = self.name_input.text().strip()
        age     = self.age_input.text().strip()
        gender  = self.gender_input.currentText()
        phone   = self.phone_input.text().strip()
        address = self.address_input.text().strip()

        # ── Validation ─────────────────────────────────
        if not name:
            self.error_lbl.setText("Please enter patient name.")
            return
        if not age.isdigit() or not (1 <= int(age) <= 120):
            self.error_lbl.setText("Please enter a valid age (1-120).")
            return
        if not phone.isdigit() or len(phone) != 10:
            self.error_lbl.setText("Please enter a valid 10-digit phone number.")
            return
        if not address:
            self.error_lbl.setText("Please enter address.")
            return

        # ── Register ───────────────────────────────────
        from data.database import register_patient
        patient = register_patient(name, age, gender, phone, address)

        # Clear form
        self.name_input.clear()
        self.age_input.clear()
        self.phone_input.clear()
        self.address_input.clear()
        self.error_lbl.setText("")

        # Show success and go back to login
        self.error_lbl.setStyleSheet("color:#3ddc97; font-size:11px;")
        self.error_lbl.setText(
            f"✓ Patient registered! ID: {patient['id']}"
        )
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.go_to("login"))