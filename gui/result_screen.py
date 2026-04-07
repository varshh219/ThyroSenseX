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
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        # ── Header ─────────────────────────────────────
        lbl = QLabel("STEP 3 OF 3 — RESULTS")
        lbl.setObjectName("section")
        title = QLabel("Diagnostic Report")
        title.setObjectName("screen_title")

        # ── Result hero card ───────────────────────────
        hero = make_card()
        hero.setStyleSheet(
            "background:#1a2a10; border:1px solid #2a5a28;"
            "border-radius:12px;"
        )
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(20, 16, 20, 16)

        icon = QLabel("⚠")
        icon.setStyleSheet("font-size:28px;")

        info = QVBoxLayout()
        pred_lbl = QLabel("PREDICTED CONDITION")
        pred_lbl.setStyleSheet(
            "font-size:10px; color:#7a90b8; letter-spacing:2px;"
        )
        self.pred_name = QLabel("Hypothyroidism")
        self.pred_name.setStyleSheet(
            "font-size:22px; font-weight:bold; color:#f0c040;"
        )
        self.conf_lbl = QLabel("Confidence: 82.4%")
        self.conf_lbl.setStyleSheet("font-size:11px; color:#7a90b8;")

        info.addWidget(pred_lbl)
        info.addWidget(self.pred_name)
        info.addWidget(self.conf_lbl)

        hero_layout.addWidget(icon)
        hero_layout.addLayout(info)
        hero_layout.addStretch()

        # ── Probability bars ───────────────────────────
        prob_lbl = QLabel("PROBABILITY DISTRIBUTION")
        prob_lbl.setObjectName("section")

        bars_card = make_card()
        bars_layout = QVBoxLayout(bars_card)
        bars_layout.setContentsMargins(16, 12, 16, 12)
        bars_layout.setSpacing(10)

        self.prob_bars = {}
        for name, pct, color in [
            ("Normal thyroid",   11, "#3ddc97"),
            ("Hypothyroidism",   82, "#f0c040"),
            ("Hyperthyroidism",   7, "#ff4f5e"),
        ]:
            row = QHBoxLayout()
            n = QLabel(name)
            n.setFixedWidth(140)
            n.setStyleSheet("font-size:11px; color:#7a90b8;")

            bar = QProgressBar()
            bar.setMaximum(100)
            bar.setValue(pct)
            bar.setTextVisible(False)
            bar.setFixedHeight(6)
            bar.setStyleSheet(
                f"QProgressBar{{background:#0a0e14;border:none;border-radius:3px;}}"
                f"QProgressBar::chunk{{background:{color};border-radius:3px;}}"
            )

            p = QLabel(f"{pct}%")
            p.setFixedWidth(36)
            p.setAlignment(Qt.AlignRight)
            p.setStyleSheet(f"font-size:11px; color:{color};")

            row.addWidget(n)
            row.addWidget(bar)
            row.addWidget(p)
            bars_layout.addLayout(row)
            self.prob_bars[name] = (bar, p)

        # ── Features grid ──────────────────────────────
        feat_lbl = QLabel("EXTRACTED FEATURES")
        feat_lbl.setObjectName("section")

        feat_card = make_card()
        feat_layout = QHBoxLayout(feat_card)
        feat_layout.setContentsMargins(16, 12, 16, 12)
        feat_layout.setSpacing(12)

        features = [
            ("Pitch",        "148 Hz",  "↓ Below avg"),
            ("Jitter",       "1.2%",    "Within range"),
            ("Thermal max",  "35.2 °C", "↓ Low"),
            ("Facial flags", "4 / 10",  "Puffy, dry…"),
            ("Shimmer",      "3.8%",    "↑ Elevated"),
            ("HNR",          "18.4 dB", "Normal"),
        ]
        for label, val, sub in features:
            col = QVBoxLayout()
            l = QLabel(label)
            l.setStyleSheet(
                "font-size:9px; color:#4a5a78;"
                "letter-spacing:1px; text-transform:uppercase;"
            )
            v = QLabel(val)
            v.setStyleSheet(
                "font-size:15px; font-weight:bold; color:#e8edf7;"
            )
            s = QLabel(sub)
            s.setStyleSheet("font-size:10px; color:#7a90b8;")
            col.addWidget(l)
            col.addWidget(v)
            col.addWidget(s)
            feat_layout.addLayout(col)

        # ── Buttons ────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_report = QPushButton("View Full Report")
        btn_report.setObjectName("outline")
        btn_report.clicked.connect(lambda: self.go_to("report"))

        btn_new = QPushButton("New Scan")
        btn_new.setObjectName("secondary")
        btn_new.clicked.connect(lambda: self.go_to("welcome"))

        btn_row.addWidget(btn_report)
        btn_row.addWidget(btn_new)

        # ── Assemble ───────────────────────────────────
        layout.addWidget(lbl)
        layout.addWidget(title)
        layout.addWidget(hero)
        layout.addWidget(prob_lbl)
        layout.addWidget(bars_card)
        layout.addWidget(feat_lbl)
        layout.addWidget(feat_card)
        layout.addStretch()
        layout.addLayout(btn_row)

    def update_result(self, prediction, confidence, probabilities):
        """
        Call this from processing screen once model runs.
        prediction   : 'Normal' | 'Hypothyroidism' | 'Hyperthyroidism'
        confidence   : float 0-100
        probabilities: dict {'Normal': x, 'Hypothyroidism': y, 'Hyperthyroidism': z}
        """
        colors = {
            "Normal":          "#3ddc97",
            "Hypothyroidism":  "#f0c040",
            "Hyperthyroidism": "#ff4f5e",
        }
        color = colors.get(prediction, "#e8edf7")
        self.pred_name.setText(prediction)
        self.pred_name.setStyleSheet(
            f"font-size:22px; font-weight:bold; color:{color};"
        )
        self.conf_lbl.setText(f"Confidence: {confidence:.1f}%")

        for name, (bar, pct_lbl) in self.prob_bars.items():
            val = int(probabilities.get(name, 0))
            bar.setValue(val)
            pct_lbl.setText(f"{val}%")