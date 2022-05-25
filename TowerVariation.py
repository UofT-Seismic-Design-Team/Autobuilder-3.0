from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5 import uic

from Model import * # Tower, Bracings, Bracing Groups, Section Groups etc.
from FileWriter import *    # save inputTable file
from Definition import InputFileKeyword

import resources    # For icons and UIs

from itertools import product

# 1. Get the tower object
# 2. Get bracing and section Groups - OK
# 3. Iterate over all panels (and members?) and add the panels and members to the variable (i.e. bracing / section groups) - OK
# 4. Create all combinations of the variables - OK
# 5. Apply combinations to panels and members and create tower variations
# 6. Save tower variations as dictionary - OK

# Goal: Generate a dict with panels and members as keys, and bracings and sections as values

class GenerateTower(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the UI Page
        fileh = QFile(':/UI/autobuilder_generatetower.ui')
        fileh.open(QFile.ReadOnly)
        uic.loadUi(fileh, self)
        fileh.close()

        self.tower = args[0].tower
        self.fileLoc = args[0].fileLoc

        self.counter = 0
        self.run = False

        # # TODO: maybe create an enum class in Definition module
        # self.variblesEnum = {
        #     'BRACING': 0,
        #     'SECTION': 1,
        #     'AREA_SECTION': 2,
        # }

        # # Iterables
        # self.componments = [self.tower.panels, self.tower.member_ids, self.tower.panels]
        # self.varGroups = [self.tower.bracingGroups, self.tower.sectionGroups, self.tower.areaSectionGroups]

        self.OkButton.clicked.connect(lambda x: self.close())

        # Update views -----------------------------
        timer  = QTimer(self)
        timer.setInterval(10) # period in miliseconds
        timer.timeout.connect(self.addProgress)
        timer.timeout.connect(self.GenerateInputTable)
        timer.start()

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

    def addMemberIdsToSectionGroups(self):
        member_ids = self.tower.member_ids
        sectionGroups = self.tower.sectionGroups

        # clear existing member id assignments
        for sg in sectionGroups.values():
            sg.assignments.clear()

        for member_id in member_ids:
            sgName = member_ids[member_id]
            sectionGroups[sgName].addAssignment(member_id)

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
        self.tower.inputTable['towerNumber'] = tower_enum

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

    def addProgress(self):
        if self.counter <= 100: # counter's max = 101
            self.counter += 1

        if self.counter == 100:
            self.run = True

        self.progressBar.setValue(self.counter)

        
