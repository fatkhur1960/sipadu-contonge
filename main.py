import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from app.ui.app_view import AppView

try:
    from ctypes import windll
    myappid = 'org.pelajarnuwsb.contonge'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

if __name__ == '__main__':
    basedir = os.path.dirname(__file__)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setWindowIcon(QIcon(os.path.join(basedir, 'icon.ico')))
    ex = AppView()
    sys.exit(app.exec())
