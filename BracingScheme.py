from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

from Model import *

class BracingScheme(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Bracing data
        #self.data = args[0].tower.bracings
        #self.data = BracingSchemeData

        # Load the UI Page
        uic.loadUi('UI/autobuilder_bracingscheme_v1.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()
        
        # Add Empty Row to List of Bracing Schemes
        self.addBracingSchemeButton.clicked.connect(self.addBracingScheme)

        # save xy coordinates of new bracing scheme
        self.updateBracingButton.clicked.connect(self.updateBracing)

        # Delete Selected Row from List of Bracing Schemes
        self.deleteBracingSchemeButton.clicked.connect(self.deleteBracingScheme)

        # Add Empty Row to List of Bracing Coordinates
        self.addCoordButton.clicked.connect(self.addBracingCoord)

        # Delete Selected Row from List of Bracing Coordinates
        self.deleteCoordButton.clicked.connect(self.deleteBracingCoord)

        # Navigate to new XY Coord Table 
        self.bracingSchemeTable.itemSelectionChanged.connect(self.UpdateScreenXYElev)
        
        # Passing in main.tower into bracing scheme
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
            bcItem = QTableWidgetItem(bracingScheme)
            '''How to disable clicking?'''
            #bcItem.setFlags(Qt.ItemIsEditable)
            self.bracingSchemeTable.setItem(row, column, bcItem)

    def UpdateScreenXYElev(self):
        '''Update BracingCoordTable'''

        '''TO DO: set exceptions for user clicking on empty cell or trying to fill out cell'''

        # if switching to an existing bracing
        if self.bracingSchemeTable.currentItem() is not None:

            self.bracingCoordTable.setRowCount(0)
            X1 = 0
            Y1 = 1
            X2 = 2
            Y2 = 3
            mat = 4

            # Set currently selected cell as current bracing object
            currBracing = self.bracingSchemeTable.currentItem().text()
            bracing = self.tower.bracings[currBracing]
            #bracing = self.data.bracingSchemes[currBracing]

            # Fill node coordinate table
            for rows, member in enumerate(bracing.members):
                sNode = member.start_node
                eNode = member.end_node
                self.bracingCoordTable.insertRow(self.bracingCoordTable.rowCount())
                self.bracingCoordTable.setItem(rows, X1, QTableWidgetItem(str(sNode.x)))
                self.bracingCoordTable.setItem(rows, Y1, QTableWidgetItem(str(sNode.y)))
                self.bracingCoordTable.setItem(rows, X2, QTableWidgetItem(str(eNode.x)))
                self.bracingCoordTable.setItem(rows, Y2, QTableWidgetItem(str(eNode.y)))
                self.bracingCoordTable.setItem(rows, mat, QTableWidgetItem(str(member.material)))
                
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
        self.addCoordButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteCoordButton.setIcon(QIcon(r"Icons\24x24\minus.png"))
        
    def addBracingScheme(self, signal):
        '''add bracing and clear coord properties (not saved yet)'''

        # add new row to bracing scheme table
        self.bracingSchemeTable.insertRow(self.bracingSchemeTable.rowCount())

        # Display default bracing
        self.bracingSchemeViewer.displayed_bracing = 'default'

        # empty coord. table
        self.bracingCoordTable.setRowCount(0)

        # clear bracing name
        self.bracingNameEdit.clear()


    def deleteBracingScheme(self, signal):
        '''delete bracing and associated coord properties'''
        
        # add warning message: Are you sure you want to delete?
        bracings = self.tower.bracings

        # Display single cross bracing as default
        self.bracingSchemeViewer.displayed_bracing = 'default'

        # remove selected rows from table
        indices = self.bracingSchemeTable.selectionModel().selectedRows()
        for index in sorted(indices):
            # remove from dictionary
            print(index.row())
            bcName = self.bracingSchemeTable.item(index.row(),0).text()
            bracings.pop(bcName, None)

            # remove row from table
            self.bracingSchemeTable.removeRow(index.row())

        # empty coord. table
        self.bracingCoordTable.setRowCount(0)

        # clear bracing name
        self.bracingNameEdit.clear()

    def addBracingCoord(self, signal):
        ''' Add empty row to coordinate table'''
        self.bracingCoordTable.insertRow(self.bracingCoordTable.rowCount())

    def deleteBracingCoord(self, signal):
        ''' Delete selected rows from coordinate table'''
        indices = self.bracingCoordTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.bracingCoordTable.removeRow(index.row())

    def updateBracing(self, signal):
        ''' Save new bracing and associated coord properties '''

        #warning = WarningMessage()
        bracings = self.tower.bracings
        bcName = self.bracingNameEdit.text()

        if not (bcName in bracings):
            newBracing = Bracing(bcName)
            self.tower.addBracing(newBracing)

        bracing = bracings[bcName]

        for row in range(self.bracingCoordTable.rowCount()):
            # changed from 1,2,3,4
            x1 = float(self.bracingCoordTable.item(row, 0).text())
            y1 = float(self.bracingCoordTable.item(row, 1).text())
            x2 = float(self.bracingCoordTable.item(row, 2).text())
            y2 = float(self.bracingCoordTable.item(row, 3).text())
            material = str(self.bracingCoordTable.item(row, 4).text())

            node1 = Node(x1, y1)
            node2 = Node(x2, y2)

            bracing.addMat(material)
            bracing.addNodes(node1, node2)

        # generate members
        bracing.generateMembersfromNodes()

        # change bracing name in main table
        newRow = self.bracingSchemeTable.rowCount()
        bcItem = QTableWidgetItem(bcName)
        '''How to disable clicking?'''
        #bcItem.setFlags(QtCore.Qt.ItemIsEditable)
        self.bracingSchemeTable.setItem(int(newRow)-1,0,bcItem)

        # set displayed bracing to new bracing
        self.bracingSchemeViewer.displayed_bracing = bcName


    '''
    def saveBracingSchemes(self, signal):

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
    '''

    def setOkandCancelButtons(self):
        '''OK and Cancel button both exit dialog but have no save function!'''
        self.OkButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(lambda x: self.close())
       #self.OkButton.clicked.connect(self.saveBracingSchemes)

        self.CancelButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

'''
class BracingSchemeData:

    def __init__(self):
        self.bracingSchemes = {}
'''