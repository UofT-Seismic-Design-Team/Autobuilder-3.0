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

        # Project Settings Data
        self.projectSettingsData = args[0].projectSettingsData

        # Reference to existing tower
        self.tower = args[0].tower

        # Tower performances
        self.allResults = []
        self.allCosts = []
        self.allCR = []

        self.buildTowers()

        self.OkButton.clicked.connect(lambda x: self.close())

        # Update views -----------------------------
        self.counter = 0
        timer = QTimer(self)
        timer.setInterval(10) # period in miliseconds
        timer.timeout.connect(self.addProgress)
        timer.start()

    def addProgress(self):
        self.counter += 1
        self.progressBar.setValue(self.counter)

    def buildTowers(self):
        SapModel = self.startSap2000()

        # Delete all members within the plans and build correct bracing scheme
        SapModel.SetPresentUnits(SAP2000Constants.Units['kip_in_F'])

        # self.roundingModelCoordinates(SapModel)

        runGMs = self.projectSettingsData.groundMotion

        # Start scatter plot of FABI
        plt.ion()
        fig = plt.figure()
        ax = plt.subplot(1,1,1)
        ax.set_xlabel('Tower Number')
        if runGMs:
            ax.set_ylabel('Total Cost')
        elif not runGMs:
            ax.set_ylabel('Period')
        xdata = []
        ydata = []
        ax.plot(xdata, ydata, 'ro', markersize=6)
        plt.grid(True)

        plt.show(block=False)

        inputTable = self.tower.inputTable
        for i, towerNum in enumerate(inputTable['towerNumber']):

            SapModel.SetModelIsLocked(False)
            SapModel.SetPresentUnits(SAP2000Constants.Units['kip_in_F'])

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

            # Save the file
            SAPFileLoc = self.SAPFolderLoc + os.sep + 'Tower ' + str(towerNum) + '.sdb'
            print('panel 1:', inputTable['Panel 1'][i])
            print(SAPFileLoc)
            SapModel.File.Save(SAPFileLoc)
            # Analyse tower and print results to spreadsheet
            
            print('\nAnalyzing tower number ' + str(towerNum))
            print('-------------------------')

            results = self.runAnalysis(SapModel)
            print(results)

            if runGMs:
                MaxAcc = results[0][0]
                MaxDisp = results[0][1]
                Weight = results[0][2]
                # Calculate model cost
                # TODO: allow user input
                Footprint = 144
                TotalHeight = [60] # inches
                TotalMass = [7.83] # kg
                costs = self.getCosts(MaxAcc, MaxDisp, Footprint, Weight, TotalMass, TotalHeight)
            else:
                costs = ['bldg cost not calculated', 'seismic cost not calculated']
                
            self.allResults.append(results)
            self.allCosts.append(costs)

            # Add cost to scatter plot
            xdata.append(towerNum)
            if runGMs:
                ydata.append(costs[0] + costs[1])
            else:
                ydata.append(results[0][3])

            ax.lines[0].set_data(xdata,ydata)
            ax.relim()
            ax.autoscale_view()
            plt.xticks(numpy.arange(min(xdata), max(xdata)+1, 1.0))
            fig.canvas.flush_events()

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
                        if member_shapely.intersects(panel_shapely) == True and member_shapely.touches(
                                panel_shapely) == False:
                            ret = SapModel.FrameObj.Delete(member_name, 0)

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

    def runAnalysis(self, SapModel):
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

        results = []
        SAPAnalysis = SAP2000Analysis(SapModel)

        # Find Roof nodes ---------------------------------------------
        roofNodeNames = SAPAnalysis.getRoofNodeNames()

        # Get WEIGHT in lbs ---------------------------------
        totalWeight = SAPAnalysis.getWeight()
        
        # Get PERIOD ---------------------------------
        period = SAPAnalysis.getPeriod()
        
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
                maxAcc = SAPAnalysis.getMaxAcceleration(roofNodeNames)

                # get joint DISPLACEMENT ---------------------------------------
                maxDisp = SAPAnalysis.getMaxDisplacement(roofNodeNames)

                # Get BASE SHEAR  ---------------------------------------
                basesh = SAPAnalysis.getBaseShear()
                
                results.append([maxAcc, maxDisp, totalWeight, period, basesh])

            else:
                results.append(['max acc not calculated', 'max disp not calculated', totalWeight, period, 'base shear not calculated'])

        return results

    def getCosts(self, maxAcc, maxDisp, footprint, weight, floorMasses, floorHeights):
        # Subtract weights. Weight is initially in lb, convert to kg
        print('Calculating costs...')
        weight = (weight * UnitConversion.Mass['lb'] - sum(floorMasses)) / UnitConversion.Mass['lb']
        design_life = 100 #years
        construction_cost = 2000000*(weight**2)+6*(10**6)
        land_cost = 35000 * footprint
        annual_building_cost = (land_cost + construction_cost) / design_life
        equipment_cost = 15000000
        return_period_1 = 50
        return_period_2 = 300
        apeak_1 = maxAcc #g's
        xpeak_1 = 100*maxDisp/(sum(floorHeights) * 25.4) #% roof drift
        structural_damage_1 = scipy.stats.norm(1.5, 0.5).cdf(xpeak_1)
        equipment_damage_1 = scipy.stats.norm(1.75, 0.7).cdf(apeak_1)
        economic_loss_1 = structural_damage_1*construction_cost + equipment_damage_1*equipment_cost
        annual_economic_loss_1 = economic_loss_1/return_period_1
        structural_damage_2 = 0.5
        equipment_damage_2 = 0.5
        economic_loss_2 = structural_damage_2*construction_cost + equipment_damage_2*equipment_cost
        annual_economic_loss_2 = economic_loss_2/return_period_2
        annual_seismic_cost = annual_economic_loss_1 + annual_economic_loss_2

        return annual_building_cost, annual_seismic_cost

