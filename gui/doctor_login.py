from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class DoctorLoginScreen(QWidget):

    def __init__(self, go_to, on_doctor_logged_in):
        super().__init__()

        self.go_to = go_to
        self.on_doctor_logged_in = on_doctor_logged_in

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(14)

        # Banner

        banner = QLabel()

        banner.setPixmap(
            QPixmap(
                "gui/resources/banners/welcome_banner.png"
            )
        )

        banner.setScaledContents(True)
        banner.setFixedHeight(170)

        layout.addWidget(banner)

        # Title

        title_row = QHBoxLayout()
        title_row.setAlignment(Qt.AlignCenter)

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
            font-size:30px;
            font-weight:bold;
        """)

        title_row.addWidget(logo)
        title_row.addSpacing(10)
        title_row.addWidget(title)

        tag = QLabel("DOCTOR LOGIN")

        tag.setAlignment(Qt.AlignCenter)

        tag.setStyleSheet("""
            font-size:13px;
            font-weight:bold;
            color:#2563eb;
            letter-spacing:2px;
        """)

        # Card

        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(450)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(
            24,
            20,
            24,
            20
        )

        card_layout.setSpacing(12)

        # Username

        card_layout.addWidget(
            self._label("Username")
        )

        self.user_input = QLineEdit()

        self.user_input.setPlaceholderText(
            "Enter username"
        )

        card_layout.addWidget(
            self.user_input
        )

        # Password

        card_layout.addWidget(
            self._label("Password")
        )

        self.pass_input = QLineEdit()

        self.pass_input.setPlaceholderText(
            "Enter password"
        )

        self.pass_input.setEchoMode(
            QLineEdit.Password
        )

        card_layout.addWidget(
            self.pass_input
        )

        # Error Label

        self.error_lbl = QLabel("")

        self.error_lbl.setAlignment(
            Qt.AlignCenter
        )

        self.error_lbl.setStyleSheet("""
            color:#ff4f5e;
            font-size:11px;
        """)

        # Login Button

        self.btn = QPushButton("LOGIN")

        self.btn.setObjectName(
            "primary"
        )

        self.btn.clicked.connect(
            self._login
        )

        # Enter key support

        self.pass_input.returnPressed.connect(
            self._login
        )

        self.user_input.returnPressed.connect(
            self._login
        )

        # Layout

        layout.addStretch()

        layout.addLayout(title_row)

        layout.addWidget(tag)

        layout.addSpacing(10)

        layout.addWidget(
            card,
            alignment=Qt.AlignCenter
        )

        layout.addWidget(
            self.error_lbl
        )

        layout.addStretch()

        layout.addWidget(
            self.btn,
            alignment=Qt.AlignCenter
        )

    def _label(self, text):

        l = QLabel(text)

        l.setStyleSheet(
            "font-size:10px;color:#64748b;letter-spacing:1px;"
        )

        return l

    def _login(self):

        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not username or not password:

            self.error_lbl.setText(
                "Please enter username and password."
            )

            return

        self.btn.setText("Logging in...")
        self.btn.setEnabled(False)

        self.error_lbl.setText("")

        try:

            from database.database import verify_doctor

            doctor = verify_doctor(
                username,
                password
            )

            if doctor:

                print(
                    f"[LOGIN] Doctor logged in: {username}"
                )

                self.user_input.clear()
                self.pass_input.clear()

                self.error_lbl.setText("")

                self.on_doctor_logged_in(
                    doctor
                )

                self.go_to(
                    "patient_login"
                )

            else:

                self.error_lbl.setText(
                    "Invalid username or password."
                )

        except Exception as e:

            print(
                "Login error:",
                e
            )

            self.error_lbl.setText(
                "Server/Database error."
            )

        finally:

            self.btn.setText(
                "LOGIN"
            )

            self.btn.setEnabled(True)