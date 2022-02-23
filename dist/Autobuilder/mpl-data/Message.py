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
        ''' Input error notification '''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def popUpConfirmation(self, title, functionToCall):
        ''' Ask user to confirm their action -> QMessageBox(), OkButton, CancelButton'''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Warning")
        msg.setInformativeText(title)
        msg.setWindowTitle("Warning")

        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        OkButton = msg.button(QMessageBox.Ok)
        OkButton.clicked.connect(functionToCall)
        OkButton.clicked.connect(lambda s: msg.close())

        CancelButton = msg.button(QMessageBox.Cancel)
        CancelButton.clicked.connect(lambda s: msg.close())

        msg.exec_()

