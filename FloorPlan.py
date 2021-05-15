from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic
from Model import *

from View2DEngine import *  # import View2DEngine
import copy

import resources    # For icons and UIs

import sys  # We need sys so that we can pass argv to QApplication
import os

class FloorPlanUI(QDialog):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        fileh = QFile(':/UI/autobuilder_floordesign_v1.ui')
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

        #Call update in the elevation Table upon the table being clicked
        self.ElevationTable.itemClicked.connect(self.updateElevations)

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

    def createElevationRow(self,rows,X,Y,elevation, checked = False):
        '''Create elevations row for the UpdateScreenXYElev'''
        self.ElevationTable.insertRow(self.ElevationTable.rowCount())
        self.ElevationTable.setItem(rows, X, QTableWidgetItem(str(elevation)))
        checkbox = QTableWidgetItem()
        checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        if checked == True:
            checkbox.setCheckState(Qt.Checked)
        else:
            checkbox.setCheckState(Qt.Unchecked)  # Uncheck those checkbox
        self.ElevationTable.setItem(rows, Y, checkbox)

    def updateScreenXYElev(self):
        '''Update everything on selected item on the right tab'''
        #Update XYCOord Table
        column = 0
        self.XYCoordTable.setRowCount(0)
        X = 0
        Y = 1
        row = self.floorPlanTable.currentRow() #returns -1 when i'm repopulation the table
        item = self.floorPlanTable.item(row,column)
        floorPlan = self.tower.floorPlans[item.text()]
        self.currentFloorPlanName = item.text()
        for rows, member in enumerate(floorPlan.members):
            node = member.start_node
            self.XYCoordTable.insertRow(self.XYCoordTable.rowCount())
            self.XYCoordTable.setItem(rows, X, QTableWidgetItem(str(node.x)))
            self.XYCoordTable.setItem(rows, Y, QTableWidgetItem(str(node.y)))

        #UpdateElevationTableView based on Selecteditems
        self.ElevationTable.setRowCount(0)
        for rows, elevation in enumerate(self.tower.elevations):
            if elevation in floorPlan.elevations:
                self.createElevationRow(rows, X, Y, elevation, checked=True)
            else:
                self.createElevationRow(rows, X, Y, elevation, checked=False)
        self.SelectedFloorName.setText(self.floorPlanTable.item(row, column).text())

        #Update the floorplan viewer
        # elev = floorPlan.elevations[1]
        # self.floorPlanViewer.elevation = elev

    def updateElevations(self):
        '''update the elevations associated with the floorplan upon the checkbox'''
        X= 0
        Y =1
        if self.SelectedFloorName.toPlainText() != '':
            floorPlan = self.tower.floorPlans[self.SelectedFloorName.toPlainText()]
            floorPlan.elevations.clear()
            for i in range(self.ElevationTable.rowCount()):
                elevation = self.ElevationTable.item(i,X).text()
                Check = self.ElevationTable.item(i,Y)
                #Check if the check box is ticked off and add the elevation
                if Check.checkState() == 2:
                    floorPlan.addElevation(float(elevation))

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
        X= 0
        Y =1
        #Check if the label associated with it is empty or not ^ occurs upon intialization
        if self.SelectedFloorName.toPlainText() != '':
            floorPlan = self.tower.floorPlans[self.SelectedFloorName.toPlainText()]
            for i in range(self.XYCoordTable.rowCount()):
                Xitem = self.XYCoordTable.item(i,X).text()
                Yitem = self.XYCoordTable.item(i,Y).text()
                node = Node(int(Xitem),int(Yitem))
                nodes.append(node)
            floorPlan.nodes = nodes
            floorPlan.generateMembersfromNodes()

    def addCoordinate(self):
        X = 0
        Y = 1
        row = self.XYCoordTable.rowCount()
        self.XYCoordTable.insertRow(self.XYCoordTable.rowCount())
        self.XYCoordTable.setItem(row, X, QTableWidgetItem(str(0)))
        self.XYCoordTable.setItem(row, Y, QTableWidgetItem(str(0)))
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

    def saveFloorPlan(self):
        '''Overwrite the tower linked to the main model'''
        self.towerRef.floorPlans = self.tower.floorPlans

        # Maybe need a wrapper function ---------------------
        # clear all faces and panels if floor plan is updated
        self.towerRef.clearFloor()
        self.towerRef.faces.clear()
        self.towerRef.panels.clear()
        self.towerRef.columns.clear()

        self.towerRef.addFloorPlansToFloors()
        for name in self.towerRef.floorPlans:
            self.towerRef.generateFacesByFloorPlan(self.towerRef.floorPlans[name])
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

