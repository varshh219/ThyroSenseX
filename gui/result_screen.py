from PyQt5.QtWidgets import (
QWidget, QVBoxLayout, QHBoxLayout,
QLabel, QPushButton, QProgressBar, QFrame
)
from PyQt5.QtCore import Qt

def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f

class ResultScreen(QWidget):
    def __init__(self, go_to):
        super().__init__()
        self.go_to = go_to
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        lbl = QLabel("STEP 3 OF 3 — RESULTS")
        title = QLabel("Diagnostic Report")

        hero = make_card()
        hero_layout = QHBoxLayout(hero)

        self.pred_name = QLabel("—")
        self.pred_name.setStyleSheet("font-size:22px; font-weight:bold;")

        self.conf_lbl = QLabel("Confidence: —")

        info = QVBoxLayout()
        info.addWidget(self.pred_name)
        info.addWidget(self.conf_lbl)

        hero_layout.addLayout(info)

        # Probabilities
        self.prob_bars = {}
        for name in ["Normal", "Hypothyroidism", "Hyperthyroidism"]:
            row = QHBoxLayout()

            label = QLabel(name)

            bar = QProgressBar()
            bar.setMaximum(100)

            pct = QLabel("0%")

            row.addWidget(label)
            row.addWidget(bar)
            row.addWidget(pct)

            layout.addLayout(row)
            self.prob_bars[name] = (bar, pct)

        btn_report = QPushButton("View Report")
        btn_report.clicked.connect(lambda: self.go_to("report"))

        btn_new = QPushButton("New Scan")
        btn_new.clicked.connect(lambda: self.go_to("welcome"))

        layout.addWidget(lbl)
        layout.addWidget(title)
        layout.addWidget(hero)
        layout.addWidget(btn_report)
        layout.addWidget(btn_new)

    def update_result(self, prediction, confidence, probabilities):
        colors = {
            "Normal": "#3ddc97",
            "Hypothyroidism": "#f0c040",
            "Hyperthyroidism": "#ff4f5e"
        }

        color = colors.get(prediction, "#ffffff")

        self.pred_name.setText(prediction)
        self.pred_name.setStyleSheet(f"font-size:22px; color:{color};")

        self.conf_lbl.setText(f"Confidence: {confidence:.1f}%")

        for name, (bar, lbl) in self.prob_bars.items():
            val = int(probabilities.get(name, 0))
            bar.setValue(val)
            lbl.setText(f"{val}%")
