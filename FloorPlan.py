from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

class FloorPlan(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('UI/autobuilder_floordesign_v1.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()
        # Add Empty Row to List of Bracing Schemes
        self.Add.clicked.connect(self.addFloorPlan)
        # Delete Selected Row from List of Bracing Schemes
        self.Delete.clicked.connect(self.deleteFloorPlan)

    def setIconsForButtons(self):
        self.Add.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.Delete.setIcon(QIcon(r"Icons\24x24\minus.png"))
    
    def addFloorPlan(self,signal):
        self.floorPlanTable.insertRow( self.floorPlanTable.rowCount() )
    
    def deleteFloorPlan(self,signal):
        indices = self.floorPlanTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.floorPlanTable.removeRow(index.row())

    def saveFloorPlan(self):
        rowdata = []
        for row in range(self.floorPlanTable.rowCount()):
            for column in range(self.floorPlanTable.columnCount()):
                item = self.floorPlanTable.item(row, column)
                if item is not None:
                    rowdata.append(item.text())
        print(rowdata)

    def setOkandCancelButtons(self):
        self.OkButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(lambda x: self.close())
        self.OkButton.clicked.connect(self.saveFloorPlan)

        self.CancelButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())


    # def setOkandCancelButtons(self):
    #     self.OkButton = self.projectSettings_buttonBox.button(QDialogButtonBox.Ok)
    #     self.OkButton.clicked.connect(lambda x: self.close())

    #     self.CancelButton = self.projectSettings_buttonBox.button(QDialogButtonBox.Cancel)
    #     self.CancelButton.clicked.connect(lambda x: self.close())