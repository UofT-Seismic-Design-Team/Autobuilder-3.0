from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os
import copy

import resources    # For icons and UIs

from Model import *    # import Model to access tower objects
from View2DEngine import *
from Definition import *    # import constants from Definition
from Message import *

class BracingScheme(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        fileh = QFile(':/UI/autobuilder_bracingscheme_v1.ui', self)
        fileh.open(QFile.ReadOnly)
        uic.loadUi(fileh, self)
        fileh.close()

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

        # Update XY Coord Table upon SELECTION change
        # ie. change is only saved when user clicks on a different cell after editing
        self.bracingCoordTable.itemSelectionChanged.connect(self.updateCoord)
        
        # Passing in main.tower into bracing scheme
        self.towerRef = args[0].tower

        # Passing in main.projectSettingsData into bracing scheme
        self.projectSettingsData = args[0].projectSettingsData

        # Create copy of tower to reassign if user saves
        self.tower = copy.deepcopy(args[0].tower)

        # Defined sections
        self.sections = list(self.projectSettingsData.sections.keys())
        
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
        self.addBracingSchemeButton.setIcon(QIcon(':/Icons/plus.png'))
        self.deleteBracingSchemeButton.setIcon(QIcon(':/Icons/minus.png'))
        self.addCoordButton.setIcon(QIcon(':/Icons/plus.png'))
        self.deleteCoordButton.setIcon(QIcon(':/Icons/minus.png'))

    def setOkandCancelButtons(self):
        '''OK and Cancel button both exit dialog but have no save function!'''
        self.OkButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveBracingSchemes)
        self.OkButton.clicked.connect(lambda x: self.close())

        self.CancelButton = self.bracingSchemeButtonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

    def saveBracingSchemes(self):
        '''Overwrite the tower linked to the main model'''
        # ensure everything is updated before saving
        self.updateCoord()
        self.towerRef.bracings = self.tower.bracings
    
    def addBracingScheme(self):
        '''add bracing and clear coord properties '''
        # Reset -----------------------------------
        # empty coord. table
        self.bracingCoordTable.setRowCount(0)
        # clear bracing name
        self.bracingNameEdit.clear()

        # Initialize new bracing scheme with at least one node pairs --------------------
        newBracing = Bracing()

        newBracing.members, newBracing.nodePairs, newBracing.materials = [], [], []

        newBracing.nodePairs.append([Node(0,0), Node(0,0)])
        newBracing.materials.append(self.sections[0])
        # Generate members
        newBracing.generateMembersfromNodes()

        id = 1
        newBracing.name = "New Bracing " + str(id)
        while newBracing.name in self.tower.bracings:
            id += 1
            newBracing.name = "New Bracing " + str(id)
        self.tower.addBracing(newBracing)

        # Refresh
        self.Populate()
        self.bracingSchemeTable.selectRow(self.bracingSchemeTable.rowCount()-1)
        self.updateScreen()

    def deleteBracingScheme(self):
        '''delete bracing and associated coord properties'''
        # remove selected rows from table
        indices = self.bracingSchemeTable.selectionModel().selectedRows()
        for i, index in enumerate(sorted(indices)):
            # remove from dictionary
            updatedRow = index.row()-i
            bcName = self.bracingSchemeTable.item(updatedRow,index.column()).text()
            self.tower.bracings.pop(bcName, None)
            # remove row from table
            self.bracingSchemeTable.removeRow(updatedRow)

        # empty coord. table
        self.bracingCoordTable.setRowCount(0)

        # clear bracing name
        self.bracingNameEdit.clear()

    def updateScreen(self):
        '''Update BracingCoordTable'''

        # save when switching between bracing schemes
        self.updateCoord()

        # clear selections in coord table to avoid error
        self.bracingCoordTable.clearSelection()

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

                # make drop-down menu for brace material
                materialCombo = QComboBox()
                for m in self.sections:
                    materialCombo.addItem(m)
                self.bracingCoordTable.setCellWidget(rows,mat,materialCombo)

                # In case of corrupted file
                if member.material in self.sections:
                    materialCombo.setCurrentText(member.material)
                else:
                    materialCombo.setCurrentText(self.sections[0])

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

        # make drop-down menu for brace material
        materialCombo = QComboBox()
        for m in self.sections:
            materialCombo.addItem(m)
        self.bracingCoordTable.setCellWidget(row,4,materialCombo)
        materialCombo.setCurrentText(self.sections[0])

        self.updateCoord()

    def deleteBracingCoord(self):
        ''' Delete selected rows from coordinate table'''
        indices = self.bracingCoordTable.selectionModel().selectedRows()

        # clear selections in coord table to avoid error
        self.bracingCoordTable.clearSelection()

        for i, index in enumerate(sorted(indices)):
            updatedRow = index.row()-i
            self.bracingCoordTable.removeRow(updatedRow)

        self.updateCoord()

    def updateCoord(self):
        '''Update coordinates and material associated with current bracing'''

        # problematic when currname isn't defined?
        currName = self.bracingNameEdit.toPlainText()
        if currName != "":
            newBracing = self.tower.bracings[currName]
            # delete all existing definitions
            newBracing.members = []
            newBracing.nodePairs = []
            newBracing.materials = []

            for row in range(self.bracingCoordTable.rowCount()):
                # changed from 1,2,3,4
                x1 = self.bracingCoordTable.item(row, 0).text()
                y1 = self.bracingCoordTable.item(row, 1).text()
                x2 = self.bracingCoordTable.item(row, 2).text()
                y2 = self.bracingCoordTable.item(row, 3).text()
    
                coords = Algebra.strToFloat(x1, y1, x2, y2)

                if not coords:
                    warning = WarningMessage()
                    warning.popUpErrorBox('Coordinates must only contain numbers or following operators: "+", "-", "*", "/"')

                    self.bracingCoordTable.setItem(row, 0, QTableWidgetItem('0'))
                    self.bracingCoordTable.setItem(row, 1, QTableWidgetItem('0'))
                    self.bracingCoordTable.setItem(row, 2, QTableWidgetItem('0'))
                    self.bracingCoordTable.setItem(row, 3, QTableWidgetItem('0'))
                    return
                
                try:
                    material = str(self.bracingCoordTable.cellWidget(row,4).currentText())
                except:
                    material = self.sections[0]

                self.bracingCoordTable.setItem(row, 0, QTableWidgetItem(str(coords[0])))                
                self.bracingCoordTable.setItem(row, 1, QTableWidgetItem(str(coords[1])))
                self.bracingCoordTable.setItem(row, 2, QTableWidgetItem(str(coords[2])))
                self.bracingCoordTable.setItem(row, 3, QTableWidgetItem(str(coords[3])))

                node1 = Node(coords[0], coords[1])
                node2 = Node(coords[2], coords[3])

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
            bcName = self.bracingSchemeTable.item(row,0).text()
            
            warning = WarningMessage()
            if bcName == '':
                warning.popUpErrorBox('Bracing name is missing.')
                self.bracingSchemeTable.item(row,0).setText(self.currentBracingName)
                return

            if bcName in self.tower.bracings:
                warning.popUpErrorBox('Bracing name already exists.')
                self.bracingSchemeTable.item(row,0).setText(self.currentBracingName)
                return

            bracing = self.tower.bracings[self.currentBracingName]
            # update bracing name to match changed cell
            bracing.name = bcName
            # assign original coordinates to new bracing name
            self.tower.bracings[bcName] = self.tower.bracings.pop(self.currentBracingName)

            # match bracing name above coord. table to main table
            self.bracingNameEdit.setText(bcName)
            
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
