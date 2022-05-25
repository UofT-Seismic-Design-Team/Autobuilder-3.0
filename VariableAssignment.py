from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

import resources    # For icons and UIs

from Message import *

class VariableAssignment(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Passing in main.tower into assignment
        self.tower = args[0].tower

        # Load the UI Page
        fileh = QFile(':/UI/autobuilder_variableassignment.ui')
        fileh.open(QFile.ReadOnly)
        uic.loadUi(fileh, self)
        fileh.close()

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Data
        self.tables = [self.BracingAssignmentTable, self.SectionAssignmentTable, self.AreaSectionAssignmentTable]
        self.groupDicts = [self.tower.bracingGroups,self.tower.sectionGroups,self.tower.areaSectionGroups]

        # Add or delete list of assignments
        self.addAssignmentButton.clicked.connect(self.addAssignment)
        self.deleteAssignmentButton.clicked.connect(self.deleteAssignment)

        self.importCSVButton.clicked.connect(self.readcsv)

        # Fill in assignment table
        self.displayAssignmentData()

    def addAssignment(self):
        for tabIndex in range(len(self.tables)):
            # If currently on tab:
            if self.tabWidget.currentIndex() == tabIndex:
                table = self.tables[tabIndex]
                groupDict = self.groupDicts[tabIndex]

                row = table.rowCount()
                table.insertRow(row)
                # Add drop down menu
                combo = QComboBox()
                for t in groupDict.keys():
                    combo.addItem(t)

                table.setCellWidget(row,1,combo)
                combo.setCurrentText(list(groupDict.keys())[0])

                # Default name is row number
                table.setItem(row,0, QTableWidgetItem(str(row+1)))

        # if self.tabWidget.currentIndex() == 0:
        #     row = self.BracingAssignmentTable.rowCount()
        #     self.BracingAssignmentTable.insertRow(row)
        #     # Add drop down menu
        #     bCombo = QComboBox()
        #     for t in self.tower.bracingGroups.keys():
        #         bCombo.addItem(t)
        #     self.BracingAssignmentTable.setCellWidget(row,1,bCombo)
        #     bCombo.setCurrentText(list(self.tower.bracingGroups.keys())[0])

        #     # Default panel name is row number
        #     self.BracingAssignmentTable.setItem(row,0, QTableWidgetItem(str(row+1)))

        # elif self.tabWidget.currentIndex() == 1:
        #     row = self.SectionAssignmentTable.rowCount()
        #     self.SectionAssignmentTable.insertRow(row)
        #     # Add drop down menu
        #     sCombo = QComboBox()
        #     for t in self.tower.sectionGroups.keys():
        #         sCombo.addItem(t)
        #     self.SectionAssignmentTable.setCellWidget(row,1,sCombo)
        #     sCombo.setCurrentText(list(self.tower.sectionGroups.keys())[0])

    def deleteAssignment(self):
        for tabIndex in range(len(self.tables)):
            if self.tabWidget.currentIndex() == tabIndex:
                table = self.tables[tabIndex]

                indices = table.selectionModel().selectedRows()
                for i, index in enumerate(sorted(indices)):
                    updatedRow = index.row()-i
                    table.removeRow(updatedRow)

        # if self.tabWidget.currentIndex() == 0:
        #     indices = self.BracingAssignmentTable.selectionModel().selectedRows()
        #     for i, index in enumerate(sorted(indices)):
        #         updatedRow = index.row()-i
        #         self.BracingAssignmentTable.removeRow(updatedRow)

        # elif self.tabWidget.currentIndex() == 1:
        #     indices = self.SectionAssignmentTable.selectionModel().selectedRows()
        #     for i, index in enumerate(sorted(indices)):
        #         updatedRow = index.row()-i
        #         self.SectionAssignmentTable.removeRow(updatedRow)
    
    def setIconsForButtons(self):
        self.addAssignmentButton.setIcon(QIcon(':/Icons/plus.png'))
        self.deleteAssignmentButton.setIcon(QIcon(':/Icons/minus.png'))

    def setOkandCancelButtons(self):
        self.OkButton = self.Assignment_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveAssignment)
        
        self.CancelButton = self.Assignment_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())
    
    # Save bracing design corresponding to each panel
    def saveAssignment(self):
        # Check for duplicates first before clearing
        warning = WarningMessage()

        rowNumB = self.BracingAssignmentTable.rowCount()
        rowNumS = self.SectionAssignmentTable.rowCount()
        rowNumAS = self.AreaSectionAssignmentTable.rowCount()
        tempB = []
        tempS = []
        tempAS = []

        # Bracing
        for i in range(rowNumB):
            panelInput = self.BracingAssignmentTable.item(i,0)

            panel = ''
            if panelInput:
                panel = panelInput.text()

            if panel not in tempB and panel in self.tower.panels.keys():
                tempB.append(panel)
            else:
                warning.popUpErrorBox('Duplicate or non-existent panels!')
                return

        # Member section
        for i in range(rowNumS):
            member_idInput = self.SectionAssignmentTable.item(i,0)

            if member_idInput:
                member_id = member_idInput.text()
            else:
                member_id = ''

            if member_id not in tempS:
                tempS.append(member_id)
            else:
                warning.popUpErrorBox('Duplicate or non-existent members!')
                return

        # Area section
        for i in range(rowNumAS):
            panelInput = self.AreaSectionAssignmentTable.item(i,0)

            panel = ''
            if panelInput:
                panel = panelInput.text()

            if panel not in tempAS and panel in self.tower.panels.keys():
                tempAS.append(panel)
            else:
                warning.popUpErrorBox('Duplicate or non-existent panels!')
                return

        # clear all existing assignments ---------------------------
        for panel in self.tower.panels:
            self.tower.panels[panel].bracingGroup = ''
            self.tower.panels[panel].areaSectionGroup = ''

        self.tower.member_ids.clear()

        # update panels and member ids --------------------------------
        for i in range(rowNumB):
            panelItem = self.BracingAssignmentTable.item(i,0)
            bg = self.BracingAssignmentTable.cellWidget(i,1).currentText()

            # Check if the row is filled
            if panelItem == None or bg == None:
                break
                # warning here?
            panel = panelItem.text()
            self.tower.panels[panel].addBracingAssignment(bg)
        
        for i in range(rowNumS):
            member_idItem = self.SectionAssignmentTable.item(i,0)
            sg = self.SectionAssignmentTable.cellWidget(i,1).currentText()

            # Check if the row is filled
            if member_idItem == None or sg == None:
                break
            member_id = member_idItem.text()
            '''TEST'''
            self.tower.member_ids[member_id] = sg

        for i in range(rowNumAS):
            panelItem = self.AreaSectionAssignmentTable.item(i,0)
            asg = self.AreaSectionAssignmentTable.cellWidget(i,1).currentText()

            # Check if the row is filled
            if panelItem == None or asg == None:
                break

            panel = panelItem.text()
            self.tower.panels[panel].addAreaSectionAssignment(asg)

        print('panel', panel,  self.tower.panels[panel].areaSectionGroup)

        self.close()    # close only if the saving process is completed successfully

    # Display list of bracing designs
    def displayAssignmentData(self):

        #Add warning for non existent bracing or member group
        i = j = k =0
        assignment_rowNumB = self.BracingAssignmentTable.rowCount()
        assignment_rowNumS = self.SectionAssignmentTable.rowCount()
        assignment_rowNumAS = self.AreaSectionAssignmentTable.rowCount()

        panels = self.tower.panels
        member_ids = self.tower.member_ids

        for panel in panels:
            # Display bracing group table
            if panels[panel].bracingGroup != '':
                # Populate cells
                panelItem = QTableWidgetItem(str(panel))
                bgItem = str(panels[panel].bracingGroup)
                if i >= assignment_rowNumB:
                    self.BracingAssignmentTable.insertRow(i)
                    self.BracingAssignmentTable.setItem(i,0,panelItem)

                    # Set dropdown menu with existing groups
                    bCombo = QComboBox()
                    for t in self.tower.bracingGroups.keys():
                        bCombo.addItem(t)
                    self.BracingAssignmentTable.setCellWidget(i,1,bCombo)
                    bCombo.setCurrentText(bgItem)
                i += 1

            # Display area section group table
            if panels[panel].areaSectionGroup != '':
                # Populate cells
                panelItem = QTableWidgetItem(str(panel))
                asgItem = str(panels[panel].areaSectionGroup)
                if k >= assignment_rowNumAS:
                    self.AreaSectionAssignmentTable.insertRow(k)
                    self.AreaSectionAssignmentTable.setItem(k,0,panelItem)

                    # Set dropdown menu with existing groups
                    asCombo = QComboBox()
                    for t in self.tower.areaSectionGroups.keys():
                        asCombo.addItem(t)
                    self.AreaSectionAssignmentTable.setCellWidget(k,1,asCombo)
                    asCombo.setCurrentText(asgItem)
                k += 1
        
        for member_id in member_ids:
            # Display section group table
            if member_id != '':
                member_idItem = QTableWidgetItem(str(member_id))
                sgItem = str(member_ids[member_id])
                if j >= assignment_rowNumS:
                    self.SectionAssignmentTable.insertRow(j)
                    self.SectionAssignmentTable.setItem(j,0,member_idItem)

                    # Set dropdown menu with existing groups
                    sCombo = QComboBox()
                    for t in self.tower.sectionGroups.keys():
                        sCombo.addItem(t)
                    self.SectionAssignmentTable.setCellWidget(j,1,sCombo)
                    sCombo.setCurrentText(sgItem)

                j += 1

    def readcsv(self, s):
        fileInfo = QFileDialog.getOpenFileName(self, "Open File", "variable assignment.csv", "Comma-Separated Values files (*.csv)")
        fileLoc = fileInfo[0]

        if fileLoc == '': # No action if no file was selected
            return

        for tabIndex in range(len(self.tables)):
            if self.tabWidget.currentIndex() == tabIndex:
                table = self.tables[tabIndex]
                variables = list(self.groupDicts[tabIndex].keys())
                break

        # reset in table
        table.setRowCount(0)

        with open(fileLoc, 'r' , encoding='utf-8-sig') as file:
            lines = file.readlines()

            for line in lines:
                data = line.rstrip('\n').split(',') # remove trailing newline

                if len(data) < 2:
                    warning = WarningMessage()
                    warning.popUpErrorBox('Imported file is not formatted correctly')
                    return

                subject = data[0]
                assignedVariable = data[1]
                if not (assignedVariable in variables):
                    assignedVariable = variables[0]

                row = table.rowCount()
                table.insertRow(row)

                table.setItem(row,0,QTableWidgetItem(subject))

                combo = QComboBox()
                for v in variables:
                    combo.addItem(v)
                table.setCellWidget(row,1,combo)
                combo.setCurrentText(assignedVariable)

    '''
    def setContextMenu(self):
        self.AssignmentTable.setContextMenuPolicy(Qt.ActionsContextMenu)
        #self.AssignmentTable.customContextMenuRequested.connect(self._show_context_menu)
        #self._contextMenu = QMenu()

        # dropdown menu
        self.AssignmentTable.addAction(pasteAction)

    
    def paste(self):
        model=self.AssignmentTable()
        pasteString=QtGui.QApplication.clipboard().text()

        rows=pasteString.split('\n')
        numRows=len(rows)
        numCols=rows[0].count('\t')+1

        selectionRanges=self.selectionModel().selection()

        #make sure we only have one selection range and not non-contiguous selections
        if len(selectionRanges)==1:
            topLeftIndex=selectionRanges[0].topLeft()
            selColumn=topLeftIndex.column()
            selRow=topLeftIndex.row()
            if selColumn+numCols>model.columnCount():
                #the number of columns we have to paste, starting at the selected cell, go beyond how many columns exist.
                #insert the amount of columns we need to accomodate the paste
                model.insertColumns(model.columnCount(), numCols-(model.columnCount()-selColumn))

            if selRow+numRows>model.rowCount():
                #the number of rows we have to paste, starting at the selected cell, go beyond how many rows exist.
                #insert the amount of rows we need to accomodate the paste
                model.insertRows(model.rowCount(), numRows-(model.rowCount()-selRow))

            #block signals so that the "dataChanged" signal from setData doesn't update the view for every cell we set
            model.blockSignals(True)  

            for row in xrange(numRows):
                columns=rows[row].split('\t')

                [model.setData(model.createIndex(selRow+row, selColumn+col), QVariant(columns[col])) for col in xrange(len(columns))]

            #unblock the signal and emit dataChangesd ourselves to update all the view at once
            model.blockSignals(False)
            model.dataChanged.emit(topLeftIndex, model.createIndex(selRow+numRows, selColumn+numCols))
 
# Store list of bracing designs corresponding to each panel
class AssignmentData:
    def __init__(self):
        self.panels = []
        self.possibleBracings = {}
        self.assignments = {}
'''