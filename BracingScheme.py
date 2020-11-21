from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os
import copy

from Model import *    # import Model to access tower objects
from View2DEngine import *
from Definition import *    # import constants from Definition
from WarningMessage import *

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

        # Update whole screen upon picking bracing scheme
        self.bracingSchemeTable.itemClicked.connect(self.updateScreen)

        # Add Empty Row to List of Bracing Coordinates
        self.addCoordButton.clicked.connect(self.addBracingCoord)

        # Delete Selected Row from List of Bracing Coordinates
        self.deleteCoordButton.clicked.connect(self.deleteBracingCoord)

        # Update XY Coord Table upon cell change
        self.bracingCoordTable.itemSelectionChanged.connect(self.updateCoord)
        
        # Passing in main.tower into bracing scheme
        self.towerRef = args[0].tower

        # Create copy of tower to reassign if user saves
        self.tower = copy.deepcopy(args[0].tower)
        
        # Fill in bracing scheme table
        self.Populate()

        # Save the current bracing name if it exists
        if self.bracingSchemeTable.item(0,0) is not None:
            self.currentBracingName = self.bracingSchemeTable.item(0,0).text()
        else:
            self.currentBracingName = None

        # change Name in main table after a name is assigned in coord table
        self.bracingSchemeTable.cellChanged.connect(self.nameChange)

        # Update 2D view constantly
        timer = QTimer(self)
        timer.timeout.connect(self.set2DViewDimension)
        timer.timeout.connect(self.updateBracingView)
        timer.timeout.connect(self.bracingSchemeViewer.update)
        timer.start()

    def setIconsForButtons(self):
        self.addBracingSchemeButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteBracingSchemeButton.setIcon(QIcon(r"Icons\24x24\minus.png"))
        self.addCoordButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteCoordButton.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def setOkandCancelButtons(self):
        '''OK and Cancel button both exit dialog but have no save function!'''
        self.OkButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveBracingSchemes)
        self.OkButton.clicked.connect(lambda x: self.close())

        self.CancelButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

    def saveBracingSchemes(self):
        '''Overwrite the tower linked to the main model'''
        self.towerRef.bracings = self.tower.bracings
    
    def addBracingScheme(self):
        '''add bracing and clear coord properties '''
        newBracing = Bracing()
        id = 1
        newBracing.name = "New Bracing " + str(id)
        while newBracing.name in self.tower.bracings:
            id += 1
            newBracing.name = "new Bracing " + str(id)
        self.tower.addBracing(newBracing)
        self.Populate()
        
        # empty coord. table
        self.bracingCoordTable.setRowCount(0)

        # clear bracing name
        self.bracingNameEdit.clear()

    def deleteBracingScheme(self):
        '''delete bracing and associated coord properties'''

        # remove selected rows from table
        indices = self.bracingSchemeTable.selectionModel().selectedRows()
        for index in sorted(indices):
            # remove from dictionary
            bcName = self.bracingSchemeTable.item(index.row(),index.column()).text()
            self.tower.bracings.pop(bcName, None)
            # remove row from table
            self.bracingSchemeTable.removeRow(index.row())

        # empty coord. table
        self.bracingCoordTable.setRowCount(0)

        # clear bracing name
        self.bracingNameEdit.clear()


    def updateScreen(self):
        '''Update BracingCoordTable'''

        # if switching to an existing bracing
        if self.currentBracingName is not None:

            self.bracingCoordTable.setRowCount(0)
            X1 = 0
            Y1 = 1
            X2 = 2
            Y2 = 3
            mat = 4
            row = self.bracingSchemeTable.currentRow()
            bcName = self.bracingSchemeTable.item(row,0)
            bracing = self.tower.bracings[bcName.text()]
            self.currentBracingName = bcName.text()

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

            # match bracing name above coord. table to main table
            self.bracingNameEdit.setText(self.bracingSchemeTable.item(row,0).text())

    def addBracingCoord(self):
        ''' Add empty row to coordinate table'''
        row = self.bracingCoordTable.rowCount()
        self.bracingCoordTable.insertRow(row)
        self.bracingCoordTable.setItem(row, 0, QTableWidgetItem(str(0)))
        self.bracingCoordTable.setItem(row, 1, QTableWidgetItem(str(0)))
        self.bracingCoordTable.setItem(row, 2, QTableWidgetItem(str(0)))
        self.bracingCoordTable.setItem(row, 3, QTableWidgetItem(str(0)))
        self.bracingCoordTable.setItem(row, 4, QTableWidgetItem(''))
        self.updateCoord()

    def deleteBracingCoord(self):
        ''' Delete selected rows from coordinate table'''
        indices = self.bracingCoordTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.bracingCoordTable.removeRow(index.row())
        self.updateCoord()

    def updateCoord(self):
        '''Update coordinates and material associated with current bracing'''
        currName = self.bracingNameEdit.toPlainText()
        if  currName != "":
            newBracing = self.tower.bracings[currName]
            # delete all existing definitions
            newBracing.members = []
            newBracing.nodePairs = []
            newBracing.materials = []
            for row in range(self.bracingCoordTable.rowCount()):
                # changed from 1,2,3,4
                x1 = float(self.bracingCoordTable.item(row, 0).text())
                y1 = float(self.bracingCoordTable.item(row, 1).text())
                x2 = float(self.bracingCoordTable.item(row, 2).text())
                y2 = float(self.bracingCoordTable.item(row, 3).text())
                material = str(self.bracingCoordTable.item(row, 4).text())

                node1 = Node(x1, y1)
                node2 = Node(x2, y2)
                newBracing.nodePairs.append([node1, node2])
                newBracing.materials.append(material)
            # generate members
            newBracing.generateMembersfromNodes()

    def Populate(self):
        '''Add existing bracing schemes to bracingSchemeTable'''
        column = 0
        self.bracingSchemeTable.setRowCount(0)
        for row, bracingScheme in enumerate(self.tower.bracings):
            self.bracingSchemeTable.insertRow(self.bracingSchemeTable.rowCount())
            bcItem = QTableWidgetItem(bracingScheme)
            self.bracingSchemeTable.setItem(row, column, bcItem)

    def nameChange(self):
        ''' change bracing name after it is defined in main table '''
        row = self.bracingSchemeTable.currentRow() #returns -1 when repopulating empty table
        if row != -1 and self.currentBracingName != None:
            bcName = self.bracingSchemeTable.item(row,0)
            bracing = self.tower.bracings[self.currentBracingName]
            # update bracing name to match changed cell
            bracing.name = bcName.text()
            # assign original coordinates to new bracing name
            self.tower.bracings[bcName.text()] = self.tower.bracings.pop(self.currentBracingName)
            self.updateScreen()

    def updateBracingView(self):
        # update only when at least 1 bracing has been defined
        if not self.tower.bracings:
            return

        vMembers, vNodes = self.View2DBracings()

        self.bracingSchemeViewer.reset()

        for vMember in vMembers:
            self.bracingSchemeViewer.addMember(vMember)

        for vNode in vNodes:
            self.bracingSchemeViewer.addNode(vNode)

    def View2DBracings(self):
        renderX = 1.0 # scaled to 1.0x regardless of project setting
        renderY = 1.0

        vMembers = []
        vNodes = []

        color_bracing = Color.Member['Bracing']
        color_node = Color.Node['Bracing']

        vMember = ViewMember()
        vNode = ViewNode()

        # Set View Objects attributes
        vMember.setColor(color_bracing)
        vMember.setSize(View2DConstants.MEMBER_SIZE)
        vMember.setDimX(renderX)
        vMember.setDimY(renderY)

        vNode.setColor(color_node)
        vNode.setSize(View2DConstants.NODE_SIZE)
        vNode.setDimX(renderX)
        vNode.setDimY(renderY)

        currName = self.bracingNameEdit.toPlainText()
        if currName in self.tower.bracings.keys():
            bracing = self.tower.bracings[currName]

            for member in bracing.members:
                vMember.addMember(member)
                
                vNode.addNode(member.start_node)
                vNode.addNode(member.end_node)

            vMembers.append(vMember)
            vNodes.append(vNode)
        
        return vMembers, vNodes

    def set2DViewDimension(self):
        '''scale bracing based on project settings'''
        size = self.bracingSchemeViewer.size()

        self.bracingSchemeViewer.dimension_x = size.width()
        self.bracingSchemeViewer.dimension_y = size.height()

        '''
    def updateCoord(self):
        #Save new bracing and associated coord properties

        #warning = WarningMessage()
        bracings = self.tower.bracings
        bcName = self.bracingNameEdit.text()

        #delete existing bracing definition
        if bcName in bracings:
            bracings.pop('bcName', None)

        newBracing = Bracing(bcName)
        self.tower.addBracing(newBracing)

        for row in range(self.bracingCoordTable.rowCount()):
            # changed from 1,2,3,4
            x1 = float(self.bracingCoordTable.item(row, 0).text())
            y1 = float(self.bracingCoordTable.item(row, 1).text())
            x2 = float(self.bracingCoordTable.item(row, 2).text())
            y2 = float(self.bracingCoordTable.item(row, 3).text())
            material = str(self.bracingCoordTable.item(row, 4).text())

            node1 = Node(x1, y1)
            node2 = Node(x2, y2)
            
            newBracing.addNodes(node1,node2)
            newBracing.addMat(material)

        # generate members
        newBracing.generateMembersfromNodes()

        # change bracing name in main table
        newRow = self.bracingSchemeTable.rowCount()
        bcItem = QTableWidgetItem(bcName)
        #How to disable clicking?
        #bcItem.setFlags(QtCore.Qt.ItemIsEditable)
        self.bracingSchemeTable.setItem(int(newRow)-1,0,bcItem)

        # set displayed bracing to new bracing
        self.bracingSchemeViewer.displayed_bracing = bcName

        try:
            if elev == '':
                break
            tempElevs.append(float(elev))
        except:
            warning.popUpErrorBox('Invalid input for elevations')
            return # terminate the saving process
        '''

    

'''
class BracingSchemeData:

    def __init__(self):
        self.bracingSchemes = {}
'''