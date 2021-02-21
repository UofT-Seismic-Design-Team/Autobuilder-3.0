from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

from WarningMessage import *

class VariableAssignment(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Passing in main.tower into assignment
        self.tower = args[0].tower

        # Load the UI Page
        uic.loadUi('UI/autobuilder_variableassignment.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Add or delete list of assignments
        self.addAssignmentButton.clicked.connect(self.addAssignment)
        self.deleteAssignmentButton.clicked.connect(self.deleteAssignment)

        # Fill in assignment table
        self.displayAssignmentData()

    def addAssignment(self):
        # If currently on Bracing tab:
        if self.tabWidget.currentIndex() == 0:
            row = self.BracingAssignmentTable.rowCount()
            self.BracingAssignmentTable.insertRow(row)
            # Add drop down menu
            bCombo = QComboBox()
            for t in self.tower.bracingGroups.keys():
                bCombo.addItem(t)
            self.BracingAssignmentTable.setCellWidget(row,1,bCombo)
            bCombo.setCurrentText(list(self.tower.bracingGroups.keys())[0])

        elif self.tabWidget.currentIndex() == 1:
            row = self.SectionAssignmentTable.rowCount()
            self.SectionAssignmentTable.insertRow(row)
            # Add drop down menu
            sCombo = QComboBox()
            for t in self.tower.sectionGroups.keys():
                sCombo.addItem(t)
            self.SectionAssignmentTable.setCellWidget(row,1,sCombo)
            sCombo.setCurrentText(list(self.tower.sectionGroups.keys())[0])

    def deleteAssignment(self):
        if self.tabWidget.currentIndex() == 0:
            #indices = self.BracingAssignmentTable.selectionModel().selectedRows()
            indices = self.BracingAssignmentTable.selectionModel().selectedIndexes()
            for index in sorted(indices):
                self.BracingAssignmentTable.removeRow(index.row())

        elif self.tabWidget.currentIndex() == 1:
            #indices = self.SectionAssignmentTable.selectionModel().selectedRows()
            indices = self.SectionAssignmentTable.selectionModel().selectedIndexes()
            for index in sorted(indices):
                self.SectionAssignmentTable.removeRow(index.row())
    
    def setIconsForButtons(self):
        self.addAssignmentButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteAssignmentButton.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def setOkandCancelButtons(self):
        self.OkButton = self.Assignment_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveAssignment)
        self.OkButton.clicked.connect(lambda x: self.close())
        
        self.CancelButton = self.Assignment_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())
    
    # Save bracing design corresponding to each panel
    def saveAssignment(self):
        # Check for duplicates first before clearing
        warning = WarningMessage()

        rowNumB = self.BracingAssignmentTable.rowCount()
        rowNumS = self.SectionAssignmentTable.rowCount()
        tempB = []
        tempS = []

        for i in range(rowNumB):
            panel = self.BracingAssignmentTable.item(i,0).text()
            if panel not in tempB and panel in self.tower.panels.keys():
                tempB.append(panel)
            else:
                warning.popUpErrorBox('Duplicate or non-existent panels!')
                return

        for i in range(rowNumS):
            panel = self.SectionAssignmentTable.item(i,0).text()
            if panel not in tempS and panel in self.tower.panels.keys():
                tempS.append(panel)
            else:
                warning.popUpErrorBox('Duplicate or non-existent panels!')
                return

        # clear all existing assignments
        for panel in self.tower.panels:
            self.tower.panels[panel].bracingGroup = ''
            self.tower.panels[panel].sectionGroup = ''

        for i in range(rowNumB):
            panelItem = self.BracingAssignmentTable.item(i,0)
            bg = self.BracingAssignmentTable.cellWidget(i,1).currentText()
            '''TEST'''
            print(bg)

            # Check if the row is filled
            if panelItem == None or bg == None:
                break
                # warning here?
            panel = panelItem.text()
            self.tower.panels[panel].bracingGroup = bg
        
        
        for i in range(rowNumS):
            panelItem = self.SectionAssignmentTable.item(i,0)
            section = self.SectionAssignmentTable.cellWidget(i,1).currentText()
            # Check if the row is filled
            if panelItem == None or section == None:
                break
            panel = panelItem.text()
            '''TEST'''
            print(section)
            self.tower.panels[panel].sectionGroup = section


    # Display list of bracing designs
    def displayAssignmentData(self):

        #Add warning for non existent bracing or member group
        i = 0
        j = 0
        assignment_rowNumB = self.BracingAssignmentTable.rowCount()
        assignment_rowNumS = self.SectionAssignmentTable.rowCount()
        panels = self.tower.panels

        for panel in panels:
            # Display bracing group table
            if panels[panel].bracingGroup != '':
                # Populate cells
                panelItem = QTableWidgetItem(str(panel))
                #bgItem = QTableWidgetItem(str(panels[panel].bracingGroup))
                bgItem = str(panels[panel].bracingGroup)
                if i >= assignment_rowNumB:
                    self.BracingAssignmentTable.insertRow(i)
                    self.BracingAssignmentTable.setItem(i,0,panelItem)
                    #self.BracingAssignmentTable.setItem(i,1,bgItem)

                    # Set dropdown menu with existing groups
                    bCombo = QComboBox()
                    for t in self.tower.bracingGroups.keys():
                        bCombo.addItem(t)
                    self.BracingAssignmentTable.setCellWidget(i,1,bCombo)
                    bCombo.setCurrentText(bgItem)
                i += 1
            
            # Display section group table
            if panels[panel].sectionGroup != '':
                panelItem = QTableWidgetItem(str(panel))
                #sgItem = QTableWidgetItem(str(panels[panel].sectionGroup))
                sgItem = str(panels[panel].sectionGroup)
                if j >= assignment_rowNumS:
                    self.SectionAssignmentTable.insertRow(j)
                    self.SectionAssignmentTable.setItem(j,0,panelItem)
                    #self.SectionAssignmentTable.setItem(j,1,sgItem)

                    # Set dropdown menu with existing groups
                    sCombo = QComboBox()
                    for t in self.tower.sectionGroups.keys():
                        sCombo.addItem(t)
                    self.SectionAssignmentTable.setCellWidget(j,1,sCombo)
                    sCombo.setCurrentText(sgItem)

                j += 1

        


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