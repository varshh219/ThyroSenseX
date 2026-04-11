from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox,
    QFileDialog
)
from PyQt5.QtCore import Qt
from datetime import datetime


def make_card(name="card"):
    f = QFrame()
    f.setObjectName(name)
    return f


class ReportScreen(QWidget):
    def __init__(self, go_to):
        super().__init__()
        self.go_to            = go_to
        self._current_result  = {}
        self._current_patient = {}
        self._current_doctor  = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Status bar ─────────────────────────────────
        status = QLabel("THYROSENSEX  ·  DIAGNOSTIC REPORT")
        status.setObjectName("status_bar")
        status.setFixedHeight(28)

        # ── Content ────────────────────────────────────
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(12)

        # Header
        lbl = QLabel("DIAGNOSTIC REPORT")
        lbl.setObjectName("section")
        title = QLabel("Session Summary")
        title.setObjectName("screen_title")

        # ── Report card ────────────────────────────────
        card = make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(0)

        self.row_values = {}
        rows = [
            ("Patient Name",      "—",                       "normal"),
            ("Patient ID",        "—",                       "accent"),
            ("Age / Gender",      "—",                       "normal"),
            ("Phone",             "—",                       "normal"),
            ("Date / Time",       "—",                       "normal"),
            ("Doctor",            "—",                       "normal"),
            ("Device ID",         "TSX-RPZ2-0042",           "normal"),
            ("Model Version",     "v2.1.4",                  "normal"),
            ("---", "", ""),
            ("Prediction",        "—",                       "warning"),
            ("Confidence",        "—",                       "warning"),
            ("Risk Level",        "—",                       "warning"),
            ("---", "", ""),
            ("Facial Flags",      "—",                       "normal"),
            ("Voice Anomalies",   "—",                       "normal"),
            ("Thermal Anomalies", "—",                       "normal"),
            ("Recommendation",    "Consult endocrinologist", "accent"),
        ]

        for key, val, style in rows:
            if key == "---":
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setStyleSheet(
                    "background:#21262d; border:none;"
                    "max-height:1px; margin:6px 0;"
                )
                card_layout.addWidget(line)
                continue

            row = QHBoxLayout()
            row.setContentsMargins(0, 4, 0, 4)

            k = QLabel(key)
            k.setStyleSheet("font-size:11px; color:#8b949e;")

            color = {
                "normal":  "#e6edf3",
                "warning": "#f0c040",
                "accent":  "#1f6feb",
            }.get(style, "#e6edf3")

            v = QLabel(val)
            v.setStyleSheet(
                f"font-size:11px; color:{color}; font-weight:500;"
            )
            v.setAlignment(Qt.AlignRight)

            row.addWidget(k)
            row.addStretch()
            row.addWidget(v)
            card_layout.addLayout(row)
            self.row_values[key] = v

        # ── Warning ────────────────────────────────────
        warning = QLabel(
            "⚠  Screening tool only. "
            "Confirm with a licensed medical professional."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet(
            "color:#484f58; font-size:10px; padding:4px 0;"
        )

        # ── Buttons ────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_save = QPushButton("Save PDF")
        btn_save.setObjectName("primary")
        btn_save.clicked.connect(self._save_pdf)

        btn_send = QPushButton("Send to Patient")
        btn_send.setObjectName("outline")
        btn_send.clicked.connect(self._send_report)

        btn_new = QPushButton("New Scan")
        btn_new.setObjectName("secondary")
        btn_new.clicked.connect(lambda: self.go_to("welcome"))

        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_send)
        btn_row.addWidget(btn_new)

        # ── Assemble content ───────────────────────────
        content_layout.addWidget(lbl)
        content_layout.addWidget(title)
        content_layout.addWidget(card)
        content_layout.addWidget(warning)
        content_layout.addStretch()
        content_layout.addLayout(btn_row)

        layout.addWidget(status)
        layout.addWidget(content)

    # ── Refresh with real data ─────────────────────────
    def refresh(self, result=None, patient=None, doctor=None):
        now = datetime.now().strftime("%d %b %Y  %H:%M")

        if patient:
            self._current_patient = patient
            self._set("Patient Name",  patient.get("name", "—"))
            self._set("Patient ID",    patient.get("patient_id", patient.get("id", "—")))
            self._set("Age / Gender",
                f"{patient.get('age','—')} yrs  ·  {patient.get('gender','—')}")
            self._set("Phone", patient.get("phone", "—"))

        if doctor:
            self._current_doctor = doctor
            self._set("Doctor", doctor.get("full_name", "—"))

        self._set("Date / Time", now)

        if result is None:
            return

        self._current_result = result
        prediction = result.get("prediction", "Unknown")
        confidence = result.get("confidence", 0.0)

        risk_map = {
            "Normal":          ("Low",      "#3ddc97"),
            "Hypothyroidism":  ("Moderate", "#f0c040"),
            "Hyperthyroidism": ("High",     "#ff4f5e"),
        }
        risk, color = risk_map.get(prediction, ("Unknown", "#e6edf3"))

        self._set_colored("Prediction", prediction, color)
        self._set_colored("Confidence", f"{confidence:.1f}%", color)
        self._set_colored("Risk Level", risk, color)

        # Features
        features = result.get("features", {})
        self._set("Facial Flags",
            str(features.get("Facial Flags", "—")))
        self._set("Voice Anomalies",
            f"Pitch: {features.get('Pitch','—')} Hz  "
            f"Jitter: {features.get('Jitter','—')}%")
        self._set("Thermal Anomalies",
            f"Mean: {features.get('Thermal Mean','—')}°C  "
            f"Max: {features.get('Thermal Max','—')}°C")

    def _set(self, key, value):
        if key in self.row_values:
            self.row_values[key].setText(str(value))

    def _set_colored(self, key, value, color):
        if key in self.row_values:
            self.row_values[key].setText(str(value))
            self.row_values[key].setStyleSheet(
                f"font-size:11px; color:{color}; font-weight:500;"
            )

    # ── Save PDF ───────────────────────────────────────
    def _save_pdf(self):
        try:
            from reports.generator import generate_report
            path = generate_report(
                self._current_result,
                patient=self._current_patient,
                doctor=self._current_doctor
            )
            msg = QMessageBox(self)
            msg.setWindowTitle("PDF Saved!")
            msg.setText(f"Report saved to:\n{path}")
            msg.setStyleSheet(
                "QMessageBox { background:#0d1117; color:#e6edf3; }"
                "QLabel { color:#e6edf3; font-size:12px; }"
                "QPushButton { background:#1f6feb; color:white;"
                "border-radius:6px; padding:6px 16px; }"
            )
            msg.exec_()
            self._last_pdf_path = path

        except Exception as e:
            QMessageBox.critical(self, "Error", f"PDF generation failed:\n{e}")

    # ── Send to Patient ────────────────────────────────
    def _send_report(self):
        patient = self._current_patient
        result  = self._current_result

        if not patient:
            QMessageBox.warning(self, "No Patient",
                "No patient selected.")
            return

        email = patient.get("email", "")
        phone = patient.get("phone", "")

        if not email and not phone:
            QMessageBox.warning(self, "No Contact",
                "Patient has no email or phone number.")
            return

        # Save PDF first if not already saved
        if not hasattr(self, '_last_pdf_path'):
            self._save_pdf()

        sent = []

        # Send email
        if email:
            try:
                from reports.email_sender import send_report_email
                send_report_email(
                    patient_email  = email,
                    patient_name   = patient.get("name", "Patient"),
                    pdf_path       = self._last_pdf_path,
                    prediction     = result.get("prediction", "—")
                )
                sent.append(f"Email → {email}")
            except Exception as e:
                print(f"Email error: {e}")

        # Send WhatsApp
        if phone:
            try:
                from reports.whatsapp_sender import send_whatsapp_report
                send_whatsapp_report(
                    patient_phone  = phone,
                    patient_name   = patient.get("name", "Patient"),
                    prediction     = result.get("prediction", "—"),
                    confidence     = result.get("confidence", 0.0)
                )
                sent.append(f"WhatsApp → {phone}")
            except Exception as e:
                print(f"WhatsApp error: {e}")

        if sent:
            msg = QMessageBox(self)
            msg.setWindowTitle("Report Sent!")
            msg.setText("Successfully sent to:\n" + "\n".join(sent))
            msg.setStyleSheet(
                "QMessageBox { background:#0d1117; color:#e6edf3; }"
                "QLabel { color:#e6edf3; }"
                "QPushButton { background:#1f6feb; color:white;"
                "border-radius:6px; padding:6px 16px; }"
            )
            msg.exec_()
        else:
            QMessageBox.warning(self, "Send Failed",
                "Could not send report. Check email/WhatsApp settings.")