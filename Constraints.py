from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic
from Model import *

from View2DEngine import *  # import View2DEngine
import copy

import sys  # We need sys so that we can pass argv to QApplication
import os

class ConstraintUI(QDialog):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('UI/autobuilder_constraint_dialog.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Add Empty Row to List of Floor Plan Schemes
        self.add.clicked.connect(self.addConstraint)

        # Delete Selected Row from List of Floor Plan Schemes
        self.delete_2.clicked.connect(self.deleteConstraint)

        # # passing in main.tower properties into constraint
        # self.populate()

        # #Save the current constraint table name and intialize for the first one for later use in changing and saving the name
        # self.currentConstraintName = self.constraintTable.item(0,0).text()

        # #Call update upon ScreenXYElev to update the whole screen upon picking floor plan
        # self.constraintTable.itemClicked.connect(self.updateScreenXYElev)
        #
        # #Call cell name change
        # self.constraintTable.cellChanged.connect(self.nameChange)


        #reference to existing tower for cache
        self.towerRef = args[0].tower

#https://stackoverflow.com/questions/701802/how-do-i-execute-a-string-containing-python-code-in-python

    
    # determine if code is valid for string
    # import ast
    # def is_valid_python(code):
    #     try:
    #         ast.parse(code)
    #     except SyntaxError:
    #         return False
    #     return True

    def populate(self):
        '''Populate the constraint Table with floorplans from the tower'''
        column = 0
        #Clear the constraint table
        self.constraintTable.setRowCount(0)
        #Iterate through and add the constraint
        for i,constraint in enumerate(self.tower.floorPlans):
            self.constraintTable.insertRow(self.constraintTable.rowCount())
            item = QTableWidgetItem()
            item.setText(self.tower.floorPlans[constraint].name)
            self.constraintTable.setItem(i, column, item)



    def setIconsForButtons(self):
        '''Set icons associated with the add/delete buttons'''
        self.add.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.delete_2.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def addConstraint(self):
        '''Adding new constraint'''
        pass
        # newfloorPlan = Constraint()
        # id = 1
        # newfloorPlan.name = "New Floor Plan " + str(id)
        # while newfloorPlan.name in self.tower.floorPlans:
        #     id += 1
        #     newfloorPlan.name = "New Floor Plan " + str(id)
        # self.tower.addConstraint(newfloorPlan)
        # self.populate()

    def deleteConstraint(self):
        '''Delete floor plan from tower'''
        indices = self.constraintTable.selectionModel().selectedRows()
        for index in sorted(indices):
            item = self.constraintTable.item(index.row(),index.column())
           # del self.tower.floorPlans[item.text()]
        for index in sorted(indices):
            self.constraintTable.removeRow(index.row())


    def cancelConstraint(self):
        '''do Nothing'''
        self.towerRef = self.towerRef

    def saveConstraint(self):
        '''Overwrite the tower linked to the main model'''
        pass

        
    def setOkandCancelButtons(self):
        #Constructor
        self.OkButton = self.constraint_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveConstraint)
        self.OkButton.clicked.connect(lambda x: self.close())

        self.CancelButton = self.constraint_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())
        self.CancelButton.clicked.connect(self.cancelConstraint)


