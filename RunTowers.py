from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

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

        # Passing in main.projectSettingsData into bracing scheme
        self.psDataRef = args[0].projectSettingsData

        # Create copy of projectSettingsData to reassign if user saves
        self.psData = copy.deepcopy(self.psDataRef)

        # SAP2000.exe path
        self.selectPath_button.clicked.connect(self.selectSAP2000path)
        
        # Set UI Elements
        self.setOkandCancelButtons()     
        self.setRunNowButton()

        self.update()
      
    def setOkandCancelButtons(self):
        self.OkButton = self.runTowers_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.save)
        self.OkButton.clicked.connect(lambda x: self.close())

        self.CancelButton = self.runTowers_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

    def setRunNowButton(self):
        self.runNow_Button.clicked.connect(self.runNow)
        self.runNow_Button.clicked.connect(lambda x: self.close())

    def Populate(self):
        # Set Text
        self.SAP2000Path_input.setPlainText(self.psData.SAPPath)
        self.nodesToAnalyze_input.setPlainText(','.join(self.psData.nodesList))
        self.footprint_input.setPlainText(str(self.psData.SAPPath.footprint))
        self.totalHeight_input.setPlainText(str(self.psData.totalHeight))
        self.totalMass_input.setPlainText(str(self.psData.totalMass))
        self.gmIdentifier_input.setPlainText(str(self.psData.gmIdentifier))

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

        # Ground Motion Identifier
        self.psData.gmIdentifier = self.gmIdentifier_input.toPlainText()
    
    def save(self):
        self.update()
        self.psDataRef = self.psData

    def runNow(self):
        self.psData.toRun = True
        self.save()

    def selectSAP2000path(self):
        modelLoc ,_  = QFileDialog.getOpenFileName(self, 'Select SAP2000.exe', '', 'SAP2000 application (*.exe)') # returns a tuple: ('file_name', 'file_type')

        # Terminate if cancelled
        if not modelLoc:
            return

        self.SAP2000Path_input.setPlainText(modelLoc)