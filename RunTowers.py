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

        self.args = args

        # Set UI Elements
        self.setOkandCancelButtons()     
        
        
        # Run Towers
        self.runNow_Button.clicked.connect(self.runNow) 
        
      
    def setOkandCancelButtons(self):
        self.OkButton = self.runTowers_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveInputs)
        self.OkButton.clicked.connect(lambda x: self.close())

        self.CancelButton = self.runTowers_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())
    
    
    def saveInputs(self):
        # SAP2000 Path
        self.args[0].SAPPAth = self.SAP2000Path_input.text()
        
        # Nodes to Analyze (assuming input is string of integers seperated by commas)
        nodesToAnalyze = []
        nodesToAnalyzeText = self.nodesToAnalyze_input.text()
        nodesToAnalyzeMark = 0
        for i in range(len(nodesToAnalyzeText)):
            if nodesToAnalyzeText[i] == ",":
                nodesToAnalyze.append(int(nodesToAnalyzeText[nodesToAnalyzeMark:i]))
                nodesToAnalyzeMark = i + 2
            elif i == (len(nodesToAnalyzeText) - 1):
                nodesToAnalyze.append(int(nodesToAnalyzeText[nodesToAnalyzeMark:]))
        self.args[0].nodesList = nodesToAnalyze
            
        # Footprint
        self.args[0].footprint = float(self.footprint_input.text())
        
        # Total Height
        self.args[0].totalHeight = float(self.totalHeight_input.text())
        
        # Total Mass
        self.args[0].totalMass = float(self.totalMass_input.text())
        
    def runNow(self):
        self.saveInputs
        self.args[0].runNow = True
        lambda x: self.close()
        