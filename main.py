import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window  import MainWindow
import config

def main():
    app    = QApplication(sys.argv)
    window = MainWindow(fullscreen=config.FULLSCREEN)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()