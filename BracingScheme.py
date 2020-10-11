from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os
COLORS_BRACING = ['blue', 'violet']
COLORS_NODE = ['green']

class BracingScheme(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('UI/autobuilder_bracingscheme_v1.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()
        # Add Empty Row to List of Bracing Schemes
        self.addBracingSchemeButton.clicked.connect(self.addBracingScheme)
        # Delete Selected Row from List of Bracing Schemes
        self.deleteBracingSchemeButton.clicked.connect(self.deleteBracingScheme)
        # passing in main.tower into floorPlan
        self.bracingSchemeTable.itemSelectionChanged.connect(self.UpdateScreenXYElev)
        self.tower = args[0].tower
        self.Populate()
        #self.BracingViewer.setTower(self.tower)

        #timer = QTimer(self)
        #timer.timeout.connect(self.set2DViewDimension)
        #timer.timeout.connect(self.BracingViewer.update)
        #timer.start()

    #A Add existing bracing schemes to bracingSchemeTable
    def Populate(self):
        column = 0
        for row, bracingScheme in enumerate(self.tower.bracings):
            self.bracingSchemeTable.insertRow(self.bracingSchemeTable.rowCount())
            self.bracingSchemeTable.setItem(row, column, QTableWidgetItem(bracing.name))


    def UpdateScreenXYElev(self):
        #Update BracingSchemeTable
        column = 0
        self.XYCoordTable.setRowCount(0)
        X = 0
        Y = 1
        row = self.BracingSchemeTable.currentRow()
        bracing = self.tower.bracings[row]
        for member in enumerate(floorPlan.members):
            startNode = member.start_node
            self.bracingCoordTable.insertRow(self.XYCoordTable.rowCount())
            self.bracingCoordTable.setItem(rows, X, QTableWidgetItem(str(node.x)))
            self.bracingCoordTable.setItem(rows, Y, QTableWidgetItem(str(node.y)))

    def set2DViewDimension(self):
        size = self.FloorPlanViewer.size()

        self.FloorPlanViewer.dimension_x = size.width()
        self.FloorPlanViewer.dimension_y = size.height()

    def setIconsForButtons(self):
        self.addBracingSchemeButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteBracingSchemeButton.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def addBracingScheme(self, signal):
        self.bracingSchemeTable.insertRow(self.bracingSchemeTable.rowCount())

    def deleteBracingScheme(self, signal):
        indices = self.bracingSchemeTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.bracingSchemeTable.removeRow(index.row())

    def saveBracingScheme(self):
        rowdata = []
        for row in range(self.bracingSchemeTable.rowCount()):
            for column in range(self.bracingSchemeTable.columnCount()):
                item = self.bracingSchemeTable.item(row, column)
                if item is not None:
                    rowdata.append(item.text())
        print(rowdata)

    def setOkandCancelButtons(self):
        self.OkButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(lambda x: self.close())
        self.OkButton.clicked.connect(self.saveBracingScheme)

        self.CancelButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())