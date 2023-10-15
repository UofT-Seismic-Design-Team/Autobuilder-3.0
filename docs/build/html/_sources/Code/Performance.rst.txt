Performance
==================

.. _performanceanalyzer:

Performance Analyzer
--------------
PerformanceAnalyzer provides methods for analyzing the performance and estimating the cost of a structure.


getWeight
~~~~~~~~~
This method calculates the total weight of the structure:

#. Set units to meters
#. Select dead loads only and retrieve base reaction forces
#. Divide the base reactions in the global Z direction by the gravitational constant g to get the weight
#. Convert the weight into lbs

The method *BaseReact()* returns zero if the reactions are successfully recovered, otherwise it returns a nonzero value.

.. code-block:: python

    def getWeight(self):
        """
        Calculate the total weight of a structure.

        This method sets the units to meters, retrieves the base reactions for the 'DEAD' case,
        and calculates the total weight in pounds.

        :return: The total weight in pounds.
        :rtype: float
        """
        SapModel = self.SapModel

        # Set units to meters
        SapModel.SetPresentUnits(SAP2000Constants.Units['N_m_C'])

        # Get base reactions
        SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        SapModel.Results.Setup.SetCaseSelectedForOutput('DEAD')
        ret = SapModel.Results.BaseReact()
        if ret[-1] != 0:
            print('ERROR getting weight')

        base_react = ret[6][0]
        total_weight = abs(base_react / Constants.g)

        # Convert to lb
        total_weight = total_weight / UnitConversion.Mass['lb']

        return total_weight



getMaxAcceleration
~~~~~~~~~~~~~~~~~~~~~~~~~~~
This method finds the maximum acceleration out of all roof nodes in units of g:

#. Set units to meters
#. Find the absolute acceleration for each roof node
#. Compare the acceleration of each node to find the maximum acceleration

The method *JointAccAbs()* returns zero if the accelerations are successfully recovered, otherwise it returns a nonzero value.

.. code-block:: python
    def getMaxAcceleration(self, roofNodeNames):
        """
        Get the maximum acceleration in g units.

        :param roofNodeNames: A list of roof node names.
        :type roofNodeNames: list
        :return: The maximum acceleration in g units.
        :rtype: float
        """
        SapModel = self.SapModel

        # Set units to meters
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



getPeriod
~~~~~~~~~
This method finds the modal period of the structure using the method *ModalPeriod()*.

The method *ModalPeriod()* returns zero if the data is successfully recovered, otherwise it returns a nonzero value.

.. code-block:: python

    def getPeriod(self):
        """
        Get the modal period of the structure.

        :return: The period of the structure.
        :rtype: float
        """
        SapModel = self.SapModel

        ret = SapModel.Results.ModalPeriod()
        if ret[-1] != 0:
            print('ERROR getting modal period')
        period = ret[4][0]

        return period



getMaxDisplacement
~~~~~~~~~~~~~~~~~~~~~~~~~~~
This method finds the maximum displacement out of all roof nodes in millimeters:

#. Set units to millimeters
#. Find the absolute displacement for each roof node
#. Compare the displacement of each node to find the maximum displacement

The method *JointAccAbs()* returns zero if the accelerations are successfully recovered, otherwise it returns a nonzero value.

.. code-block:: python

    def getMaxDisplacement(self, roofNodeNames):
        """
        Get the maximum displacement of the roof nodes in millimeters.

        :param roofNodeNames: A list of roof node names.
        :type roofNodeNames: list
        :return: The maximum displacement in millimeters.
        :rtype: float
        """    
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



getBaseShear
~~~~~~~~~~~~~~~~~~
This method finds the base shear forces of the structure using the method *BaseReact(*). 
The base shear force is the base reaction in the global X direction.

The method *BaseReact()* returns zero if the reactions are successfully recovered, otherwise it returns a nonzero value.

.. code-block:: python

    def getBaseShear(self):
    """
     Get the base shear forces of the structure.

    :return: The base shear force
    :rtype: float
    """
        SapModel = self.SapModel

        ret = SapModel.Results.BaseReact()
        if ret[-1] != 0:
            print('ERROR getting base reaction')

        if len(ret[4]) > 1:
            basesh = max(abs(ret[4][0]), abs(ret[4][1]))
        else:
            basesh = abs(ret[4][0])
        
        return basesh



getRoofNodeNames
~~~~~~~~~~~~~~~~~~
This method finds the names of the roof nodes out of all the nodes of the structure:

#. Retrieve the names of all the nodes of the structure
#. Find the X, Y, Z coordinates for each node
#. Compare the coordinates of each node to find the maximum X, Y, Z coordinates and minimum X, Y coordinates. These coordinates indicates the coordinates of the roof corners. 
#. Find the names of the roof corners


