from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

import resources    # For icons and UIs

class WarningMessage:
    def __init__(self):
        self._ = 0

    def popUpErrorBox(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

