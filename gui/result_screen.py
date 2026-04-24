from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QFrame
)
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
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Diagnostic Result")
        title.setObjectName("screen_title")

        layout.addWidget(title)

        # ── Prediction ─────────────────────
        self.pred_lbl = QLabel("—")
        self.pred_lbl.setAlignment(Qt.AlignCenter)

        self.risk_lbl = QLabel("Risk: —")
        self.risk_lbl.setAlignment(Qt.AlignCenter)

        self.conf_bar = QProgressBar()
        self.conf_bar.setRange(0, 100)

        layout.addWidget(self.pred_lbl)
        layout.addWidget(self.risk_lbl)
        layout.addWidget(self.conf_bar)

        # ── Details ────────────────────────
        self.details = {}

        for key in ["Mean Temp", "Temp Range", "Image", "Audio"]:
            row = QHBoxLayout()
            k = QLabel(key)
            v = QLabel("—")
            row.addWidget(k)
            row.addStretch()
            row.addWidget(v)
            layout.addLayout(row)
            self.details[key] = v

        # Buttons
        btn = QPushButton("Full Report")
        btn.clicked.connect(lambda: self.go_to("report"))

        layout.addWidget(btn)

    # ── UPDATE RESULT ─────────────────────
    def update_result(self, result):
        prediction = result.get("prediction", "Unknown")
        confidence = result.get("confidence", 0)

        if confidence <= 1:
            confidence *= 100

        color, risk = RESULT_META.get(prediction, ("#fff", "—"))

        self.pred_lbl.setText(prediction)
        self.pred_lbl.setStyleSheet(f"font-size:24px; color:{color};")

        self.risk_lbl.setText(f"Risk: {risk}")

        self.conf_bar.setValue(int(confidence))

        # ── Features ─────────────────────
        feat = result.get("features", {})

        mean = feat.get("thermal_mean", "—")
        tmin = feat.get("thermal_min", "—")
        tmax = feat.get("thermal_max", "—")

        self.details["Mean Temp"].setText(
            f"{mean} °C" if mean != "—" else "—"
        )

        self.details["Temp Range"].setText(
            f"{tmin} – {tmax} °C" if tmin != "—" else "—"
        )

        self.details["Image"].setText(feat.get("image", "—"))

        audio_ok = feat.get("audio_ok", False)

        self.details["Audio"].setText(
            "✓ Recorded" if audio_ok else "⚠ Not captured"
        )