.. code-block:: python

    def getRoofNodeNames(self):
        """
        Get the names of nodes on the roof of the structure.

        This method identifies the nodes on the roof based on their coordinates and selects nodes
        at the quarter points on the top floor.

        :return: A list of node names on the roof.
        :rtype: list of str
        """
        SapModel = self.SapModel

        roofNodeNames = []
        # Retrieve names of all nodes and store in allNodeNames (list)
        [number_nodes, allNodeNames, ret] = SapModel.PointObj.GetNameList()
        
        # Initialize variables to track the maximum and minimum X, Y, Z coordinates of the nodes
        z_max = 0
        x_max = 0
        y_max = 0
        x_min = 0
        y_min = 0

        # Obtain the maximum X, Y, Z coordinates and minimum X, Y coordinates relative to the origin
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



getMemberStress
~~~~~~~~~~~~~~~~~~
This method calculates the maximum stress of the selected members in a structure:

#. Set units to millimeters
#. Find the names of the selected members
#. For all but the maximum stress load combinations: 

   a. Select "combo" for load combinations
   b. Set "Envelope" as the output option for modal history results
   c. Get the name of the member section and then the properties of the member
   d. For each member, find the maximum Tensile Stress, Compressive Stress, and Bending and Shear about both major and minor axes


Modal History describes the structure responds to dynamic loading over time.
The envelope type of modal history helps determine the maximum displacements, accelerations, 
or other response quantities that the structure may experience due to dynamic loadings.


The method *GetSection(member)* finds the name of the member section
The method *GetSectProps(sectNames)* displays the mechanical properties of the member section, including the cross-sectional area, shear areas, torsional constant, and the moment of inertia, section modulus of bending, plastic modulus of bending of the local 2 and 3 axes

.. code-block:: python

    def getMemberStress(self, selectedFrameMembers=[], selectedWallMembers=[],  maxStressIdentifier='', allCombos=[]):
        """
        Calculate and return stress dataframes for frame members.

        This method calculates and returns four dataframes (Tensile, Compressive, Bending, Shear) that contain stress
        information for selected frame members. The stress data includes maximum tensile stress, maximum compressive stress,
        maximum bending stress, and maximum shear stress.

        :param selectedFrameMembers: List of selected frame members (optional, default is empty list).
        :type selectedFrameMembers: list of str
        :param selectedWallMembers: List of selected wall members (optional, default is empty list).
        :type selectedWallMembers: list of str
        :param maxStressIdentifier: Identifier for the maximum stress calculation (optional).
        :type maxStressIdentifier: str
        :param allCombos: List of load combinations (optional, default is empty list).
        :type allCombos: list of str
        :return: Four dataframes containing stress information (Tensile, Compressive, Bending, Shear) and two lists of maximum Tensile+Bending stress and maximum Compressive+Bending stress.
        :rtype: tuple
        """
        # Steps
        # 1. Get all or selected frame/wall members
        # 2. Get section props of individual memebers
        # 3. Get forces in members (i.e. tension, compression and bendings)
        # 4. convert forces to stress, including bending stress
        # 5. Output "max stress, member type, member name"

        SapModel = self.SapModel

        # Set units to millimetres
        SapModel.SetPresentUnits(SAP2000Constants.Units['N_mm_C'])

        # Initialize dictTemplate to keep track of Stress, Member Type, Load Case and Member Name
        dictTemplate = {
            'Stress': [0],
            'Type': [None], # 'F': Frame; 'W': Wall
            'LC': [None],
            'Name': [None],
        }
        # Initialize variables to keep track of maximum Tension, Compression, Bending and Shear
        maxTs, maxCs, maxMs, maxVs = [dictTemplate.copy() for i in range(4)]

        maxTwBs = [0]
        maxCwBs = [0]

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
                    maxM2Stress = abs(maxM2pos) / S22 # Bending Stress = Bending / Section Modulus of Bending
                else:
                    maxM2Stress = abs(maxM2neg) / S22
                
                maxM3pos = max(M3)
                maxM3neg = min(M3)
                if abs(maxM3pos) >= abs(maxM3neg):
                    maxM3Stress = abs(maxM3pos) / S33
                else:
                    maxM3Stress = abs(maxM3neg) / S33

                # Find maximum bending stress between the bending stresses about the 2 local axes
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
                    maxV2stress = abs(maxV2pos) / As2 # Shear Stress = Shear Force / Shear Area
                else:
                    maxV2stress = abs(maxV2neg) / As2
                
                maxV3pos = max(V3)
                maxV3neg = min(V3)
                if abs(maxV3pos) >= abs(maxV3neg):
                    maxV3stress = abs(maxV3pos) / As3
                else:
                    maxV3stress = abs(maxV3neg) / As3

                # Find the maximum shear stress between the shear stresses along the 2 local axes (Optional)
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
        
        # Return 4 dataframes
        maxTs_df = pd.DataFrame(data=maxTs)
        maxCs_df = pd.DataFrame(data=maxCs)
        maxMs_df = pd.DataFrame(data=maxMs)
        maxVs_df = pd.DataFrame(data=maxVs)

        return maxTs_df, maxCs_df, maxMs_df, maxVs_df, maxTwBs, maxCwBs



getCosts
~~~~~~~~~
This method is used to estimate the annual building cost and the annual maintenance cost.

