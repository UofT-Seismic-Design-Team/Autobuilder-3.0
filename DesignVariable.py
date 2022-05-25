from re import T
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

        self.currentBracingGroupName = ""
        self.currentSectionGroupName = ""
        self.currentAreaSectionGroupName = ""

        # Data --------------------------
        self.typeEnum = {
            'bracing': 0,
            'section': 1,
            'areaSection': 2,
        }

        # Attributes of design variable groups ------------------------
        self.currentNames = ['' for i in range(3)]
        self.tables = [self.bracingGroupTable, self.sectionGroupTable, self.areaSectionGroupTable]
        self.groupDicts = [self.tower.bracingGroups,self.tower.sectionGroups,self.tower.areaSectionGroups]
        self.variableDicts = [self.tower.bracings, self.projectSettingsData.sections, self.projectSettingsData.areaSections]

        # Fill tables
        self.Populate()

        # Refresh tables after changing tabs
        self.tabWidget.currentChanged.connect(self.changeTab)

        for index in range(len(self.tables)):
            table = self.tables[index]

            # Save names if exist ---------------------------------
            if table.item(0,0) is not None:
                self.currentNames[index] = table.item(0,0).text()
            
            # react to name change events -------------------------
            table.cellChanged.connect(self.nameChange)

    def changeTab(self):
        '''wipe group name and repopulate dialog'''

        self.GroupNameEdit.clear()

        for index in range(len(self.tables)):
            table = self.tables[index]
            if table.item(0,0) is not None:
                self.currentNames[index] = table.item(0,0).text()
                
        # if self.bracingGroupTable.item(0,0) is not None:
        #     self.currentBracingGroupName = self.bracingGroupTable.item(0,0).text()
        # if self.sectionGroupTable.item(0,0) is not None:
        #     self.currentSectionGroupName = self.sectionGroupTable.item(0,0).text()
        # if self.areaSectionGroupTable.item(0,0) is not None:
        #     self.currentSectionGroupName = self.areaSectionGroupTable.item(0,0).text()
        
        self.Populate()
        # Refresh iteration table
        for tabIndex in range(len(self.tables)):
            if self.tabWidget.currentIndex() == tabIndex:
                table = self.tables[tabIndex]
                if table.rowCount() > 0:
                    table.selectRow(0)
                    self.updateScreen()
                else:
                    self.IterationTable.setRowCount(0)

        # if self.tabWidget.currentIndex() == 0:
        #     if self.bracingGroupTable.rowCount() > 0:
        #         self.bracingGroupTable.selectRow(0)
        #         self.updateScreen()
        #     else:
        #         self.IterationTable.setRowCount(0)

        # elif self.tabWidget.currentIndex() == 1:
        #     if self.sectionGroupTable.rowCount() > 0:
        #         self.sectionGroupTable.selectRow(0)
        #         print('section group name:',self.currentSectionGroupName)
        #         self.updateScreen()
        #     else:
        #         self.IterationTable.setRowCount(0)

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
        self.towerRef.areaSectionGroups = self.tower.areaSectionGroups
        print('areaSectionGroups:', self.towerRef.areaSectionGroups)

    def addGroup(self):
        ''' Add Bracing Group and clear iteration table '''

        # Setup ---------------------------------------------------
        # Intialize group with first variable available
        newBracingGroup = BracingGroup()
        newBracingGroup.bracings = [list(self.tower.bracings.keys())[0]]

        newSectionGroup = SectionGroup()
        newSectionGroup.sections = [list(self.projectSettingsData.sections.keys())[0]]

        newAreaSectionGroup = AreaSectionGroup()
        newAreaSectionGroup.sections = [list(self.projectSettingsData.areaSections.keys())[0]]

        newGroups = [newBracingGroup, newSectionGroup, newAreaSectionGroup]
        newNamePrefixes = ['New Bracing Group','New Section Group','New Area Section Group']

        for tabIndex in range(len(self.tables)):
            if self.tabWidget.currentIndex() == tabIndex:
                # Intialize new bracing group with a random bracing
                newGroup = newGroups[tabIndex]
                groupDict = self.groupDicts[tabIndex]

                id = 1
                newGroup.name = '{} {}'.format(newNamePrefixes[tabIndex], str(id))
                while newGroup.name in groupDict:
                    id += 1
                    newGroup.name = '{} {}'.format(newNamePrefixes[tabIndex], str(id))

                # Add new group to its group dictionary in the tower object
                groupDict[newGroup.name] = newGroup

                break

        # # If currently on Bracing tab:
        # if self.tabWidget.currentIndex() == 0:
        #     # Intialize new bracing group with a random bracing
        #     newBracingGroup = BracingGroup()
        #     newBracingGroup.bracings = [list(self.tower.bracings.keys())[0]]

        #     id = 1
        #     newBracingGroup.name = "New Bracing Group " + str(id)
        #     while newBracingGroup.name in self.tower.bracingGroups:
        #         id += 1
        #         newBracingGroup.name = "New Bracing Group " + str(id)
        #     self.tower.addBracingGroup(newBracingGroup)

        # # If currently on Section tab:
        # elif self.tabWidget.currentIndex() == 1:
        #     # Intialize new section group with a random section
        #     newSectionGroup = SectionGroup()
        #     newSectionGroup.sections = [list(self.projectSettingsData.sections.keys())[0]]

        #     id = 1
        #     newSectionGroup.name = "New Section Group " + str(id)
        #     while newSectionGroup.name in self.tower.sectionGroups:
        #         id += 1
        #         newSectionGroup.name = "New Section Group " + str(id)
        #     self.tower.addSectionGroup(newSectionGroup)
        
        self.Populate()

        # Select new group --------------------
        for tabIndex in range(len(self.tables)):
            if self.tabWidget.currentIndex() == tabIndex:
                self.tables[tabIndex].selectRow(self.tables[tabIndex].rowCount()-1)

        # if self.tabWidget.currentIndex() == 0:
        #     self.bracingGroupTable.selectRow(self.bracingGroupTable.rowCount()-1)

        # elif self.tabWidget.currentIndex() == 1:
        #     self.sectionGroupTable.selectRow(self.sectionGroupTable.rowCount()-1)

        # Update ----------------------
        self.updateScreen()

    def deleteGroup(self):
        '''delete group and associated iterations'''

        for tabIndex in range(len(self.tables)):
            if self.tabWidget.currentIndex() == tabIndex:
                # remove selected rows from table
                indices = self.tables[tabIndex].selectionModel().selectedRows()
                for i, index in enumerate(sorted(indices)):
                    # remove from dictionary
                    updatedRow = index.row()-i
                    name = self.tables[tabIndex].item(updatedRow,0).text()
                    self.groupDicts[tabIndex].pop(name, None)
                    # remove row from table
                    self.tables[tabIndex].removeRow(updatedRow)
                break

        # if self.tabWidget.currentIndex() == 0:
        #     # remove selected rows from table
        #     indices = self.bracingGroupTable.selectionModel().selectedRows()
        #     for i, index in enumerate(sorted(indices)):
        #         # remove from dictionary
        #         updatedRow = index.row()-i
        #         BGName = self.bracingGroupTable.item(updatedRow,0).text()
        #         self.tower.bracingGroups.pop(BGName, None)
        #         # remove row from table
        #         self.bracingGroupTable.removeRow(updatedRow)

        # elif self.tabWidget.currentIndex() == 1:
        #     # remove selected rows from table
        #     indices = self.sectionGroupTable.selectionModel().selectedRows()
        #     for i, index in enumerate(sorted(indices)):
        #         # remove from dictionary
        #         updatedRow = index.row()-i
        #         SGName = self.sectionGroupTable.item(updatedRow,0).text()
        #         self.tower.sectionGroups.pop(SGName, None)
        #         # remove row from table
        #         self.sectionGroupTable.removeRow(updatedRow)

        # empty coord. table
        self.IterationTable.setRowCount(0)

        # clear group name
        self.GroupNameEdit.clear()

    def updateScreen(self):
        '''Update Iteration Table'''

        self.updateIteration()

        # to avoid error with drop down
        self.IterationTable.clearSelection()

        print('updateScreen')
        for tabIndex in range(len(self.tables)):
            print('tabIndex', tabIndex)
            if self.tabWidget.currentIndex() == tabIndex and self.currentNames[tabIndex] is not None:
                self.IterationTable.setRowCount(0)
                row = self.tables[tabIndex].currentRow()
                name = self.tables[tabIndex].item(row,0).text()
                self.currentNames[tabIndex] = name

                group = self.groupDicts[tabIndex][name]
                for rows, varName in enumerate(group.variables):
                    self.IterationTable.insertRow(self.IterationTable.rowCount())
                    optionCombo = QComboBox()
                    for v in self.variableDicts[tabIndex]:
                        optionCombo.addItem(v)
                    self.IterationTable.setCellWidget(rows, 0, optionCombo)
                    optionCombo.setCurrentText(varName)

                self.GroupNameEdit.setText(self.tables[tabIndex].item(row,0).text())

        # if self.tabWidget.currentIndex() == 0:
        #     if self.currentBracingGroupName is not None:
        #         self.IterationTable.setRowCount(0)
        #         row = self.bracingGroupTable.currentRow()
        #         bgName = self.bracingGroupTable.item(row,0).text()
        #         bg = self.tower.bracingGroups[bgName]
        #         self.currentBracingGroupName = bgName

        #         for rows, bracing in enumerate(bg.bracings):
        #             self.IterationTable.insertRow(self.IterationTable.rowCount())
        #             optionCombo = QComboBox()
        #             for b in self.tower.bracings:
        #                 optionCombo.addItem(b)
        #             self.IterationTable.setCellWidget(rows, 0, optionCombo)
        #             optionCombo.setCurrentText(bracing)

        #         self.GroupNameEdit.setText(self.bracingGroupTable.item(row,0).text())

        # elif self.tabWidget.currentIndex() == 1:
        #     if self.currentSectionGroupName is not None:
        #         self.IterationTable.setRowCount(0)
        #         row = self.sectionGroupTable.currentRow()
        #         sgName = self.sectionGroupTable.item(row, 0).text()
        #         sg = self.tower.sectionGroups[sgName]
        #         self.currentSectionGroupName = sgName

        #         for rows, section in enumerate(sg.sections):
        #             self.IterationTable.insertRow(self.IterationTable.rowCount())
        #             optionCombo = QComboBox()
        #             for s in self.projectSettingsData.sections:
        #                 optionCombo.addItem(s)
        #             self.IterationTable.setCellWidget(rows, 0, optionCombo)
        #             optionCombo.setCurrentText(section)

        #         self.GroupNameEdit.setText(self.sectionGroupTable.item(row,0).text())

    def addIteration(self):
        ''' Add empty row to iteration table '''
        row = self.IterationTable.rowCount()
        self.IterationTable.insertRow(row)

        varCombo = QComboBox()

        # if self.tabWidget.currentIndex() == 0:
        #     variables = list(self.tower.bracings)
        # elif self.tabWidget.currentIndex() == 1:
        #     variables = list(self.projectSettingsData.sections)

        for tabIndex in range(len(self.tables)):
            if self.tabWidget.currentIndex() == tabIndex:
                vars = list(self.variableDicts[tabIndex])
                for v in vars:
                    varCombo.addItem(v)

                self.IterationTable.setCellWidget(row, 0, varCombo)
                varCombo.setCurrentText(vars[0])
                break

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
            for tabIndex in range(len(self.tables)):
                if self.tabWidget.currentIndex() == tabIndex:
                    newGroup = self.groupDicts[tabIndex][currName]
                    newGroup.variables = []

                    for row in range(self.IterationTable.rowCount()):
                        cell = self.IterationTable.cellWidget(row, 0)
                        if cell != None:
                            varName = cell.currentText()
                            newGroup.variables.append(varName)
            
            # elif self.tabWidget.currentIndex() == 1:
            #     newSG = self.tower.sectionGroups[currName]
            #     newSG.sections = []
            #     for row in range(self.IterationTable.rowCount()):
            #         cell = self.IterationTable.cellWidget(row, 0)
            #         if cell != None:
            #             section = cell.currentText()
            #             newSG.sections.append(section)
    
    def Populate(self):
        column = 0

        for tabIndex in range(len(self.tables)):
            if self.tabWidget.currentIndex() == tabIndex:
                self.tables[tabIndex].setRowCount(0)
                for row, varGroup in enumerate(self.groupDicts[tabIndex]):
                    print('{} group populate'.format(tabIndex))
                    self.tables[tabIndex].insertRow(self.tables[tabIndex].rowCount())
                    groupItem = QTableWidgetItem(varGroup)
                    self.tables[tabIndex].setItem(row, column, groupItem)

        # if self.tabWidget.currentIndex() == 0:
        #     self.bracingGroupTable.setRowCount(0)
        #     for row, bracingGroup in enumerate(self.tower.bracingGroups):
        #         print('bracing group populate')
        #         self.bracingGroupTable.insertRow(self.bracingGroupTable.rowCount())
        #         bgItem = QTableWidgetItem(bracingGroup)
        #         self.bracingGroupTable.setItem(row, column, bgItem)

        # elif self.tabWidget.currentIndex() == 1:
        #     self.sectionGroupTable.setRowCount(0)
        #     for row, sectionGroup in enumerate(self.tower.sectionGroups):
        #         print('section group populate')
        #         self.sectionGroupTable.insertRow(self.sectionGroupTable.rowCount())
        #         sgItem = QTableWidgetItem(sectionGroup)
        #         self.sectionGroupTable.setItem(row, column, sgItem)

    def nameChange(self):
        ''' change group name after it was defined in main table '''
        warning = WarningMessage()

        warningPrefixes = ['Bracing group', 'Section group','Area section group']

        # TODO: replace these loop statements with zip()
        for tabIndex in range(len(self.tables)):
            if self.tabWidget.currentIndex() == tabIndex:
                row = self.tables[tabIndex].currentRow() #returns -1 when repopulating empty table
                print('{} namechange'.format(warningPrefixes[tabIndex]))

                if row != -1 and self.currentNames[tabIndex] != None:
                    newName = self.tables[tabIndex].item(row,0).text()

                    # Error handling -----------------------------
                    # Missing group name
                    if newName == '':
                        warning.popUpErrorBox('{} name is missing.'.format(warningPrefixes[tabIndex]))
                        self.tables[tabIndex].item(row,0).setText(self.currentNames[tabIndex])
                        return

                    # Check name duplicates
                    for groupDict in self.groupDicts:
                        if newName in groupDict:
                            warning.popUpErrorBox('"{}" already exists in {}.'.format(newName, warningPrefixes[tabIndex]))
                            self.tables[tabIndex].item(row,0).setText(self.currentNames[tabIndex])
                            return

                    # Change name while preserving the order
                    groupKeys = list(self.groupDicts[tabIndex].keys())
                    groupValues = list(self.groupDicts[tabIndex].values())

                    self.groupDicts[tabIndex].clear()
                    for i in range(len(groupKeys)):
                        # bracing group to be changed
                        if groupKeys[i] == self.currentNames[tabIndex]:
                            # update the name of group
                            groupValues[i].name = newName
                            # assign original iterations to new name
                            self.groupDicts[tabIndex][newName] = groupValues[i]
                        else:
                            self.groupDicts[tabIndex][groupKeys[i]] = groupValues[i]
                    
                    # match group name to item name in main table
                    self.GroupNameEdit.setText(newName)
                    
                    self.updateScreen()

        # if self.tabWidget.currentIndex() == 0:
        #     row = self.bracingGroupTable.currentRow() #returns -1 when repopulating empty table
        #     print('bracing group namechange')
        #     if row != -1 and self.currentBracingGroupName != None:
        #         newName = self.bracingGroupTable.item(row,0).text()

        #         # Error handling
        #         if newName == '':
        #             warning.popUpErrorBox('Bracing group name is missing.')
        #             self.bracingGroupTable.item(row,0).setText(self.currentBracingGroupName)
        #             return

        #         if newName in self.tower.bracingGroups:
        #             warning.popUpErrorBox('Bracing group name already exists.')
        #             self.bracingGroupTable.item(row,0).setText(self.currentBracingGroupName)
        #             return

        #         # Change name while preserving the order
        #         bgKeys = list(self.tower.bracingGroups.keys())
        #         bgValues = list(self.tower.bracingGroups.values())

        #         self.tower.bracingGroups.clear()
        #         for i in range(len(bgKeys)):
        #             # bracing group to be changed
        #             if bgKeys[i] == self.currentBracingGroupName:
        #                 # update the name of group
        #                 bgValues[i].name = newName
        #                 # assign original iterations to new name
        #                 self.tower.bracingGroups[newName] = bgValues[i]
        #             else:
        #                 self.tower.bracingGroups[bgKeys[i]] = bgValues[i]
                
        #         # match group name to item name in main table
        #         self.GroupNameEdit.setText(newName)
                
        #         self.updateScreen()

        # elif self.tabWidget.currentIndex() == 1:
        #     row = self.sectionGroupTable.currentRow() #returns -1 when repopulating empty table
        #     if row != -1 and self.currentSectionGroupName != None:
        #         newName = self.sectionGroupTable.item(row,0).text()

        #         if newName == '':
        #             warning.popUpErrorBox('Section group name is missing.')
        #             self.sectionGroupTable.item(row,0).setText(self.currentSectionGroupName)
        #             return

        #         if newName in self.tower.sectionGroups:
        #             warning.popUpErrorBox('Section group name already exists.')
        #             self.sectionGroupTable.item(row,0).setText(self.currentSectionGroupName)
        #             return
                
        #         # Change name while preserving the order
        #         sgKeys = list(self.tower.sectionGroups.keys())
        #         sgValues = list(self.tower.sectionGroups.values())

        #         self.tower.sectionGroups.clear()
        #         for i in range(len(sgKeys)):
        #             # section group to be changed
        #             if sgKeys[i] == self.currentSectionGroupName:
        #                 # update the name of group
        #                 sgValues[i].name = newName
        #                 # assign original iterations to new name
        #                 self.tower.sectionGroups[newName] = sgValues[i]
        #             else:
        #                 self.tower.sectionGroups[sgKeys[i]] = sgValues[i]
                
        #         # match group name to item name in main table
        #         self.GroupNameEdit.setText(newName)

        #         self.updateScreen()
    
