from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5 import uic

import Model    # contains tower design components
import ProjectSettings  # contains data in project settings
from Definition import *    # file extensions, EnumToString conversion
import pandas as pd  # use data frame to write files

import os
import sys
import comtypes.client
import comtypes.gen

import win32com.client
import random
import re
import time
import scipy
import numpy
from scipy.stats import norm
import datetime
import matplotlib.pyplot as plt
import shapely.geometry

class BuildTower(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
  
        # Load the UI Page
        uic.loadUi(r'UI\autobuilder_buildtower.ui', self)

        self.tower = args[0].tower
        self.fileLoc = args[0].fileLoc

        self.counter = 0

        # redundant; may be useful later
        #self.inputTable = {}    # keys: "tower", panel, member id; values: num, bracing, section
        #self.combos = () # all combinations of the variables

        self.buildTowers()
        self.runAnalysis()

        self.OkButton.clicked.connect(lambda x: self.close())

        # Update views -----------------------------
        timer  = QTimer(self)
        timer.setInterval(10) # period in miliseconds
        timer.timeout.connect(self.addProgress) # updateGL calls paintGL automatically!!
        timer.start()

        #set the following flag to True to attach to an existing instance of the program
        #otherwise a new instance of the program will be started
        AttachToInstance = False

        #set the following flag to True to manually specify the path to SAP2000.exe
        #this allows for a connection to a version of SAP2000 other than the latest installation
        #otherwise the latest installed version of SAP2000 will be launched
        SpecifyPath = True

        #if the above flag is set to True, specify the path to SAP2000 below
        ProgramPath = 'C:\Program Files\Computers and Structures\SAP2000 22\SAP2000.exe'

        if AttachToInstance:
            #attach to a running instance of SAP2000
            try:
                #get the active SapObject
                SapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")

            except (OSError, comtypes.COMError):
                print("No running instance of the program found or failed to attach.")
                sys.exit(-1)
        else:
            #create API helper object
            helper = comtypes.client.CreateObject('SAP2000v1.Helper')
            helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
            if SpecifyPath:
                try:
                    #'create an instance of the SAPObject from the specified path
                    SapObject = helper.CreateObject(ProgramPath)

                except (OSError, comtypes.COMError):
                    print("Cannot start a new instance of the program from " + ProgramPath)
                    sys.exit(-1)
            else:
                try:
                    #create an instance of the SAPObject from the latest installed SAP2000
                    SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")

                except (OSError, comtypes.COMError):
                    print("Cannot start a new instance of the program.")
                    sys.exit(-1)

            #start SAP2000 application
            SapObject.ApplicationStart()

        # start SAP2000
        SapModel = SapObject.SapModel

    def addProgress(self):
        self.counter += 1
        self.progressBar.setValue(self.counter)