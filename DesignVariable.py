from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os
import copy

from Model import *
from Message import *

class DesignVariable(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('UI/autobuilder_designvariable_v1.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Add or Delete Empty Row to List of Groups
        self.addGroupButton.clicked.connect(self.addGroup)
        self.deleteGroupButton.clicked.connect(self.deleteGroup)

        # Update whole screen after a group is picked
        self.bracingGroupTable.itemClicked.connect(self.updateScreen)
        self.sectionGroupTable.itemClicked.connect(self.updateScreen)

        # Add Empty Row to List of Group Iterations
        self.addIterationButton.clicked.connect(self.addIteration)

        # Delete Selected Row from List of Group Iterations
        self.deleteIterationButton.clicked.connect(self.deleteIteration)

        # Update iteration table upon cell change
        self.IterationTable.itemSelectionChanged.connect(self.updateIteration)
        self.IterationTable.itemSelectionChanged.connect(self.updateIteration)
        
        # Passing in main.tower into bracing scheme
        self.towerRef = args[0].tower

        # Create copy of tower to reassign if user saves
        self.tower = copy.deepcopy(args[0].tower)
        
        # Fill tables
        self.Populate()

        # Refresh tables after changing tabs
        self.tabWidget.currentChanged.connect(self.changeTab)

        self.currentBracingGroupName = ""
        self.currentSectionGroupName = ""

        # Save the current bracing group name if it exists
        if self.bracingGroupTable.item(0,0) is not None:
            self.currentBracingGroupName = self.bracingGroupTable.item(0,0).text()

        # Save the current section group name if it exists
        if self.sectionGroupTable.item(0,0) is not None:
            self.currentSectionGroupName = self.sectionGroupTable.item(0,0).text()

        self.bracingGroupTable.cellChanged.connect(self.nameChange)
        self.sectionGroupTable.cellChanged.connect(self.nameChange)

    def changeTab(self):
        '''wipe group name and repopulate dialog'''
        self.GroupNameEdit.clear()
        if self.bracingGroupTable.item(0,0) is not None:
            self.currentBracingGroupName = self.bracingGroupTable.item(0,0).text()
        if self.sectionGroupTable.item(0,0) is not None:
            self.currentSectionGroupName = self.sectionGroupTable.item(0,0).text()
        self.Populate()

    def setIconsForButtons(self):
        self.addGroupButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteGroupButton.setIcon(QIcon(r"Icons\24x24\minus.png"))
        self.addIterationButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteIterationButton.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def setOkandCancelButtons(self):
        '''OK and Cancel button both exit dialog but have no save function!'''
        self.OkButton = self.bracingGroupButtonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveGroups)
        self.OkButton.clicked.connect(lambda x: self.close())
        
        self.CancelButton = self.bracingGroupButtonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

    def saveGroups(self):
        self.towerRef.bracingGroups = self.tower.bracingGroups
        self.towerRef.sectionGroups = self.tower.sectionGroups

    def addGroup(self):
        ''' Add Bracing Group and clear iteration table '''

        # If currently on Bracing tab:
        if self.tabWidget.currentIndex() == 0:
            newBracingGroup = BracingGroup()
            id = 1
            newBracingGroup.name = "New Bracing Group " + str(id)
            while newBracingGroup.name in self.tower.bracingGroups:
                id += 1
                newBracingGroup.name = "New Bracing Group " + str(id)
            self.tower.addBracingGroup(newBracingGroup)

        # If currently on Section tab:
        elif self.tabWidget.currentIndex() == 1:
            newSectionGroup = SectionGroup()
            id = 1
            newSectionGroup.name = "New Section Group " + str(id)
            while newSectionGroup.name in self.tower.sectionGroups:
                id += 1
                newSectionGroup.name = "New Section Group " + str(id)
            self.tower.addSectionGroup(newSectionGroup)
        
        self.Populate()

        # empty coord. table
        self.IterationTable.setRowCount(0)

        # clear bracing name
        self.GroupNameEdit.clear()

    def deleteGroup(self):
        '''delete group and associated iterations'''

        if self.tabWidget.currentIndex() == 0:
            # remove selected rows from table
            indices = self.bracingGroupTable.selectionModel().selectedRows()
            for index in sorted(indices):
                # remove from dictionary
                BGName = self.bracingGroupTable.item(index.row(),0).text()
                self.tower.bracingGroups.pop(BGName, None)
                # remove row from table
                self.bracingGroupTable.removeRow(index.row())

        elif self.tabWidget.currentIndex() == 1:
            # remove selected rows from table
            indices = self.sectionGroupTable.selectionModel().selectedRows()
            for index in sorted(indices):
                # remove from dictionary
                SGName = self.sectionGroupTable.item(index.row(),0).text()
                self.tower.bracingGroups.pop(SGName, None)
                # remove row from table
                self.sectionGroupTable.removeRow(index.row())

        # empty coord. table
        self.IterationTable.setRowCount(0)

        # clear group name
        self.GroupNameEdit.clear()

    def updateScreen(self):
        '''Update Iteration Table'''

        if self.tabWidget.currentIndex() == 0:
            if self.currentBracingGroupName is not None:
                self.IterationTable.setRowCount(0)
                row = self.bracingGroupTable.currentRow()
                bgName = self.bracingGroupTable.item(row,0).text()
                bg = self.tower.bracingGroups[bgName]
                self.currentBracingGroupName = bgName

                for rows, bracing in enumerate(bg.bracings):
                    self.IterationTable.insertRow(self.IterationTable.rowCount())
                    self.IterationTable.setItem(rows, 0, QTableWidgetItem(str(bracing)))

                self.GroupNameEdit.setText(self.bracingGroupTable.item(row,0).text())

        elif self.tabWidget.currentIndex() == 1:
            if self.currentSectionGroupName is not None:
                self.IterationTable.setRowCount(0)
                row = self.sectionGroupTable.currentRow()
                sgName = self.sectionGroupTable.item(row, 0).text()
                sg = self.tower.sectionGroups[sgName]
                self.currentSectionGroupName = sgName

                for rows, section in enumerate(sg.sections):
                    self.IterationTable.insertRow(self.IterationTable.rowCount())
                    self.IterationTable.setItem(rows, 0, QTableWidgetItem(str(section)))
       
                self.GroupNameEdit.setText(self.sectionGroupTable.item(row,0).text())

    def addIteration(self):
        ''' Add empty row to iteration table '''
        row = self.IterationTable.rowCount()
        self.IterationTable.insertRow(row)
        self.IterationTable.setItem(row, 0, QTableWidgetItem(str(0)))
        self.updateIteration()

    def deleteIteration(self):
        ''' Delete selected rows from iter table'''
        indices = self.BGIterationTable.selectionModel().selectedRows()
        for index in sorted(indices):
            self.IterationTable.removeRow(index.row())
        self.updateIteration()

    def updateIteration(self):
        currName = self.GroupNameEdit.toPlainText()
        if currName != "":
            if self.tabWidget.currentIndex() == 0:
                newBG = self.tower.bracingGroups[currName]
                newBG.bracings = []
                for row in range(self.IterationTable.rowCount()):
                    bracing = self.IterationTable.item(row, 0).text()
                    newBG.bracings.append(bracing)
            
            elif self.tabWidget.currentIndex() == 1:
                newSG = self.tower.sectionGroups[currName]
                newSG.sections = []
                for row in range(self.IterationTable.rowCount()):
                    section = self.IterationTable.item(row, 0).text()
                    newSG.sections.append(section)
    
    def Populate(self):
        ''' Add existing bracing groups to bracingGroupTable '''
        column = 0

        self.bracingGroupTable.setRowCount(0)
        for row, bracingGroup in enumerate(self.tower.bracingGroups):
            self.bracingGroupTable.insertRow(self.bracingGroupTable.rowCount())
            bgItem = QTableWidgetItem(bracingGroup)
            self.bracingGroupTable.setItem(row, column, bgItem)

        self.sectionGroupTable.setRowCount(0)
        for row, sectionGroup in enumerate(self.tower.sectionGroups):
            self.sectionGroupTable.insertRow(self.sectionGroupTable.rowCount())
            sgItem = QTableWidgetItem(sectionGroup)
            self.sectionGroupTable.setItem(row, column, sgItem)

    def nameChange(self):
        ''' change group name after it is defined in main table '''
        if self.tabWidget.currentIndex() == 0:
            row = self.bracingGroupTable.currentRow() #returns -1 when repopulating empty table
            if row != -1 and self.currentBracingGroupName != None:
                bgName = self.bracingGroupTable.item(row,0).text()
                bg = self.tower.bracingGroups[self.currentBracingGroupName]
                # update group name to match changed cell
                bg.name = bgName
                # assign original iterations to group name
                self.tower.bracingGroups[bgName] = self.tower.bracingGroups.pop(self.currentBracingGroupName)
                self.updateScreen()

        elif self.tabWidget.currentIndex() == 1:
            row = self.sectionGroupTable.currentRow() #returns -1 when repopulating empty table
            if row != -1 and self.currentSectionGroupName != None:
                sgName = self.sectionGroupTable.item(row,0).text()
                sg = self.tower.sectionGroups[self.currentSectionGroupName]
                # update group name to match changed cell
                sg.name = sgName
                # assign original iterations to group name
                self.tower.sectionGroups[sgName] = self.tower.sectionGroups.pop(self.currentSectionGroupName)
                self.updateScreen()
    
'''
    def refreshBGTable(self):
        # Display bracing iteration table for existing bracing group

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

    
    def updateBGIteration(self):

        #Update bracing group with new iteration info

        BGs = self.tower.bracingGroups
        BGName = self.BGNameEdit.text()

        if not (BGName in BGs):
            newBG = BracingGroup(BGName)
            self.tower.addBracingGroup(newBG)

        BG = BGs[BGName]

        for row in range(self.BGIterationTable.rowCount()):
            bracing = self.BGIterationTable.item(row,0).text()
            if bracing not in BG.bracings:
                BG.addBracing(bracing)

        # Change BG name in main table
        newRow = self.bracingGroupTable.rowCount()
        BGItem = QTableWidgetItem(BGName)
        self.bracingGroupTable.setItem(int(newRow)-1,0,BGItem)
'''