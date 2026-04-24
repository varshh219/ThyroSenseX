from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt


def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f


class LoginScreen(QWidget):
    def __init__(self, go_to, on_patient_selected):
        super().__init__()
        self.go_to = go_to
        self.on_patient_selected = on_patient_selected
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        # ── Header ─────────────────────────────
        title_row = QHBoxLayout()

        for text, color in [
            ("Thyro", "#e8edf7"),
            ("Sense", "#4f8dff"),
            ("X", "#e8edf7")
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"font-size:22px; font-weight:bold; color:{color};"
            )
            title_row.addWidget(lbl)

        title_row.addStretch()

        tag = QLabel("PATIENT MANAGEMENT")
        tag.setObjectName("section")

        # ── Search ─────────────────────────────
        search_row = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or Patient ID...")
        self.search_input.textChanged.connect(self._search)

        btn_new = QPushButton("+ New Patient")
        btn_new.setObjectName("primary")
        btn_new.setFixedWidth(130)
        btn_new.clicked.connect(lambda: self.go_to("patient_register"))

        search_row.addWidget(self.search_input)
        search_row.addWidget(btn_new)

        # ── Patient List ───────────────────────
        lbl = QLabel("SELECT PATIENT")
        lbl.setObjectName("section")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.addStretch()

        scroll.setWidget(self.list_widget)

        # ── Layout ────────────────────────────
        layout.addLayout(title_row)
        layout.addWidget(tag)
        layout.addLayout(search_row)
        layout.addWidget(lbl)
        layout.addWidget(scroll)

    # ── REFRESH ─────────────────────────────
    def refresh(self):
        self.search_input.clear()   # ✅ clear search
        self._load_patients()

    # ── LOAD PATIENTS ───────────────────────
    def _load_patients(self, query=""):
        try:
            from database.database import get_all_patients, search_patients

            # Clear list
            while self.list_layout.count() > 1:
                item = self.list_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Fetch
            if query.strip():
                patients = search_patients(query.strip())
            else:
                patients = get_all_patients()

            if not patients:
                empty = QLabel("No patients found.\nClick '+ New Patient'")
                empty.setAlignment(Qt.AlignCenter)
                self.list_layout.insertWidget(0, empty)
                return

            # Latest first
            for patient in reversed(patients):
                card = self._make_patient_card(patient)
                self.list_layout.insertWidget(0, card)

        except Exception as e:
            print("[LoginScreen] Load error:", e)

    # ── PATIENT CARD ───────────────────────
    def _make_patient_card(self, patient):
        card = make_card()
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)

        # Avatar
        name_text = patient.get("name", "Unknown")
        initials = "".join(w[0].upper() for w in name_text.split()[:2])

        avatar = QLabel(initials)
        avatar.setFixedSize(44, 44)
        avatar.setAlignment(Qt.AlignCenter)

        # Info
        info = QVBoxLayout()

        name = QLabel(name_text)

        patient_id = patient.get("patient_id", "N/A")
        age = patient.get("age", "--")
        gender = patient.get("gender", "--")

        details = QLabel(f"{patient_id} · {age} yrs · {gender}")

        scans = patient.get("scans", [])
        if scans:
            last = scans[-1]
            last_scan = QLabel(
                f"Last: {last.get('date','--')} — {last.get('prediction','--')}"
            )
        else:
            last_scan = QLabel("No scans yet")

        info.addWidget(name)
        info.addWidget(details)
        info.addWidget(last_scan)

        # Button
        btn = QPushButton("Select")
        btn.setFixedWidth(70)
        btn.clicked.connect(lambda _, p=patient: self._select_patient(p))

        card_layout.addWidget(avatar)
        card_layout.addLayout(info)
        card_layout.addStretch()
        card_layout.addWidget(btn)

        return card

    # ── SEARCH ─────────────────────────────
    def _search(self, query):
        self._load_patients(query)

    # ── SELECT ─────────────────────────────
    def _select_patient(self, patient):
        print(f"[PATIENT] Selected: {patient.get('name')}")

        self.on_patient_selected(patient)
        self.go_to("welcome")