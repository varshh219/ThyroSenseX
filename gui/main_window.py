from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt

from gui.styles import STYLE
from gui.doctor_login import DoctorLoginScreen
from gui.login_screen import LoginScreen
from gui.patient_screen import PatientRegisterScreen
from gui.welcome_screen import WelcomeScreen
from gui.capture_screen import CaptureScreen
from gui.processing_screen import ProcessingScreen
from gui.result_screen import ResultScreen
from gui.report_screen import ReportScreen


class MainWindow(QMainWindow):
    def __init__(self, fullscreen=False):
        super().__init__()

        self.setWindowTitle("ThyroSenseX")
        self.setMinimumSize(480, 680)
        self.setStyleSheet(STYLE)

        self._current_doctor  = None
        self._current_patient = None
        self._last_result     = {}

        # ── Stack ───────────────────────────
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ── Screens ─────────────────────────
        self.doctor_login  = DoctorLoginScreen(self.go_to, self._on_doctor_login)
        self.patient_login = LoginScreen(self.go_to, self._on_patient_selected)
        self.patient_reg   = PatientRegisterScreen(self.go_to)
        self.welcome       = WelcomeScreen(self.go_to)
        self.capture       = CaptureScreen(self.go_to)
        self.processing    = ProcessingScreen(self.go_to, self._on_prediction)
        self.result        = ResultScreen(self.go_to)
        self.report        = ReportScreen(self.go_to)

        self.screens = {
            "doctor_login":     self.doctor_login,
            "patient_login":    self.patient_login,
            "patient_register": self.patient_reg,
            "welcome":          self.welcome,
            "capture":          self.capture,
            "processing":       self.processing,
            "result":           self.result,
            "report":           self.report,
        }

        for screen in self.screens.values():
            self.stack.addWidget(screen)

        if fullscreen:
            self.showFullScreen()
            self.setCursor(Qt.BlankCursor)

        self.go_to("doctor_login")

    # ── Navigation ───────────────────────────
    def go_to(self, name):
        widget = self.screens.get(name)
        if not widget:
            print(f"[MainWindow] Unknown screen: '{name}'")
            return

        self.stack.setCurrentWidget(widget)

        # ── Screen Logic ─────────────────────
        if name == "patient_login":
            self.patient_login.refresh()

        elif name == "capture":
            self.capture.reset()
            self.capture.start_preview()

        elif name == "processing":
            if not self._current_patient:
                print("[MainWindow] No patient selected")
                self.go_to("patient_login")
                return

            # ✅ PASS CAPTURE DATA
            self.processing.start(
                self._current_patient,
                self.capture.image_bytes,
                self.capture.thermal_bytes,
                self.capture.audio_bytes,
                self.capture.audio_ok
            )

        elif name == "report":
            self.report.refresh(
                result=self._last_result,
                patient=self._current_patient,
                doctor=self._current_doctor,
            )

    # ── Callbacks ───────────────────────────
    def _on_doctor_login(self, doctor):
        self._current_doctor = doctor
        self.patient_reg.set_doctor(doctor)

        print(f"[MainWindow] Doctor logged in: {doctor.get('full_name','?')}")

    def _on_patient_selected(self, patient):
        self._current_patient = patient
        self.welcome.set_patient(patient)

        print(f"[MainWindow] Patient selected: {patient.get('name','?')}")

    def _on_prediction(self, result: dict, patient=None):
        self._last_result = result or {}

        if patient:
            self._current_patient = patient

        # Update result screen
        self.result.update_result(self._last_result)

        # Move to result screen
        self.go_to("result")