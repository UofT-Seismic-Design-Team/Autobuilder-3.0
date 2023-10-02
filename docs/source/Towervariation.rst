Tower Variation
===============
The **Tower Variation** code is used to generate a dictionary of tower variations. It accomplishes this by creating all possible combinations of variables associated with bracing groups, section groups, and area section groups. These combinations are then applied to panels and members, resulting in different tower variations. In the following pages, you will find detailed explanations of the code's different functions and their parameters.

Functions
----------

addPanelsToBracingGroups
~~~~~~~~~~~~~~~~~~~~~~~~~~
This function is designed to associate panels with their corresponding bracing groups within a tower configuration. It iterates through the panels in the tower and assigns each panel to its designated bracing group if such an assignment exists. It begins by accessing two dictionaries: **panels**, which contains panel objects, and **bracingGroups**, which holds bracing group objects, both residing within the **self.tower** object. To ensure a clean slate, the function first clears any existing panel assignments within each bracing group by iterating through all the bracing groups in the **bracingGroups** dictionary and clearing the assignments attribute for each group. Subsequently, it iterates through the **panels** and, for each panel, retrieves its **bracingGroup** attribute, indicating the name of the designated bracing group. If the **bracingGroup** name is not an empty string, signifying a designated group, the function associates the panel with the corresponding bracing group by calling the **addAssignment** method and passing the panel as an argument. This process ensures that panels are correctly assigned to their respective bracing groups.

.. code-block:: python

   def addPanelsToBracingGroups(self):
        panels = self.tower.panels
        bracingGroups = self.tower.bracingGroups

        # clear existing panel assignments
        for bg in bracingGroups.values():
            bg.assignments.clear()

        for pName in panels:
            panel = panels[pName]
            bgName = panel.bracingGroup

            if bgName != '':
                bracingGroups[bgName].addAssignment(panel)

addMemberIdsToSectionGroups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This function, is similar to the **addPanelsToBracingGroups** fuction but focuses on the association of member IDs with their respective section groups within a tower object. Initially, it accesses two dictionaries, **member_ids** and **sectionGroups**, representing member IDs and section groups, respectively, retrieved from the **self.tower** object. To prepare for new assignments, the function systematically clears any pre-existing member ID assignments within each section group by iterating through the section groups and emptying their assignments attribute. Subsequently, the function iterates through the member IDs, fetching the corresponding section group name, and then utilizes this name to access the corresponding section group object within the **sectionGroups** dictionary. Finally, the **addAssignment** method is used on the section group, associating the member ID with its designated section group, ensuring precise member ID assignments within the tower's section groups.

.. code-block:: python

    def addMemberIdsToSectionGroups(self):
        member_ids = self.tower.member_ids
        sectionGroups = self.tower.sectionGroups

        # clear existing member id assignments
        for sg in sectionGroups.values():
            sg.assignments.clear()

        for member_id in member_ids:
            sgName = member_ids[member_id]
            sectionGroups[sgName].addAssignment(member_id)

addPanelsToAreaSectionGroups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **addPanelsToAreaSectionGroups** function, is responsible for associating panels with their respective area section groups within a tower object. It begins by accessing two dictionaries: **panels**, which contains panel objects, and **areaSectionGroups**, which holds area section group objects. Both dictionaries are retrieved from self.tower, representing tower components. To ensure a clean slate, the function clears any pre-existing panel assignments within each area section group by iterating through all the groups and clearing their assignments attribute. Subsequently, it iterates through the panels, retrieving the associated area section group name for each panel from the **areaSectionGroup** attribute. If a panel has a designated area section group, the function assigns the panel to the corresponding area section group by calling the **addAssignment** method of that group and passing the panel as an argument. The function concludes by testing and printing the names of area section groups and their assigned components. In essence, it ensures that panels are correctly assigned to their respective area section groups.

