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
        
        self.SAPPath = self.args[0].SAPPath
        self.nodesList = self.args[0].nodesList
        self.footprint = self.args[0].footprint
        self.totalHeight = self.args[0].totalHeight
        self.totalMass = self.args[0].totalMass
        self.toRun = False
        
        # Set Text
        self.SAP2000Path_input.setPlainText(self.SAPPath)
        
        nodesListString = ''
        for i in range(len(self.nodesList)):
            if i < len(self.nodesList)-1:
                nodesListString = nodesListString + str(self.nodesList[i]) + ', '
            else:
                nodesListString = nodesListString + str(self.nodesList[i])
        self.nodesToAnalyze_input.setPlainText(nodesListString)
        
        self.footprint_input.setPlainText(str(self.footprint))
        self.totalHeight_input.setPlainText(str(self.totalHeight))
        self.totalMass_input.setPlainText(str(self.totalMass))
        
        # Set UI Elements
        self.setOkandCancelButtons()     
        self.setRunNowButton()
        #self.runNow_Button.clicked.connect(self.runNow) 
        
      
    def setOkandCancelButtons(self):
        self.OkButton = self.runTowers_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveInputs)
        self.OkButton.clicked.connect(lambda x: self.close())

        self.CancelButton = self.runTowers_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())
    
    
    def saveInputs(self):
        
        # SAP2000 Path
        self.SAPPath = self.SAP2000Path_input.toPlainText()
        
        # Nodes to Analyze (assuming input is string of integers seperated by commas)
        nodesToAnalyze = []
        nodesToAnalyzeText = self.nodesToAnalyze_input.toPlainText()
        nodesToAnalyzeMark = 0
        for i in range(len(nodesToAnalyzeText)):
            if nodesToAnalyzeText[i] == ",":
                nodesToAnalyze.append(int(nodesToAnalyzeText[nodesToAnalyzeMark:i]))
                nodesToAnalyzeMark = i + 2
            elif i == (len(nodesToAnalyzeText) - 1):
                nodesToAnalyze.append(int(nodesToAnalyzeText[nodesToAnalyzeMark:]))
        self.nodesList = nodesToAnalyze
            
        # Footprint
        self.footprint = float(self.footprint_input.toPlainText())
        
        # Total Height
        self.totalHeight = float(self.totalHeight_input.toPlainText())
        
        # Total Mass
        self.totalMass = float(self.totalMass_input.toPlainText())
        
        self.toRun = False
        
        
    def setRunNowButton(self):
        #self.RunNowButton = self.runNow_Button.button(QPushButton)
        self.runNow_Button.clicked.connect(self.saveInputs)
        self.runNow_Button.clicked.connect(self.runNow)
        self.runNow_Button.clicked.connect(lambda x: self.close())    
        
        
    def runNow(self):
        self.toRun = True