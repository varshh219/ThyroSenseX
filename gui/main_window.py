from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore    import Qt
from gui.styles            import STYLE
from gui.doctor_login      import DoctorLoginScreen
from gui.login_screen      import LoginScreen
from gui.patient_screen    import PatientRegisterScreen
from gui.welcome_screen    import WelcomeScreen
from gui.capture_screen    import CaptureScreen
from gui.processing_screen import ProcessingScreen
from gui.result_screen     import ResultScreen
from gui.report_screen     import ReportScreen

class MainWindow(QMainWindow):
    def __init__(self, fullscreen=False):
        super().__init__()
        self.setWindowTitle('ThyroSenseX')
        self.setMinimumSize(480, 680)
        self.setStyleSheet(STYLE)

        # Session state
        self._current_doctor  = None
        self._current_patient = None
        self._last_result     = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create all screens
        self.doctor_login = DoctorLoginScreen(
            self.go_to, self._on_doctor_login)
        self.patient_login = LoginScreen(
            self.go_to, self._on_patient_selected)
        self.patient_reg  = PatientRegisterScreen(self.go_to)
        self.welcome      = WelcomeScreen(self.go_to)
        self.capture      = CaptureScreen(self.go_to)
        self.processing   = ProcessingScreen(
            self.go_to, on_result=self._on_prediction)
        self.result       = ResultScreen(self.go_to)
        self.report       = ReportScreen(self.go_to)

        self.screens = {
            'doctor_login':   self.doctor_login,
            'patient_login':  self.patient_login,
            'patient_register': self.patient_reg,
            'welcome':        self.welcome,
            'capture':        self.capture,
            'processing':     self.processing,
            'result':         self.result,
            'report':         self.report,
        }
        for w in self.screens.values():
            self.stack.addWidget(w)

        if fullscreen:
            self.showFullScreen()
            self.setCursor(Qt.BlankCursor)

        self.go_to('doctor_login')

    def go_to(self, name):
        widget = self.screens.get(name)
        if not widget: return
        self.stack.setCurrentWidget(widget)
        if name == 'patient_login': self.patient_login.refresh()
        if name == 'capture':       self.capture.reset()
        if name == 'processing':    self.processing.start(self._current_patient)
        if name == 'report':
            self.report.refresh(
                patient=self._current_patient,
                doctor=self._current_doctor,
                result=self._last_result
            )
    def _on_doctor_login(self, doctor):
        self._current_doctor = doctor
        self.patient_reg.set_doctor(doctor)   # 🔥 ADD THIS
        print(f'Doctor logged in: {doctor["full_name"]}')
    def _on_patient_selected(self, patient):
        self._current_patient = patient
        self.welcome.set_patient(patient)

    def _on_prediction(self, result):
        self._last_result = result
        # Save to PostgreSQL
        if self._current_patient and self._current_doctor:
            from data.database import save_scan_result
            save_scan_result(
                self._current_patient['patient_id'],
                self._current_doctor['id'],
                result
            )
        self.result.update_result(
            result['prediction'],
            result['confidence'],
            result['probabilities']
        )