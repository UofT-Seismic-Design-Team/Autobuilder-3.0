from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

from Model import *
from View2DEngine import *  # import View2DEngine
from Message import *

import copy

import resources    # For icons and UIs

import sys  # We need sys so that we can pass argv to QApplication
import os

class FloorPlanUI(QDialog):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        fileh = QFile(':/UI/autobuilder_floordesign_v2.ui')
        fileh.open(QFile.ReadOnly)
        uic.loadUi(fileh, self)
        fileh.close()

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Add Empty Row to List of Floor Plan Schemes
        self.addFloorPlan_button.clicked.connect(self.addFloorPlan)

        #set up add coordinates button
        self.addCoord.clicked.connect(self.addCoordinate)

        #set up add member button
        self.addMember_button.clicked.connect(self.addMember)

        # Delete Selected Row from List of Floor Plan Schemes
        self.deleteFloorPlan_button.clicked.connect(self.deleteFloorPlan)

        #Set up delete coordinates button
        self.deleteCoord.clicked.connect(self.deleteCoordinate)

        #set up delete member button
        self.deleteMember_button.clicked.connect(self.deleteMember)

        #Call update on the Coordinate table upon change in cell
        self.XYCoordTable.itemSelectionChanged.connect(self.updateCoordinates)

        #Call update on the member table upon change in cell
        self.memberTable.itemSelectionChanged.connect(self.updateCoordinates)

        #Call update in the elevation Table upon upon change in cell
        self.ElevationTable.itemSelectionChanged.connect(self.updateElevations)

        #Call update in the centre of mass Table upon upon change in cell
        self.COMTable.itemSelectionChanged.connect(self.updateCOMs)

        #create a copy of the tower to reassign if user saves.
        self.tower = copy.deepcopy(args[0].tower)

        # passing in main.tower properties into floorPlan
        self.populate()

        #Save the current floorplan table name and intialize for the first one for later use in changing and saving the name
        self.currentFloorPlanName = self.floorPlanTable.item(0,0).text()

        #Call update upon ScreenXYElev to update the whole screen upon picking floor plan
        self.floorPlanTable.itemClicked.connect(self.updateScreenXYElev)

        #Call cell name change
        self.floorPlanTable.cellChanged.connect(self.nameChange)

        self.projectSettingsData = args[0].projectSettingsData

        #reference to existing tower for cache
        self.towerRef = args[0].tower

        # Flags
        self.stopUpdateCoordinates = False

        timer = QTimer(self)
        timer.timeout.connect(self.set2DViewDimension)
        timer.timeout.connect(self.updateSectionView)
        timer.timeout.connect(self.floorPlanViewer.update)
        timer.start()


    def populate(self):
        '''Populate the floorPlan Table with floorplans from the tower'''
        column = 0
        #Clear the floorplan table
        self.floorPlanTable.setRowCount(0)
        #Iterate through and add the floor plans
        for i,floorPlan in enumerate(self.tower.floorPlans):
            self.floorPlanTable.insertRow(self.floorPlanTable.rowCount())
            item = QTableWidgetItem()
            item.setText(self.tower.floorPlans[floorPlan].name)
            self.floorPlanTable.setItem(i, column, item)

        self.populateElevationTable()
        self.populateCOMTable()

    def populateElevationTable(self):
        '''update the elevations and the associated floor plans'''
        self.ElevationTable.setRowCount(0)
        
        for rows, elev in enumerate(self.tower.elevations):
            if elev in self.tower.floors:

                floorPlans = self.tower.floors[elev].floorPlans
                numFPs = len(floorPlans)

                fpName1 = ''
                fpName2 = ''

                if numFPs >= 1:
                    fpName1 = floorPlans[0].name
                if numFPs == 2:
                    fpName2 = floorPlans[1].name

                self.createElevationRow(rows, elev, fpName1, fpName2)

    def createElevationRow(self,rows,elevation, floorPlan1, floorPlan2):
        '''Create elevations row for the UpdateScreenXYElev'''

        self.ElevationTable.insertRow(self.ElevationTable.rowCount())

        # To prevent user from editing the elevation column
        elevItem = QTableWidgetItem(str(elevation))
        elevItem.setFlags(Qt.ItemIsEnabled)

        self.ElevationTable.setItem(rows, 0, elevItem)
        self.ElevationTable.setItem(rows, 1, QTableWidgetItem(floorPlan1))
        self.ElevationTable.setItem(rows, 2, QTableWidgetItem(floorPlan2))

    def populateCOMTable(self):
        '''update the elevations and the associated COMs'''
        self.COMTable.setRowCount(0)
        
        for rows, elev in enumerate(self.tower.elevations):
            if elev in self.tower.floors:

                comX = str(self.tower.floors[elev].comX)
                comY = str(self.tower.floors[elev].comY)

                self.createCOMRow(rows, elev, comX, comY)

    def createCOMRow(self, rows, elevation, comX, comY):
        '''Create rows for Centre of Mass Table'''

        self.COMTable.insertRow(self.COMTable.rowCount())

        # To prevent user from editing the elevation column
        elevItem = QTableWidgetItem(str(elevation))
        elevItem.setFlags(Qt.ItemIsEnabled)

        self.COMTable.setItem(rows, 0, elevItem)
        self.COMTable.setItem(rows, 1, QTableWidgetItem(comX))
        self.COMTable.setItem(rows, 2, QTableWidgetItem(comY))

    def updateScreenXYElev(self):
        '''Update everything on selected item on the right tab'''

        # Disable updateCoords when resetting tables -----------------------------
        self.stopUpdateCoordinates = True
        self.memberTable.setRowCount(0)
        self.XYCoordTable.setRowCount(0)
        self.stopUpdateCoordinates = False

        column = 0
        #Update XYCOord Table
        X = 0
        Y = 1
        botCol = 2
        topCol = 3

        fp_row = self.floorPlanTable.currentRow() #returns -1 when i'm repopulation the table
        item = self.floorPlanTable.item(fp_row,column)
        floorPlan = self.tower.floorPlans[item.text()]
        self.currentFloorPlanName = item.text()

        # Update X Y coordinates
        for XY_row, node in enumerate(floorPlan.nodes):
            self.XYCoordTable.insertRow(self.XYCoordTable.rowCount())
            self.XYCoordTable.setItem(XY_row, X, QTableWidgetItem(str(node.x)))
            self.XYCoordTable.setItem(XY_row, Y, QTableWidgetItem(str(node.y)))

        # Update top connection labels
        for top in floorPlan.topConnections:
            list_top_row = floorPlan.topConnections[top]
            for top_row in list_top_row:
                self.XYCoordTable.setItem(top_row, topCol, QTableWidgetItem(str(top)))

        # Update bottom connection labels
        for bot in floorPlan.bottomConnections:
            list_bot_row = floorPlan.bottomConnections[bot]
            for bot_row in list_bot_row:
                self.XYCoordTable.setItem(bot_row, botCol, QTableWidgetItem(str(bot)))

        # Update member table
        # NOTE: add 1 to start and end in member table to reflect row numbers in XYCoordTable (e.g starts from 1)
        for row, [start, end] in enumerate(floorPlan.nodePairs):
            self.memberTable.insertRow(self.memberTable.rowCount())
            self.memberTable.setItem(row, 0, QTableWidgetItem(str(start+1)))
            self.memberTable.setItem(row, 1, QTableWidgetItem(str(end+1)))

        #UpdateElevationTableView based on Selecteditems
        self.SelectedFloorName.setText(self.floorPlanTable.item(fp_row, column).text())

    def nameChange(self):
        '''Change the name according '''
        column = 0
        row = self.floorPlanTable.currentRow() #returns -1 when i'm repopulation the table
        add = False
        if row == -1:
            row = 0
            add = True
        item = self.floorPlanTable.item(row,column)
        #adding new rows also prompt the name change, ergo handle exception
        if add == False:

            warning = WarningMessage()
            if item.text() == '':
                warning.popUpErrorBox('Floor plan name is missing.')
                self.floorPlanTable.item(row,0).setText(self.currentBracingName)
                return

            if item.text() in self.tower.floorPlans:
                warning.popUpErrorBox('Floor plan name already exists.')
                self.floorPlanTable.item(row,0).setText(self.currentBracingName)
                return

            floorPlan = self.tower.floorPlans[self.currentFloorPlanName]
            floorPlan.name =  item.text()
            self.tower.floorPlans[item.text()] = self.tower.floorPlans.pop(self.currentFloorPlanName)
            self.updateScreenXYElev()

    def setIconsForButtons(self):
        '''Set icons associated with the add/delete buttons'''
        self.addFloorPlan_button.setIcon(QIcon(':/Icons/plus.png'))
        self.deleteFloorPlan_button.setIcon(QIcon(':/Icons/minus.png'))
        self.addCoord.setIcon(QIcon(':/Icons/plus.png'))
        self.deleteCoord.setIcon(QIcon(':/Icons/minus.png'))
        self.addMember_button.setIcon(QIcon(':/Icons/plus.png'))
        self.deleteMember_button.setIcon(QIcon(':/Icons/minus.png'))

    def addFloorPlan(self):
        '''Adding new floor plans'''
        newfloorPlan = FloorPlan()
        id = 1
        newfloorPlan.name = "New Floor Plan " + str(id)
        while newfloorPlan.name in self.tower.floorPlans:
            id += 1
            newfloorPlan.name = "New Floor Plan " + str(id)
        self.tower.addFloorPlan(newfloorPlan)
        self.populate()

    def deleteFloorPlan(self):
        '''Delete floor plan from tower'''
        indices = self.floorPlanTable.selectionModel().selectedRows()
        for i, index in enumerate(sorted(indices)):
            # remove from dictionary
            updatedRow = index.row()-i
            fpName = self.floorPlanTable.item(updatedRow,index.column()).text()
            self.tower.floorPlans.pop(fpName, None)
            # remove row from table
            self.floorPlanTable.removeRow(updatedRow)

    def updateCoordinates(self):
        '''Update the coordinates associated with the floor plan based on current '''
        if self.stopUpdateCoordinates:
            return

        X = 0
        Y = 1
        botCol = 2
        topCol = 3 

        #Check if the label associated with it is empty or not occurs upon intialization
        if self.SelectedFloorName.toPlainText() != '':
            floorPlan = self.tower.floorPlans[self.SelectedFloorName.toPlainText()]

            # reset floor plan data
            floorPlan.topConnections.clear()
            floorPlan.bottomConnections.clear()
            floorPlan.nodePairs.clear()
            floorPlan.nodes.clear()
            floorPlan.members.clear()
            
            # Iterate through XYCoordTable
            for i in range(self.XYCoordTable.rowCount()):
                Xitem = self.XYCoordTable.item(i,X).text()
                Yitem = self.XYCoordTable.item(i,Y).text()

                coords = Algebra.strToFloat(Xitem, Yitem)

                if not coords:
                    warning = WarningMessage()
                    warning.popUpErrorBox('Coordinates must only contain numbers or following operators: "+", "-", "*", "/"')
                    self.XYCoordTable.setItem(i, X, QTableWidgetItem('1'))
                    self.XYCoordTable.setItem(i, Y, QTableWidgetItem('1'))
                    return

                self.XYCoordTable.setItem(i, X, QTableWidgetItem(str(coords[0])))
                self.XYCoordTable.setItem(i, Y, QTableWidgetItem(str(coords[1])))

                node = Node(coords[0], coords[1])
                
                floorPlan.nodes.append(node)

                botItem = self.XYCoordTable.item(i,botCol).text()
                topItem = self.XYCoordTable.item(i,topCol).text()

                floorPlan.addBottomConnection(botItem, i)
                floorPlan.addTopConnection(topItem, i)

            # Iterate through member table
            for i in range(self.memberTable.rowCount()):
                startItem = self.memberTable.item(i,0).text()
                endItem = self.memberTable.item(i,1).text()

                try:
                    start = int(startItem) - 1
                    end = int(endItem) - 1

                except:
                    warning = WarningMessage()
                    warning.popUpErrorBox('Node index must be an integer')
                    self.memberTable.setItem(i, 0, QTableWidgetItem('1'))
                    self.memberTable.setItem(i, 1, QTableWidgetItem('1'))
                    return

                outOfRange = False
                for j, index in enumerate((start, end)):
                    if not (index in range(len(floorPlan.nodes))):
                        warning = WarningMessage()
                        warning.popUpErrorBox('Node index is out of range')
                        self.memberTable.setItem(i, j, QTableWidgetItem('1'))
                        outOfRange = True

                if not outOfRange:
                    floorPlan.nodePairs.append([start, end])
                    floorPlan.generateMemberFromNodePair(-1)

    def addCoordinate(self):
        X = 0
        Y = 1
        topCol = 2
        botCol = 3

        row = self.XYCoordTable.rowCount()
        self.XYCoordTable.insertRow(row)

        itemX, itemY, itemTop, itemBot = (QTableWidgetItem('0'), QTableWidgetItem('0'), QTableWidgetItem(str(row+1)), QTableWidgetItem(str(row+1)))
        self.XYCoordTable.setItem(row, X, itemX)
        self.XYCoordTable.setItem(row, Y, itemY)
        self.XYCoordTable.setItem(row, topCol, itemTop)
        self.XYCoordTable.setItem(row, botCol, itemBot)

        self.updateCoordinates()

    def deleteCoordinate(self):
        '''delete coordinates and call update coordinates on the table for the floor plan nodes and members'''
        indices = self.XYCoordTable.selectionModel().selectedRows()
        for i, index in enumerate(sorted(indices)):
            updatedRow = index.row()-i
            self.XYCoordTable.removeRow(updatedRow)

        self.updateCoordinates()

    def addMember(self):
        startIndex = 0
        endIndex = 1

        row = self.memberTable.rowCount()
        self.memberTable.insertRow(row)

        itemStart, itemEnd = (QTableWidgetItem('1'), QTableWidgetItem('1'))
        self.memberTable.setItem(row, startIndex, itemStart)
        self.memberTable.setItem(row, endIndex, itemEnd)

        self.updateCoordinates()

    def deleteMember(self):
        '''delete members and call update coordinates on the table for the floor plan nodes and members'''
        indices = self.memberTable.selectionModel().selectedRows()
        for i, index in enumerate(sorted(indices)):
            updatedRow = index.row()-i
            self.memberTable.removeRow(updatedRow)
        self.updateCoordinates()

    def cancelFloorPlan(self):
        '''do Nothing'''
        self.towerRef = self.towerRef

    def updateElevations(self):
        ''' Update the floor object on every elevation with the associated floor plans based on current '''

        for i in range(self.ElevationTable.rowCount()):
            elevationItem = self.ElevationTable.item(i,0).text()
            floorPlan1Item = self.ElevationTable.item(i,1).text()
            floorPlan2Item = self.ElevationTable.item(i,2).text()

            # clear existing floor plans on each floor
            elevation = float(elevationItem)
            floor = self.tower.floors[elevation]
            floor.floorPlans.clear()

            if floorPlan1Item in self.tower.floorPlans:
                floor.addFloorPlan(self.tower.floorPlans[floorPlan1Item])
            if floorPlan2Item in self.tower.floorPlans:
                floor.addFloorPlan(self.tower.floorPlans[floorPlan2Item])

    def updateCOMs(self):
        ''' Update the floor object on every elevation with the associated COM locations based on current '''

        for i in range(self.COMTable.rowCount()):
            elevationItem = self.COMTable.item(i,0).text()
            comXStr = self.COMTable.item(i,1).text()
            comYStr = self.COMTable.item(i,2).text()

            # clear existing floor plans on each floor
            elevation = float(elevationItem)

            com = Algebra.strToFloat(comXStr, comYStr)

            if not com:
                warning = WarningMessage()
                warning.popUpErrorBox('Centre of Mass Coordinates must only contain numbers or following operators: "+", "-", "*", "/"')
                self.COMTable.setItem(i, 1, QTableWidgetItem('0.0'))
                self.COMTable.setItem(i, 2, QTableWidgetItem('0.0'))
                return
            
            comX, comY = com

            self.tower.floors[elevation].comX = comX
            self.tower.floors[elevation].comY = comY

    def saveFloorPlan(self):
        '''Overwrite the tower linked to the main model'''
        if self.towerRef.panels:
            warning = WarningMessage()
            title = 'You will overwrite the existing tower configuration. Do you want to proceed?'
            warning.popUpConfirmation(title, self.updateTowerConfig)

        else:
            self.updateTowerConfig()
            self.close()

    def updateTowerConfig(self):
        self.towerRef.floorPlans = self.tower.floorPlans
        self.towerRef.floors = self.tower.floors

        # Clear and regenerate all tower components that depend on floor plans
        self.towerRef.faces.clear()
        self.towerRef.panels.clear()
        for elev in self.towerRef.elevations:
            floor = self.towerRef.floors[elev]
            floor.panels.clear()
        self.towerRef.columns.clear()       

        self.towerRef.generateFaces()
        self.towerRef.generateColumnsByFace()
    
    def setOkandCancelButtons(self):
        #Constructor
        self.OkButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveFloorPlan)

        self.CancelButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())
        self.CancelButton.clicked.connect(self.cancelFloorPlan)

    # For 2D view -----------------------------------------------------
    def set2DViewDimension(self):
        size = self.floorPlanViewer.size()
        self.floorPlanViewer.dimension_x = size.width()
        self.floorPlanViewer.dimension_y = size.height()

    def View2DObjects(self):
        ''' --> list(ViewMember), list(ViewNode), list(ViewText) '''

        renderX = self.projectSettingsData.renderX
        renderY = self.projectSettingsData.renderY

        # Step 1: Get floor plan from text

        vMembers = []
        vNodes = []
        vTexts = []

        # Step 2: Create view object for floor plans
        color_fplan = Color.FloorPlan['MainMenu']
        color_node = Color.Node['MainMenu']
        color_text = Color.Text['MainMenu']

        vMember = ViewMember()
        vNode = ViewNode()
        vText = ViewText()

        # Set View Objects attributes --------------------------------
        vMember.setColor(color_fplan[0])
        vMember.setSize(View2DConstants.MEMBER_SIZE)
        vMember.setDimX(renderX)
        vMember.setDimY(renderY)

        vNode.setColor(color_node)
        vNode.setSize(View2DConstants.NODE_SIZE)
        vNode.setDimX(renderX)
        vNode.setDimY(renderY)

        vText.setColor(color_text)
        vText.setSize(View2DConstants.TEXT_SIZE)
        vText.setDimX(renderX)
        vText.setDimY(renderY)

        # Floor plan members and nodes -------------------------------
        if self.SelectedFloorName.toPlainText() in self.tower.floorPlans.keys():
            floorPlan= self.tower.floorPlans[self.SelectedFloorName.toPlainText()]
            
            # Floor plan members ------------------------
            for member in floorPlan.members:
                vMember.addMember(member)

            # Floor plan nodes ------------------------
            for i, node in enumerate(floorPlan.nodes):
                vNode.addNode(node)

                # label ------------------------
                label = str(i+1)

                nodeShifted = copy.deepcopy(node)
                nodeShifted.x = node.x - 1

                vText.addMember(Member(node, nodeShifted))
                vText.addText(label)
                vText.setLocation(Node(1, 0.5)) # midpoint

            vMembers.append(vMember)
            vNodes.append(vNode)
            vTexts.append(vText)

        return vMembers, vNodes, vTexts

    def updateSectionView(self):

        if not self.tower.floors:  # update only when floors are provided
            return

        vMembers, vNodes, vTexts = self.View2DObjects()

        self.floorPlanViewer.reset()  # clear all the existing objects

        for vMember in vMembers:
            self.floorPlanViewer.addMember(vMember)

        for vNode in vNodes:
            self.floorPlanViewer.addNode(vNode)

        for vText in vTexts:
            self.floorPlanViewer.addText(vText)

