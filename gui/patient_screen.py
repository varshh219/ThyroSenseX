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
        self.doctor = None
        self.doctor_id = None
        self._build_ui()

    # ── SET DOCTOR ───────────────────────────
    def set_doctor(self, doctor):
        self.doctor = doctor
        self.doctor_id = doctor.get("id")

    # ── UI ───────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        lbl = QLabel("PATIENT REGISTRATION")
        lbl.setObjectName("section")

        title = QLabel("New Patient")
        title.setObjectName("screen_title")

        card = make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(12)

        input_style = (
            "background:#0a0e14; border:1px solid #1e2d45;"
            "border-radius:8px; padding:10px 14px;"
            "font-size:12px; color:#e8edf7;"
        )

        # Name
        card_layout.addWidget(self._label("Full Name *"))
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(input_style)
        card_layout.addWidget(self.name_input)

        # Age + Gender
        ag_row = QHBoxLayout()

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Age")
        self.age_input.setStyleSheet(input_style)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Female", "Male", "Other"])
        self.gender_input.setStyleSheet(input_style)

        ag_row.addWidget(self.age_input)
        ag_row.addWidget(self.gender_input)

        card_layout.addLayout(ag_row)

        # 🔥 NEW: Weight
        card_layout.addWidget(self._label("Weight (kg) *"))
        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Enter weight")
        self.weight_input.setStyleSheet(input_style)
        card_layout.addWidget(self.weight_input)

        # Phone
        card_layout.addWidget(self._label("Phone *"))
        self.phone_input = QLineEdit()
        self.phone_input.setStyleSheet(input_style)
        card_layout.addWidget(self.phone_input)

        # Email
        card_layout.addWidget(self._label("Email"))
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(input_style)
        card_layout.addWidget(self.email_input)

        # Address
        card_layout.addWidget(self._label("Address"))
        self.address_input = QLineEdit()
        self.address_input.setStyleSheet(input_style)
        card_layout.addWidget(self.address_input)

        self.error_lbl = QLabel("")
        self.error_lbl.setAlignment(Qt.AlignCenter)

        btn_row = QHBoxLayout()

        self.btn_register = QPushButton("Register")
        self.btn_register.setObjectName("primary")
        self.btn_register.clicked.connect(self._register)

        btn_back = QPushButton("Back")
        btn_back.clicked.connect(lambda: self.go_to("patient_login"))

        btn_row.addWidget(self.btn_register)
        btn_row.addWidget(btn_back)

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

    # ── REGISTER ─────────────────────────────
    def _register(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        gender = self.gender_input.currentText()
        weight = self.weight_input.text().strip()   # 🔥 NEW
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()

        # Validation
        if not name or not age or not phone or not weight:
            self._error("Fill required fields")
            return

        if not age.isdigit():
            self._error("Invalid age")
            return

        if not weight.replace('.', '', 1).isdigit():
            self._error("Invalid weight")
            return

        if len(phone) < 10:
            self._error("Invalid phone")
            return

        if not self.doctor_id:
            self._error("Doctor not set")
            return

        self.btn_register.setText("Saving...")
        self.btn_register.setEnabled(False)

        try:
            from database.database import register_patient

            patient = register_patient(
                name,
                int(age),
                gender,
                phone,
                email,
                address,
                self.doctor_id,
                float(weight)   # 🔥 PASS WEIGHT
            )

            pid = patient.get("patient_id", patient.get("id"))

            self.error_lbl.setStyleSheet("color:#3ddc97;")
            self.error_lbl.setText(f"Added: {pid}")

            self._clear_form()
            self.go_to("patient_login")

        except Exception as e:
            print("[PatientRegister] Error:", e)
            self._error("DB error")

        finally:
            self.btn_register.setText("Register")
            self.btn_register.setEnabled(True)

    def _error(self, msg):
        self.error_lbl.setStyleSheet("color:#ff4f5e;")
        self.error_lbl.setText(msg)

    def _clear_form(self):
        self.name_input.clear()
        self.age_input.clear()
        self.weight_input.clear()   # 🔥 NEW
        self.phone_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.gender_input.setCurrentIndex(0)