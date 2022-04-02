import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from qt_material import apply_stylesheet

from app.ui.app_view import AppView
import env

try:
    from ctypes import windll
    myappid = 'org.pelajarnuwsb.contonge'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

if __name__ == '__main__':
    print("Debug mode:", env.app_debug)
    app = QApplication(sys.argv)
    
    apply_stylesheet(app, theme='light_cyan_500.xml', extra={'density_scale': '-1', 'font_family': 'Roboto'})
    with open('style/app.qss', 'r') as style:
        styleSheet = app.styleSheet()
        qss = style.read()
        app.setStyleSheet(styleSheet + qss)
    
    basedir = os.path.dirname(__file__)
    app.setWindowIcon(QIcon(os.path.join(basedir, 'icon.ico')))
    
    ex = AppView()
    sys.exit(app.exec())
