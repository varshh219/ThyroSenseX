STYLE = '''
QWidget {
    background-color: #eef6ff;
    color: #1f2937;
    font-family: "Segoe UI";
}

/* CARD */
QFrame#card {
    background-color: white;
    border-radius: 20px;
    border: 1px solid #dbeafe;
    padding: 10px;
}

/* PRIMARY BUTTON */
QPushButton#primary {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 14px;
    padding: 14px 24px;
    font-size: 15px;
    font-weight: bold;
}

QPushButton#primary:hover {
    background-color: #1d4ed8;
}

/* SECONDARY BUTTON */
QPushButton#secondary {
    background-color: white;
    color: #2563eb;
    border: 2px solid #2563eb;
    border-radius: 14px;
    padding: 12px 22px;
    font-size: 14px;
}

QPushButton#secondary:hover {
    background-color: #eff6ff;
}

/* INPUTS */
QLineEdit,
QComboBox {
    background: white;
    border: 2px solid #dbeafe;
    border-radius: 12px;
    padding: 12px;
    color: #1f2937;
}

QLineEdit:focus,
QComboBox:focus {
    border: 2px solid #2563eb;
}

/* TITLE */
QLabel#screen_title {
    font-size: 28px;
    font-weight: 700;
    color: #1e3a8a;
}

/* STATUS */
QLabel#status_bar {
    background: white;
    border-radius: 10px;
    padding: 8px;
    color: #374151;
}

/* PROGRESS */
QProgressBar {
    border: none;
    border-radius: 12px;
    background: #dbeafe;
    height: 18px;
}

QProgressBar::chunk {
    border-radius: 12px;
    background: #2563eb;
}

/* SUCCESS */
QLabel#success {
    color: #16a34a;
}

/* ERROR */
QLabel#error {
    color: #dc2626;
}

/* WARNING */
QLabel#warning {
    color: #d97706;
}
'''