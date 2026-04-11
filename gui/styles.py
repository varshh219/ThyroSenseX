STYLE = '''
QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: Courier New, monospace;
}
QPushButton#primary {
    background-color: #1f6feb;
    color: white; border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px; font-weight: bold;
    min-width: 120px;
}
QPushButton#primary:hover   { background-color: #388bfd; }
QPushButton#primary:disabled{ background-color: #21262d; color:#484f58; }
QPushButton#secondary {
    background-color: #21262d;
    color: #8b949e;
    border: 1px solid #30363d;
    border-radius: 8px; padding: 10px 20px;
    font-size: 13px;
    min-width: 100px;
}
QPushButton#secondary:hover { background:#30363d; color:#e6edf3; }
QProgressBar {
    background-color: #21262d;
    border: none; border-radius: 3px; height: 6px;
}
QProgressBar::chunk {
    background-color: #1f6feb; border-radius: 3px;
}
QFrame#card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
}
QLineEdit {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px; padding: 8px 12px;
    font-size: 12px; color: #e6edf3;
}
QLineEdit:focus { border-color: #1f6feb; }
QComboBox {
    background: #0d1117; border: 1px solid #30363d;
    border-radius: 6px; padding: 8px 12px;
    font-size: 12px; color: #e6edf3;
}
QLabel#screen_title {
    font-size: 17px; font-weight: bold; color: #e6edf3;
}
QLabel#section {
    font-size: 9px; color: #484f58; letter-spacing: 2px;
}
QScrollArea { border: none; background: transparent; }
'''