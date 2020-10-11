from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

from WarningMessage import *
from BracingsToTry import *


class BracingDesign(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('UI/autobuilder_bracingdesign_v3.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Add Empty Row to List of Bracing Design
        self.addBracingDesignButton.clicked.connect(self.addBracingDesign)

        # Delete Row from List of Bracing Design
        self.deleteBracingDesignButton.clicked.connect(self.deleteBracingDesign)

        # Open Bracings To Try Table
        self.bracingDesignTable.itemDoubleClicked.connect(self.openBracingsToTry)  

        self.bracingDesignData = BracingDesignData()
        self.bracingsToTryData = BracingsToTryData()


    def setIconsForButtons(self):
        self.addBracingDesignButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteBracingDesignButton.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def addBracingDesign(self, signal):
        self.bracingDesignTable.insertRow(self.bracingDesignTable.rowCount())

    def deleteBracingDesign(self, signal):
        indices = self.bracingDesignTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.bracingDesignTable.removeRow(index.row())

    
    def openBracingsToTry(self, signal):
        
        item = self.bracingDesignTable.currentItem()
        bracingsToTry = BracingsToTry(self)
        bracingsToTry.setBracingsToTryData(self.bracingsToTryData)
        self.bracingsToTryData.currDesign = str(item.text())
        self.bracingsToTryData.bracings = self.bracingDesignData.bracingVersions
        bracingsToTry.displayBracingsToTryData()

        bracingsToTry.exec_()

    # Save list of bracings corresponding to each design in BracingDesignData
    def saveBracingDesign(self):
        
        bracingsToTry = BracingsToTry(self)
        bracingsToTry.setBracingsToTryData(self.bracingsToTryData)
        #add to bracing versions, not equal
        for key in bracingsToTry.bracingsToTryData.bracings:
            if key not in self.bracingDesignData.bracingVersions:
                self.bracingDesignData.bracingVersions[key] = bracingsToTry.bracingsToTryData.bracings.get(key)
            bracingsToTry.bracingsToTryData.bracings

        #delete design from BracingDesignData if deleted in table
        curr_list = []
        curr_row_count = self.bracingDesignTable.rowCount()
        i = 0
        while i < curr_row_count:
            if self.bracingDesignTable.item(i,0) is not None:
                curr_list.append(self.bracingDesignTable.item(i,0).text())
            i+=1
        for ver in self.bracingDesignData.bracingVersions:
            if ver not in curr_list:
                del self.bracingDesignData.bracingVersions[ver]

    # Display list of bracing designs
    def displayBracingDesignData(self):
        
        data = self.bracingDesignData.bracingVersions
        i = 0
        bd_rowNum = self.bracingDesignTable.rowCount()
        for ver in data.keys():
            item = QTableWidgetItem(str(ver))
            if i >= bd_rowNum:
                self.bracingDesignTable.insertRow(i)
            self.bracingDesignTable.setItem(i,0,item)
            i += 1
        #return self.bracingDesignData

    def setBracingDesignData(self, bracingsToTryData):
        self.bracingDesignData = bracingsToTryData
    
    def setOkandCancelButtons(self):
        self.OkButton = self.bracingDesign_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveBracingDesign)

        self.OkButton.clicked.connect(lambda x: self.close())
        
        self.CancelButton = self.bracingDesign_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

# Store list of bracings and corresponding bracing design
class BracingDesignData:
    def __init__(self):
        self.bracingVersions = {}
    