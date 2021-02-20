from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

from Model import *

from Message import *

import sys  # We need sys so that we can pass argv to QApplication
import os

class DisplaySettingsUI(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi(r'UI\autobuilder_displaysettings_v1.ui', self)

        # Reference to existing tower for cache
        self.displaySettingsRef = args[0].tower.displaySettings

        self.populate()

        # Set UI Elements
        self.setOkandCancelButtons()

    def setOkandCancelButtons(self):
        self.OkButton = self.displaySettings_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(self.save)

        self.CancelButton = self.displaySettings_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda signal: self.close())

    def populate(self):
        self.pName_checkBox.setChecked(self.displaySettingsRef.pName)
        self.pLength_checkBox.setChecked(self.displaySettingsRef.pLength)

    def save(self):
        self.displaySettingsRef.pName = self.pName_checkBox.isChecked()
        self.displaySettingsRef.pLength = self.pLength_checkBox.isChecked()

# Struct for display settings
class DisplaySettings:
    def __init__(self):
        # 2D view
        self.pName = True
        self.pLength = False
