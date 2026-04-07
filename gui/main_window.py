from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt

from gui.welcome_screen    import WelcomeScreen
from gui.capture_screen    import CaptureScreen
from gui.processing_screen import ProcessingScreen
from gui.result_screen     import ResultScreen
from gui.report_screen     import ReportScreen
from gui.login_screen      import LoginScreen
from gui.patient_screen    import PatientRegisterScreen
from gui.styles            import STYLE


class MainWindow(QMainWindow):
    def __init__(self, fullscreen=False):
        super().__init__()
        self.setWindowTitle("ThyroSenseX")
        self.setMinimumSize(480, 680)
        self.setStyleSheet(STYLE)

        # ── Current patient ────────────────────────────
        self._current_patient = None
        self._last_result     = None

        # ── Stacked widget ─────────────────────────────
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ── Create screens ─────────────────────────────
        self.login    = LoginScreen(
            self.go_to,
            on_patient_selected=self._on_patient_selected
        )
        self.register = PatientRegisterScreen(self.go_to)
        self.welcome  = WelcomeScreen(self.go_to)
        self.capture  = CaptureScreen(self.go_to)
        self.processing = ProcessingScreen(
            self.go_to,
            on_result=self._on_prediction
        )
        self.result   = ResultScreen(self.go_to)
        self.report   = ReportScreen(self.go_to)

        # ── Add to stack ───────────────────────────────
        self.screens = {
            "login":             self.login,
            "patient_register":  self.register,
            "welcome":           self.welcome,
            "capture":           self.capture,
            "processing":        self.processing,
            "result":            self.result,
            "report":            self.report,
        }
        for widget in self.screens.values():
            self.stack.addWidget(widget)

        # ── Fullscreen on Pi ───────────────────────────
        if fullscreen:
            self.showFullScreen()
            self.setCursor(Qt.BlankCursor)

        # ── Start on login screen ──────────────────────
        self.go_to("login")

    def go_to(self, name):
        """Navigate to a screen by name."""
        widget = self.screens.get(name)
        if not widget:
            print(f"Screen '{name}' not found!")
            return

        self.stack.setCurrentWidget(widget)

        # Screen specific actions
        if name == "login":
            self.login.refresh()

        if name == "processing":
            self.processing.start()

        if name == "capture":
            self.capture.reset()

        if name == "report":
            self.report.refresh(
                self._last_result,
                self._current_patient
            )

    def _on_patient_selected(self, patient):
        """Called when patient is selected from login screen."""
        self._current_patient = patient
        print(f"Current patient: {patient['name']} ({patient['id']})")

        # Update welcome screen with patient name
        self.welcome.set_patient(patient)

    def _on_prediction(self, result):
        """Called when model finishes prediction."""
        self._last_result = result

        # Save scan to patient history
        if self._current_patient:
            from data.database import save_scan_result
            save_scan_result(
                self._current_patient["id"],
                result
            )

        # Update result screen
        self.result.update_result(
            prediction    = result["prediction"],
            confidence    = result["confidence"],
            probabilities = result["probabilities"],
        )