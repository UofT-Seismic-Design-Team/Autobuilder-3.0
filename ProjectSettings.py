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
        self.projectSettingsData = ProjectSettingsData()

        # Load the UI Page
        uic.loadUi('autobuilder_projectsettings_v1.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

        # Elevations table row control
        self.floorElev_add.clicked.connect(lambda x: self.floorElev_table.insertRow(self.floorElev_table.rowCount()))
        self.floorElev_del.clicked.connect(lambda x: self.floorElev_table.removeRow(self.floorElev_table.rowCount()-1))
        
        # Section properties table row control
        self.sectionProp_add.clicked.connect(lambda x: self.sectionProp_table.insertRow(self.sectionProp_table.rowCount()))
        self.sectionProp_del.clicked.connect(lambda x: self.sectionProp_table.removeRow(self.sectionProp_table.rowCount()-1))

        # SAP2000 model location
        self.SAPModelLoc = ''
        self.sapModel_button.clicked.connect(self.saveSAPModelLoc)

    def setProjectSettingsData(self, projectSettingsData):
        self.projectSettingsData = projectSettingsData

    def setIconsForButtons(self):
        self.floorElev_add.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.sectionProp_add.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.floorElev_del.setIcon(QIcon(r"Icons\24x24\minus.png"))
        self.sectionProp_del.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def setOkandCancelButtons(self):
        self.OkButton = self.projectSettings_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.saveProjectSettings)

        self.CancelButton = self.projectSettings_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda signal: self.close())

    def saveSAPModelLoc(self, signal):
        fileInfo = QFileDialog.getOpenFileName(self, 'Open SAP2000 model') # returns a tuple: ('file_name', 'file_type')
        modelLoc = fileInfo[0]
        self.SAPModelLoc = modelLoc

        fileName = modelLoc.split('/')[-1]
        self.projectSettingsData.fileName = fileName
        self.sapModelLoc_label.setText(fileName)

    def displayProjectSettingsData(self):
        data = self.projectSettingsData

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
        self.sapModelLoc_label.setText(data.fileName)

        # Render settings
        self.x_input.setText(str(data.renderX))
        self.y_input.setText(str(data.renderY))
        self.z_input.setText(str(data.renderZ))

    def saveProjectSettings(self, signal):
        warning = WarningMessage()

        # Elevations
        self.projectSettingsData.floorElevs = [] # reset floor elevations

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
                self.projectSettingsData.floorElevs.append(int(elev))
            except:
                warning.popUpWarningBox('Invalid input for elevations')
                return # terminate the saving process

        # Section properties
        self.projectSettingsData.sectionProps = [] # reset section properties

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
                self.projectSettingsData.sectionProps.append(sect)
            except:
                warning.popUpWarningBox('Invalid input for section properties')
                return # terminate the saving process

        # Render settings
        try:
            self.projectSettingsData.renderX = int(self.x_input.text())
            self.projectSettingsData.renderY = int(self.y_input.text())
            self.projectSettingsData.renderZ = int(self.z_input.text())
        except:
            warning.popUpWarningBox('Invalid input for render settings')
            return # terminate the saving process

        # Analysis options
        self.projectSettingsData.groundMotion = self.gm_checkBox.isChecked()
        self.projectSettingsData.analysisType = self.analysisType_comboBox.currentIndex()
        self.projectSettingsData.SAPModelLoc = self.SAPModelLoc

        self.close()

# Enum for Analysis types
class ATYPE:
    TIME_HISTORY = 0
    RSA = 1

# struct to store data for project settings
class ProjectSettingsData:

    def __init__(self):
        self.floorElevs = [6,9,12,15,21,27,33,39,45,51,57,60]
        self.sectionProps = ['BALSA_0.5x0.5','BALSA_0.1875x0.1875']

        # Analysis options
        self.groundMotion = False
        self.analysisType = ATYPE.TIME_HISTORY
        self.SAPModelLoc = ''
        self.fileName = ''

        # Render Settings
        self.renderX = 12
        self.renderY = 12
        self.renderZ = 60
