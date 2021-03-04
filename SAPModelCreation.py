from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5 import uic

from Model import * # tower and other design components
from ProjectSettings import *   # project settings data
from TowerVariation import * # dict of combinations

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

class RunTower(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
  
        # Load the UI Page
        uic.loadUi(r'UI\autobuilder_buildtower.ui', self)

        # Project Settings Data
        self.projectSettingsData = args[0].projectSettingsData

        # Reference to existing tower
        self.tower = args[0].tower

        print(self.tower.inputTable)

        self.buildTowers()

        #self.runAnalysis()

        self.OkButton.clicked.connect(lambda x: self.close())

        # Update views -----------------------------
        self.counter = 0
        timer  = QTimer(self)
        timer.setInterval(10) # period in miliseconds
        timer.timeout.connect(self.addProgress) # updateGL calls paintGL automatically!!
        timer.start()

    def addProgress(self):
        self.counter += 1
        self.progressBar.setValue(self.counter)

    def startSap2000(self):

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
            # attach to a running instance of SAP2000
            try:
                # get the active SapObject
                mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
            except (OSError, comtypes.COMError):
                print("No running instance of the program found or failed to attach.")
                sys.exit(-1)
        else:
            # create API helper object
            helper = comtypes.client.CreateObject('SAP2000v1.Helper')
            helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
            if SpecifyPath:
                try:
                    # 'create an instance of the SAPObject from the specified path
                    mySapObject = helper.CreateObject(ProgramPath)
                except (OSError, comtypes.COMError):
                    print("Cannot start a new instance of the program from " + ProgramPath)
                    sys.exit(-1)
            else:
                try:
                    # create an instance of the SAPObject from the latest installed SAP2000
                    mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
                except (OSError, comtypes.COMError):
                    print("Cannot start a new instance of the program.")
                    sys.exit(-1)
            # start SAP2000 application
            mySapObject.ApplicationStart()
            # create SapModel Object
            SapModel = mySapObject.SapModel
            # initialize model
            SapModel.InitializeNewModel()

            # open model at specified file path in project settings
            ret = SapModel.File.OpenFile(self.projectSettingsData.SAPModelLoc)
        return SapModel

    def buildTowers(self):
        SapModel = self.startSap2000()
        inputTable = self.tower.inputTable
        for i, towerNum in enumerate(inputTable['towerNumber']):
            for key in inputTable:
                if "Panel" in key:
                    bracing = self.tower.bracings[inputTable[key][i]]
                    panel = self.tower.panels[key.strip('Panel ')]
                    self.clearPanel(SapModel, panel)
                    self.buildBracing(SapModel, panel, bracing)
                if "Member" in key:
                    memberID = key.strip('Member ')
                    sectionName = inputTable[key][i]
                    # build members

    def clearPanel(self, SapModel, panel):
        # Deletes all members that are in the panel
        if panel.IDs == ["UNKNOWN"]:
            vec1_x = panel.lowerLeft.x - panel.upperLeft.x
            vec1_y = panel.lowerLeft.y - panel.upperLeft.y
            vec1_z = panel.lowerLeft.z - panel.upperLeft.z
            vec2_x = panel.lowerLeft.x - panel.upperRight.x
            vec2_y = panel.lowerLeft.y - panel.upperRight.y
            vec2_z = panel.lowerLeft.z - panel.upperRight.z
            vec1 = [vec1_x, vec1_y, vec1_z]
            vec2 = [vec2_x, vec2_y, vec2_z]
            norm_vec = numpy.cross(numpy.array(vec1), numpy.array(vec2))

            [number_members, all_member_names, ret] = SapModel.FrameObj.GetNameList()
            # Loop through all members in model
            for member_name in all_member_names:
                # Get member coordinates
                [member_pt1_name, member_pt2_name, ret] = SapModel.FrameObj.GetPoints(member_name)
                if ret != 0:
                    print('ERROR checking member ' + member_name)
                [member_pt1_x, member_pt1_y, member_pt1_z, ret] = SapModel.PointObj.GetCoordCartesian(member_pt1_name)
                if ret != 0:
                    print('ERROR getting coordinate of point ' + member_pt1_name)
                [member_pt2_x, member_pt2_y, member_pt2_z, ret] = SapModel.PointObj.GetCoordCartesian(member_pt2_name)
                if ret != 0:
                    print('ERROR getting coordinate of point ' + member_pt2_name)

                # Round the member coordinates
                max_decimal_places = 6
                member_pt1_x = round(member_pt1_x, max_decimal_places)
                member_pt1_y = round(member_pt1_y, max_decimal_places)
                member_pt1_z = round(member_pt1_z, max_decimal_places)
                member_pt2_x = round(member_pt2_x, max_decimal_places)
                member_pt2_y = round(member_pt2_y, max_decimal_places)
                member_pt2_z = round(member_pt2_z, max_decimal_places)

                # Check if the member is within the elevation of the panel
                panel_max_z = max(panel.lowerLeft.z, panel.upperLeft.z, panel.upperRight.z, panel.lowerRight.z)
                panel_min_z = min(panel.lowerLeft.z, panel.upperLeft.z, panel.upperRight.z, panel.lowerRight.z)
                if member_pt1_z <= panel_max_z and member_pt1_z >= panel_min_z and member_pt2_z <= panel_max_z and member_pt2_z >= panel_min_z:
                    member_vec_x = member_pt2_x - member_pt1_x
                    member_vec_y = member_pt2_y - member_pt1_y
                    member_vec_z = member_pt2_z - member_pt1_z
                    member_vec = [member_vec_x, member_vec_y, member_vec_z]

                    # Check if member is in the same plane as the panel
                    if numpy.dot(member_vec, norm_vec) == 0:
                        # To do this, check if the vector between a member point and a plane point is parallel to plane
                        test_vec = [member_pt1_x - panel.lowerLeft.x, member_pt1_y - panel.lowerLeft.y,
                                    member_pt1_z - panel.lowerLeft.z]
                        if numpy.dot(test_vec, norm_vec) == 0:
                            # Check if the member lies within the limits of the panel
                            # First, transform the frame of reference since Shapely only works in 2D
                            # Create unit vectors
                            ref_vec_1 = vec1
                            ref_vec_2 = numpy.cross(ref_vec_1, norm_vec)
                            # Project each point defining the panel onto each reference vector
                            point1=[panel.lowerLeft.x, panel.lowerLeft.y, panel.lowerLeft.z]
                            point2=[panel.upperLeft.x, panel.upperLeft.y, panel.upperLeft.z]
                            point3=[panel.upperRight.x, panel.upperRight.y, panel.upperRight.z]
                            point4=[panel.lowerRight.x, panel.lowerRight.y, panel.lowerRight.z]
                            panel_pt1_trans_1 = numpy.dot(point1, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            panel_pt1_trans_2 = numpy.dot(point1, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            panel_pt2_trans_1 = numpy.dot(point2, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            panel_pt2_trans_2 = numpy.dot(point2, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            panel_pt3_trans_1 = numpy.dot(point3, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            panel_pt3_trans_2 = numpy.dot(point3, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            panel_pt4_trans_1 = numpy.dot(point4, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            panel_pt4_trans_2 = numpy.dot(point4, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            # Project each point defining the member onto the reference vector
                            member_pt1 = [member_pt1_x, member_pt1_y, member_pt1_z]
                            member_pt2 = [member_pt2_x, member_pt2_y, member_pt2_z]
                            member_pt1_trans_1 = numpy.dot(member_pt1, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            member_pt1_trans_2 = numpy.dot(member_pt1, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            member_pt2_trans_1 = numpy.dot(member_pt2, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            member_pt2_trans_2 = numpy.dot(member_pt2, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            # Create shapely geometries to check if member is in the panel
                            poly_coords = [(panel_pt1_trans_1, panel_pt1_trans_2),
                                           (panel_pt2_trans_1, panel_pt2_trans_2),
                                           (panel_pt3_trans_1, panel_pt3_trans_2),
                                           (panel_pt4_trans_1, panel_pt4_trans_2)]
                            member_coords = [(member_pt1_trans_1, member_pt1_trans_2),
                                             (member_pt2_trans_1, member_pt2_trans_2)]
                            panel_shapely = shapely.geometry.Polygon(poly_coords)
                            member_shapely = shapely.geometry.LineString(member_coords)
                            # Delete member if it is inside the panel
                            if member_shapely.intersects(panel_shapely) == True and member_shapely.touches(
                                    panel_shapely) == False:
                                ret = SapModel.FrameObj.Delete(member_name, 0)
            panel.IDs = []

        else:
            # Delete members that are contained in the panel
            for memberID in panel.IDs:
                ret = SapModel.FrameObj.Delete(memberID, 0)
                if ret != 0:
                    print('ERROR deleting member ' + memberID)
            panel.IDs = []

    def buildBracing(self, SapModel, panel, bracing):
        if panel.IDs == ["UNKNOWN"]:
            self.clearPanel(SapModel, panel)
        for member in bracing.members:
            node1 = member.start_node
            node2 = member.end_node
            section = member.material
            # Scale the member start and end points to fit the panel location and dimensions
            # Get unit vectors to define the panel
            panel_vec_horiz_x = panel.lowerRight.x - panel.lowerLeft.x
            panel_vec_horiz_y = panel.lowerRight.y - panel.lowerLeft.y
            panel_vec_horiz_z = panel.lowerRight.z - panel.lowerLeft.z
            panel_vec_vert_x = panel.upperRight.x - panel.lowerRight.x
            panel_vec_vert_y = panel.upperRight.y - panel.lowerRight.y
            panel_vec_vert_z = panel.upperRight.z - panel.lowerRight.z
            panel_vec_horiz = [panel_vec_horiz_x, panel_vec_horiz_y, panel_vec_horiz_z]
            panel_vec_vert = [panel_vec_vert_x, panel_vec_vert_y, panel_vec_vert_z]
            # Get the scaled start and end coordinates for the member
            # Translate point "horizontally" and "vertically"
            start_node_x = panel.lowerLeft.x + node1.x * panel_vec_horiz[0] + node1.y * panel_vec_vert[0]
            start_node_y = panel.lowerLeft.y + node1.x * panel_vec_horiz[1] + node1.y * panel_vec_vert[1]
            start_node_z = panel.lowerLeft.z + node1.x * panel_vec_horiz[2] + node1.y * panel_vec_vert[2]
            end_node_x = panel.lowerLeft.x + node2.x * panel_vec_horiz[0] + node2.y * panel_vec_vert[0]
            end_node_y = panel.lowerLeft.y + node2.x * panel_vec_horiz[1] + node2.y * panel_vec_vert[1]
            end_node_z = panel.lowerLeft.z + node2.x * panel_vec_horiz[2] + node2.y * panel_vec_vert[2]
            # Create the member
            [member_name, ret] = SapModel.FrameObj.AddByCoord(start_node_x, start_node_y, start_node_z, end_node_x,
                                                              end_node_y, end_node_z, PropName=section)
            if ret != 0:
                print('ERROR building member in panel')
            panel.IDs.append(member_name)