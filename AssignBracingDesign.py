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
        
        # Passing in main.tower into assignment
        self.tower = args[0].tower

        # Load the UI Page
        uic.loadUi('UI/autobuilder_assignbracingdesign.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Fill in assignment table
        self.displayAssignmentData()

        '''
        Set right-click dropdown menu (to be implemented)
        #self.setContextMenu()
        '''

    # Save bracing design corresponding to each panel
    def saveAssignment(self):
        
        self.tower.assignments.clear() # reset assignment properties

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
                self.tower.assignments[panel] = bracing
            except:
                warning.popUpErrorBox('Invalid input for assignment properties')
                return # terminate the saving process

    # Display list of bracing designs
    def displayAssignmentData(self):

        i = 0
        assignment_rowNum = self.AssignmentTable.rowCount()

        for panel in self.tower.panels:

            panelItem = QTableWidgetItem(str(panel))
            if i >= assignment_rowNum:
                self.AssignmentTable.insertRow(i)
            self.AssignmentTable.setItem(i,0,panelItem)
            
            if panel in self.tower.assignments.keys():
                bracingItem = QTableWidgetItem(self.tower.assignments[panel].bracingGroup)
                self.AssignmentTable.setItem(i,1,bracingItem)

            else:
                TBD = QTableWidgetItem('TBD')
                self.AssignmentTable.setItem(i,1,TBD)
            
            i += 1

    def setIconsForButtons(self):
        self.addAssignmentButton.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.deleteAssignmentButton.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def setOkandCancelButtons(self):
        self.OkButton = self.Assignment_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveAssignment)

        self.OkButton.clicked.connect(lambda x: self.close())
        
        self.CancelButton = self.Assignment_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())

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