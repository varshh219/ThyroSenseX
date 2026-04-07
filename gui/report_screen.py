from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from datetime import datetime


def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f


class ReportScreen(QWidget):
    def __init__(self, go_to):
        super().__init__()
        self.go_to = go_to
        self._current_result  = {}
        self._current_patient = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        # ── Header ─────────────────────────────────────
        lbl = QLabel("DIAGNOSTIC REPORT")
        lbl.setObjectName("section")
        title = QLabel("Session Summary")
        title.setObjectName("screen_title")

        # ── Report card ────────────────────────────────
        card = make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(0)

        self.row_values = {}
        rows = [
            ("Patient Name",     "—",                       "normal"),
            ("Patient ID",       "—",                       "normal"),
            ("Age / Gender",     "—",                       "normal"),
            ("Date / Time",      "—",                       "normal"),
            ("Device ID",        "TSX-RPZ2-0042",           "normal"),
            ("Scan Duration",    "43.7 s",                  "normal"),
            ("Model Version",    "v2.1.4",                  "normal"),
            ("---", "", ""),
            ("Prediction",       "—",                       "warning"),
            ("Confidence",       "—",                       "warning"),
            ("Risk Level",       "—",                       "warning"),
            ("---", "", ""),
            ("Facial flags",     "4 of 10",                 "normal"),
            ("Voice anomalies",  "Shimmer ↑, Pitch ↓",     "normal"),
            ("Thermal anomalies","Low neck temp",            "normal"),
            ("Recommendation",   "Consult endocrinologist", "accent"),
        ]

        for key, val, style in rows:
            if key == "---":
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setStyleSheet(
                    "color:#1e2d45; background:#1e2d45;"
                    "border:none; max-height:1px; margin:6px 0;"
                )
                card_layout.addWidget(line)
                continue

            row = QHBoxLayout()
            k = QLabel(key)
            k.setStyleSheet("font-size:12px; color:#7a90b8;")

            color = {
                "normal":  "#e8edf7",
                "warning": "#f0c040",
                "accent":  "#4f8dff",
            }.get(style, "#e8edf7")

            v = QLabel(val)
            v.setStyleSheet(
                f"font-size:12px; color:{color}; font-weight:500;"
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
            "Confirm results with a licensed medical professional."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color:#4a5a78; font-size:10px;")

        # ── Buttons ────────────────────────────────────
        btn_row = QHBoxLayout()

        btn_save = QPushButton("Save PDF Report")
        btn_save.setObjectName("primary")
        btn_save.clicked.connect(self._save_pdf)

        btn_new = QPushButton("New Scan")
        btn_new.setObjectName("secondary")
        btn_new.clicked.connect(lambda: self.go_to("login"))

        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_new)

        # ── Assemble ───────────────────────────────────
        layout.addWidget(lbl)
        layout.addWidget(title)
        layout.addWidget(card)
        layout.addWidget(warning)
        layout.addStretch()
        layout.addLayout(btn_row)

    def refresh(self, result=None, patient=None):
        """Update report with real prediction and patient details."""
        now = datetime.now().strftime("%d %b %Y  %H:%M")
        if "Date / Time" in self.row_values:
            self.row_values["Date / Time"].setText(now)

        # ── Patient details ────────────────────────────
        if patient:
            self._current_patient = patient
            if "Patient Name" in self.row_values:
                self.row_values["Patient Name"].setText(patient["name"])
            if "Patient ID" in self.row_values:
                self.row_values["Patient ID"].setText(patient["id"])
            if "Age / Gender" in self.row_values:
                self.row_values["Age / Gender"].setText(
                    f"{patient['age']} yrs  ·  {patient['gender']}"
                )

        if result is None:
            return

        # ── Prediction details ─────────────────────────
        self._current_result = result
        prediction = result.get("prediction", "Unknown")
        confidence = result.get("confidence", 0.0)

        risk_map = {
            "Normal":          ("Low",      "#3ddc97"),
            "Hypothyroidism":  ("Moderate", "#f0c040"),
            "Hyperthyroidism": ("High",     "#ff4f5e"),
        }
        risk, color = risk_map.get(prediction, ("Unknown", "#e8edf7"))

        self.row_values["Prediction"].setText(prediction)
        self.row_values["Prediction"].setStyleSheet(
            f"font-size:12px; color:{color}; font-weight:500;"
        )
        self.row_values["Confidence"].setText(f"{confidence:.1f}%")
        self.row_values["Confidence"].setStyleSheet(
            f"font-size:12px; color:{color}; font-weight:500;"
        )
        self.row_values["Risk Level"].setText(risk)
        self.row_values["Risk Level"].setStyleSheet(
            f"font-size:12px; color:{color}; font-weight:500;"
        )

    def _save_pdf(self):
        from reports.generator import generate_report
        from PyQt5.QtWidgets import QMessageBox
        import os

        path = generate_report(
            self._current_result,
            patient=self._current_patient
        )

        msg = QMessageBox()
        msg.setWindowTitle("Report Saved!")
        msg.setText(f"PDF saved to:\n{os.path.abspath(path)}")
        msg.setStyleSheet("background:#0a0e14; color:#e8edf7;")
        msg.exec_()