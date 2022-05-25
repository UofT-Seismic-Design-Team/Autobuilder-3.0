import os
import sys
import comtypes.client
import comtypes.gen
import pandas as pd  # Dataframe

import scipy

from Definition import *    # file extensions, EnumToString conversion, 

class PerformanceAnalyzer:
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
        ''' return max acceleration in g '''
        SapModel = self.SapModel

        # Set units to metres
        SapModel.SetPresentUnits(SAP2000Constants.Units['N_m_C'])

        maxAcc = 0
        for roofNodeName in roofNodeNames:
            ret = SapModel.Results.JointAccAbs(roofNodeName, 0)

            if ret[-1] != 0:
                print('ERROR getting acceleration at Node {}'.format(roofNodeName))

            max_and_min_acc = ret[6]
            
            max_pos_acc = max_and_min_acc[0]
            min_neg_acc = max_pos_acc

            # Error handling: in case no acceleration is available
            if len(max_and_min_acc) > 1:
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

            if ret[-1] != 0:
                print('ERROR getting displacement at Node {}'.format(roofNodeName))

            max_and_min_disp = ret[6]

            max_pos_disp = max_and_min_disp[0]
            min_neg_disp = max_pos_disp

            # Error handling: in case displacements are not available
            if len(max_and_min_disp) > 1:
                min_neg_disp = max_and_min_disp[1]

            currentMaxDisp = max(abs(max_pos_disp), abs(min_neg_disp))
            maxDisp = max(maxDisp, currentMaxDisp)

        return maxDisp

    def getBaseShear(self):
        SapModel = self.SapModel

        ret = SapModel.Results.BaseReact()
        if ret[-1] != 0:
            print('ERROR getting base reaction')

        if len(ret[4]) > 1:
            basesh = max(abs(ret[4][0]), abs(ret[4][1]))
        else:
            basesh = abs(ret[4][0])
        
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

    def getMemberStress(self, selectedFrameMembers=[], selectedWallMembers=[],  maxStressIdentifier='', allCombos=[]):
        ''' -> 4 dataframes: Tensile, Compressive, Bending, Shear '''
        # Steps
        # 1. Get all or selected frame/wall members
        # 2. Get section props of individual memebers
        # 3. Get forces in members (i.e. tension, compression and bendings)
        # 4. convert forces to stress, including bending stress
        # 5. Output "max stress, member type, member name"

        SapModel = self.SapModel

        # Set units to millimetres
        SapModel.SetPresentUnits(SAP2000Constants.Units['N_mm_C'])
        dictTemplate = {
            'Stress': [],
            'Type': [], # 'F': Frame; 'W': Wall
            'LC': [],
            'Name': [],
        }

        maxTs, maxCs, maxMs, maxVs = [dictTemplate.copy() for i in range(4)]

        maxTwBs = []
        maxCwBs = []

        # Frame members ------------------------
        if selectedFrameMembers == []:
            [numberNames, allNames, ret] = SapModel.FrameObj.GetNameList()
            selectedFrameMembers = allNames

        for combo in allCombos:
            if not(maxStressIdentifier in combo):
                continue

            SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
            SapModel.Results.Setup.SetComboSelectedForOutput(combo)
            # set type to envelope
            SapModel.Results.Setup.SetOptionModalHist(1)

            for member in selectedFrameMembers:
                # Get section props of memebers
                [sectName, sAuto , ret] = SapModel.FrameObj.GetSection(member)
                [Area, As2, As3, Torsion, I22, I33, S22, S33, Z22, Z33, R22, R33, ret] = SapModel.PropFrame.GetSectProps(sectName)
                # Note: As2 and As3 refer to the reduced effective shear areas. This to reflect the parabolic distribution of shear stress in the section. Assume SAP2000 is correct
                
                # Get forces in members (i.e. tension, compression and bendings)
                OBJECT_ELEM = 0
                [NumberResults, Obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, P, V2, V3, T, M2, M3, ret] = SapModel.Results.FrameForce(member, OBJECT_ELEM)
                print('Load Case:', LoadCase)

                # in case no forces found
                if not LoadCase:
                    continue

                # Max Tensile Stress
                maxT = max(P)
                maxTStress = maxT / Area

                maxTs['Stress'].append(maxTStress)
                maxTs['Type'].append('F')
                maxTs['LC'].append(combo)
                maxTs['Name'].append(member)
                
                # Max Compressive Stress
                maxC = min(P)
                maxCStress = abs(maxC) / Area

                maxCs['Stress'].append(maxCStress)
                maxCs['Type'].append('F')
                maxCs['LC'].append(combo)
                maxCs['Name'].append(member)

                # Max Bending Stress - major and minor bending axes
                maxM2pos = max(M2)
                maxM2neg = min(M2)
                if abs(maxM2pos) >= abs(maxM2neg):
                    maxM2Stress = abs(maxM2pos) / S22
                else:
                    maxM2Stress = abs(maxM2neg) / S22
                
                maxM3pos = max(M3)
                maxM3neg = min(M3)
                if abs(maxM3pos) >= abs(maxM3neg):
                    maxM3Stress = abs(maxM3pos) / S33
                else:
                    maxM3Stress = abs(maxM3neg) / S33

                if maxM2Stress >= maxM3Stress:
                    maxMStress = maxM2Stress
                else:
                    maxMStress = maxM3Stress

                maxMs['Stress'].append(maxMStress)
                maxMs['Type'].append('F')
                maxMs['LC'].append(combo)
                maxMs['Name'].append(member)

                # Max shear stress - major and minor local axes
                maxV2pos = max(V2)
                maxV2neg = min(V2)
                if abs(maxV2pos) >= abs(maxV2neg):
                    maxV2stress = abs(maxV2pos) / As2
                else:
                    maxV2stress = abs(maxV2neg) / As2
                
                maxV3pos = max(V3)
                maxV3neg = min(V3)
                if abs(maxV3pos) >= abs(maxV3neg):
                    maxV3stress = abs(maxV3pos) / As3
                else:
                    maxV3stress = abs(maxV3neg) / As3

                if maxV2stress >= maxV3stress:
                    maxVStress = maxV2stress
                else:
                    maxVStress = maxV3stress

                maxVs['Stress'].append(maxVStress)
                maxVs['Type'].append('F')
                maxVs['LC'].append(combo)
                maxVs['Name'].append(member)

                maxTwBs.append(maxTStress + maxMStress)
                maxCwBs.append(maxCStress + maxMStress)

        maxTs_df = pd.DataFrame(data=maxTs)
        maxCs_df = pd.DataFrame(data=maxCs)
        maxMs_df = pd.DataFrame(data=maxMs)
        maxVs_df = pd.DataFrame(data=maxVs)

        return maxTs_df, maxCs_df, maxMs_df, maxVs_df, maxTwBs, maxCwBs

    def getCosts(self, maxAcc, maxDisp, footprint, weight, totalMass, totalHeight):
        # Subtract weights. Weight is initially in lb, convert to kg
        print('Calculating costs...')

        weight = (weight * UnitConversion.Mass['lb'] - totalMass) / UnitConversion.Mass['lb']
        design_life = 100 # years
        construction_cost = 2000000*(weight**2)+6*(10**6)
        land_cost = 35000 * footprint
        annual_building_cost = (land_cost + construction_cost) / design_life
        
        equipment_cost = 15000000
        return_period_1 = 50
        return_period_2 = 300
        apeak_1 = maxAcc #g's
        xpeak_1 = 100*maxDisp/(totalHeight * 25.4) #% roof drift
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

    def getCR(self, towerElevs):
        ''' Single floor CR '''
        # TODO: implement all floor CR
        SapModel = self.SapModel
        SapModel.SetModelIsLocked(False)
        SapModel.SetPresentUnits(SAP2000Constants.Units['kip_in_F'])
        towerCRs = {}

        # Get names of nodes on each floor
        [number_nodes, all_node_names, ret] = SapModel.PointObj.GetNameList()
        floor_nodes = {}
        for node_name in all_node_names:
            [x, y, z, ret] = SapModel.PointObj.GetCoordCartesian(node_name, 0, 0, 0)
            if z in towerElevs:
                if z not in floor_nodes:
                    floor_nodes[z] = []
                floor_nodes[z].append(node_name)

        # remove existing diaphragm constraints
        for elev in floor_nodes:
            nodes = floor_nodes[elev]
            for node in nodes:
                ret = SapModel.PointObj.DeleteConstraint(node, 0)
                if ret != 0:
                    print('ERROR deleting diaphragm constraint from floor at elevation ' + str(elev))

        # Define and set diaphragm constraint if not defined already
        print('Defining and Setting diaphragm constraint...')
        for elev in towerElevs:
            diaphragmType = 'Diaphragm' + str(elev)
            [axis, csys, ret] = SapModel.ConstraintDef.GetDiaphragm(diaphragmType)
            if ret != 0:
                SapModel.ConstraintDef.SetDiaphragm(diaphragmType, 3)
            
            nodes = floor_nodes[elev]
            for node in nodes:
                ret = SapModel.PointObj.SetConstraint(node, diaphragmType, 0, True)
                if ret != 0:
                    print('ERROR setting diaphragm constraint from floor at elevation ' + str(elev))
                
            
        # Create unit X, unit Y, and unit Z load cases if they haven't already been set
        print('Defining unit load cases...')
        [number_patterns, all_load_patterns, ret] = SapModel.LoadPatterns.GetNameList()
        LTYPE_DEAD = 1
        unitLoadPatterns = {
            'Unit X': [1, 0, 0, 0, 0, 0], 
            'Unit Y': [0, 1, 0, 0, 0, 0], 
            'Unit Moment': [0, 0, 0, 0, 0, 1]}

        for unitLoadPattern in unitLoadPatterns:
            for elev in towerElevs:
                loadCaseName = unitLoadPattern + ' - ' + str(elev)
                if loadCaseName not in all_load_patterns:
                    ret = SapModel.LoadPatterns.Add(loadCaseName, LTYPE_DEAD)
                    if ret != 0:
                        print('ERROR adding ' + loadCaseName + ' load case')
                
        # Only set the unit load cases to run
        SapModel.Analyze.SetRunCaseFlag('', False, True)
        for unitLoadPattern in unitLoadPatterns:
            for elev in towerElevs:
                SapModel.Analyze.SetRunCaseFlag(unitLoadPattern + ' - ' + str(elev), True, False)

        # Add loads to all floors
        nodeNum = 0
        for elev in towerElevs:
            node = floor_nodes[elev][nodeNum]
            for unitLoadPattern in unitLoadPatterns:
                loadCaseName = unitLoadPattern + ' - ' + str(elev)
                SapModel.PointObj.SetLoadForce(node, loadCaseName, unitLoadPatterns[unitLoadPattern], True, 'GLOBAL', 0)

        # Run analysis -----------------------------------------------------------------------------------------------
        print()
        print('Running model in SAP2000...')
        SapModel.Analyze.RunAnalysis()
        print('Finished running.')
        print()

        # For each floor, assign unit loads, run case, find rotations, find Crx and Cry
        for elev in towerElevs:
            # skip elevation 0
            if elev <= 0:
                continue

            print('Calculating Cr...')

            node = floor_nodes[elev][nodeNum]

            # Get rotations at joint
            rotations = []
            for patternName in unitLoadPatterns:
                SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
                SapModel.Results.Setup.SetCaseSelectedForOutput(patternName + ' - ' + str(elev), True)

                OBJECT_ELEM = 0
                number_results = 0
                object_names = []
                element_names = []
                load_cases = []
                step_types = []
                step_nums = []
                u1 = []
                u2 = []
                u3 = []
                r1 = []
                r2 = []
                r3 = []
                ret = 0

                [number_results, object_names, element_names, load_cases, step_types, step_nums, u1, u2, u3, r1, r2, r3, ret] = SapModel.Results.JointDisplAbs(node, OBJECT_ELEM, number_results, object_names, element_names, load_cases, step_types, step_nums, u1, u2, u3, r1, r2, r3)

                if ret != 0:
                    print('ERROR getting rotations from ' + patternName + ' - ' + str(elev) + ' case')
                rotations.append(r3[0])

            Rzx, Rzy, Rzz = rotations
            
            [load_x, load_y, load_z, ret] = SapModel.PointObj.GetCoordCartesian(node, 0, 0, 0)
            Crx = load_x - Rzy/ (Rzz + Algebra.EPSILON)
            Cry = load_y + Rzx/ (Rzz + Algebra.EPSILON)
            floorCR = [Crx, Cry]
            # Append results
            towerCRs[elev] = floorCR

        # Unlock model
        SapModel.SetModelIsLocked(False)

        for elev in towerElevs:
            print('Deleting unit loads and constraints...')
            node = floor_nodes[elev][nodeNum]
            for patternName in unitLoadPatterns:
                # Delete unit loads
                ret = SapModel.PointObj.DeleteLoadForce(node, patternName + ' - ' + str(elev), 0)
                if ret != 0:
                    print('ERROR deleting' + patternName + ' on floor at elevation ' + str(elev))
            
            nodes = floor_nodes[elev]
            for node in nodes:
                # Delete diaphragm constraint from floor
                ret = SapModel.PointObj.DeleteConstraint(node, 0)
                if ret != 0:
                    print('ERROR deleting diaphragm constraint from floor at elevation ' + str(elev))
            
        # Set all load cases to run again, except for the unit load cases
        SapModel.Analyze.SetRunCaseFlag('', True, True)
        for patternName in unitLoadPatterns:
            SapModel.Analyze.SetRunCaseFlag(patternName, False, False)

        return towerCRs

    def getEccentricity(self, towerCRs, tower):
        ''' Maximum and Average eccentricity '''
        eccs = []

        for elev in towerCRs:
            crX, crY = towerCRs[elev]
            comX = tower.floors[elev].comX
            comY = tower.floors[elev].comY

            xEcc = abs(crX - comX)
            yEcc = abs(crY - comY)

            eccs.append(xEcc)
            eccs.append(yEcc)

        maxEcc = max(eccs)
        avgEcc = sum(eccs)/max(len(eccs),1)

        return maxEcc, avgEcc

