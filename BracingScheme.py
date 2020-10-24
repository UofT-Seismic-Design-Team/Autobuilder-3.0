from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

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
        self.bracingSchemeViewer.setProjectSettingsData(args[0].projectSettingsData)
        self.bracingSchemeViewer.setTower(self.tower)

        timer = QTimer(self)
        timer.timeout.connect(self.set2DViewDimension)
        timer.timeout.connect(self.bracingSchemeViewer.update)
        timer.start()

    # Add existing bracing schemes to bracingSchemeTable
    def Populate(self):
        column = 0
        for row, bracingScheme in enumerate(self.tower.bracings):
            self.bracingSchemeTable.insertRow(self.bracingSchemeTable.rowCount())
            self.bracingSchemeTable.setItem(row, column, QTableWidgetItem(bracingScheme))

# floor plan are numbered, not named?

    def UpdateScreenXYElev(self):
        #Update BracingSchemeTable
        column = 0
        self.bracingCoordTable.setRowCount(0)
        X1 = 0
        Y1 = 1
        X2 = 2
        Y2 = 3

        row = self.bracingCoordTable.currentRow()
        currBracing = self.bracingSchemeTable.currentItem().text()
        bracing = self.tower.bracings[currBracing]
        for rows, member in enumerate(bracing.members):
            sNode = member.start_node
            eNode = member.end_node
            self.bracingCoordTable.insertRow(self.bracingCoordTable.rowCount())
            self.bracingCoordTable.setItem(rows, X1, QTableWidgetItem(str(sNode.x)))
            self.bracingCoordTable.setItem(rows, Y1, QTableWidgetItem(str(sNode.y)))
            self.bracingCoordTable.setItem(rows, X2, QTableWidgetItem(str(eNode.x)))
            self.bracingCoordTable.setItem(rows, Y2, QTableWidgetItem(str(eNode.y)))


    def set2DViewDimension(self):
        size = self.bracingSchemeViewer.size()

        self.bracingSchemeViewer.dimension_x = size.width()
        self.bracingSchemeViewer.dimension_y = size.height()

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

    def setOkandCancelButtons(self):
        self.OkButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(lambda x: self.close())
        self.OkButton.clicked.connect(self.saveBracingScheme)

        self.CancelButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())