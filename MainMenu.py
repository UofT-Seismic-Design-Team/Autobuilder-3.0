from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *   # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

from Model import * # import Model to access tower objects
from Definition import *    # import constants from Definition

from ProjectSettings import *   # open project settings dialog
from AssignBracingDesign import *    # open panel assignment dialog
from BracingScheme import *    # open bracing definition dialog
from FloorPlan import *  # open floor plan ui
from DesignVariable import * # open bracing group UI
from Panels import *

from View2DEngine import *  # import View2DEngine

from FileWriter import *    # save or overwrite file
from FileReader import *    # open existing file

import math as m

import sys  # We need sys so that we can pass argv to QApplication
import os


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs,)

        # Load the UI Page
        uic.loadUi(r'UI\autobuilder_mainwindow_v3.ui', self)

        # Project Settings data object
        self.projectSettingsData = ProjectSettingsData()

        # Tower object
        elevs = self.projectSettingsData.floorElevs
        self.tower = Tower(elevs)

        # TESTING ----------------------------------------------

        self.tower.defineFloors()

        floorPlan = FloorPlan()
        floorPlan.nodes = [Node(2,0), Node(4,0), Node(12,6), Node(12,9), Node(0,9)]
        floorPlan.generateMembersfromNodes()

        floorPlan2 = FloorPlan()
        floorPlan2.nodes = [Node(3,0),Node(4,0),Node(4,6),Node(12,6),Node(12,9),Node(0,9)]
        floorPlan2.generateMembersfromNodes()

        default = Bracing('default')
        default.nodePairs = [[Node(0,0), Node(0,1)], [Node(0,1), Node(1,1)], [Node(1,1), Node(1,0)], [Node(1,0), Node(0,0)]]
        default.materials = ['BALSA_0.1875X0.1875', 'BALSA_0.1875X0.1875', 'BALSA_0.1875X0.1875', 'BALSA_0.1875X0.1875']
        default.generateMembersfromNodes()
        self.tower.addBracing(default)

        for elev in elevs[5:]:
            floorPlan.addElevation(elev)

        for elev in elevs[:5+1]:
            floorPlan2.addElevation(elev)

        self.tower.addFloorPlan(floorPlan)
        self.tower.addFloorPlan(floorPlan2)

        self.tower.addFloorPlansToFloors()

        self.tower.generateFacesByFloorPlan(floorPlan)
        self.tower.generateFacesByFloorPlan(floorPlan2)

        self.tower.generatePanelsByFace()
        self.tower.addPanelsToFloors()

        self.tower.generateColumnsByFace()

        #------------------------------------------------

        # Set project settings data for all views
        self.setProjectSettingsDataForViews()

        # Set menu bar
        self.setMenu()

        # Add icons to the toolbars
        self.setIconsForToolbar()

        # Add icons to section view
        self.setIconsForSectionView()

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
        self.view_2D_up.setIcon(QIcon(r'Icons\24x24\arrow-090.png'))

        # Set icon for down button
        self.view_2D_down.setIcon(QIcon(r"Icons\24x24\arrow-270.png"))

        # Set icon for panels orientation button
        self.view_2D_panel_orientation.setIcon(QIcon(r"Icons\24x24\flip.png"))

    def setIconsForToolbar(self):
        # For file managment tools----------------------------------
        # Add button for opening files
        self.openFile_button = QAction(QIcon(r"Icons\24x24\folder-horizontal-open.png"), "Open File", self)
        self.openFile_button.setStatusTip("Open File")
        self.openFile_button.triggered.connect(self.openFile)

        self.files_toolbar.addAction(self.openFile_button)

        # Add button for saving files
        self.saveFile_button = QAction(QIcon(r"Icons\24x24\disk.png"), "Save File", self)
        self.saveFile_button.setStatusTip("Save File")
        self.saveFile_button.triggered.connect(self.saveFile)

        self.files_toolbar.addAction(self.saveFile_button)

        # For general tools-------------------------------------------
        # Add button for Project Settings
        self.setting_button = QAction(QIcon(r"Icons\24x24\gear.png"), "Project Settings", self)
        self.setting_button.setStatusTip("Project Settings")

        self.setting_button.triggered.connect(self.openProjectSettings)

        self.functions_toolbar.addAction(self.setting_button)

        # Add button for Editing Bracing Scheme
        self.brace_button = QAction(QIcon(r"Icons\24x24\Bracing - 24x24.png"), "Edit Brace Scheme", self)
        self.brace_button.setStatusTip("Edit Brace Scheme")

        self.brace_button.triggered.connect(self.openBracingScheme)

        self.functions_toolbar.addAction(self.brace_button)

        # Add button for Editing Floor Plan
        self.floorPlan_button = QAction(QIcon(r"Icons\24x24\Floor Plan - 24x24.png"), "Edit Floor Plan", self)
        self.floorPlan_button.setStatusTip("Edit Floor Plan")

        self.floorPlan_button.triggered.connect(self.openFloorDesign)

        self.functions_toolbar.addAction(self.floorPlan_button)

        # Add button for Editing Panel
        self.panel_button = QAction(QIcon(r"Icons\24x24\Panel - 24x24.png"), "Edit Panel", self)
        self.panel_button.setStatusTip("Edit Panel")
        self.panel_button.triggered.connect(self.openPanel)

        self.functions_toolbar.addAction(self.panel_button)

        # Add button for Editing Bracing Groups
        self.editDesignVariable_button = QAction(QIcon(r"Icons\24x24\pencil.png"),"Edit Bracing Group", self)
        self.editDesignVariable_button.setStatusTip("Edit Bracing Group")

        self.editDesignVariable_button.triggered.connect(self.DesignVariable)

        self.functions_toolbar.addAction(self.editDesignVariable_button)

        # Add button for Assign Design variable
        self.assignDesignVariable_button = QAction(QIcon(r"Icons\24x24\pencil_plus.png"),"Assign Bracing Design", self)
        self.assignDesignVariable_button.setStatusTip("Assign Bracing Design")

        self.assignDesignVariable_button.triggered.connect(self.openAssignment)
        
        self.functions_toolbar.addAction(self.assignDesignVariable_button)

        # Add button for Generating Tower
        self.generateTower_button = QAction(QIcon(r"Icons\24x24\Generate Tower - 24x24.png"), "Generate Tower", self)
        self.generateTower_button.setStatusTip("Generate Tower")

        self.functions_toolbar.addAction(self.generateTower_button)

        # Add button for Running Tower
        self.runTower_button = QAction(QIcon(r"Icons\24x24\Run Tower - 24x24.png"), "Run Tower", self)
        self.runTower_button.setStatusTip("Run Tower")

        self.functions_toolbar.addAction(self.runTower_button)

        # For views controls------------------------------------------
        # Add button for going up the tower
        self.up_button = QAction(QIcon(r"Icons\24x24\arrow-090.png"), "Up", self)
        self.up_button.setStatusTip("Up")
        self.up_button.triggered.connect(lambda x: self.view_3D_opengl.moveUp())

        self.views_toolbar.addAction(self.up_button)

        # Add button for going down the tower
        self.down_button = QAction(QIcon(r"Icons\24x24\arrow-270.png"), "Down", self)
        self.down_button.setStatusTip("Down")
        self.down_button.triggered.connect(lambda x: self.view_3D_opengl.moveDown())

        self.views_toolbar.addAction(self.down_button)

    def setMenu(self):
        # Project Settings
        self.action_ProjectSettings.triggered.connect(self.openProjectSettings)
        # Bracing Scheme
        self.action_BracingScheme.triggered.connect(self.openBracingScheme)
        # Bracing Design
        self.action_DesignVariable.triggered.connect(self.DesignVariable)
        # Assign Bracing Design
        self.action_AssignVariable.triggered.connect(self.openAssignment)
        # Save File
        self.action_Save.triggered.connect(self.saveFile)
        # Open File
        self.action_Open.triggered.connect(self.openFile)
        self.action_FloorPlan.triggered.connect(self.openFloorDesign)

    # Save file ------------------------------------------------------------------------------
    def saveFile(self, signal):
        fileInfo = QFileDialog.getSaveFileName(self, "Save File", "autobuilder.ab", "Autobuilder files (*.ab)")
        fileLoc = fileInfo[0]

        if fileLoc:  # No action if no file was selected
            filewriter = FileWriter(fileLoc, self.tower, self.projectSettingsData)
            filewriter.writeFiles()

    # Open file ------------------------------------------------------------------------------
    def openFile(self, signal):
        fileInfo = QFileDialog.getOpenFileName(self, "Open File", "autobuilder.ab", "Autobuilder files (*.ab)")
        fileLoc = fileInfo[0]

        if fileLoc: # No action if no file was selected
            self.tower.reset() # clean all data in tower

            filereader = FileReader(fileLoc, self.tower, self.projectSettingsData)
            filereader.readMainFile()

            print(self.tower)
            self.tower.build()

    # For Project Settings --------------------------------------------
    def openProjectSettings(self, signal):
        projectSettings = ProjectSettings.ProjectSettings(self)

        projectSettings.setData(self.projectSettingsData)
        projectSettings.setTower(self.tower)
        projectSettings.display()

        projectSettings.exec_()

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
            vText.addMember(Member(lowerLeft, lowerRight))
            vText.addText(panel.name)
            vText.setLocation(Node(0.5, 0.5*self.panel_direction)) # midpoint

        vTexts.append(vText)

        # Step 3: Create view object for floor plans
        color_fplan = Color.FloorPlan['MainMenu']
        color_node = Color.Node['MainMenu']

        limit = len(color_fplan) - 1
        i = 0
        for fpName in floorPlans:
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
            
            # Floor plan members and nodes -------------------------------
            floorPlan = floorPlans[fpName]

            for member in floorPlan.members:
                vMember.addMember(member)
                
                vNode.addNode(member.start_node)
                vNode.addNode(member.end_node) # redundant but just in case

            vMembers.append(vMember)
            vNodes.append(vNode)

            i += 1

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

    def translate_z_up_2DView(self, signal):
        # prevent list to go out of range
        self.elevation_index = min(len(self.tower.elevations)-1, self.elevation_index+1)
        self.elevation = self.tower.elevations[self.elevation_index]

        self.view_2D_elevation.setText("Z = " + str(self.elevation))

    def translate_z_down_2DView(self, signal):
         # prevent list to go out of range
        self.elevation_index = max(0, self.elevation_index-1)
        self.elevation = self.tower.elevations[self.elevation_index]

        self.view_2D_elevation.setText("Z = " + str(self.elevation))

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

    # For Bracing Group --------------------------------------------
    def DesignVariable(self, signal):
        designVariable = DesignVariable(self)
        designVariable.exec_()

    def openAssignment(self, signal):
        assignment = BracingAssignment(self)
        assignment.displayAssignmentData()

        assignment.exec_()
