from MainMenu import *
from Model import *

try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    myappid = 'com.seismic.autobuilder'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)    
except ImportError:
    pass

# TESTING only 
def main():
    app = QApplication(sys.argv)

    main = MainWindow()

    main.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()