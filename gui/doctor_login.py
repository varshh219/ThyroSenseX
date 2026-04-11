from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame
)
from PyQt5.QtCore import Qt

class DoctorLoginScreen(QWidget):
    def __init__(self, go_to, on_doctor_logged_in):
        super().__init__()
        self.go_to = go_to
        self.on_doctor_logged_in = on_doctor_logged_in
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(14)

        # Title
        title_row = QHBoxLayout()
        title_row.setAlignment(Qt.AlignCenter)
        for text, color in [('Thyro','#e6edf3'),('Sense','#1f6feb'),('X','#e6edf3')]:
            l = QLabel(text)
            l.setStyleSheet(f'font-size:26px;font-weight:bold;color:{color};')
            title_row.addWidget(l)

        tag = QLabel('DOCTOR LOGIN')
        tag.setObjectName('section')
        tag.setAlignment(Qt.AlignCenter)

        # Form card
        card = QFrame(); card.setObjectName('card')
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)

        card_layout.addWidget(self._label('Username'))
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText('Enter username')
        card_layout.addWidget(self.user_input)

        card_layout.addWidget(self._label('Password'))
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText('Enter password')
        self.pass_input.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.pass_input)

        self.error_lbl = QLabel('')
        self.error_lbl.setStyleSheet('color:#ff4f5e;font-size:11px;')
        self.error_lbl.setAlignment(Qt.AlignCenter)

        btn = QPushButton('LOGIN')
        btn.setObjectName('primary')
        btn.clicked.connect(self._login)

        layout.addStretch()
        layout.addLayout(title_row)
        layout.addWidget(tag)
        layout.addSpacing(10)
        layout.addWidget(card)
        layout.addWidget(self.error_lbl)
        layout.addStretch()
        layout.addWidget(btn, alignment=Qt.AlignCenter)

    def _label(self, text):
        l = QLabel(text)
        l.setStyleSheet('font-size:10px;color:#8b949e;letter-spacing:1px;')
        return l

    def _login(self):
        from data.database import verify_doctor
        username = self.user_input.text().strip()
        password = self.pass_input.text()
        if not username or not password:
            self.error_lbl.setText('Please enter username and password.')
            return
        doctor = verify_doctor(username, password)
        if doctor:
            self.error_lbl.setText('')
            self.on_doctor_logged_in(doctor)
            self.go_to('patient_login')
        else:
            self.error_lbl.setText('Invalid username or password.')