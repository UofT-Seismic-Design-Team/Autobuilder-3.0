from PyQt5.QtCore import *  # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # extends QtCore with GUI functionality
from PyQt5 import uic

from Model import * # Tower, Bracings, Bracing Groups, Section Groups etc.
from FileWriter import *    # save inputTable file

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

        self.GenerateInputTable()

        self.OkButton.clicked.connect(lambda x: self.close())

        # Update views -----------------------------
        timer  = QTimer(self)
        timer.setInterval(10) # period in miliseconds
        timer.timeout.connect(self.addProgress)
        timer.start()

    def addPanelsToBracingGroups(self):
        panels = self.tower.panels
        bracingGroups = self.tower.bracingGroups

        # clear existing panel assignments
        for bg in bracingGroups.values():
            bg.panelAssignments.clear()

        for pName in panels:
            panel = panels[pName]
            bgName = panel.bracingGroup

            if bgName != '':
                bracingGroups[bgName].addPanel(panel)

    def addMemberIdsToSectionGroups(self):
        member_ids = self.tower.member_ids
        sectionGroups = self.tower.sectionGroups

        # clear existing member id assignments
        for sg in sectionGroups.values():
            sg.memberIdAssignments.clear()

        for member_id in member_ids:
            sgName = member_ids[member_id]
            sectionGroups[sgName].addMemberId(member_id)

    def GenerateInputTable(self):
        self.addPanelsToBracingGroups()
        self.addMemberIdsToSectionGroups()

        bracingGroups = self.tower.bracingGroups
        sectionGroups = self.tower.sectionGroups

        dict_of_combos = {}

        for bgName in bracingGroups:
            bg = bracingGroups[bgName]
            if bg.panelAssignments: # only generate combo it's assigned to panel
                dict_of_combos[bgName] = []
                for bracing in bg.bracings:
                    dict_of_combos[bgName].append(str(bracing))

        for sgName in sectionGroups:
            sg = sectionGroups[sgName]
            if sg.memberIdAssignments: # only generate combo it's assigned to member
                dict_of_combos[sgName] = []
                for section in sg.sections:
                    dict_of_combos[sgName].append(str(section))

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

        for varName in dict_of_combos:
            values = dict_of_combos[varName]

            inputTable['Variable-' + varName] = values

            if varName in bracingGroups:
                bg = bracingGroups[varName]
                for panel in bg.panelAssignments:
                    pName = str(panel)
                    inputTable[pName] = values

            if varName in sectionGroups:
                sg = sectionGroups[varName]
                for memberId in sg.memberIdAssignments:
                    inputTable['Member '+ memberId] = values

        # Convert list of dicts
        tower_enum = [i for i in range(1,len(list_of_combos)+1)]
        self.tower.inputTable['towerNumber'] = tower_enum

        # for var in dict_of_combos:
        self.tower.inputTable.update(inputTable)

        print(inputTable)

        # Save inputTable
        filewriter = FileWriter(self.fileLoc, self.tower)
        filewriter.writeInputTable(self.tower.inputTable)

    def addProgress(self):
        self.counter += 1
        self.progressBar.setValue(self.counter)
