import os
import sys
import comtypes.client
import comtypes.gen

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
                SapModel.PointObj.SetConstraint(node, diaphragmType, 0, True)
                if ret != 0:
                    print('ERROR deleting diaphragm constraint from floor at elevation ' + str(elev))
            
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
        # key: load combo; values: index
        self.maxAcc = {}
        self.maxDisp = {}
        self.basesh = {} # base shear
        self.totalWeight = 0
        self.period = 0

        # SDC metrics
        # key: load combo; values: index
        self.buildingCost = {}
        self.seismicCost = {}

        # For asymmetrical tower
        # key: floor; values: CRx, CRy
        self.CR = {}

    def addVariable(self, variableName, assignedValue):
        self.variables[variableName] = assignedValue

    def avgBuildingCost(self):
        ''' -> float'''
        avgBuildingCost = 0
        for bdCost in self.buildingCost.values():
            avgBuildingCost += bdCost
        avgBuildingCost /= len(self.buildingCost)

        return avgBuildingCost

    def avgSeismicCost(self):
        ''' -> float'''
        avgSeismicCost = 0
        for sCost in self.seismicCost.values():
            avgSeismicCost += sCost
        avgSeismicCost /= len(self.seismicCost)

        return avgSeismicCost