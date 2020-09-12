from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import uic

import sys  # We need sys so that we can pass argv to QApplication
import os

class ProjectSettings(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('UI/autobuilder_floordesign_v1.ui', self)

        # Set UI Elements
        self.setIconsForButtons()
        self.setOkandCancelButtons()

    def setIconsForButtons(self):
        self.Add.setIcon(QIcon(r"Icons\24x24\plus.png"))
        self.Delete.setIcon(QIcon(r"Icons\24x24\minus.png"))

    def setOkandCancelButtons(self):
        self.OkButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Ok)
        self.OkButton.clicked.connect(lambda x: self.close())

        self.CancelButton = self.FloorPlan_buttonBox.button(QDialogButtonBox.Cancel)
        self.CancelButton.clicked.connect(lambda x: self.close())