class SAP2000Analysis:
    def __init__(self, SapModel):
        self.SapModel = SapModel

    def getWeight(self):
        ''' None -> float '''
        SapModel = self.SapModel

        # Set units to metres
        SapModel.SetPresentUnits(SAP2000Constants.Units['N_m_C'])

        # Get base reactions
        SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        SapModel.Results.Setup.SetCaseSelectedForOutput('DEAD')
        ret = SapModel.Results.BaseReact()
        if ret[-1] != 0:
            print('ERROR getting weight')

        base_react = ret[6][0]
        total_weight = abs(base_react / Constants.g)

        # convert to lb
        total_weight = total_weight / UnitConversion.Mass['lb']

        return total_weight

    def getMaxAcceleration(self, roofNodeNames):
        SapModel = self.SapModel

        # Set units to metres
        SapModel.SetPresentUnits(SAP2000Constants.Units['N_m_C'])

        maxAcc = 0
        for roofNodeName in roofNodeNames:
            ret = SapModel.Results.JointAccAbs(roofNodeName, 0)

            max_and_min_acc = ret[6]
            max_pos_acc = max_and_min_acc[0]
            min_neg_acc = max_and_min_acc[1]

            currentMaxAcc = max(abs(max_pos_acc), abs(min_neg_acc)) / Constants.g
            maxAcc = max(maxAcc, currentMaxAcc)

        return maxAcc

    def getPeriod(self):
        SapModel = self.SapModel

        ret = SapModel.Results.ModalPeriod()
        if ret[-1] != 0:
            print('ERROR getting modal period')
        period = ret[4][0]

        return period

    def getMaxDisplacement(self, roofNodeNames):
        SapModel = self.SapModel

        # Set units to millimetres
        SapModel.SetPresentUnits(SAP2000Constants.Units['N_mm_C'])

        maxDisp = 0
        for roofNodeName in roofNodeNames:
            ret = SapModel.Results.JointDispl(roofNodeName, 0)
            max_and_min_disp = ret[6]
            max_pos_disp = max_and_min_disp[0]
            min_neg_disp = max_and_min_disp[1]

            currentMaxDisp = max(abs(max_pos_disp), abs(min_neg_disp))
            maxDisp = max(maxDisp, currentMaxDisp)

        return maxDisp

    def getBaseShear(self):
        SapModel = self.SapModel

        ret = SapModel.Results.BaseReact()
        if ret[-1] != 0:
            print('ERROR getting base reaction')
        basesh = max(abs(ret[4][0]), abs(ret[4][1]))
        
        return basesh

    def getRoofNodeNames(self):
        ''' -> [str] '''
        SapModel = self.SapModel

        roofNodeNames = []
        [number_nodes, allNodeNames, ret] = SapModel.PointObj.GetNameList()
        z_max = 0
        x_max = 0
        y_max = 0
        x_min = 0
        y_min = 0

        for nodeName in allNodeNames:
            [x, y, z, ret] = SapModel.PointObj.GetCoordCartesian(nodeName, 0, 0, 0)
            x = round(x, SAP2000Constants.MaxDecimalPlaces)
            y = round(y, SAP2000Constants.MaxDecimalPlaces)
            z = round(z, SAP2000Constants.MaxDecimalPlaces)

            x_max = max(x_max, x)
            y_max = max(y_max, y)
            z_max = max(z_max, z)

            x_min = min(x_min, x)
            y_min = min(y_min, y)

        x_width = abs(x_max - x_min)
        y_width = abs(y_max - y_min)

        # Make sure we get results from a node that is at the quarter points on the top floor
        for nodeName in allNodeNames:
            [x, y, z, ret] = SapModel.PointObj.GetCoordCartesian(nodeName, 0, 0, 0)
            if z == z_max:
                roofNodeNames.append(nodeName)
            if len(roofNodeNames) == 4:
                break

        return roofNodeNames