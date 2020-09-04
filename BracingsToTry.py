from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

class BracingsToTry(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('UI/autobuilder_bracingstotry_v3.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()
        # Add Empty Row to List of Bracing Schemes
        self.addBracingsToTryButton.clicked.connect(self.addBracingsToTry)
        # Delete Selected Row from List of Bracing Schemes
        self.deleteBracingsToTryButton.clicked.connect(self.deleteBracingsToTry)

    def setIconsForButtons(self):
        self.addBracingsToTryButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteBracingsToTryButton.setIcon(QIcon(r"Icons\24x24\minus.png"))
    
    def addBracingsToTry(self,signal):
        self.bracingsToTryTable.insertRow( self.bracingsToTryTable.rowCount() )
    
    def deleteBracingsToTry(self,signal):
        indices = self.bracingsToTryTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.bracingsToTryTable.removeRow(index.row())

    def saveBracingsToTry(self):
        rowdata = []
        for row in range(self.bracingsToTryTable.rowCount()):
            for column in range(self.bracingsToTryTable.columnCount()):
                item = self.bracingsToTryTable.item(row, column)
                if item is not None:
                    rowdata.append(item.text())
        print(rowdata)

    def setOkandCancelButtons(self):
        self.OkButton = self.bracingsToTry_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(lambda x: self.close())
        self.OkButton.clicked.connect(self.saveBracingsToTry)

        self.CancelButton = self.bracingsToTry_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())


    # def setOkandCancelButtons(self):
    #     self.OkButton = self.projectSettings_buttonBox.button(QDialogButtonBox.Ok)
    #     self.OkButton.clicked.connect(lambda x: self.close())

    #     self.CancelButton = self.projectSettings_buttonBox.button(QDialogButtonBox.Cancel)
    #     self.CancelButton.clicked.connect(lambda x: self.close())