from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

from Model import * # import Model to access tower objects
from ProjectSettings import *   # open project settings dialog
from BracingDesign import *    # open design variable dialog
from AssignBracingDesign import *    # open panel assignment dialog
from BracingScheme import *    # open panel assignment dialog

from FileWriter import *    # save or overwrite file
from FileReader import *    # open existing file

import sys  # We need sys so that we can pass argv to QApplication
import os

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi(r'UI\autobuilder_mainwindow_v2.ui', self)

        # Project Settings data object
        self.projectSettingsData = ProjectSettingsData()

        # Bracing Design data object
        self.bracingDesignData = BracingDesignData()

        # Bracing Design Assignment data object
        self.assignmentData = AssignmentData()

        # Tower object
        elevs = self.projectSettingsData.floorElevs
        self.tower = Tower(elevs)

        # TESTING ----------------------------------------------
        '''
        self.tower.defineFloors()

        floorPlan = FloorPlan()
        floorPlan.nodes = [Node(-1,0), Node(4,0), Node(13,6), Node(12,9), Node(0,30)]
        floorPlan.generateMemebersfromNodes()

        floorPlan2 = FloorPlan()
        floorPlan2.nodes = [Node(0,0),Node(4,0),Node(4,6),Node(12,6),Node(12,9),Node(0,30)]
        floorPlan2.generateMemebersfromNodes()

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
        '''
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
        self.view_2D_up.clicked.connect(self.translate_z_up_2DView)
        self.view_2D_down.clicked.connect(self.translate_z_down_2DView)
        self.view_2D_panel_orientation.clicked.connect(self.change_panel_orientation)

        # Update the views
        timer  = QTimer(self)
        timer.setInterval(20) # period in miliseconds
        timer.timeout.connect(self.view_3D_opengl.updateGL) # updateGL calls paintGL automatically!!
        timer.timeout.connect(self.set2DViewDimension)
        timer.timeout.connect(self.view_2D_painter.update)
        timer.start()

    def setTowerInViews(self):
        self.view_3D_opengl.setTower(self.tower)
        self.view_2D_painter.setTower(self.tower)

    def setProjectSettingsDataForViews(self):
        self.view_3D_opengl.setProjectSettingsData(self.projectSettingsData)
        self.view_2D_painter.setProjectSettingsData(self.projectSettingsData)
    
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
        self.openFile_button = QAction(QIcon(r"Icons\24x24\folder-horizontal-open.png"),"Open File", self) 
        self.openFile_button.setStatusTip("Open File")
        self.openFile_button.triggered.connect(self.openFile)

        self.files_toolbar.addAction(self.openFile_button)

        # Add button for saving files
        self.saveFile_button = QAction(QIcon(r"Icons\24x24\disk.png"),"Save File", self)
        self.saveFile_button.setStatusTip("Save File")
        self.saveFile_button.triggered.connect(self.saveFile)

        self.files_toolbar.addAction(self.saveFile_button)

        # For general tools-------------------------------------------
        # Add button for Project Settings
        self.setting_button = QAction(QIcon(r"Icons\24x24\gear.png"),"Project Settings", self)
        self.setting_button.setStatusTip("Project Settings")

        self.setting_button.triggered.connect(self.openProjectSettings)

        self.functions_toolbar.addAction(self.setting_button)

        # Add button for Editing Bracing Scheme
        self.brace_button = QAction(QIcon(r"Icons\24x24\Bracing - 24x24.png"),"Edit Bracing Scheme", self)
        self.brace_button.setStatusTip("Edit Brace Scheme")

        self.setting_button.triggered.connect(self.openBracingScheme)

        self.functions_toolbar.addAction(self.brace_button)

        # Add button for Editing Floor Plan
        self.floorPlan_button = QAction(QIcon(r"Icons\24x24\Floor Plan - 24x24.png"),"Edit Floor Plan", self)
        self.floorPlan_button.setStatusTip("Edit Floor Plan")

        self.functions_toolbar.addAction(self.floorPlan_button)

        # Add button for Editing Panel
        self.panel_button = QAction(QIcon(r"Icons\24x24\Panel - 24x24.png"),"Edit Panel", self)
        self.panel_button.setStatusTip("Edit Panel")

        self.functions_toolbar.addAction(self.panel_button)

        # Add button for Editing Design variable
        self.editDesignVariable_button = QAction(QIcon(r"Icons\24x24\pencil.png"),"Edit Bracing Design", self)
        self.editDesignVariable_button.setStatusTip("Edit Bracing Design")

        self.editDesignVariable_button.triggered.connect(self.openBracingDesign)

        self.functions_toolbar.addAction(self.editDesignVariable_button)

        # Add button for Assign Design variable
        self.assignDesignVariable_button = QAction(QIcon(r"Icons\24x24\pencil_plus.png"),"Assign Bracing Design", self)
        self.assignDesignVariable_button.setStatusTip("Assign Bracing Design")

        self.assignDesignVariable_button.triggered.connect(self.openAssignment)
        
        self.functions_toolbar.addAction(self.assignDesignVariable_button)

        # Add button for Generating Tower
        self.generateTower_button = QAction(QIcon(r"Icons\24x24\Generate Tower - 24x24.png"),"Generate Tower", self)
        self.generateTower_button.setStatusTip("Generate Tower")

        self.functions_toolbar.addAction(self.generateTower_button)

        # Add button for Running Tower
        self.runTower_button = QAction(QIcon(r"Icons\24x24\Run Tower - 24x24.png"),"Run Tower", self)
        self.runTower_button.setStatusTip("Run Tower")

        self.functions_toolbar.addAction(self.runTower_button)

        # For views controls------------------------------------------
        # Add button for going up the tower
        self.up_button = QAction(QIcon(r"Icons\24x24\arrow-090.png"),"Up", self)
        self.up_button.setStatusTip("Up")
        self.up_button.triggered.connect(lambda x: self.view_3D_opengl.moveUp())

        self.views_toolbar.addAction(self.up_button)

        # Add button for going down the tower
        self.down_button = QAction(QIcon(r"Icons\24x24\arrow-270.png"),"Down", self)
        self.down_button.setStatusTip("Down")
        self.down_button.triggered.connect(lambda x: self.view_3D_opengl.moveDown())

        self.views_toolbar.addAction(self.down_button)

    def setMenu(self):
        # Project Settings
        self.action_ProjectSettings.triggered.connect(self.openProjectSettings)
        # Bracing Scheme
        self.action_BracingScheme.triggered.connect(self.openBracingScheme)
        # Bracing Design
        self.action_DesignVariable.triggered.connect(self.openBracingDesign)
        # Assign Bracing Design
        self.action_AssignVariable.triggered.connect(self.openAssignment)
        # Save File
        self.action_Save.triggered.connect(self.saveFile)
        # Open File
        self.action_Open.triggered.connect(self.openFile)

    # Save file
    def saveFile(self, signal):
        fileInfo = QFileDialog.getSaveFileName(self, "Save File", "autobuilder.ab", "Autobuilder files (*.ab)")
        fileLoc = fileInfo[0]

        if fileLoc:  # No action if no file was selected
            filewriter = FileWriter(fileLoc, self.tower, self.projectSettingsData)
            filewriter.writeFiles()

    # Open file
    def openFile(self, signal):
        fileInfo = QFileDialog.getOpenFileName(self, "Open File", "autobuilder.ab", "Autobuilder files (*.ab)")
        fileLoc = fileInfo[0]

        if fileLoc: # No action if no file was selected
            self.tower.reset()

            filereader = FileReader(fileLoc, self.tower, self.projectSettingsData, self.bracingDesignData, self.assignmentData)
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
        #bracingScheme.setData(self.bracingSchemeData)
        #bracingScheme.display()

        bracingScheme.exec_()

    # For 2D view -----------------------------------------------------
    def set2DViewDimension(self):
        size = self.view_2D_painter.size()

        self.view_2D_painter.dimension_x = size.width()
        self.view_2D_painter.dimension_y = size.height()

    def translate_z_up_2DView(self, signal):
        self.view_2D_painter.elevationUp()
        self.view_2D_elevation.setText("Z = " + str(self.view_2D_painter.elevation))

    def translate_z_down_2DView(self, signal):
        self.view_2D_painter.elevationDown()
        self.view_2D_elevation.setText("Z = " + str(self.view_2D_painter.elevation))

    def change_panel_orientation(self, signal):
        self.view_2D_painter.changePanelDirection()

    # For Bracing Design --------------------------------------------
    def openBracingDesign(self, signal):
        bracingDesign = BracingDesign(self)  
        bracingDesign.setBracingDesignData(self.bracingDesignData)
        bracingDesign.displayBracingDesignData()

        bracingDesign.exec_()

    def openAssignment(self, signal):
        assignment = AssignBracingDesign.AssignBracingDesign(self)

        assignment.setAssignmentData(self.assignmentData)
        self.assignmentData.panels = list(self.tower.panels.keys())
        self.assignmentData.possibleBracings = self.tower.bracings
        assignment.displayAssignmentData()

        assignment.exec_()