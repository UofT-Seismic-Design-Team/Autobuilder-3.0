from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic
from Model import *

from View2DEngine import *  # import View2DEngine
import copy

import sys  # We need sys so that we can pass argv to QApplication
import os

class panelsUI(QDialog):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('UI/autobuilder_paneldesign_v1.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Add Empty Row to List of Floor Plan Schemes
        self.add.clicked.connect(self.addPanel)

        # Delete Selected Row from List of Floor Plan Schemes
        self.delete_2.clicked.connect(self.deletePanel)

        #Call update on the Coordinate table upon change in cell
        self.CoordTable.itemChanged.connect(self.updateCoordinates)

        #create a copy of the tower to reassign if user saves.
        self.tower = copy.deepcopy(args[0].tower)

        # passing in main.tower properties into panel
        self.populate()

        #Save the current floorplan table name and intialize for the first one for later use in changing and saving the name
        if self.panelTable.item(0,0):
            self.currentPanelName = self.panelTable.item(0,0).text()
        else:
            self.currentPanelName = ''

        #Call update upon ScreenXYElev to update the whole screen upon picking floor plan
        self.panelTable.itemClicked.connect(self.updateScreenXYElev)

        #Call cell name change
        self.panelTable.cellChanged.connect(self.nameChange)

        self.projectSettingsData = args[0].projectSettingsData

        #reference to existing tower for cache
        self.towerRef = args[0].tower

        # Set project settings data for all views
        self.setProjectSettingsDataForViews()

        # Views ----------------------------
        self.setTowerInViews()

        #Nodes to Color for the Panel Viewer
        self.nodes = []

        # Update views -----------------------------
        timer  = QTimer(self)
        timer.setInterval(20) # period in miliseconds
        timer.timeout.connect(self.Panel3DViewer.updateGL) # updateGL calls paintGL automatically!!
        timer.start()

    def setTowerInViews(self):
        self.Panel3DViewer.setTower(self.tower)

    def setProjectSettingsDataForViews(self):
        self.Panel3DViewer.setProjectSettingsData(self.projectSettingsData)

    def populate(self):
        '''Populate the panel Table with Panel from the tower'''
        column = 0
        bottom = 1
        top = 2
        #Clear the floorplan table
        self.panelTable.setRowCount(0)
        #Iterate through and add the floor plans
        for i,panel in enumerate(self.tower.panels):
            Lower = min(self.tower.panels[panel].lowerLeft.z,self.tower.panels[panel].lowerRight.z)
            Upper = max(self.tower.panels[panel].upperLeft.z,self.tower.panels[panel].upperRight.z)
            self.panelTable.insertRow(self.panelTable.rowCount())
            itemName = QTableWidgetItem()
            itemName.setText(self.tower.panels[panel].name)
            itemBot = QTableWidgetItem()
            itemBot.setText(str(Lower))
            itemTop = QTableWidgetItem()
            itemTop.setText(str(Upper))
            self.panelTable.setItem(i, column, itemName)
            self.panelTable.setItem(i, bottom, itemBot)
            self.panelTable.setItem(i, top, itemTop)

    def updateScreenXYElev(self):
        '''Update everything on selected item on the right tab'''
        column = 0
        TableIndex = {
            'lowerLeft' : 1,
            'upperLeft' : 0,
            'upperRight' :2,
            'lowerRight' :3
        }

        CoordIndex = {
            'x' : 0,
            'y' : 1,
            'z' : 2
        }

        self.selectedPanelName.setText('')
        row = self.panelTable.currentRow()
        item = self.panelTable.item(row, column)
        panel = self.tower.panels[item.text()]
        self.currentPanelName = item.text()
        for key in TableIndex:
            for coord in CoordIndex:
                node = getattr(panel,key)
                value= getattr(node,coord)
                self.CoordTable.setItem(TableIndex[key], CoordIndex[coord], QTableWidgetItem(str(value)))

        line_1 = [panel.lowerLeft,panel.upperLeft]
        line_2 = [panel.upperLeft,panel.upperRight]
        line_3 = [panel.upperRight,panel.lowerRight]
        line_4 = [panel.lowerRight,panel.lowerLeft]
        self.Panel3DViewer.nodes = [line_1,line_2,line_3,line_4]

        self.selectedPanelName.setText(item.text())



    def nameChange(self):
        '''Change the name according '''
        column = 0
        row = self.panelTable.currentRow() #returns -1 when i'm repopulation the table
        add = False
        if row == -1:
            row = 0
            add = True
        item = self.panelTable.item(row,column)
        #adding new rows also prompt the name change, ergo handle exception
        if add == False:
            panel = self.tower.panels[self.currentPanelName]
            panel.name =  item.text()
            self.tower.panels[item.text()]=self.tower.panels.pop(self.currentPanelName)
            self.updateScreenXYElev


    def setIconsForButtons(self):
        '''Set icons associated with the add/delete buttons'''
        self.add.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.delete_2.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def addPanel(self):
        '''Adding new floor plans'''
        newPanel = Panel()
        id = 1
        newPanel.name = str(id)
        while newPanel.name in self.tower.panels:
            id += 1
            newPanel.name = str(id)
        self.tower.addPanel(newPanel)
        self.populate()

    def deletePanel(self):
        '''Delete floor plan from tower'''
        indices = self.panelTable.selectionModel().selectedRows()
        for index in sorted(indices):
            item = self.panelTable.item(index.row(),index.column())
            del self.tower.panels[item.text()]
        for index in sorted(indices):
            self.panelTable.removeRow(index.row())

    def updateCoordinates(self):
        '''Update the coordinates associated with the floor plan based on current '''
        TableIndex = {
            'lowerLeft' : 1,
            'upperLeft' : 0,
            'upperRight' :2,
            'lowerRight' :3
        }

        CoordIndex = {
            'x' : 0,
            'y' : 1,
            'z' : 2
        }
        # Check if the label associated with it is empty or not ^ occurs upon intialization
        if self.selectedPanelName.toPlainText() != '':
            panel = self.tower.panels[self.selectedPanelName.toPlainText()]
            for key in TableIndex:
                for index in CoordIndex:
                    coord = float(self.CoordTable.item(TableIndex[key],CoordIndex[index]).text())
                    node = (getattr(panel,key))
                    setattr(node,index,coord)
                    self.populate()


    def cancelPanel(self):
        '''do Nothing'''
        self.towerRef = self.towerRef

    def savePanel(self):
        '''Overwrite the tower linked to the main model'''
        self.towerRef.panels = self.tower.panels

    def setOkandCancelButtons(self):
        #Constructor
        self.OkButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.savePanel)
        self.OkButton.clicked.connect(lambda x: self.close())

        self.CancelButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())
        self.CancelButton.clicked.connect(self.cancelPanel)

