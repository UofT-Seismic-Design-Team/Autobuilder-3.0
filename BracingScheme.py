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

        # Bracing data
        self.data = args[0].tower.bracings

        # Load the UI Page
        uic.loadUi('UI/autobuilder_bracingscheme_v1.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # save xy coordinates of new bracing scheme
        self.updateBracingButton.clicked.connect(self.updateBracing)
        
        # Add Empty Row to List of Bracing Schemes
        self.addBracingSchemeButton.clicked.connect(self.addBracingScheme)

        # Delete Selected Row from List of Bracing Schemes
        self.deleteBracingSchemeButton.clicked.connect(self.deleteBracingScheme)

        # Passing in main.tower into floorPlan
        self.bracingSchemeTable.itemSelectionChanged.connect(self.UpdateScreenXYElev)
        self.tower = args[0].tower
        
        # Fill in bracing scheme table
        self.Populate()
        
        # Scale bracing scheme according to project settings
        self.bracingSchemeViewer.setProjectSettingsData(args[0].projectSettingsData)
        
        # Tower
        self.bracingSchemeViewer.setTower(self.tower)

        # Update 2D view constantly
        timer = QTimer(self)
        timer.timeout.connect(self.set2DViewDimension)
        timer.timeout.connect(self.bracingSchemeViewer.update)
        timer.start()

    def Populate(self):
        '''Add existing bracing schemes to bracingSchemeTable'''
        column = 0
        for row, bracingScheme in enumerate(self.tower.bracings):
            self.bracingSchemeTable.insertRow(self.bracingSchemeTable.rowCount())
            self.bracingSchemeTable.setItem(row, column, QTableWidgetItem(bracingScheme))

    def UpdateScreenXYElev(self):
        '''Update BracingSchemeTable'''
        column = 0
        self.bracingCoordTable.setRowCount(0)
        X1 = 0
        Y1 = 1
        X2 = 2
        Y2 = 3

        # Set currently selected cell as current bracing object
        currBracing = self.bracingSchemeTable.currentItem().text()
        bracing = self.tower.bracings[currBracing]

        # Fill node coordinate table
        for rows, member in enumerate(bracing.members):
            sNode = member.start_node
            eNode = member.end_node
            self.bracingCoordTable.insertRow(self.bracingCoordTable.rowCount())
            self.bracingCoordTable.setItem(rows, X1, QTableWidgetItem(str(sNode.x)))
            self.bracingCoordTable.setItem(rows, Y1, QTableWidgetItem(str(sNode.y)))
            self.bracingCoordTable.setItem(rows, X2, QTableWidgetItem(str(eNode.x)))
            self.bracingCoordTable.setItem(rows, Y2, QTableWidgetItem(str(eNode.y)))

        # Display 2D view of currently selected bracing
        self.bracingSchemeViewer.displayed_bracing = currBracing

        # Display name of currently selected bracing
        self.bracingNameEdit.setText(currBracing)

    def set2DViewDimension(self):
        '''scale bracing based on project settings'''
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

    def updateBracing(self, signal):

        #warning = WarningMessage()
        newBracingCoord = []

        for row in range(self.bracingCoordTable.rowCount()):
            for column in range(self.bracingCoordTable.columnCount()):
                item = self.bracingCoordTable.item(row, column)
                if item is not None:
                    newBracingCoord.append(item.text())

        self.data[self.bracingNameEdit.text()] = newBracingCoord

    def saveBracingScheme(self, signal):

        self.data.clear() # reset assignment properties

        rowNum = self.bracingSchemeTable.rowCount()
        for i in range(rowNum):
            bracingItem = self.bracingSchemeTable.item(i,0)
            # Check if the row is filled
            if panelItem == None:
                break
            bracing = bracingItem.text()
            try:
                # Check if the item is filled
                if bracing == '':
                    break
                self.data.bracingNames.append()
            except:
                warning.popUpErrorBox('Invalid input for bracing names')
                return # terminate the saving process

    def setOkandCancelButtons(self):
        self.OkButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Ok)
        #self.OkButton.clicked.connect(lambda x: self.close())
        self.OkButton.clicked.connect(self.saveBracingScheme)

        self.CancelButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

class BracingSchemeData:

    def __init__(self):
        self.bracingSchemes = {}
        self.bracingNames = []