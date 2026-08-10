from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QFrame
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f


RESULT_META = {
    "Normal":          ("#3ddc97", "Low"),
    "Hypothyroidism":  ("#f0c040", "Moderate"),
    "Hyperthyroidism": ("#ff4f5e", "High"),
    "Error":           ("#8b949e", "—"),
}


class ResultScreen(QWidget):

    def __init__(self, go_to):
        super().__init__()

        self.go_to = go_to

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        layout.setSpacing(15)

        # Logo

        logo = QLabel()

        logo.setPixmap(
            QPixmap(
                "gui/resources/logos/thyroid_logo.png"
            ).scaled(
                90,
                90,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        logo.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            logo
        )

        # Title

        title = QLabel(
            "AI Diagnostic Result"
        )

        title.setObjectName(
            "screen_title"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title
        )

        # Result Card

        result_card = make_card()

        result_layout = QVBoxLayout(
            result_card
        )

        self.pred_lbl = QLabel("—")

        self.pred_lbl.setAlignment(
            Qt.AlignCenter
        )

        self.pred_lbl.setStyleSheet("""
            font-size:32px;
            font-weight:bold;
        """)

        self.risk_lbl = QLabel(
            "Risk: —"
        )

        self.risk_lbl.setAlignment(
            Qt.AlignCenter
        )

        self.risk_lbl.setStyleSheet("""
            font-size:16px;
        """)

        self.conf_bar = QProgressBar()

        self.conf_bar.setRange(
            0,
            100
        )

        result_layout.addWidget(
            self.pred_lbl
        )

        result_layout.addWidget(
            self.risk_lbl
        )

        result_layout.addWidget(
            self.conf_bar
        )

        layout.addWidget(
            result_card
        )

        # Details Card

        details_card = make_card()

        details_layout = QVBoxLayout(
            details_card
        )

        self.details = {}

        for key in [
            "Age",
            "Weight",
            "Mean Temp",
            "Temp Range",
            "Image",
            "Audio"
        ]:

            row = QHBoxLayout()

            k = QLabel(key)

            k.setStyleSheet("""
                color:#8b949e;
                font-size:11px;
            """)

            v = QLabel("—")

            row.addWidget(k)

            row.addStretch()

            row.addWidget(v)

            details_layout.addLayout(
                row
            )

            self.details[key] = v

        layout.addWidget(
            details_card
        )

        # Button

        btn = QPushButton(
            "📄 View Full Report"
        )

        btn.setObjectName(
            "primary"
        )

        btn.setMinimumHeight(
            50
        )

        btn.clicked.connect(
            lambda: self.go_to(
                "report"
            )
        )

        layout.addStretch()

        layout.addWidget(
            btn
        )

    def update_result(self, result):

        prediction = result.get(
            "prediction",
            "Unknown"
        )

        confidence = result.get(
            "confidence",
            0
        )

        if confidence <= 1:
            confidence *= 100

        color, risk = RESULT_META.get(
            prediction,
            ("#fff", "—")
        )

        self.pred_lbl.setText(
            prediction
        )

        self.pred_lbl.setStyleSheet(
            f"""
            font-size:32px;
            font-weight:bold;
            color:{color};
            """
        )

        self.risk_lbl.setText(
            f"Risk Level: {risk}"
        )

        self.conf_bar.setValue(
            int(confidence)
        )

        patient = result.get(
            "patient",
            {}
        )

        self.details["Age"].setText(
            str(
                patient.get(
                    "age",
                    "—"
                )
            )
        )

        weight = patient.get(
            "weight"
        )

        self.details["Weight"].setText(
            f"{weight} kg"
            if weight
            else "—"
        )

        feat = result.get(
            "features",
            {}
        )

        mean = feat.get(
            "thermal_mean"
        )

        tmin = feat.get(
            "thermal_min"
        )

        tmax = feat.get(
            "thermal_max"
        )

        self.details["Mean Temp"].setText(
            f"{mean:.1f} °C"
            if isinstance(
                mean,
                (int, float)
            )
            else "—"
        )

        self.details["Temp Range"].setText(
            f"{tmin:.1f} – {tmax:.1f} °C"
            if isinstance(
                tmin,
                (int, float)
            )
            and isinstance(
                tmax,
                (int, float)
            )
            else "—"
        )

        self.details["Image"].setText(
            result.get(
                "image",
                "—"
            )
        )

        audio_text = result.get(
            "audio",
            ""
        )

        self.details["Audio"].setText(
            "✓ Recorded"
            if audio_text == "Recorded"
            else "⚠ Not captured"
        )