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
        self.add.clicked.connect(self.addFloorPlan)

        #set up add coordinates button
        self.addCoord.clicked.connect(self.addCoordinate)

        # Delete Selected Row from List of Floor Plan Schemes
        self.delete_2.clicked.connect(self.deleteFloorPlan)

        #Set up delete coordinates button
        self.deleteCoord.clicked.connect(self.deleteCoordinate)

        #Call update on the Coordinate table upon change in cell
        self.XYCoordTable.itemSelectionChanged.connect(self.updateCoordinates)

        #Call update in the elevation Table upon upon change in cell
        self.ElevationTable.itemSelectionChanged.connect(self.updateElevations)

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

    def populateElevationTable(self):
        '''update the elevations and the associated floor plans'''
        X = 0
        Y = 1
        Z = 2

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

                self.createElevationRow(rows, X, Y, Z, elev, fpName1, fpName2)

    def createElevationRow(self,rows,X,Y,Z,elevation, floorPlan1, floorPlan2):
        '''Create elevations row for the UpdateScreenXYElev'''
        self.ElevationTable.insertRow(self.ElevationTable.rowCount())

        # To prevent user from editing the elevation column
        elevItem = QTableWidgetItem(str(elevation))
        elevItem.setFlags(Qt.ItemIsEnabled)

        self.ElevationTable.setItem(rows, X, elevItem)
        self.ElevationTable.setItem(rows, Y, QTableWidgetItem(floorPlan1))
        self.ElevationTable.setItem(rows, Z, QTableWidgetItem(floorPlan2))

    def updateScreenXYElev(self):
        '''Update everything on selected item on the right tab'''
        #Update XYCOord Table
        column = 0
        self.XYCoordTable.setRowCount(0)

        X = 0
        Y = 1
        botCol = 2
        topCol = 3

        fp_row = self.floorPlanTable.currentRow() #returns -1 when i'm repopulation the table
        item = self.floorPlanTable.item(fp_row,column)
        floorPlan = self.tower.floorPlans[item.text()]
        self.currentFloorPlanName = item.text()

        # Update X Y coordinates
        for XY_row, member in enumerate(floorPlan.members):
            node = member.start_node
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
            floorPlan = self.tower.floorPlans[self.currentFloorPlanName]
            floorPlan.name =  item.text()
            self.tower.floorPlans[item.text()]=self.tower.floorPlans.pop(self.currentFloorPlanName)
            self.updateScreenXYElev()

    def setIconsForButtons(self):
        '''Set icons associated with the add/delete buttons'''
        self.add.setIcon(QIcon(':/Icons/plus.png'))
        self.delete_2.setIcon(QIcon(':/Icons/minus.png'))
        self.addCoord.setIcon(QIcon(':/Icons/plus.png'))
        self.deleteCoord.setIcon(QIcon(':/Icons/minus.png'))

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
        for index in sorted(indices):
            item = self.floorPlanTable.item(index.row(),index.column())
            del self.tower.floorPlans[item.text()]
        for index in sorted(indices):
            self.floorPlanTable.removeRow(index.row())

    def updateCoordinates(self):
        '''Update the coordinates associated with the floor plan based on current '''
        nodes = []
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

            for i in range(self.XYCoordTable.rowCount()):
                Xitem = self.XYCoordTable.item(i,X).text()
                Yitem = self.XYCoordTable.item(i,Y).text()

                try:
                    node = Node(float(Xitem),float(Yitem))
                except:
                    warning = WarningMessage()
                    warning.popUpErrorBox('Coordinates must be in numbers')

                    self.XYCoordTable.setItem(i, X, QTableWidgetItem('0'))
                    self.XYCoordTable.setItem(i, Y, QTableWidgetItem('0'))
                    return
                
                nodes.append(node)

                botItem = self.XYCoordTable.item(i,botCol).text()
                topItem = self.XYCoordTable.item(i,topCol).text()

                floorPlan.addBottomConnection(botItem, i)
                floorPlan.addTopConnection(topItem, i)

            floorPlan.nodes = nodes
            floorPlan.generateMembersfromNodes()

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
        '''delete coordinates and call update coordinates on the table for the floor plan nodes'''
        indices = self.XYCoordTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.XYCoordTable.removeRow(index.row())
        self.updateCoordinates()

    def cancelFloorPlan(self):
        '''do Nothing'''
        self.towerRef = self.towerRef

    def updateElevations(self):
        ''' Update the floor object on every elevation with the associated floor plans based on current '''
        X = 0
        Y = 1
        Z = 2

        for i in range(self.ElevationTable.rowCount()):
            elevationItem = self.ElevationTable.item(i,X).text()
            floorPlan1Item = self.ElevationTable.item(i,Y).text()
            floorPlan2Item = self.ElevationTable.item(i,Z).text()

            # clear existing floor plans on each floor
            elevation = float(elevationItem)
            floor = self.tower.floors[elevation]
            floor.floorPlans.clear()

            if floorPlan1Item in self.tower.floorPlans:
                floor.addFloorPlan(self.tower.floorPlans[floorPlan1Item])
            if floorPlan2Item in self.tower.floorPlans:
                floor.addFloorPlan(self.tower.floorPlans[floorPlan2Item])

    def saveFloorPlan(self):
        '''Overwrite the tower linked to the main model'''
        self.towerRef.floorPlans = self.tower.floorPlans
        self.towerRef.floors = self.tower.floors

        # Maybe need a wrapper function ---------------------
        # clear all faces, panels, floors and columns if floor plan is updated
        self.towerRef.faces.clear()
        self.towerRef.panels.clear()
        for elev in self.towerRef.elevations:
            floor  = self.towerRef.floors[elev]
            floor.panels.clear()
        self.towerRef.columns.clear()       

        self.towerRef.generateFaces()
        self.towerRef.generateColumnsByFace()     
        
    def setOkandCancelButtons(self):
        #Constructor
        self.OkButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveFloorPlan)
        self.OkButton.clicked.connect(lambda x: self.close())

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

        vMember = ViewMember()
        vNode = ViewNode()

        # Set View Objects attributes --------------------------------
        vMember.setColor(color_fplan[0])
        vMember.setSize(View2DConstants.MEMBER_SIZE)
        vMember.setDimX(renderX)
        vMember.setDimY(renderY)

        vNode.setColor(color_node)
        vNode.setSize(View2DConstants.NODE_SIZE)
        vNode.setDimX(renderX)
        vNode.setDimY(renderY)

        # Floor plan members and nodes -------------------------------
        if self.SelectedFloorName.toPlainText() in self.tower.floorPlans.keys():
            floorPlan= self.tower.floorPlans[self.SelectedFloorName.toPlainText()]
            for member in floorPlan.members:
                vMember.addMember(member)

                vNode.addNode(member.start_node)
                vNode.addNode(member.end_node)  # redundant but just in case

            vMembers.append(vMember)
            vNodes.append(vNode)

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

