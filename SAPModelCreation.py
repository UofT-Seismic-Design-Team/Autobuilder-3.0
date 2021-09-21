from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5 import uic

from Model import * # tower and other design components
from ProjectSettings import *   # project settings data
from TowerVariation import * # dict of combinations
from Performance import * # results
from FileWriter import *
from Plot import * # For graphs and plots

from Definition import *    # file extensions, EnumToString conversion

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
from skimage.transform import ProjectiveTransform

class RunTower(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mainFileLoc = args[0].fileLoc
        self.folderLoc = self.mainFileLoc.replace('.ab', '')
        self.SAPFolderLoc = self.folderLoc + FileExtension.SAPModels

        # Create new directory for data
        try:
            os.mkdir(self.SAPFolderLoc)
        except:
            pass
  
        # Load the UI Page
        fileh = QFile(':/UI/autobuilder_buildtower.ui')
        fileh.open(QFile.ReadOnly)
        uic.loadUi(fileh, self)
        fileh.close()
        
        # Store Variables From Run Towers Dialog
        self.SAPPath = args[0].SAPPath
        self.nodesList = args[0].nodesList
        self.footprint = args[0].footprint
        self.totalHeight = args[0].totalHeight
        self.totalMass = args[0].totalMass
        
        # Project Settings Data
        self.projectSettingsData = args[0].projectSettingsData

        # Reference to existing tower
        self.tower = args[0].tower

        # Members to be divided at intersections
        self.membersToDivide = []

        # TODO: allow user input
        self.costCalcIdentifier = 'GM1'
        self.footprint = 144
        self.totalHeight = [60] # inches
        self.totalMass = [7.83] # kg

        # Tower performances
        self.towerPerformances = {}

        self.runGMs = self.projectSettingsData.groundMotion

        # Start scatter plot of tower performance
        xlabel = 'Tower Number'
        if self.runGMs:
            ylabel = 'Total Cost'
        else:
            ylabel = 'Period'
        self.plotter = Plotter(xlabel, ylabel)
        self.plotter.show()

        # Establish alternate thread to run SAP2000
        self.threadpool = QThreadPool()
        sapRunnable = SAPRunnable(self)
        self.threadpool.start(sapRunnable)

        self.OkButton.clicked.connect(lambda x: self.close())

    def addProgress(self):
        self.counter += 1
        self.progressBar.setValue(self.counter)

    def resetProgress(self, max):
        self.counter = 0
        self.progressBar.setValue(self.counter)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(max)

    def buildTowers(self):
        SapModel = self.startSap2000()

        # Delete all members within the plans and build correct bracing scheme
        SapModel.SetPresentUnits(SAP2000Constants.Units['kip_in_F'])

        inputTable = self.tower.inputTable
        self.resetProgress(len(inputTable['towerNumber']))
        for i, towerNum in enumerate(inputTable['towerNumber']):
            self.addProgress()

            SapModel.SetModelIsLocked(False)
            SapModel.SetPresentUnits(SAP2000Constants.Units['kip_in_F'])

            # Define tower performance object to store results
            towerPerformance = TowerPerformance(str(towerNum))

            for key in inputTable:
                if "Panel" in key:
                    bracing = self.tower.bracings[inputTable[key][i]]
                    panel = self.tower.panels[key.strip('Panel ')]
                    self.clearPanel(SapModel, panel)
                    self.buildBracing(SapModel, panel, bracing)

                # TODO: update member later
                if "Member" in key:
                    memberID = key.strip('Member ')
                    sectionName = inputTable[key][i]
                    # build members
                    self.changeMemberSection(SapModel, memberID, sectionName)

                if "Variable-" in key:
                    variableName = key.strip('Variable-')
                    assignedValue = inputTable[key][i]

                    towerPerformance.addVariable(variableName, assignedValue)
            
            print('round coordinates...')
            self.roundingModelCoordinates(SapModel)
            #self.divideMembersAtIntersection(SapModel)

            # Save the file
            SAPFileLoc = self.SAPFolderLoc + os.sep + 'Tower ' + str(towerNum) + '.sdb'
            print(SAPFileLoc)
            SapModel.File.Save(SAPFileLoc)

            # Analyse tower and print results to spreadsheet
            print('\nAnalyzing tower number ' + str(towerNum))
            print('-------------------------')
            self.runAnalysis(SapModel, towerPerformance)
                
            self.towerPerformances[str(towerNum)] = towerPerformance

            self.plotter.addxData(towerNum)

            # TODO: fix below
            if self.runGMs:
                avgBuildingCost = towerPerformance.avgBuildingCost()
                avgSeismicCost = towerPerformance.avgSeismicCost()

                self.plotter.addyData(avgBuildingCost + avgSeismicCost)
            else:
                self.plotter.addyData(towerPerformance.period)

            self.plotter.updatePlot()

        # Create output table
        filewriter = FileWriter(self.mainFileLoc)
        filewriter.writeOutputTable(self.towerPerformances)

        # Save tower performances
        self.tower.towerPerformances.clear()
        self.tower.towerPerformances.update(self.towerPerformances)

        # reset
        for panel in self.tower.panels.values():
            panel.IDs = ["UNKNOWN"]

    def startSap2000(self):
        #set the following flag to True to attach to an existing instance of the program
        #otherwise a new instance of the program will be started
        AttachToInstance = False

        #set the following flag to True to manually specify the path to SAP2000.exe
        #this allows for a connection to a version of SAP2000 other than the latest installation
        #otherwise the latest installed version of SAP2000 will be launched
        SpecifyPath = True

        #if the above flag is set to True, specify the path to SAP2000 below
        ProgramPath = self.SAPPath

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

    def roundingModelCoordinates(self, SapModel):
        SapModel.SetModelIsLocked(False)
        [NumberPoints, AllPointNames, ret] = SapModel.PointObj.GetNameList()

        for PointName in AllPointNames:
            [x, y, z, ret] = SapModel.PointObj.GetCoordCartesian(PointName, 0, 0, 0)
            x = round(x, SAP2000Constants.MaxDecimalPlaces)
            y = round(y, SAP2000Constants.MaxDecimalPlaces)
            z = round(z, SAP2000Constants.MaxDecimalPlaces)
            ret = SapModel.EditPoint.ChangeCoordinates_1(PointName, x, y, z, True)
            if ret != 0:
                print('ERROR rounding coordinates of point ' + PointName)

    def clearPanel(self, SapModel, panel):
        # Deletes all members that are in the panel
        if panel.IDs == ["UNKNOWN"]:
            self.clearExistingMembersinPanel(SapModel, panel)
        else:
            # Delete members that are contained in the panel
            for memberID in panel.IDs:
                ret = SapModel.FrameObj.Delete(memberID)
                if ret != 0:
                    print('ERROR deleting member ' + memberID)
        panel.IDs.clear()

    def clearExistingMembersinPanel(self, SapModel, panel):
        vec1_x = panel.lowerLeft.x - panel.upperLeft.x
        vec1_y = panel.lowerLeft.y - panel.upperLeft.y
        vec1_z = panel.lowerLeft.z - panel.upperLeft.z
        vec2_x = panel.lowerLeft.x - panel.upperRight.x
        vec2_y = panel.lowerLeft.y - panel.upperRight.y
        vec2_z = panel.lowerLeft.z - panel.upperRight.z

        # Two vectors defining the panel
        vec1 = [vec1_x, vec1_y, vec1_z]
        vec2 = [vec2_x, vec2_y, vec2_z]
        
        # Normal vector of panel
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

            # Check if the member is within the elevation of the panel
            panel_max_z = max(panel.lowerLeft.z, panel.upperLeft.z, panel.upperRight.z, panel.lowerRight.z)
            panel_min_z = min(panel.lowerLeft.z, panel.upperLeft.z, panel.upperRight.z, panel.lowerRight.z)
            
            if min(member_pt1_z, member_pt2_z) >= panel_min_z and max(member_pt1_z, member_pt2_z) <= panel_max_z:
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
                        panelPoints = [
                            [panel.lowerLeft.x, panel.lowerLeft.y, panel.lowerLeft.z],
                            [panel.upperLeft.x, panel.upperLeft.y, panel.upperLeft.z],
                            [panel.upperRight.x, panel.upperRight.y, panel.upperRight.z],
                            [panel.lowerRight.x, panel.lowerRight.y, panel.lowerRight.z]
                        ]

                        panelPointsTrans = []

                        for panelPoint in panelPoints:
                            panelPointTrans1 = numpy.dot(panelPoint, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            panelPointTrans2 = numpy.dot(panelPoint, ref_vec_2) / numpy.linalg.norm(ref_vec_2)

                            panelPointsTrans.append([panelPointTrans1, panelPointTrans2])

                        # Project each point defining the member onto the reference vector
                        member_pt1 = [member_pt1_x, member_pt1_y, member_pt1_z]
                        member_pt2 = [member_pt2_x, member_pt2_y, member_pt2_z]
                        member_pt1_trans_1 = numpy.dot(member_pt1, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                        member_pt1_trans_2 = numpy.dot(member_pt1, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                        member_pt2_trans_1 = numpy.dot(member_pt2, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                        member_pt2_trans_2 = numpy.dot(member_pt2, ref_vec_2) / numpy.linalg.norm(ref_vec_2)

                        # Create shapely geometries to check if member is in the panel
                        poly_coords = panelPointsTrans
                        member_coords = [[member_pt1_trans_1, member_pt1_trans_2],
                                            [member_pt2_trans_1, member_pt2_trans_2]]

                        # round coordinates
                        for i in range(len(poly_coords)):
                            poly_coords[i][0] = round(poly_coords[i][0], SAP2000Constants.MaxDecimalPlaces)
                            poly_coords[i][1] = round(poly_coords[i][1], SAP2000Constants.MaxDecimalPlaces)

                        for i in range(len(member_coords)):
                            member_coords[i][0] = round(member_coords[i][0], SAP2000Constants.MaxDecimalPlaces)
                            member_coords[i][1] = round(member_coords[i][1], SAP2000Constants.MaxDecimalPlaces)

                        panel_shapely = shapely.geometry.Polygon(poly_coords)
                        member_shapely = shapely.geometry.LineString(member_coords)

                        # Delete member if it is inside the panel
                        if member_shapely.intersects(panel_shapely):
                            if not member_shapely.touches(panel_shapely):
                                ret = SapModel.FrameObj.Delete(member_name, 0)
                                
                            # Get members needed to be divided at intersections
                            else:
                                self.membersToDivide.append(member_name)

    def buildBracing(self, SapModel, panel, bracing):
        # Scale the member start and end points to fit the panel location and dimensions
        # Get unit vectors to define the panel
        panel_vec_horiz_x = panel.lowerRight.x - panel.lowerLeft.x
        panel_vec_horiz_y = panel.lowerRight.y - panel.lowerLeft.y
        panel_vec_horiz_z = panel.lowerRight.z - panel.lowerLeft.z
        panel_vec_vert_x = panel.upperLeft.x - panel.lowerLeft.x
        panel_vec_vert_y = panel.upperLeft.y - panel.lowerLeft.y
        panel_vec_vert_z = panel.upperLeft.z - panel.lowerLeft.z

        panel_vec_horiz = [panel_vec_horiz_x, panel_vec_horiz_y, panel_vec_horiz_z]
        panel_vec_vert = [panel_vec_vert_x, panel_vec_vert_y, panel_vec_vert_z]

        panel_norm_vec = numpy.cross(numpy.array(panel_vec_horiz), numpy.array(panel_vec_vert))

        # Convert panel coordinates to the local coordinate system of panel (defined by vec_horiz and vec_vert)
        panel_points = [
            [panel.lowerLeft.x, panel.lowerLeft.y, panel.lowerLeft.z],
            [panel.upperLeft.x, panel.upperLeft.y, panel.upperLeft.z],
            [panel.upperRight.x, panel.upperRight.y, panel.upperRight.z],
            [panel.lowerRight.x, panel.lowerRight.y, panel.lowerRight.z],
        ]

        # Reference vectors for the local coordinate system of the panel
        ref_vec_1 = panel_vec_horiz
        ref_vec_2 = numpy.cross(panel_vec_horiz, panel_norm_vec)

        panel_points_trans = [[numpy.dot(point,ref_vec_1) / numpy.linalg.norm(ref_vec_1),
                                numpy.dot(point,ref_vec_2) / numpy.linalg.norm(ref_vec_2)] 
                                for point in panel_points]

        # Generate a matrix which projects the "bracing scheme space" to the "panel space"
        t = ProjectiveTransform()
        src = numpy.asarray([[0, 0], [0, 1], [1, 1], [1, 0]])
        dst = numpy.asarray(panel_points_trans)

        if not t.estimate(src, dst): raise Exception("estimate failed")

        for member in bracing.members:
            node1 = member.start_node
            node2 = member.end_node
            section = member.material

            memberData = numpy.array([
                [node1.x, node1.y],
                [node2.x, node2.y],
            ])

            # Project member's coordinate onto the panel
            memberData_local = t(memberData)

            panel_vec_horiz_hat = numpy.array(ref_vec_1) / numpy.linalg.norm(ref_vec_1)
            panel_vec_vert_hat = numpy.array(ref_vec_2) / numpy.linalg.norm(ref_vec_2)

            # Convert member coordinates from the local 2D coordinate system of panel to the global 3D coordinate system
            start_node_x = panel.lowerLeft.x + (memberData_local[0][0] - panel_points_trans[0][0]) * panel_vec_horiz_hat[0] + (memberData_local[0][1] - panel_points_trans[0][1]) * panel_vec_vert_hat[0]
            start_node_y = panel.lowerLeft.y + (memberData_local[0][0] - panel_points_trans[0][0]) * panel_vec_horiz_hat[1] + (memberData_local[0][1] - panel_points_trans[0][1]) * panel_vec_vert_hat[1]
            start_node_z = panel.lowerLeft.z + (memberData_local[0][0] - panel_points_trans[0][0]) * panel_vec_horiz_hat[2] + (memberData_local[0][1] - panel_points_trans[0][1]) * panel_vec_vert_hat[2]
            end_node_x = panel.lowerLeft.x + (memberData_local[1][0] - panel_points_trans[0][0]) * panel_vec_horiz_hat[0] + (memberData_local[1][1] - panel_points_trans[0][1]) * panel_vec_vert_hat[0]
            end_node_y = panel.lowerLeft.y + (memberData_local[1][0] - panel_points_trans[0][0]) * panel_vec_horiz_hat[1] + (memberData_local[1][1] - panel_points_trans[0][1]) * panel_vec_vert_hat[1]
            end_node_z = panel.lowerLeft.z + (memberData_local[1][0] - panel_points_trans[0][0]) * panel_vec_horiz_hat[2] + (memberData_local[1][1] - panel_points_trans[0][1]) * panel_vec_vert_hat[2]

            # Create the member
            [member_name, ret] = SapModel.FrameObj.AddByCoord(start_node_x, start_node_y, start_node_z, end_node_x,
                                                              end_node_y, end_node_z, PropName=section)

            if ret != 0:
                print('ERROR building member in panel', panel.name)

            if member_name is not None:
                panel.IDs.append(member_name)

    def divideMembersAtIntersection(self, SapModel):
        '''  May not be necessary '''
        # Make sure no duplicates
        self.membersToDivide = list(dict.fromkeys(self.membersToDivide))

        for memberName in self.membersToDivide:

            ret = SapModel.SelectObj.All(False)
            if ret != 0:
                print('ERROR selecting all members')

            num = 0
            newNames = []
            [num, newNames, ret] = SapModel.EditFrame.DivideAtIntersections(memberName, num, newNames)
            if ret != 0:
                print('ERROR dividing member ' + memberName)

            else:
                for newName in newNames:
                    self.membersToDivide.append(newName)

        ret = SapModel.SelectObj.All(True)

    def changeMemberSection(self, SapModel, memberID, sectionName):
        # Change the section properties of specified members
        print('\nChanging section properties of specified members...')
        print('Changed section of member ' + str(memberID))
        ret = SapModel.FrameObj.SetSection(str(memberID), sectionName, 0)
        if ret != 0 :
            print('ERROR changing section of member ' + str(memberID))

    def runAnalysis(self, SapModel, towerPerformance):
        SapModel.SetPresentUnits(SAP2000Constants.Units['kip_in_F'])

        run_GMs = self.projectSettingsData.groundMotion

        if run_GMs:
            SapModel.Analyze.SetRunCaseFlag('', True, True)
        else:
            SapModel.Analyze.SetRunCaseFlag('', False, True)
            SapModel.Analyze.SetRunCaseFlag('GM1', False, False)
            SapModel.Analyze.SetRunCaseFlag('GM2', False, False)
            SapModel.Analyze.SetRunCaseFlag('DEAD', True, False)
            SapModel.Analyze.SetRunCaseFlag('MODAL', True, False)

        #Run Analysis
        print('Running model in SAP2000...')
        SapModel.Analyze.RunAnalysis()
        print('Finished running.')

        print('Getting results...')

        analyzer = PerformanceAnalyzer(SapModel)

        # Find Roof nodes ---------------------------------------------
        roofNodeNames = self.nodesList

        # Get WEIGHT in lbs ---------------------------------
        totalWeight = analyzer.getWeight()
        
        # Get PERIOD ---------------------------------
        period = analyzer.getPeriod()
        
        [NumberCombo, AllCombos, ret] = SapModel.RespCombo.GetNameList()
        for combo in AllCombos:
            if run_GMs:
                # Only run combo with ground motions
                if not ('GM' in combo):
                    continue

                SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
                SapModel.Results.Setup.SetComboSelectedForOutput(combo)
                # set type to envelope
                SapModel.Results.Setup.SetOptionModalHist(1)

                # get max ACCELERATION ---------------------------------------
                maxAcc = analyzer.getMaxAcceleration(roofNodeNames)

                # get joint DISPLACEMENT ---------------------------------------
                maxDisp = analyzer.getMaxDisplacement(roofNodeNames)

                # Get BASE SHEAR  ---------------------------------------
                basesh = analyzer.getBaseShear()
                
                if self.costCalcIdentifier in combo:
                    buildingCost, seismicCost = analyzer.getCosts(maxAcc, maxDisp, self.footprint, totalWeight, self.totalMass, self.totalHeight)
                    towerPerformance.buildingCost[combo] = buildingCost
                    towerPerformance.seismicCost[combo] = seismicCost

            else:
                maxAcc = 'max acc not calculated'
                maxDisp = 'max disp not calculated'
                basesh = 'base shear not calculated'

            # Store performance data to struct
            towerPerformance.maxAcc[combo] = maxAcc
            towerPerformance.maxDisp[combo] = maxDisp
            towerPerformance.basesh[combo] = basesh

        towerPerformance.totalWeight = totalWeight
        towerPerformance.period = period    
        
        # Get Centre of Rigidity ---------------------------------
        towerPerformance.CR = analyzer.getCR(self.tower.elevations)

class SAPRunnable(QRunnable):
    ''' Worker thread; to avoid freezing GUI '''

    def __init__(self, runTower):
        super().__init__()
        self.runTower = runTower

    def run(self):
        self.runTower.buildTowers()
