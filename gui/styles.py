STYLE = """
QWidget {
    background-color: #0a0e14;
    color: #e8edf7;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QPushButton#primary {
    background-color: #4f8dff;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#primary:hover { background-color: #3a7aee; }
QPushButton#primary:disabled { background-color: #1e2d45; color: #4a5a78; }
QPushButton#secondary {
    background-color: transparent;
    color: #7a90b8;
    border: 1px solid #1e2d45;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 12px;
}
QPushButton#secondary:hover { background-color: #161c28; color: #e8edf7; }
QPushButton#outline {
    background-color: #161c28;
    color: #e8edf7;
    border: 1px solid #1e2d45;
    border-radius: 9px;
    padding: 11px 24px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#outline:hover { border-color: #4f8dff; }
QProgressBar {
    background-color: #161c28;
    border: none;
    border-radius: 4px;
    height: 6px;
}
QProgressBar::chunk {
    background-color: #4f8dff;
    border-radius: 4px;
}
QFrame#card {
    background-color: #161c28;
    border: 1px solid #1e2d45;
    border-radius: 12px;
}
QLabel#screen_title {
    font-size: 18px;
    font-weight: bold;
    color: #e8edf7;
}
QLabel#section {
    font-size: 10px;
    color: #4a5a78;
    letter-spacing: 2px;
}
"""