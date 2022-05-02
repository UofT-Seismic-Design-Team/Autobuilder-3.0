from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *  # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os
import copy

import resources    # For icons and UIs

from Model import *
from Message import *

class DesignVariable(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        fileh = QFile(':/UI/autobuilder_designvariable_v1.ui')
        fileh.open(QFile.ReadOnly)
        uic.loadUi(fileh, self)
        fileh.close()

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
        
        # Passing in main.tower into bracing scheme
        self.towerRef = args[0].tower

        self.projectSettingsData = args[0].projectSettingsData

        # Create copy of tower to reassign if user saves
        self.tower = copy.deepcopy(args[0].tower)
        
        # Fill tables
        self.Populate()

        # Refresh tables after changing tabs
        self.tabWidget.currentChanged.connect(self.changeTab)

        self.currentBracingGroupName = ""
        self.currentSectionGroupName = ""

        self.typeEnum = {
            'bracing': 0,
            'section': 1,
        }

        self.currentNames = {
            0: '',
            1: '',
        }
        
        # key: tab index; value: qtablewidget
        self.tables = {
            0: self.bracingGroupTable,
            1: self.sectionGroupTable,
        }

        # Save names if exist
        for index in self.tables:
            table = self.tables[index]
            if table.item(0,0) is not None:
                self.currentNames[index] = table.item(0,0).text()

        # # Save the current bracing group name if it exists
        # if self.bracingGroupTable.item(0,0) is not None:
        #     self.currentBracingGroupName = self.bracingGroupTable.item(0,0).text()

        # # Save the current section group name if it exists
        # if self.sectionGroupTable.item(0,0) is not None:
        #     self.currentSectionGroupName = self.sectionGroupTable.item(0,0).text()

        self.sectionGroupTable.cellChanged.connect(self.nameChange)
        self.bracingGroupTable.cellChanged.connect(self.nameChange)

    def changeTab(self):
        '''wipe group name and repopulate dialog'''

        self.GroupNameEdit.clear()
        if self.bracingGroupTable.item(0,0) is not None:
            self.currentBracingGroupName = self.bracingGroupTable.item(0,0).text()
        if self.sectionGroupTable.item(0,0) is not None:
            self.currentSectionGroupName = self.sectionGroupTable.item(0,0).text()
        
        self.Populate()

        # Refresh iteration table
        # Give 0 & 1 meaning!
        if self.tabWidget.currentIndex() == 0:
            if self.bracingGroupTable.rowCount() > 0:
                self.bracingGroupTable.selectRow(0)
                self.updateScreen()
            else:
                self.IterationTable.setRowCount(0)

        elif self.tabWidget.currentIndex() == 1:
            if self.sectionGroupTable.rowCount() > 0:
                self.sectionGroupTable.selectRow(0)
                print('section group name:',self.currentSectionGroupName)
                self.updateScreen()
            else:
                self.IterationTable.setRowCount(0)

    def setIconsForButtons(self):
        self.addGroupButton.setIcon(QIcon(':/Icons/plus.png'))
        self.deleteGroupButton.setIcon(QIcon(':/Icons/minus.png'))
        self.addIterationButton.setIcon(QIcon(':/Icons/plus.png'))
        self.deleteIterationButton.setIcon(QIcon(':/Icons/minus.png'))

    def setOkandCancelButtons(self):
        '''OK and Cancel button both exit dialog but have no save function!'''
        self.OkButton = self.bracingGroupButtonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveGroups)
        self.OkButton.clicked.connect(lambda x: self.close())
        
        self.CancelButton = self.bracingGroupButtonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

    def saveGroups(self):
        self.towerRef.bracingGroups = self.tower.bracingGroups
        print('bracingGroups:', self.towerRef.bracingGroups)
        self.towerRef.sectionGroups = self.tower.sectionGroups

    def addGroup(self):
        ''' Add Bracing Group and clear iteration table '''
        # If currently on Bracing tab:
        if self.tabWidget.currentIndex() == 0:
            # Intialize new bracing group with a random bracing
            newBracingGroup = BracingGroup()
            newBracingGroup.bracings = [list(self.tower.bracings.keys())[0]]

            id = 1
            newBracingGroup.name = "New Bracing Group " + str(id)
            while newBracingGroup.name in self.tower.bracingGroups:
                id += 1
                newBracingGroup.name = "New Bracing Group " + str(id)
            self.tower.addBracingGroup(newBracingGroup)

        # If currently on Section tab:
        elif self.tabWidget.currentIndex() == 1:
            # Intialize new section group with a random section
            newSectionGroup = SectionGroup()
            newSectionGroup.sections = [list(self.projectSettingsData.sections.keys())[0]]

            id = 1
            newSectionGroup.name = "New Section Group " + str(id)
            while newSectionGroup.name in self.tower.sectionGroups:
                id += 1
                newSectionGroup.name = "New Section Group " + str(id)
            self.tower.addSectionGroup(newSectionGroup)
        
        self.Populate()

        # Select new group --------------------
        if self.tabWidget.currentIndex() == 0:
            self.bracingGroupTable.selectRow(self.bracingGroupTable.rowCount()-1)

        elif self.tabWidget.currentIndex() == 1:
            self.sectionGroupTable.selectRow(self.sectionGroupTable.rowCount()-1)

        # Update ----------------------
        self.updateScreen()

    def deleteGroup(self):
        '''delete group and associated iterations'''

        if self.tabWidget.currentIndex() == 0:
            # remove selected rows from table
            indices = self.bracingGroupTable.selectionModel().selectedRows()
            for i, index in enumerate(sorted(indices)):
                # remove from dictionary
                updatedRow = index.row()-i
                BGName = self.bracingGroupTable.item(updatedRow,0).text()
                self.tower.bracingGroups.pop(BGName, None)
                # remove row from table
                self.bracingGroupTable.removeRow(updatedRow)

        elif self.tabWidget.currentIndex() == 1:
            # remove selected rows from table
            indices = self.sectionGroupTable.selectionModel().selectedRows()
            for i, index in enumerate(sorted(indices)):
                # remove from dictionary
                updatedRow = index.row()-i
                SGName = self.sectionGroupTable.item(updatedRow,0).text()
                self.tower.sectionGroups.pop(SGName, None)
                # remove row from table
                self.sectionGroupTable.removeRow(updatedRow)

        # empty coord. table
        self.IterationTable.setRowCount(0)

        # clear group name
        self.GroupNameEdit.clear()

    def updateScreen(self):
        '''Update Iteration Table'''

        self.updateIteration()

        # to avoid error with drop down
        self.IterationTable.clearSelection()

        if self.tabWidget.currentIndex() == 0:
            if self.currentBracingGroupName is not None:
                self.IterationTable.setRowCount(0)
                row = self.bracingGroupTable.currentRow()
                bgName = self.bracingGroupTable.item(row,0).text()
                bg = self.tower.bracingGroups[bgName]
                self.currentBracingGroupName = bgName

                for rows, bracing in enumerate(bg.bracings):
                    self.IterationTable.insertRow(self.IterationTable.rowCount())
                    optionCombo = QComboBox()
                    for b in self.tower.bracings:
                        optionCombo.addItem(b)
                    self.IterationTable.setCellWidget(rows, 0, optionCombo)
                    optionCombo.setCurrentText(bracing)

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
                    optionCombo = QComboBox()
                    for s in self.projectSettingsData.sections:
                        optionCombo.addItem(s)
                    self.IterationTable.setCellWidget(rows, 0, optionCombo)
                    optionCombo.setCurrentText(section)

                self.GroupNameEdit.setText(self.sectionGroupTable.item(row,0).text())

    def addIteration(self):
        ''' Add empty row to iteration table '''
        row = self.IterationTable.rowCount()
        self.IterationTable.insertRow(row)

        varCombo = QComboBox()

        if self.tabWidget.currentIndex() == 0:
            variables = list(self.tower.bracings)
        elif self.tabWidget.currentIndex() == 1:
            variables = list(self.projectSettingsData.sections)

        for v in variables:
            varCombo.addItem(v)

        self.IterationTable.setCellWidget(row, 0, varCombo)
        varCombo.setCurrentText(variables[0])
        
        self.updateIteration()

    def deleteIteration(self):
        ''' Delete selected rows from iter table'''
        indices = self.IterationTable.selectionModel().selectedRows()

        # avoid error with drop down
        self.IterationTable.clearSelection()

        for i, index in enumerate(sorted(indices)):
            updatedRow = index.row()-i
            self.IterationTable.removeRow(updatedRow)

        print('delete iter:', self.IterationTable.rowCount())
        
        self.updateIteration()

    def updateIteration(self):
        currName = self.GroupNameEdit.toPlainText()

        if currName != "":
            if self.tabWidget.currentIndex() == 0:
                newBG = self.tower.bracingGroups[currName]
                newBG.bracings = []
                for row in range(self.IterationTable.rowCount()):
                    cell = self.IterationTable.cellWidget(row, 0)
                    if cell != None:
                        bracing = cell.currentText()
                        newBG.bracings.append(bracing)
            
            elif self.tabWidget.currentIndex() == 1:
                newSG = self.tower.sectionGroups[currName]
                newSG.sections = []
                for row in range(self.IterationTable.rowCount()):
                    cell = self.IterationTable.cellWidget(row, 0)
                    if cell != None:
                        section = cell.currentText()
                        newSG.sections.append(section)
    
    def Populate(self):
        column = 0

        if self.tabWidget.currentIndex() == 0:
            self.bracingGroupTable.setRowCount(0)
            for row, bracingGroup in enumerate(self.tower.bracingGroups):
                print('bracing group populate')
                self.bracingGroupTable.insertRow(self.bracingGroupTable.rowCount())
                bgItem = QTableWidgetItem(bracingGroup)
                self.bracingGroupTable.setItem(row, column, bgItem)

        elif self.tabWidget.currentIndex() == 1:
            self.sectionGroupTable.setRowCount(0)
            for row, sectionGroup in enumerate(self.tower.sectionGroups):
                print('section group populate')
                self.sectionGroupTable.insertRow(self.sectionGroupTable.rowCount())
                sgItem = QTableWidgetItem(sectionGroup)
                self.sectionGroupTable.setItem(row, column, sgItem)

    def nameChange(self):
        ''' change group name after it was defined in main table '''
        warning = WarningMessage()

        if self.tabWidget.currentIndex() == 0:
            row = self.bracingGroupTable.currentRow() #returns -1 when repopulating empty table
            print('bracing group namechange')
            if row != -1 and self.currentBracingGroupName != None:
                newName = self.bracingGroupTable.item(row,0).text()

                # Error handling
                if newName == '':
                    warning.popUpErrorBox('Bracing group name is missing.')
                    self.bracingGroupTable.item(row,0).setText(self.currentBracingGroupName)
                    return

                if newName in self.tower.bracingGroups:
                    warning.popUpErrorBox('Bracing group name already exists.')
                    self.bracingGroupTable.item(row,0).setText(self.currentBracingGroupName)
                    return

                # Change name while preserving the order
                bgKeys = list(self.tower.bracingGroups.keys())
                bgValues = list(self.tower.bracingGroups.values())

                self.tower.bracingGroups.clear()
                for i in range(len(bgKeys)):
                    # bracing group to be changed
                    if bgKeys[i] == self.currentBracingGroupName:
                        # update the name of group
                        bgValues[i].name = newName
                        # assign original iterations to new name
                        self.tower.bracingGroups[newName] = bgValues[i]
                    else:
                        self.tower.bracingGroups[bgKeys[i]] = bgValues[i]
                
                # match group name to item name in main table
                self.GroupNameEdit.setText(newName)
                
                self.updateScreen()

        elif self.tabWidget.currentIndex() == 1:
            row = self.sectionGroupTable.currentRow() #returns -1 when repopulating empty table
            if row != -1 and self.currentSectionGroupName != None:
                newName = self.sectionGroupTable.item(row,0).text()

                if newName == '':
                    warning.popUpErrorBox('Section group name is missing.')
                    self.sectionGroupTable.item(row,0).setText(self.currentSectionGroupName)
                    return

                if newName in self.tower.sectionGroups:
                    warning.popUpErrorBox('Section group name already exists.')
                    self.sectionGroupTable.item(row,0).setText(self.currentSectionGroupName)
                    return
                
                # Change name while preserving the order
                sgKeys = list(self.tower.sectionGroups.keys())
                sgValues = list(self.tower.sectionGroups.values())

                self.tower.sectionGroups.clear()
                for i in range(len(sgKeys)):
                    # section group to be changed
                    if sgKeys[i] == self.currentSectionGroupName:
                        # update the name of group
                        sgValues[i].name = newName
                        # assign original iterations to new name
                        self.tower.sectionGroups[newName] = sgValues[i]
                    else:
                        self.tower.sectionGroups[sgKeys[i]] = sgValues[i]
                
                # match group name to item name in main table
                self.GroupNameEdit.setText(newName)

                self.updateScreen()
    
