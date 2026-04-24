from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox
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
        self.go_to = go_to

        self._current_result = {}
        self._current_patient = {}
        self._current_doctor = {}
        self._last_pdf_path = None

        self._build_ui()

    # ── UI ───────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("THYROSENSEX DIAGNOSTIC REPORT")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size:18px; font-weight:bold; color:#58a6ff;"
        )

        # ── Highlight ─────────────────────────
        self.highlight = make_card()
        hl_layout = QVBoxLayout(self.highlight)

        self.prediction_label = QLabel("—")
        self.prediction_label.setAlignment(Qt.AlignCenter)

        self.conf_bg = QFrame()
        self.conf_bg.setFixedHeight(8)

        self.conf_fill = QFrame(self.conf_bg)
        self.conf_fill.setFixedHeight(8)

        hl_layout.addWidget(QLabel("Prediction Summary"))
        hl_layout.addWidget(self.prediction_label)
        hl_layout.addWidget(self.conf_bg)

        # ── Details ──────────────────────────
        card = make_card()
        card_layout = QVBoxLayout(card)

        self.row_values = {}

        def add_row(key):
            row = QHBoxLayout()

            k = QLabel(key)
            k.setStyleSheet("color:#8b949e; font-size:11px;")

            v = QLabel("—")
            v.setStyleSheet("color:#d1d9e0; font-size:11px;")

            row.addWidget(k)
            row.addStretch()
            row.addWidget(v)

            card_layout.addLayout(row)
            self.row_values[key] = v

        rows = [
            "Patient Name", "Patient ID", "Age / Gender",
            "Phone", "Doctor", "Date / Time",
            "Prediction", "Confidence", "Risk Level",
            "Facial Flags", "Voice Anomalies", "Thermal Anomalies"
        ]

        for r in rows:
            add_row(r)

        warning = QLabel("⚠ Screening tool only. Consult a doctor.")
        warning.setAlignment(Qt.AlignCenter)

        # Buttons
        btn_row = QHBoxLayout()

        btn_save = QPushButton("Save PDF")
        btn_save.setObjectName("primary")
        btn_save.clicked.connect(self._save_pdf)

        btn_new = QPushButton("New Scan")
        btn_new.clicked.connect(lambda: self.go_to("welcome"))

        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_new)

        layout.addWidget(title)
        layout.addWidget(self.highlight)
        layout.addWidget(card)
        layout.addWidget(warning)
        layout.addLayout(btn_row)

    # ── REFRESH ─────────────────────────────
    def refresh(self, result=None, patient=None, doctor=None):
        now = datetime.now().strftime("%d %b %Y %H:%M")

        # Patient
        if patient:
            self._current_patient = patient
            self._set("Patient Name", patient.get("name", "—"))
            self._set("Patient ID", patient.get("patient_id", patient.get("id", "—")))
            self._set("Age / Gender",
                      f"{patient.get('age','—')} · {patient.get('gender','—')}")
            self._set("Phone", patient.get("phone", "—"))

        # Doctor
        if doctor:
            self._current_doctor = doctor
            self._set("Doctor", doctor.get("full_name", "—"))

        self._set("Date / Time", now)

        if not result:
            return

        self._current_result = result

        prediction = result.get("prediction", "Unknown")
        confidence = result.get("confidence", 0)

        if confidence <= 1:
            confidence *= 100

        # Colors
        if prediction == "Normal":
            color = "#3ddc97"
            risk = "Low"
        elif prediction == "Hyperthyroid":
            color = "#ff4f5e"
            risk = "High"
        else:
            color = "#f0c040"
            risk = "Moderate"

        # Prediction UI
        self.prediction_label.setText(prediction)
        self.prediction_label.setStyleSheet(
            f"font-size:22px; font-weight:bold; color:{color};"
        )

        # Confidence bar (FIXED)
        total_width = 200
        self.conf_bg.setFixedWidth(total_width)

        fill_width = int((confidence / 100) * total_width)
        self.conf_fill.setFixedWidth(max(fill_width, 5))
        self.conf_fill.setStyleSheet(f"background:{color}; border-radius:4px;")

        # Rows
        self._set("Prediction", prediction)
        self._set("Confidence", f"{confidence:.1f}%")
        self._set("Risk Level", risk)

        # Features
        features = result.get("features", {})

        # Face
        face_flag = "Detected" if features.get("face_area", 0) > 0 else "Not Detected"
        self._set("Facial Flags", face_flag)

        # Voice
        pitch = features.get("pitch_mean", 0)
        voice_text = f"Pitch: {pitch:.1f} Hz" if pitch > 0 else "No voice data"
        self._set("Voice Anomalies", voice_text)

        # Thermal
        temp = features.get("thermal_mean", 0)
        thermal_text = f"Mean: {temp:.1f} °C" if temp > 0 else "No thermal data"
        self._set("Thermal Anomalies", thermal_text)

    def _set(self, key, value):
        if key in self.row_values:
            self.row_values[key].setText(str(value))

    # ── SAVE PDF ─────────────────────────────
    def _save_pdf(self):
        try:
            from reports.generator import generate_report

            path = generate_report(
                self._current_result,
                patient=self._current_patient,
                doctor=self._current_doctor
            )

            self._last_pdf_path = path

            QMessageBox.information(
                self,
                "Saved",
                f"PDF saved successfully!\n\n{path}"
            )

        except Exception as e:
            print("PDF Error:", e)
            QMessageBox.critical(self, "Error", "Failed to generate PDF")