from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os
COLORS_FLOOR_PLAN = ['blue', 'violet']
COLORS_NODE = ['green']

class FloorPlanUI(QDialog):

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
        # passing in main.tower into floorPlan
        self.floorPlanTable.itemSelectionChanged.connect(self.UpdateScreenXYElev)
        self.tower = args[0].tower
        self.Populate()
        self.FloorPlanViewer.setProjectSettingsData(args[0].projectSettingsData)
        self.FloorPlanViewer.setTower(self.tower)

        timer = QTimer(self)
        timer.timeout.connect(self.set2DViewDimension)
        timer.timeout.connect(self.FloorPlanViewer.update)
        timer.start()

    def Populate(self):
        column = 0
        for i in self.tower.floorPlans:
            self.floorPlanTable.insertRow(self.floorPlanTable.rowCount())
            self.floorPlanTable.setItem(int(i)-1, column, QTableWidgetItem(self.tower.floorPlans[i].name))

    def UpdateScreenXYElev(self):
        #Update FloorPlanTable
        column = 0
        self.XYCoordTable.setRowCount(0)
        X = 0
        Y = 1
        row = self.floorPlanTable.currentRow()
        floorPlan = self.tower.floorPlans[str(row+1)]
        for rows, member in enumerate(floorPlan.members):
            node = member.start_node
            self.XYCoordTable.insertRow(self.XYCoordTable.rowCount())
            self.XYCoordTable.setItem(rows, X, QTableWidgetItem(str(node.x)))
            self.XYCoordTable.setItem(rows, Y, QTableWidgetItem(str(node.y)))

        #UpdateElevationTableView based on Selecteditems
        self.ElevationTable.setRowCount(0)
        for rows, elevation in enumerate(self.tower.elevations):
            if elevation in floorPlan.elevations:
                self.ElevationTable.insertRow(self.ElevationTable.rowCount())
                self.ElevationTable.setItem(rows, X, QTableWidgetItem(str(elevation)))
                checkbox = QTableWidgetItem()
                checkbox.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
                checkbox.setCheckState(Qt.Checked)
                self.ElevationTable.setItem(rows, Y, checkbox)
            else:
                self.ElevationTable.insertRow(self.ElevationTable.rowCount())
                self.ElevationTable.setItem(rows, X, QTableWidgetItem(str(elevation)))
                checkbox = QTableWidgetItem()
                checkbox.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
                checkbox.setCheckState(Qt.Unchecked)
                self.ElevationTable.setItem(rows, Y, checkbox)
        self.SelectedFloorName.setText(self.floorPlanTable.item(row, column).text())

        elev = floorPlan.elevations[1]
        self.FloorPlanViewer.elevation = elev

    def set2DViewDimension(self):
        size = self.FloorPlanViewer.size()

        self.FloorPlanViewer.dimension_x = size.width()
        self.FloorPlanViewer.dimension_y = size.height()

    def setIconsForButtons(self):
        self.Add.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.Delete.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def addFloorPlan(self, signal):
        self.floorPlanTable.insertRow(self.floorPlanTable.rowCount())

    def deleteFloorPlan(self, signal):
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

    def setOkandCancelButtons(self):
        self.OkButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(lambda x: self.close())
        self.OkButton.clicked.connect(self.saveFloorPlan)

        self.CancelButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())