.. code-block:: python

    def getCosts(self, maxAcc, maxDisp, footprint, weight, totalMass, totalHeight):
        """
        Calculate the annual building and seismic costs.

        This method calculates the annual building cost and annual seismic cost based on various parameters,
        including maximum acceleration, maximum displacement, footprint, weight, total mass, and total height.

        :param maxAcc: The maximum acceleration in g units.
        :type maxAcc: float
        :param maxDisp: The maximum displacement in millimeters.
        :type maxDisp: float
        :param footprint: The footprint of the structure.
        :type footprint: float
        :param weight: The weight of the structure in pounds.
        :type weight: float
        :param totalMass: The total mass of the structure.
        :type totalMass: float
        :param totalHeight: The total height of the structure in millimeters.
        :type totalHeight: float
        :return: A tuple containing the annual building cost and annual seismic cost (float, float).
        :rtype: tuple
        """    
        # Subtract weights. Weight is initially in lb, convert to kg
        print('Calculating costs...')

        weight = max((weight * UnitConversion.Mass['lb'] - totalMass) / UnitConversion.Mass['lb'], 0)   # weight must be greater than 0
        design_life = 100 # years
        construction_cost = 2000000*(weight**2)+6*(10**6)
        land_cost = 35000 * footprint
        annual_building_cost = (land_cost + construction_cost) / design_life
        
        equipment_cost = 15000000
        return_period_1 = 50
        return_period_2 = 300
        apeak_1 = maxAcc # in units of g
        xpeak_1 = 100*maxDisp/(totalHeight * 25.4) # % roof drift
        structural_damage_1 = scipy.stats.norm(1.5, 0.5).cdf(xpeak_1) # CDF of a standard normal distribution with Mean = 1.5 and S.D. = 0.5
        equipment_damage_1 = scipy.stats.norm(1.75, 0.7).cdf(apeak_1)
        economic_loss_1 = structural_damage_1*construction_cost + equipment_damage_1*equipment_cost
        annual_economic_loss_1 = economic_loss_1/return_period_1
        structural_damage_2 = 0.5
        equipment_damage_2 = 0.5
        economic_loss_2 = structural_damage_2*construction_cost + equipment_damage_2*equipment_cost
        annual_economic_loss_2 = economic_loss_2/return_period_2
        annual_seismic_cost = annual_economic_loss_1 + annual_economic_loss_2

        return annual_building_cost, annual_seismic_cost



getCR
~~~~~~~~~
This method finds the centre of rigidity for each floor of the structure. 
#. Unlock the model
#. Set units to inches
#. Get the names of the nodes of each floor
#. Remove any constraints assigned to the nodes
#. Define and assign diaphram constraints to the nodes of each floor
#. Retrieve the names of all load patterns and add in the unit load cases
#. Set only unit load cases to run, add unit loads to each floor and run analysis
#. Select each of the unit load cases
#. Find the rotation about the local 3 axis for all nodes at each floor but the ground
#. Calculate the X and Y coordinates of the Centre of Rigidity
#. Unlock the model
#. Remove unit loads and remove diaphram constraint from the nodes of each floor
#. Set all cases but the unit load cases to run

The method *DeleteConstraint(node, 0)* removes any constraint assignments to the node. 
The method *SetDiaphragm(diaphragmType, 3)* defines a diaphram constraint orthogonal to the Z axis. 
The method *SetConstraint(node, diaphragmType, 0, True)* sets the diaphram constraint for each node. Any previous constraints will be replaced. 
The method 
All the methods each return zero if each of them are successful, otherwise they return a nonzero value.

.. code-block:: python
    
    def getCR(self, towerElevs):
        """
        Calculate and return the Centre of Rigidity for each floor in a tower.

        :param towerElevs: List of elevation levels for tower floors.
        :type towerElevs: list of float
        :return: Dictionary containing CR for each floor at the specified elevations.
        :rtype: dict
        """
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
        # Retrieve the names of all load patterns
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
                
        # Set all unit load cases to run
        SapModel.Analyze.SetRunCaseFlag('', False, True)
        # Set only unit load cases to run
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



getEccentricity
~~~~~~~~~~~~~~~~~~
This method calculates the maximum and average eccentricity of the tower.
#. Calculate for each floor, the difference between the X or Y coordinates of centre of regidity and the centre of mass to find the eccentricity of the structure.
#. Find the maximum and average value for eccentricty.

.. code-block:: python

    def getEccentricity(self, towerCRs, tower):
        """
        Calculate the maximum and average eccentricity for a structure.

        This method calculates and returns the maximum and average eccentricity for a tower based on CR (Center of Rotation)
        values and the center of mass of each floor.

        :param towerCRs: Dictionary containing CR (Center of Rotation) for each floor at specified elevations.
        :type towerCRs: dict
        :param tower: Tower object containing floor information.
        :type tower: Tower
        :return: Maximum and average eccentricity (X and Y) values.
        :rtype: tuple
        """
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


.. _towerperformance:


Tower Performance
----------------------
The class tower performance finds the average building and seismic costs

.. code-block:: python 

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

        def addVariable(self, variableName, assignedValue): # Add a variable with an assigned value to the tower.
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