from MainMenu import *
from Model import *


# TESTING only
def main():
    app = QApplication(sys.argv)

    main = MainWindow()

    main.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()