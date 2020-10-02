from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

from WarningMessage import *

class AssignBracingDesign(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Assigning Bracing Design to Panel Data
        self.data = AssignmentData()

        # Load the UI Page
        uic.loadUi('UI/autobuilder_assignbracingdesign.ui', self)

        # Set UI Elements
        #self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Add Empty Row to List of Assignments
        #self.addAssignmentButton.clicked.connect(self.addAssignment)

        # Delete Row from List of Assignments
        #self.deleteAssignmentButton.clicked.connect(self.deleteAssignment)

        #self.assignmentData = AssignmentData()
        #self.bracingDesignData = BracingDesignData()

    #def setIconsForButtons(self):
        #self.addAssignmentButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        #self.deleteAssignmentButton.setIcon(QIcon(r"Icons\24x24\minus.png"))

    # Insert new row in bracing design table
    #def addAssignment(self,signal):
        #self.AssignmentTable.insertRow( self.AssignmentTable.rowCount() )

    # Delete selected row in bracing design table
    #def deleteAssignment(self,signal):
        #indices = self.AssignmentTable.selectionModel().selectedRows()
        #for index in sorted(indices):
            #self.AssignmentTable.removeRow(index.row())

    # Save bracing design corresponding to each panel
    def saveAssignment(self):
        
        self.data.assignments.clear() # reset assignment properties

        rowNum = self.AssignmentTable.rowCount()
        for i in range(rowNum):
            panelItem = self.AssignmentTable.item(i,0)
            bracingItem = self.AssignmentTable.item(i,1)
            # Check if the row is filled
            if panelItem == None or bracingItem == None:
                break
            panel = panelItem.text()
            bracing = bracingItem.text()
            try:
                # Check if the item is filled
                if panel == '' or bracing == '':
                    break
                self.data.assignments[panel] = bracing
            except:
                warning.popUpErrorBox('Invalid input for assignment properties')
                return # terminate the saving process

    # Display list of bracing designs
    def displayAssignmentData(self):
        
        for panel in self.assignments.keys():
            #self.data.panels.append(panel)
            panelItem = QTableWidgetItem(panel)
            self.AssignmentTable.setItem(i,0,panelItem)

            if panel in self.data.panels:
                bracing = QTableWidgetItem(self.data.assignments.get(panel))
                self.AssignmentTable.setItem(i,1,bracingItem)
            else:
                TBD = QTableWidgetItem('TBD')
                self.AssignmentTable.setItem(i,1,TBD)


        # i = 0
        # assign_rowNum = self.AssignmentTable.rowCount()
        # while i < len(self.data.panels):
        #     panelItem = self.data.panels[i]
        #     if i >= assign_rowNum:
        #         self.AssignmentTable.insertRow(i)
        #     self.AssignmentTable.setItem(i,0,panelItem)
            
        #     i += 1
            # check if panel item in dict
            
        # i = 0
        # assign_rowNum = self.AssignmentTable.rowCount()
        # for panel in self.data.assignments.keys():
        #     panelItem = QTableWidgetItem(panel)
        #     bracingItem = QTableWidgetItem(self.data.assignments.get(panel))
        #     if i >= assign_rowNum:
        #         self.AssignmentTable.insertRow(i)
        #     self.AssignmentTable.setItem(i,0,panelItem)
        #     self.AssignmentTable.setItem(i,1,bracingItem)
        #     i += 1
        #     print(panelItem,bracingItem)
        

    def setAssignmentData(self, data):
        self.data = data
    
    def setOkandCancelButtons(self):
        self.OkButton = self.Assignment_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveAssignment)

        self.OkButton.clicked.connect(lambda x: self.close())
        
        self.CancelButton = self.Assignment_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

# Store list of bracing designs corresponding to each panel
class AssignmentData:
    def __init__(self):
        self.panels = []
        self.possibleBracings = {}
        self.assignments = {}
    