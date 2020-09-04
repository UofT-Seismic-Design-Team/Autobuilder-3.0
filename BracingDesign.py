from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

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
        # Add Empty Row to List of Bracing Schemes
        self.deleteBracingDesignButton.clicked.connect(self.deleteBracingDesign)
        # Open Bracings To Try Table
        self.bracingDesignTable.itemDoubleClicked.connect(self.openBracingsToTry)        


        #item = QTableWidgetItem('12/1/12')
        #self.bracingDesignTable.setItem(0, 0, item)
        #self.bracingDesignTable.setCurrentItem(item)
        # create an cell widget
        # btn = QPushButton(self.bracingDesignTable)
        # btn.setText('Edit')
        # self.bracingDesignTable.setCellWidget(0, 0, btn)

    def setIconsForButtons(self):
        self.addBracingDesignButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteBracingDesignButton.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def addBracingDesign(self,signal):
        self.bracingDesignTable.insertRow( self.bracingDesignTable.rowCount() )

    def deleteBracingDesign(self,signal):
        indices = self.bracingDesignTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.bracingDesignTable.removeRow(index.row())
    
    def openBracingsToTry(self, signal):
        bracingDesign = BracingsToTry(self)
        bracingDesign.exec_()

    def saveBracingDesign(self):
        rowdata = []
        for row in range(self.bracingDesignTable.rowCount()):
            for column in range(self.bracingDesignTable.columnCount()):
                item = self.bracingDesignTable.item(row, column)
                if item is not None:
                    rowdata.append(item.text())
        print(rowdata)

    def setOkandCancelButtons(self):
        self.OkButton = self.bracingDesign_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(lambda x: self.close())
        self.OkButton.clicked.connect(self.saveBracingDesign)

        self.CancelButton = self.bracingDesign_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

    