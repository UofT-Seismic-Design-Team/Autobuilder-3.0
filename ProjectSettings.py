from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

from Model import *

from WarningMessage import *

import sys  # We need sys so that we can pass argv to QApplication
import os

class ProjectSettings(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Project Settings Data
        self.data = ProjectSettingsData()

        # Tower
        self.tower = Tower()

        # Load the UI Page
        uic.loadUi(r'UI\autobuilder_projectsettings_v1.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Elevations table row control
        self.floorElev_add.clicked.connect(lambda x: self.floorElev_table.insertRow(self.floorElev_table.rowCount()))
        self.floorElev_del.clicked.connect(lambda x: self.floorElev_table.removeRow(self.floorElev_table.rowCount()-1))
        
        # Control saving process
        self.saveElevs = False

        # Section properties table row control
        self.sectionProp_add.clicked.connect(lambda x: self.sectionProp_table.insertRow(self.sectionProp_table.rowCount()))
        self.sectionProp_del.clicked.connect(lambda x: self.sectionProp_table.removeRow(self.sectionProp_table.rowCount()-1))

        # SAP2000 model location
        self.SAPModelLoc = ''
        self.sapModel_button.clicked.connect(self.saveSAPModelLoc)

    def setData(self, data):
        self.data = data

    def setTower(self, tower):
        self.tower = tower

    def setIconsForButtons(self):
        self.floorElev_add.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.sectionProp_add.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.floorElev_del.setIcon(QIcon(r"Icons\24x24\minus.png"))
        self.sectionProp_del.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def setOkandCancelButtons(self):
        self.OkButton = self.projectSettings_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.save)

        self.CancelButton = self.projectSettings_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda signal: self.close())

    def saveSAPModelLoc(self, signal):
        fileInfo = QFileDialog.getOpenFileName(self, 'Open SAP2000 model', '', 'SAP2000 files (*.sdb)') # returns a tuple: ('file_name', 'file_type')
        modelLoc = fileInfo[0]
        self.SAPModelLoc = modelLoc

        modelName = modelLoc.split('/')[-1]
        self.sapModelLoc_label.setText(modelName)

    def display(self):
        
        data = self.data

        # Elevations
        i = 0
        floorElev_rowNum = self.floorElev_table.rowCount()
        for elev in data.floorElevs:
            item = QTableWidgetItem(str(elev))
            if i >= floorElev_rowNum:
                self.floorElev_table.insertRow(i)
            self.floorElev_table.setItem(i,0,item)
            i += 1

        # Section properties
        i = 0
        sectionProp_rowNum = self.sectionProp_table.rowCount()
        for sect in data.sectionProps:
            item = QTableWidgetItem(str(sect))
            if i >= sectionProp_rowNum:
                self.sectionProp_table.insertRow(i)
            self.sectionProp_table.setItem(i,0,item)
            i += 1

        # Analysis options
        self.gm_checkBox.setChecked(data.groundMotion)
        self.analysisType_comboBox.setCurrentIndex(data.analysisType)
        self.SAPModelLoc = data.SAPModelLoc
        self.sapModelLoc_label.setText(data.modelName)

        # Render settings
        self.x_input.setText(str(data.renderX))
        self.y_input.setText(str(data.renderY))
        self.z_input.setText(str(data.renderZ))

    def save(self, signal):
        warning = WarningMessage()

        # Elevations
        prev_floorElevs = list(self.data.floorElevs)

        tempElevs = []
        rowNum = self.floorElev_table.rowCount()
        for i in range(rowNum):
            elevItem = self.floorElev_table.item(i,0)
            # Check if the item exists
            if elevItem == None:
                break
            elev = elevItem.text()
            # Check if the item is filled
            try:
                if elev == '':
                    break
                tempElevs.append(float(elev))
            except:
                warning.popUpErrorBox('Invalid input for elevations')
                return # terminate the saving process

        # Check if floor elevations are modified
        cancelSaving = False
        if tempElevs != prev_floorElevs:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Warning")
            msg.setInformativeText('Current model data will be deleted as floor elevations are modified')
            msg.setWindowTitle("Warning")

            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            OkButton = msg.button(QMessageBox.Ok)
            OkButton.clicked.connect(self.saveElevations)
            OkButton.clicked.connect(lambda s: msg.close())

            CancelButton = msg.button(QMessageBox.Cancel)
            CancelButton.clicked.connect(lambda s: msg.close())

            msg.exec_()

            # if the Ok button was clicked, redefine floors and floor elevations
            if self.saveElevs:
                # clear data stored in project settings and tower (except for floor plans)
                self.data.floorElevs.clear()
                self.tower.elevations.clear()
                self.tower.floors.clear()
                self.tower.columns.clear()
                self.tower.panels.clear()
                self.tower.faces.clear()

                for elev in tempElevs:
                    self.data.floorElevs.append(elev) # will update elevations in tower object simultaneously
                
                self.tower.defineFloors()
            else:
                return # terminate the saving process

        # Section properties
        self.data.sectionProps.clear() # reset section properties

        rowNum = self.sectionProp_table.rowCount()
        for i in range(rowNum):
            sectItem = self.sectionProp_table.item(i,0)
            # Check if the row is filled
            if sectItem == None:
                break
            sect = sectItem.text()
            try:
                # Check if the item is filled
                if sect == '':
                    break
                self.data.sectionProps.append(sect)
            except:
                warning.popUpErrorBox('Invalid input for section properties')
                return # terminate the saving process

        # Render settings
        try:
            self.data.renderX = float(self.x_input.text())
            self.data.renderY = float(self.y_input.text())
            self.data.renderZ = float(self.z_input.text())
        except:
            warning.popUpErrorBox('Invalid input for render settings')
            return # terminate the saving process

        # Analysis options
        self.data.groundMotion = self.gm_checkBox.isChecked()
        self.data.analysisType = self.analysisType_comboBox.currentIndex()
        self.data.SAPModelLoc = self.SAPModelLoc
        self.data.modelName = self.sapModelLoc_label.text()

        self.close()

    def saveElevations(self, s):
        self.saveElevs = True

# Enum for Analysis types
class ATYPE:
    TIME_HISTORY = 0
    RSA = 1

# struct to store data for project settings
class ProjectSettingsData:

    def __init__(self):
        self.floorElevs = [0.0,6.0,9.0,12.0,15.0,21.0,27.0,33.0,39.0,45.0,51.0,57.0,60.0]
        self.sectionProps = ['BALSA_0.5x0.5','BALSA_0.1875x0.1875']

        # Analysis options
        self.groundMotion = False
        self.analysisType = ATYPE.TIME_HISTORY
        self.SAPModelLoc = ''
        self.modelName = ''

        # Render Settings
        self.renderX = 12
        self.renderY = 12
        self.renderZ = 60
