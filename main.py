import sys
import traceback
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

# Optional config import safety
try:
    import config
    FULLSCREEN = getattr(config, "FULLSCREEN", False)
except Exception:
    FULLSCREEN = False


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ThyroSenseX")

    try:
        window = MainWindow(fullscreen=FULLSCREEN)
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        print("❌ Application Error:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()