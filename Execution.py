from MainMenu import *
import time 

try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    myappid = 'com.seismic.autobuilder'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)    
except ImportError:
    pass

def main():
    app = QApplication(sys.argv)

    pixmap = QPixmap(':/Icons/letter_A_blue-512.png')
    splash = QSplashScreen(pixmap)
    splash.show()
    app.processEvents()

    main = MainWindow()
    time.sleep(1)
    splash.close()
    main.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()