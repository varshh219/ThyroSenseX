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
        self.go_to               = go_to
        self.on_patient_selected = on_patient_selected
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        # ── Header ─────────────────────────────────────
        title_row = QHBoxLayout()
        t1 = QLabel("Thyro")
        t1.setStyleSheet("font-size:22px; font-weight:bold; color:#e8edf7;")
        t2 = QLabel("Sense")
        t2.setStyleSheet("font-size:22px; font-weight:bold; color:#4f8dff;")
        t3 = QLabel("X")
        t3.setStyleSheet("font-size:22px; font-weight:bold; color:#e8edf7;")
        title_row.addWidget(t1)
        title_row.addWidget(t2)
        title_row.addWidget(t3)
        title_row.addStretch()

        tag = QLabel("PATIENT MANAGEMENT")
        tag.setObjectName("section")

        # ── Search bar ─────────────────────────────────
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by name or Patient ID..."
        )
        self.search_input.setStyleSheet(
            "background:#161c28; border:1px solid #1e2d45;"
            "border-radius:8px; padding:10px 14px;"
            "font-size:12px; color:#e8edf7;"
        )
        self.search_input.textChanged.connect(self._search)

        btn_new = QPushButton("+ New Patient")
        btn_new.setObjectName("primary")
        btn_new.setFixedWidth(130)
        btn_new.clicked.connect(lambda: self.go_to("patient_register"))

        search_row.addWidget(self.search_input)
        search_row.addWidget(btn_new)

        # ── Patient list ───────────────────────────────
        lbl = QLabel("SELECT PATIENT")
        lbl.setObjectName("section")

        # Scroll area for patient cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border:none; background:transparent; }"
        )

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.addStretch()

        scroll.setWidget(self.list_widget)

        # ── Assemble ───────────────────────────────────
        layout.addLayout(title_row)
        layout.addWidget(tag)
        layout.addLayout(search_row)
        layout.addWidget(lbl)
        layout.addWidget(scroll)

    def refresh(self):
        """Reload patient list when screen is shown."""
        self._load_patients()

    def _load_patients(self, query=""):
        """Load and display patients."""
        from data.database import get_all_patients, search_patients

        # Clear existing cards
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get patients
        if query:
            patients = search_patients(query)
        else:
            patients = get_all_patients()

        if not patients:
            empty = QLabel(
                "No patients found.\nClick '+ New Patient' to register."
            )
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color:#4a5a78; font-size:12px;")
            self.list_layout.insertWidget(0, empty)
            return

        # Show newest first
        for patient in reversed(patients):
            card = self._make_patient_card(patient)
            self.list_layout.insertWidget(0, card)

    def _make_patient_card(self, patient):
        """Create a clickable patient card."""
        card = make_card()
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)

        # Avatar circle with initials
        initials = "".join(
            w[0].upper() for w in patient["name"].split()[:2]
        )
        avatar = QLabel(initials)
        avatar.setFixedSize(44, 44)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            "background:#1a2a4a; border-radius:22px;"
            "font-size:14px; font-weight:bold; color:#4f8dff;"
        )

        # Patient info
        info = QVBoxLayout()
        name = QLabel(patient["name"])
        name.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#e8edf7;"
        )
        details = QLabel(
            f"{patient['id']}  ·  {patient['age']} yrs  "
            f"·  {patient['gender']}"
        )
        details.setStyleSheet("font-size:11px; color:#7a90b8;")

        # Last scan
        scans = patient.get("scans", [])
        if scans:
            last = scans[-1]
            last_scan = QLabel(
                f"Last scan: {last['date']}  —  {last['prediction']}"
            )
        else:
            last_scan = QLabel("No scans yet")
        last_scan.setStyleSheet("font-size:10px; color:#4a5a78;")

        info.addWidget(name)
        info.addWidget(details)
        info.addWidget(last_scan)

        # Select button
        btn = QPushButton("Select")
        btn.setObjectName("secondary")
        btn.setFixedWidth(70)
        btn.clicked.connect(
            lambda _, p=patient: self._select_patient(p)
        )

        card_layout.addWidget(avatar)
        card_layout.addLayout(info)
        card_layout.addStretch()
        card_layout.addWidget(btn)

        return card

    def _search(self, query):
        """Live search as user types."""
        self._load_patients(query)

    def _select_patient(self, patient):
        """Called when a patient is selected."""
        print(f"Selected: {patient['name']} ({patient['id']})")
        self.on_patient_selected(patient)
        self.go_to("welcome")