# struct for tower performance
class TowerPerformance:
    # static variable for id
    id = 1

    def __init__(self, name):
        self.name = name
        if not name:
            self.name = str(TowerPerformance.id)
            TowerPerformance.id += 1

        # Variables & assigned values
        self.variables = {}

        # results from SAP2000
        # key: load combo; values
        self.maxAcc = {}
        self.maxDisp = {}
        self.basesh = {} # base shear
        self.totalWeight = 0
        self.period = 0

        # Member Stress
        self.tensileStress = pd.DataFrame()
        self.compressiveStress = pd.DataFrame()
        self.bendingStress = pd.DataFrame()
        self.shearStress = pd.DataFrame()

        # Demand-capacity ratios
        self.tensionDCR = 0
        self.compDCR = 0
        self.shearDCR = 0

        # SDC metrics
        # key: load combo; values
        self.buildingCost = {}
        self.seismicCost = {}

        # For asymmetrical tower
        # key: floor; values: CRx, CRy
        self.CR = {}
        self.maxEcc = 0
        self.avgEcc = 0

        # Member Stresses
        self.max_T = pd.DataFrame()
        self.max_C = pd.DataFrame()
        self.max_M = pd.DataFrame()
        self.max_V = pd.DataFrame()
        self.max_CombT = 0
        self.max_CombC = 0

    def addVariable(self, variableName, assignedValue):
        self.variables[variableName] = assignedValue

    def avgBuildingCost(self):
        ''' -> float'''
        avgBuildingCost = 0
        for bdCost in self.buildingCost.values():
            avgBuildingCost += bdCost
        if len(self.buildingCost) > 0:
            avgBuildingCost /= min(len(self.buildingCost),1)

        return avgBuildingCost

    def avgSeismicCost(self):
        ''' -> float'''
        avgSeismicCost = 0
        for sCost in self.seismicCost.values():
            avgSeismicCost += sCost
            avgSeismicCost /= min(len(self.seismicCost),1)

        return avgSeismicCost

    def memberStress(self):
        ''' -> dataframe'''
