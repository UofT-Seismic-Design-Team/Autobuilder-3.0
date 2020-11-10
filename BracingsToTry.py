from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

from WarningMessage import *

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

        # Bracings to try data object
        self.bracingsToTryData = BracingsToTryData()


    def setIconsForButtons(self):
        self.addBracingsToTryButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteBracingsToTryButton.setIcon(QIcon(r"Icons\24x24\minus.png"))
    
    # Insert new row in bracings to try table
    def addBracingsToTry(self,signal):
        self.bracingsToTryTable.insertRow( self.bracingsToTryTable.rowCount() )
    
    # Delete row in bracings to try table
    def deleteBracingsToTry(self,signal):
        indices = self.bracingsToTryTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.bracingsToTryTable.removeRow(index.row())

    # Save list of bracings corresponding to each design in BracingsToTryData
    def saveBracingsToTry(self):
        warning = WarningMessage()

        rowNum = self.bracingsToTryTable.rowCount()
        listofBracing = []
        for i in range(rowNum):
            bracItem = self.bracingsToTryTable.item(i,0)
            # Check if the item exists
            if bracItem == None:
                break
            brac = bracItem.text()
            listofBracing.append(str(brac))
        self.bracingsToTryData.bracings[self.bracingsToTryData.currDesign] = listofBracing

    # Display list of bracings
    def displayBracingsToTryData(self):
        i = 0
        bracings_rowNum = self.bracingsToTryTable.rowCount()
        allBracing = self.bracingsToTryData.bracings
        currDesign = self.bracingsToTryData.currDesign
        if currDesign in allBracing:
            currList = allBracing[currDesign]
            for brac in currList:
                item = QTableWidgetItem(str(brac))
                if i < len(currList):
                    self.bracingsToTryTable.insertRow(i)
                    self.bracingsToTryTable.setItem(i,0,item)
                    i += 1

    def setBracingsToTryData(self, bracingsToTryData):
        self.bracingsToTryData = bracingsToTryData

    def setOkandCancelButtons(self):
        self.OkButton = self.bracingsToTry_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveBracingsToTry)
        self.OkButton.clicked.connect(lambda x: self.close())
        
        self.CancelButton = self.bracingsToTry_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

# Store list of bracings and corresponding design
class BracingsToTryData:
    def __init__(self):
        self.bracings = {}
        self.currDesign = ""