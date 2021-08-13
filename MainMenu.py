from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *   # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

from Model import * # import Model to access tower objects
from Definition import *    # import constants from Definition
from Message import *    # pop up window for illegal entries

from ProjectSettings import *   # open project settings dialog
from DisplaySettings import *   # open display settings dialog
from VariableAssignment import *    # open panel assignment dialog
from BracingScheme import *    # open bracing definition dialog
from FloorPlan import *  # open floor plan ui
from DesignVariable import * # open bracing and section group UI
from TowerVariation import *    # generate tower variations
from SAPModelCreation import * # create and run towers in SAP2000
from Panels import *
from RunTowers import * # open run towers dialog

from View2DEngine import *  # import View2DEngine
from View3DEngine import * # import View3DEngine

from FileWriter import *    # save or overwrite file
from FileReader import *    # open existing file

import resources    # For icons and UIs

import math as m

import sys  # We need sys so that we can pass argv to QApplication
import os

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs,)

        # Load the UI
        fileh = QFile(':/UI/autobuilder_mainwindow_v3.ui')
        fileh.open(QFile.ReadOnly)
        uic.loadUi(fileh, self)
        fileh.close()

        # Project Settings data object
        self.projectSettingsData = ProjectSettingsData()

        # Tower object
        elevs = self.projectSettingsData.floorElevs
        self.tower = Tower(elevs)
        self.tower.setSections(self.projectSettingsData.sections)
        
        # Run Towers variables
        self.SAPPath = 'C:\Program Files\Computers and Structures\SAP2000 22\SAP2000.exe'
        self.nodesList = []
        self.footprint = 144
        self.totalHeight = 60
        self.totalMass = 7.83
        self.runNow = False        

        # File location
        self.fileLoc = ''

        # TESTING ----------------------------------------------

        # self.tower.defineFloors()

        # floorPlan = FloorPlan()
        # floorPlan.nodes = [Node(2,0), Node(4,0), Node(12,6), Node(12,9), Node(0,9)]
        # floorPlan.generateMembersfromNodes()

        # floorPlan2 = FloorPlan()
        # floorPlan2.nodes = [Node(3,0),Node(4,0),Node(4,6),Node(12,6),Node(12,9),Node(0,9)]
        # floorPlan2.generateMembersfromNodes()

        # default = Bracing('default')
        # default.nodePairs = [[Node(0,0), Node(0,1)], [Node(0,1), Node(1,1)], [Node(1,1), Node(1,0)], [Node(1,0), Node(0,0)]]
        # default.materials = ['BALSA_0.1875X0.1875', 'BALSA_0.1875X0.1875', 'BALSA_0.1875X0.1875', 'BALSA_0.1875X0.1875']
        # default.generateMembersfromNodes()
        # self.tower.addBracing(default)

        # for elev in elevs[5:]:
        #     floorPlan.addElevation(elev)

        # for elev in elevs[:5+1]:
        #     floorPlan2.addElevation(elev)

        # self.tower.addFloorPlan(floorPlan)
        # self.tower.addFloorPlan(floorPlan2)

        # self.tower.addFloorPlansToFloors()

        # self.tower.generateFacesByFloorPlan(floorPlan)
        # self.tower.generateFacesByFloorPlan(floorPlan2)

        # self.tower.generatePanelsByFace()
        # self.tower.addPanelsToFloors()

        # self.tower.generateColumnsByFace()

        # Default for 2021 competition tower

        self.tower.defineFloors()

        floorPlan11 = FloorPlan()
        floorPlan11.nodes = [Node(0,0), Node(12,0), Node(12,12), Node(0,12)]
        floorPlan11.generateMembersfromNodes()

        floorPlan12 = FloorPlan()
        floorPlan12.nodes = [Node(2/3,0), Node(12,0), Node(12,12), Node(2/3,12)]
        floorPlan12.generateMembersfromNodes()

        floorPlan13 = FloorPlan()
        floorPlan13.nodes = [Node(1+1/3,0), Node(12,0), Node(12,12), Node(1+1/3,12)]
        floorPlan13.generateMembersfromNodes()

        floorPlan14 = FloorPlan()
        floorPlan14.nodes = [Node(2,0), Node(12,0), Node(12,12), Node(2,12)]
        floorPlan14.generateMembersfromNodes()

        floorPlan15 = FloorPlan()
        floorPlan15.nodes = [Node(2+2/3,0), Node(12,0), Node(12,12), Node(2+2/3,12)]
        floorPlan15.generateMembersfromNodes()

        floorPlan16 = FloorPlan()
        floorPlan16.nodes = [Node(3+1/3,0), Node(12,0), Node(12,12), Node(3+1/3,12)]
        floorPlan16.generateMembersfromNodes()        

        floorPlan17 = FloorPlan()
        floorPlan17.nodes = [Node(4,0), Node(12,0), Node(12,12), Node(4,12)]
        floorPlan17.generateMembersfromNodes()

        floorPlan18 = FloorPlan()
        floorPlan18.nodes = [Node(4+2/3,0), Node(12,0), Node(12,12), Node(4+2/3,12)]
        floorPlan18.generateMembersfromNodes()

        floorPlan19 = FloorPlan()
        floorPlan19.nodes = [Node(5+1/3,0), Node(12,0), Node(12,12), Node(5+1/3,12)]
        floorPlan19.generateMembersfromNodes()

        floorPlan20 = FloorPlan()
        floorPlan20.nodes = [Node(6,0), Node(12,0),Node(12,12), Node(6,12)]
        floorPlan20.generateMembersfromNodes()   

        allFloorPlans = [floorPlan11, floorPlan12, floorPlan13, floorPlan14, floorPlan15, floorPlan16, floorPlan17, floorPlan18, floorPlan19, floorPlan20] 

        for fp in allFloorPlans:
            numNodes = len(fp.nodes)
            for i in range(numNodes):
                fp.addTopConnection(str(i+1), i)
                fp.addBottomConnection(str(i+1), i)

        default = Bracing('default')
        default.nodePairs = [[Node(0,0), Node(0,1)], [Node(0,1), Node(1,1)], [Node(1,1), Node(1,0)], [Node(1,0), Node(0,0)]]
        default.materials = ['BALSA_0.1875X0.1875', 'BALSA_0.1875X0.1875', 'BALSA_0.1875X0.1875', 'BALSA_0.1875X0.1875']
        default.generateMembersfromNodes()
        self.tower.addBracing(default)

        for elev in elevs[:13]:
            self.tower.floors[elev].addFloorPlan(floorPlan11)

        for i, elev in enumerate(elevs[12:]):
            self.tower.floors[elev].addFloorPlan(allFloorPlans[i+1])
        
        for plan in allFloorPlans:
            self.tower.addFloorPlan(plan)

        self.tower.generateFaces()
        self.tower.generateColumnsByFace()

        # for plan in allFloorPlans:
        #     self.tower.generateFacesByFloorPlan(plan)

        # self.tower.generateFacesByFloorPlans(allFloorPlans)       
        # self.tower.generatePanelsByFace()
        # self.tower.addPanelsToFloors()
        # self.tower.generateColumnsByFace()

        #------------------------------------------------
        # Set project settings data for all views
        self.setProjectSettingsDataForViews()

        # Set menu bar
        self.setMenu()

        # Add icons to the toolbars
        self.setIconsForToolbar()

        # Add icons to section view
        self.setIconsForSectionView()

        # Icon for MainWindow
        self.setWindowIcon(QIcon(':/Icons/letter_A_blue-512.png'))

        # Views ----------------------------
        self.setTowerInViews()

        # View 2D --------------------------
        self.elevation_index = 0
        self.elevation = 0
        self.panel_direction = 1

        self.view_2D_up.clicked.connect(self.translate_z_up_2DView)
        self.view_2D_down.clicked.connect(self.translate_z_down_2DView)
        self.view_2D_panel_orientation.clicked.connect(self.change_panel_orientation)

        # Update views -----------------------------
        timer  = QTimer(self)
        timer.setInterval(20) # period in miliseconds
        timer.timeout.connect(self.view_3D_opengl.updateGL) # updateGL calls paintGL automatically!!
        timer.timeout.connect(self.set2DViewDimension)
        timer.timeout.connect(self.updateSectionView)
        timer.timeout.connect(self.view_2D_painter.update)
        timer.start()

    def setTowerInViews(self):
        self.view_3D_opengl.setTower(self.tower)

    def setProjectSettingsDataForViews(self):
        self.view_3D_opengl.setProjectSettingsData(self.projectSettingsData)
    
    def setIconsForSectionView(self):
        # Set icon for up button
        self.view_2D_up.setIcon(QIcon(':/Icons/arrow-090.png'))

        # Set icon for down button
        self.view_2D_down.setIcon(QIcon(':/Icons/arrow-270.png'))

        # Set icon for panels orientation button
        self.view_2D_panel_orientation.setIcon(QIcon(':/Icons/flip.png'))

    def setIconsForToolbar(self):
        # For file managment tools----------------------------------
        # Add button for opening files
        self.openFile_button = QAction(QIcon(':/Icons/folder-horizontal-open.png'), "Open File", self)
        self.openFile_button.setStatusTip("Open File")
        self.openFile_button.triggered.connect(self.openFile)

        self.files_toolbar.addAction(self.openFile_button)

        # Add button for saving files
        self.saveFile_button = QAction(QIcon(':/Icons/disk.png'), "Save File", self)
        self.saveFile_button.setStatusTip("Save File")
        self.saveFile_button.triggered.connect(self.saveFile)

        self.files_toolbar.addAction(self.saveFile_button)

        # For general tools-------------------------------------------
        # Add button for Project Settings
        self.setting_button = QAction(QIcon(':/Icons/gear.png'), "Project Settings", self)
        self.setting_button.setStatusTip("Project Settings")

        self.setting_button.triggered.connect(self.openProjectSettings)

        self.functions_toolbar.addAction(self.setting_button)

        # Add button for Display Settings
        self.displaySetting_button = QAction(QIcon(':/Icons/application-sidebar.png'), "Display Settings", self)
        self.displaySetting_button.setStatusTip("Display Settings")

        self.displaySetting_button.triggered.connect(self.openDisplaySettings)

        self.functions_toolbar.addAction(self.displaySetting_button)

        # Add button for Editing Bracing Scheme
        self.brace_button = QAction(QIcon(':/Icons/Bracing - 24x24.png'), "Edit Brace Scheme", self)
        self.brace_button.setStatusTip("Edit Brace Scheme")

        self.brace_button.triggered.connect(self.openBracingScheme)

        self.functions_toolbar.addAction(self.brace_button)

        # Add button for Editing Floor Plan
        self.floorPlan_button = QAction(QIcon(':/Icons/Floor Plan - 24x24.png'), "Edit Floor Plan", self)
        self.floorPlan_button.setStatusTip("Edit Floor Plan")

        self.floorPlan_button.triggered.connect(self.openFloorDesign)

        self.functions_toolbar.addAction(self.floorPlan_button)

        # Add button for Editing Panel
        self.panel_button = QAction(QIcon(':/Icons/Panel - 24x24.png'), "Edit Panel", self)
        self.panel_button.setStatusTip("Edit Panel")
        self.panel_button.triggered.connect(self.openPanel)

        self.functions_toolbar.addAction(self.panel_button)

        # Add button for Editing Bracing Groups
        self.editDesignVariable_button = QAction(QIcon(':/Icons/pencil.png'),"Edit Design Variables", self)
        self.editDesignVariable_button.setStatusTip("Edit Design Variables")

        self.editDesignVariable_button.triggered.connect(self.DesignVariable)

        self.functions_toolbar.addAction(self.editDesignVariable_button)

        # Add button for Assign Design variable
        self.assignDesignVariable_button = QAction(QIcon(':/Icons/pencil_plus.png'),"Assign Bracing Design", self)
        self.assignDesignVariable_button.setStatusTip("Assign Bracing Design")

        self.assignDesignVariable_button.triggered.connect(self.openAssignment)
        
        self.functions_toolbar.addAction(self.assignDesignVariable_button)

        # Add button for Constraint
        self.constraint_button = QAction(QIcon(':/Icons/filter - 24x24.png'), "Modify Constraint", self)
        self.constraint_button.setStatusTip("Modify Constraint")

        self.constraint_button.triggered.connect(lambda x: x)    # add function

        self.functions_toolbar.addAction(self.constraint_button)

        # Add button for Generating Tower
        self.generateTower_button = QAction(QIcon(':/Icons/Generate Tower - 24x24.png'), "Generate Tower", self)
        self.generateTower_button.setStatusTip("Generate Tower")

        self.generateTower_button.triggered.connect(self.generateInputTable)

        self.functions_toolbar.addAction(self.generateTower_button)

        # Add button for Running Tower
        self.runTower_button = QAction(QIcon(':/Icons/Run Tower - 24x24.png'), "Run Tower", self)
        self.runTower_button.setStatusTip("Run Tower")

        self.runTower_button.triggered.connect(self.openRunTowers)

        self.functions_toolbar.addAction(self.runTower_button)

        # For views controls------------------------------------------
        # Add button for going up the tower
        self.up_button = QAction(QIcon(':/Icons/arrow-090.png'), "Up", self)
        self.up_button.setStatusTip("Up")
        self.up_button.triggered.connect(lambda x: self.view_3D_opengl.moveUp())

        self.views_toolbar.addAction(self.up_button)

        # Add button for going down the tower
        self.down_button = QAction(QIcon(':/Icons/arrow-270.png'), "Down", self)
        self.down_button.setStatusTip("Down")
        self.down_button.triggered.connect(lambda x: self.view_3D_opengl.moveDown())

        self.views_toolbar.addAction(self.down_button)

    def setMenu(self):
        # Project Settings
        self.action_ProjectSettings.triggered.connect(self.openProjectSettings)
        # Floor plans
        self.action_FloorPlan.triggered.connect(self.openFloorDesign)
        # Generate Panels from Floor Plans
        self.action_GPFromFloorPlan.triggered.connect(self.generatePanelsFromFloorPlan)
        # Panels
        self.action_Panel.triggered.connect(self.openPanel)
        # Bracing Scheme
        self.action_BracingScheme.triggered.connect(self.openBracingScheme)
        # Bracing Design
        self.action_DesignVariable.triggered.connect(self.DesignVariable)
        # Assign Bracing Design
        self.action_AssignVariable.triggered.connect(self.openAssignment)
        # Modify Constraint
        self.action_Constraint.triggered.connect(lambda x: x)
        # Generate Tower
        self.action_GenerateTowers.triggered.connect(self.generateInputTable)
        # Run Tower
        self.action_RunTowers.triggered.connect(self.openRunTowers)
        # Save File
        self.action_Save.triggered.connect(self.saveFile)
        # Open File
        self.action_Open.triggered.connect(self.openFile)

    # Save file ------------------------------------------------------------------------------
    def saveFile(self, signal=None):
        fileInfo = QFileDialog.getSaveFileName(self, "Save File", "autobuilder.ab", "Autobuilder files (*.ab)")
        self.fileLoc = fileInfo[0]

        if self.fileLoc:  # No action if no file was selected
            filewriter = FileWriter(self.fileLoc, self.tower, self.projectSettingsData)
            filewriter.writeFiles()

    # Open file ------------------------------------------------------------------------------
    def openFile(self, signal=None):
        fileInfo = QFileDialog.getOpenFileName(self, "Open File", "autobuilder.ab", "Autobuilder files (*.ab)")
        self.fileLoc = fileInfo[0]

        if self.fileLoc: # No action if no file was selected
            self.tower.reset() # clean all data in tower

            filereader = FileReader(self.fileLoc, self.tower, self.projectSettingsData)
            filereader.readMainFile()

            self.tower.build()

    # For Project Settings --------------------------------------------
    def openProjectSettings(self, signal):
        projectSettings = ProjectSettings.ProjectSettings(self)
        projectSettings.display()

        projectSettings.exec_()

    # For Display Settings --------------------------------------------
    def openDisplaySettings(self, signal):
        displaySettings = DisplaySettingsUI(self)
        
        displaySettings.exec_()

    # For Bracing Scheme --------------------------------------------
    def openBracingScheme(self, signal):
        bracingScheme = BracingScheme(self)

        bracingScheme.exec_()

    # For 2D view -----------------------------------------------------
    def set2DViewDimension(self):
        size = self.view_2D_painter.size()

        self.view_2D_painter.dimension_x = size.width()
        self.view_2D_painter.dimension_y = size.height()

    def View2DObjects(self):
        ''' --> list(ViewMember), list(ViewNode), list(ViewText) '''

        renderX = self.projectSettingsData.renderX
        renderY = self.projectSettingsData.renderY

        # Step 1: Get floor plan and panels at the current elevation level
        floor = self.tower.floors[self.elevation]

        floorPlans = floor.floorPlans
        panels = floor.panels

        vMembers = []
        vNodes = []
        vTexts = []

        # Step 2: Create view objects for panels
        color_panel = Color.Panel['MainMenu']
        color_text = Color.Text['MainMenu']

        vText = ViewText()
        for panel in panels:
            vMember = ViewMember()

            # Set View Objects attributes --------------------------------
            vMember.setColor(color_panel)
            vMember.setSize(View2DConstants.MEMBER_SIZE)
            vMember.setDimX(renderX)
            vMember.setDimY(renderY)

            vText.setColor(color_text)
            vText.setSize(View2DConstants.TEXT_SIZE)
            vText.setDimX(renderX)
            vText.setDimY(renderY)

            # Find panel corners coordinates
            lowerLeft = panel.lowerLeft
            lowerRight = panel.lowerRight
            
            base = Member(lowerLeft, lowerRight)
            angle = base.angle()

            rot = self.panel_direction * m.pi/2

            dx = m.cos(angle - rot)
            dy = m.sin(angle - rot)

            upperLeft = Node(lowerLeft.x + dx, lowerLeft.y + dy)
            upperRight =  Node(lowerRight.x + dx, lowerRight.y + dy)

            # Panel members ------------------------------------
            vMember.addMember(Member(lowerLeft, upperLeft))
            vMember.addMember(Member(upperLeft, upperRight))
            vMember.addMember(Member(upperRight, lowerRight))

            vMembers.append(vMember)

            # Panel labels --------------------------------------
            label = ''

            dsettings = self.tower.displaySettings

            checkList = [
                dsettings.pName,
                dsettings.pLength,
            ]

            value = [
                'P-' + panel.name,
                'L=' + str(panel.averageSideLength()),
            ]

            for i, check in enumerate(checkList):
                if check:
                    label = label + value[i] + ' '

            vText.addMember(Member(lowerLeft, lowerRight))
            vText.addText(label)
            vText.setLocation(Node(0.5, 0.5*self.panel_direction)) # midpoint

        vTexts.append(vText)

        # Step 3: Create view object for floor plans
        color_fplan = Color.FloorPlan['MainMenu']
        color_node = Color.Node['MainMenu']

        limit = len(color_fplan) - 1

        for i, floorPlan in enumerate(floorPlans):
            vMember = ViewMember()
            vNode = ViewNode()

            # Set View Objects attributes --------------------------------
            vMember.setColor(color_fplan[min(i, limit)])
            vMember.setSize(View2DConstants.MEMBER_SIZE)
            vMember.setDimX(renderX)
            vMember.setDimY(renderY)

            vNode.setColor(color_node)
            vNode.setSize(View2DConstants.NODE_SIZE)
            vNode.setDimX(renderX)
            vNode.setDimY(renderY)
            
            # Floor plan members and nodes ------------------------------
            for member in floorPlan.members:
                vMember.addMember(member)
                
                vNode.addNode(member.start_node)
                vNode.addNode(member.end_node) # redundant but just in case

            vMembers.append(vMember)
            vNodes.append(vNode)

        return vMembers, vNodes, vTexts

    def updateSectionView(self):
        if not self.tower.floors: # update only when floors are provided
            return
        
        vMembers, vNodes, vTexts = self.View2DObjects()

        self.view_2D_painter.reset()    # clear all the existing objects

        for vMember in vMembers:
            self.view_2D_painter.addMember(vMember)

        for vNode in vNodes:
            self.view_2D_painter.addNode(vNode)

        for vText in vTexts:
            self.view_2D_painter.addText(vText)

        self.view_2D_elevation.setText("Z = " + str(self.elevation))

    def translate_z_up_2DView(self, signal):
        # prevent list to go out of range
        self.elevation_index = min(len(self.tower.elevations)-1, self.elevation_index+1)
        self.elevation = self.tower.elevations[self.elevation_index]

    def translate_z_down_2DView(self, signal):
         # prevent list to go out of range
        self.elevation_index = max(0, self.elevation_index-1)
        self.elevation = self.tower.elevations[self.elevation_index]

    def change_panel_orientation(self, signal):
        self.panel_direction *= -1

    # For FloorDesign--------------------------------------------
    def openFloorDesign(self, signal):
        floorPlan = FloorPlanUI(self)
        floorPlan.exec_()

    # For Panel--------------------------------------------
    def openPanel(self, signal):
        panel= panelsUI(self)
        panel.exec_()

    def generatePanelsFromFloorPlan(self, signal):  
        if self.tower.panels:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Warning")
            msg.setInformativeText('Do you want to generate panels in addition to the existing ones?')
            msg.setWindowTitle("Warning")

            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            OkButton = msg.button(QMessageBox.Ok)
            OkButton.clicked.connect(lambda s: self.tower.generatePanels_addToFloors())
            OkButton.clicked.connect(lambda s: msg.close())

            CancelButton = msg.button(QMessageBox.Cancel)
            CancelButton.clicked.connect(lambda s: msg.close())

            msg.exec_()

        else:
            self.tower.generatePanels_addToFloors()

    # For Bracing Group --------------------------------------------
    def DesignVariable(self, signal):
        designVariable = DesignVariable(self)
        designVariable.exec_()

    def openAssignment(self, signal):
        assignment = VariableAssignment(self)
        warning = WarningMessage()
        try:
            # make sure bracing groups and section groups have been defined
            skey = list(self.tower.bracingGroups.keys())[0]
            bkey = list(self.tower.sectionGroups.keys())[0]
            assignment.exec_()
        except:
                warning.popUpErrorBox('Please define bracing and section groups first!')
                return # terminate the saving process

    # For Tower Variations --------------------------------------------
    def generateInputTable(self, signal):
        if self.fileLoc == '':
            msg = WarningMessage()
            msg.popUpErrorBox('Please save before generating input table')
            return
        generateTower = GenerateTower(self)
        generateTower.exec_()

    # Run towers --------------------------------------------
    def createSAPModels(self, signal):

        if not self.tower.inputTable:
            msg = WarningMessage()
            msg.popUpErrorBox('Please generate input table before running SAP2000')
            return

        runTower = RunTower(self)
        runTower.exec_()
        
    def openRunTowers(self, signal):
        pass
        """
        runTowers = RunTowers(self)
        runTowers.exec_()
        """
        '''
        if self.runNow == True:
            self.createSAPModels()
        '''
        
