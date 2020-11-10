from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

from Model import *
#from WarningMessage import *

class BracingIteration(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('UI/autobuilder_bracinggroup_v1.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Add Empty Row to List of Bracing Groups
        self.addBracingGroupButton.clicked.connect(self.addBracingGroup)

        # save xy coordinates of new bracing group
        self.updateBGIterationButton.clicked.connect(self.updateBGIteration)

        # Delete Selected Row from List of Bracing Groups
        self.deleteBracingGroupButton.clicked.connect(self.deleteBracingGroup)

        # Add Empty Row to List of Bracing Group Iterations
        self.addBGIterationButton.clicked.connect(self.addBGIteration)

        # Delete Selected Row from List of Bracing Group Iterations
        self.deleteBGIterationButton.clicked.connect(self.deleteBGIteration)

        # Navigate to new bracing group iteration table
        self.bracingGroupTable.itemSelectionChanged.connect(self.refreshBGTable)
        
        # Passing in main.tower into bracing group
        self.tower = args[0].tower
        
        # Fill in bracing group table
        self.Populate()

    def Populate(self):
        ''' Add existing bracing groups to bracingGroupTable '''
        column = 0
        for row, bracingGroup in enumerate(self.tower.bracingGroups):
            self.bracingGroupTable.insertRow(self.bracingGroupTable.rowCount())
            bgItem = QTableWidgetItem(bracingGroup)
            '''How to disable clicking?'''
            #bcItem.setFlags(Qt.ItemIsEditable)
            self.bracingGroupTable.setItem(row, column, bgItem)

    def refreshBGTable(self):
        ''' Display bracing iteration table for existing bracing group '''

        # if switching to an existing bracing group
        if self.bracingGroupTable.currentItem() is not None:

            self.BGIterationTable.setRowCount(0)

            # Set currently selected cell as current bracing object
            currBG = self.bracingGroupTable.currentItem().text()
            BG = self.tower.bracingGroups[currBG]

            # Fill itereation table
            for row, bracing in enumerate(BG.bracings):
                self.BGIterationTable.insertRow(self.BGIterationTable.rowCount())
                self.BGIterationTable.setItem(row, 0, QTableWidgetItem(str(bracing)))

            # Display name of currently selected bracing
            self.BGNameEdit.setText(currBG)

    def addBracingGroup(self, signal):
        ''' Add Bracing Group and clear bracing iteration table (not saved yet)'''

        # Add new row to BG table
        self.bracingGroupTable.insertRow(self.bracingGroupTable.rowCount())

        # empty coord. table
        self.BGIterationTable.setRowCount(0)

        # clear bracing name
        self.BGNameEdit.clear()

    def deleteBracingGroup(self, signal):
        '''delete bracing group and associated bracing iterations'''
        
        # add warning message: Are you sure you want to delete?
        BGs = self.tower.bracingGroups

        # remove selected rows from table
        indices = self.bracingGroupTable.selectionModel().selectedRows()
        for index in sorted(indices):
            # remove from dictionary
            print(index.row())
            BGName = self.bracingGroupTable.item(index.row(),0).text()
            BGs.pop(BGName, None)

            # remove row from table
            self.bracingGroupTable.removeRow(index.row())

        # empty coord. table
        self.BGIterationTable.setRowCount(0)

        # clear bracing name
        self.BGNameEdit.clear()

    def updateBGIteration(self):

        ''' Update bracing group with new iteration info '''

        BGs = self.tower.bracingGroups
        BGName = self.BGNameEdit.text()

        if not (BGName in BGs):
            newBG = BracingGroup(BGName)
            self.tower.addBracingGroup(newBG)

        BG = BGs[BGName]

        for row in range(self.BGIterationTable.rowCount()):
            bracing = self.BGIterationTable.item(row,0).text()
            BG.addBracing(bracing)

        # Change BG name in main table
        newRow = self.bracingGroupTable.rowCount()
        BGItem = QTableWidgetItem(BGName)
        ''' TO DO: Disable clicking '''
        self.bracingGroupTable.setItem(int(newRow)-1,0,BGItem)


    def addBGIteration(self, signal):
        ''' Add empty row to iteration table '''
        self.BGIterationTable.insertRow(self.BGIterationTable.rowCount())

    def deleteBGIteration(self, signal):
        ''' Delete selected rows from iter table'''
        indices = self.BGIterationTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.BGIterationTable.removeRow(index.row())

    def setIconsForButtons(self):
        self.addBracingGroupButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteBracingGroupButton.setIcon(QIcon(r"Icons\24x24\minus.png"))
        self.addBGIterationButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteBGIterationButton.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def setOkandCancelButtons(self):
        '''OK and Cancel button both exit dialog but have no save function!'''
        self.OkButton = self.bracingGroupButtonBox.button(QDialogButtonBox.Ok)
        #self.OkButton.clicked.sconnect(self.saveBracingGroup)
        self.OkButton.clicked.connect(lambda x: self.close())
        
        self.CancelButton = self.bracingGroupButtonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())
