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

    def set_doctor(self, doctor):
        self.doctor = doctor
        self.doctor_id = doctor['id']

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        # Header
        lbl = QLabel("PATIENT REGISTRATION")
        lbl.setObjectName("section")
        title = QLabel("New Patient")
        title.setObjectName("screen_title")

        # Form card
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
        card_layout.addWidget(self._label("Full Name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Varshitha S")
        self.name_input.setStyleSheet(input_style)
        card_layout.addWidget(self.name_input)

        # Age + Gender
        ag_row = QHBoxLayout()

        age_col = QVBoxLayout()
        age_col.addWidget(self._label("Age"))
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("25")
        self.age_input.setStyleSheet(input_style)
        age_col.addWidget(self.age_input)

        gender_col = QVBoxLayout()
        gender_col.addWidget(self._label("Gender"))
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Female", "Male", "Other"])
        self.gender_input.setStyleSheet(input_style)
        gender_col.addWidget(self.gender_input)

        ag_row.addLayout(age_col)
        ag_row.addLayout(gender_col)
        card_layout.addLayout(ag_row)

        # Phone
        card_layout.addWidget(self._label("Phone"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("9876543210")
        self.phone_input.setStyleSheet(input_style)
        card_layout.addWidget(self.phone_input)

        # Email
        card_layout.addWidget(self._label("Email"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@gmail.com")
        self.email_input.setStyleSheet(input_style)
        card_layout.addWidget(self.email_input)

        # Address
        card_layout.addWidget(self._label("Address"))
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Bangalore")
        self.address_input.setStyleSheet(input_style)
        card_layout.addWidget(self.address_input)

        # Error label
        self.error_lbl = QLabel("")
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.setStyleSheet("color:red; font-size:11px;")

        # Buttons
        btn_row = QHBoxLayout()

        btn_register = QPushButton("Register")
        btn_register.clicked.connect(self._register)

        btn_back = QPushButton("Back")
        btn_back.clicked.connect(lambda: self.go_to("patient_login"))

        btn_row.addWidget(btn_register)
        btn_row.addWidget(btn_back)

        # Layout
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
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        gender = self.gender_input.currentText()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()

        if not name or not age or not phone:
            self.error_lbl.setText("Fill all required fields")
            return

        if not age.isdigit():
            self.error_lbl.setText("Invalid age")
            return

        if not self.doctor_id:
            self.error_lbl.setText("Doctor not set")
            return

        from data.database import register_patient

        patient = register_patient(
            name,
            int(age),
            gender,
            phone,
            email,
            address,
            self.doctor_id
        )

        self.error_lbl.setStyleSheet("color:green")
        self.error_lbl.setText(f"Patient Added: {patient['id']}")