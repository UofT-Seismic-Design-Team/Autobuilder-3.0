from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

from Message import *
from FileReader import *
from ProjectSettings import *

import sys  # We need sys so that we can pass argv to QApplication
import os
import copy

import resources    # For icons and UIs

'''
from Model import *    # import Model to access tower objects
from View2DEngine import *
from Definition import *    # import constants from Definition
from Message import *
'''

class RunTowers(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        fileh = QFile(':/UI/autobuilder_runtowers_v2.ui', self)
        fileh.open(QFile.ReadOnly)
        uic.loadUi(fileh, self)
        fileh.close()

        # Passing in mainmenu into run towers
        self.mainmenuRef = args[0]

        # Passing in tower into run towers
        self.towerRef = args[0].tower

        # Create copy of projectSettingsData to reassign if user saves
        self.psData = copy.deepcopy(args[0].projectSettingsData)

        # SAP2000.exe path
        self.selectPath_button.clicked.connect(self.selectSAP2000path)
        
        # Set UI Elements
        self.setOkandCancelButtons()     
        self.setRunNowButton()
        self.setImportInputTableButton()

        self.Populate()
      
    def setOkandCancelButtons(self):
        self.OkButton = self.runTowers_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.save)
        self.OkButton.clicked.connect(self.close)

        self.CancelButton = self.runTowers_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(self.close)

    def setRunNowButton(self):
        self.runNow_Button.clicked.connect(self.runNow)
        self.runNow_Button.clicked.connect(self.save)
        self.runNow_Button.clicked.connect(self.close)

    def setImportInputTableButton(self):
        self.importInputTable_Button.clicked.connect(self.importInputTable)

    def Populate(self):
        # Building Cost and Seismic Cost Calculation ----------------------------------------------------
        self.nodesToAnalyze_input.setPlainText(','.join(self.psData.nodesList))
        self.footprint_input.setPlainText(str(self.psData.footprint))
        self.totalHeight_input.setPlainText(str(self.psData.totalHeight))
        self.totalMass_input.setPlainText(str(self.psData.totalMass))
        self.forceReductionFactor_input.setPlainText(str(self.psData.forceReductionFactor))

        # Load Combination Keywords ----------------------------------------------------------------
        self.seismicPerformanceId_input.setPlainText(str(self.psData.gmIdentifier)) # naming inconsistency
        self.memberUtilizationId_input.setPlainText(str(self.psData.memberUtilizationId))

        # Analysis Setup ----------------------------------------------------------------
        self.SAP2000Path_input.setPlainText(self.psData.SAPPath)

        # Centre of Rigidity ----------------------------------------------------------------
        # Reset
        self.doNotRun_radioButton.setChecked(False)
        self.singleFloor_radioButton.setChecked(False)
        self.allFloor_radioButton.setChecked(False)

        if self.psData.centreOfRigidity == CRTYPE.DO_NOT_RUN:
            self.doNotRun_radioButton.setChecked(True)
        elif self.psData.centreOfRigidity == CRTYPE.SINGLE_FLOOR:
            self.singleFloor_radioButton.setChecked(True)
        elif self.psData.centreOfRigidity == CRTYPE.ALL_FLOOR:
            self.allFloor_radioButton.setChecked(True)
        else:
            self.doNotRun_radioButton.setChecked(True)

        # Others ----------------------------------------------------------------
        self.keepExistingMembers_checkBox.setChecked(self.psData.keepExistingMembers)
        self.divideAllMembersAtIntersections_checkBox.setChecked(self.psData.divideAllMembersAtIntersections)

    def update(self):
        # SAP2000 Path
        self.psData.SAPPath = self.SAP2000Path_input.toPlainText()
        
        # Nodes to Analyze (assuming input is string of integers seperated by commas)
        nodesToAnalyze = self.nodesToAnalyze_input.toPlainText()
        self.psData.nodesList = nodesToAnalyze.split(',')
            
        # Footprint
        self.psData.footprint = float(self.footprint_input.toPlainText())
        
        # Total Height
        self.psData.totalHeight = float(self.totalHeight_input.toPlainText())
        
        # Total Mass
        self.psData.totalMass = float(self.totalMass_input.toPlainText())

        # Force Reduction Factor
        self.psData.forceReductionFactor = float(self.forceReductionFactor_input.toPlainText())

        # Load Combination Keywords
        self.psData.gmIdentifier = self.seismicPerformanceId_input.toPlainText()
        self.psData.memberUtilizationId = self.memberUtilizationId_input.toPlainText()

        # Centre of Rigidity ------------------------------
        if self.doNotRun_radioButton.isChecked():
            self.psData.centreOfRigidity = CRTYPE.DO_NOT_RUN
        elif self.singleFloor_radioButton.isChecked():
            self.psData.centreOfRigidity = CRTYPE.SINGLE_FLOOR
        elif self.allFloor_radioButton.isChecked():
            self.psData.centreOfRigidity = CRTYPE.ALL_FLOOR
        else:
            self.psData.centreOfRigidity = CRTYPE.DO_NOT_RUN

        # Keep Existing Members
        self.psData.keepExistingMembers = self.keepExistingMembers_checkBox.isChecked()
        self.psData.divideAllMembersAtIntersections = self.divideAllMembersAtIntersections_checkBox.isChecked()
    
    def save(self):
        self.update()
        self.mainmenuRef.projectSettingsData = self.psData

    def runNow(self):
        self.psData.toRun = True
        self.save()

    def importInputTable(self):
        tableLoc, _ = QFileDialog.getOpenFileName(self, 'Open Input Table', '', '.csv files (*.csv)') # returns a tuple: ('file_name', 'file_type')

        # Terminate if cancelled
        if not tableLoc:
            return

        filereader = FileReader(tower=self.towerRef)
        filereader.readInputTable(tableLoc)

        # try:
        #     filereader = FileReader(tower=self.towerRef)
        #     filereader.readInputTable(tableLoc)

        # except:
        #     warning = WarningMessage()
        #     warning.popUpErrorBox('Fail to open file. Please check if the selected file is corrupted.')

    def selectSAP2000path(self):
        modelLoc ,_  = QFileDialog.getOpenFileName(self, 'Select SAP2000.exe', '', 'SAP2000 application (*.exe)') # returns a tuple: ('file_name', 'file_type')

        # Terminate if cancelled
        if not modelLoc:
            return

        self.SAP2000Path_input.setPlainText(modelLoc)