.. code-block:: python

    def addPanelsToAreaSectionGroups(self):
        panels = self.tower.panels
        areaSectionGroups = self.tower.areaSectionGroups

        # clear existing panel assignments
        for asg in areaSectionGroups.values():
            asg.assignments.clear()

        for pName in panels:
            panel = panels[pName]
            asgName = panel.areaSectionGroup

            if asgName != '':
                areaSectionGroups[asgName].addAssignment(panel)

        # --- TEST ---
        for asgName in areaSectionGroups:
            print(asgName)
            asg = areaSectionGroups[asgName]
            print([str(name) for name in asg.assignments])


GenerateInputTable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **GenerateInputTable** function within the provided code is responsible for generating an input table that captures various combinations of variables and their associated values for a tower-building application. It begins by preparing the necessary data, including associations between tower components and their respective groups (bracing groups, section groups, and area section groups). The function then constructs all possible combinations of these variables and their values. Subsequently, it organizes these combinations into a dictionary called **inputTable**. For each group of variables, it creates entries in **inputTable**, appending the values associated with those variables. Depending on the group type (e.g., bracing, section, or area section), it applies specific naming conventions to the entries. Finally, the function saves the generated **inputTable** as part of the tower object. In case of an error during the input table saving process, the code displays a error message with the text "Unable to create input table."

.. code-block:: python

    def GenerateInputTable(self): 
        if not self.run:
            return

        self.addPanelsToBracingGroups()
        self.addMemberIdsToSectionGroups()
        self.addPanelsToAreaSectionGroups()

        bracingGroups = self.tower.bracingGroups
        sectionGroups = self.tower.sectionGroups
        areaSectionGroups = self.tower.areaSectionGroups

        variableGroups = [bracingGroups, sectionGroups, areaSectionGroups]

        dict_of_combos = {}

        for variableGroup in variableGroups:
            for groupName in variableGroup:
                group = variableGroup[groupName]

                if group.assignments: # only generate combo it's assigned to tower components
                    dict_of_combos[groupName] = []
                    for var in group.variables:
                        dict_of_combos[groupName].append(str(var))

        # list_of_combos contains the variables and the values in each values
        list_of_combos = [dict(zip(dict_of_combos.keys(),v)) for v in product(*dict_of_combos.values())]

        # reset dict
        for key in dict_of_combos:
            dict_of_combos[key] = []
        
        # add to dict
        for combo in list_of_combos:
            for key in combo:
                dict_of_combos[key].append(combo[key])

        inputTable = {}

        for groupName in dict_of_combos:
            value = dict_of_combos[groupName]

            inputTable['{}-{}'.format(InputFileKeyword.variable, groupName)] = value

            if groupName in bracingGroups:
                bg = bracingGroups[groupName]
                print(groupName)
                for panel in bg.assignments:
                    pName = str(panel)
                    print(pName)
                    inputTable['{}-{}'.format(pName, InputFileKeyword.bracing)] = value

            elif groupName in sectionGroups:
                sg = sectionGroups[groupName]
                for memberId in sg.assignments:
                    inputTable['{}-{}'.format(InputFileKeyword.member, memberId)] = value

            elif groupName in areaSectionGroups:
                asg = areaSectionGroups[groupName]
                print(groupName)
                for panel in asg.assignments:
                    pName = str(panel)
                    print(pName)
                    inputTable['{}-{}'.format(pName, InputFileKeyword.shearWall)] = value

        # Convert list of dicts
        tower_enum = [i for i in range(1,len(list_of_combos)+1)]
        inputTable['towerNumber'] = tower_enum

        self.tower.inputTable = inputTable

        # Save inputTable
        filewriter = FileWriter(self.fileLoc, self.tower)
        try:
            filewriter.writeInputTable(self.tower.inputTable)
        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to create input table')
            self.close()

        self.run = False

addProgress
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The **addProgress** function updates a progress bar within the application window by incrementing a counter variable, which ranges from 0 to 100, to represent the progress of a certain task. When the counter reaches 100, it sets a flag to indicate that the task is complete.

.. code-block:: python

        def addProgress(self): 
        if self.counter <= 100: # counter's max = 101
            self.counter += 1

        if self.counter == 100:
            self.run = True

        self.progressBar.setValue(self.counter)






