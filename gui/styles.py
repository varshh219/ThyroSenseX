STYLE = '''
QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: "Segoe UI", "Inter", monospace;
}

/* PRIMARY BUTTON */
QPushButton#primary {
    background-color: #1f6feb;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: bold;
    min-width: 120px;
}
QPushButton#primary:hover   { background-color: #388bfd; }
QPushButton#primary:pressed { background-color: #1a5fd0; }
QPushButton#primary:disabled{
    background-color: #21262d;
    color:#484f58;
}

/* SECONDARY BUTTON */
QPushButton#secondary {
    background-color: #161b22;
    color: #8b949e;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    min-width: 100px;
}
QPushButton#secondary:hover {
    background:#21262d;
    color:#e6edf3;
}

/* PROGRESS BAR */
QProgressBar {
    background-color: #161b22;
    border: none;
    border-radius: 4px;
    height: 6px;
}
QProgressBar::chunk {
    background-color: #3ddc97;
    border-radius: 4px;
}

/* CARD */
QFrame#card {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
}

/* INPUT */
QLineEdit {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    color: #e6edf3;
}
QLineEdit:focus {
    border: 1px solid #1f6feb;
}

/* COMBOBOX */
QComboBox {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    color: #e6edf3;
}
QComboBox:focus {
    border: 1px solid #1f6feb;
}

/* TITLES */
QLabel#screen_title {
    font-size: 18px;
    font-weight: bold;
    color: #f0f6fc;
}

QLabel#section {
    font-size: 9px;
    color: #6e7681;
    letter-spacing: 2px;
}

/* STATUS BAR */
QLabel#status_bar {
    background:#161b22;
    color:#8b949e;
    padding-left:10px;
    font-size:10px;
}

/* WARNING */
QLabel#warning {
    color:#ffb020;
    font-size:11px;
}

/* SUCCESS */
QLabel#success {
    color:#3ddc97;
    font-size:11px;
}

/* ERROR */
QLabel#error {
    color:#ff4f5e;
    font-size:11px;
}

/* SCROLL */
QScrollArea {
    border: none;
    background: transparent;
}
'''