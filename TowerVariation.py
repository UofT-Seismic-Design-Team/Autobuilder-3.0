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

        # redundant; may be useful later
        # use the inputtable in tower class
        #self.inputTable = {}    # keys: "tower", panel, member id; values: num, bracing, section
        #self.combos = () # all combinations of the variables

        self.GenerateInputTable()

        self.OkButton.clicked.connect(lambda x: self.close())

        # Update views -----------------------------
        timer  = QTimer(self)
        timer.setInterval(10) # period in miliseconds
        timer.timeout.connect(self.addProgress) # updateGL calls paintGL automatically!!
        timer.start()

    def addPanelsToBracingGroups(self):
        panels = self.tower.panels
        bracingGroups = self.tower.bracingGroups

        for pName in panels:
            panel = panels[pName]
            bgName = panel.bracingGroup

            if bgName != '':
                bracingGroups[bgName].addPanel(panel)

    def addMemberIdsToSectionGroups(self):
        member_ids = self.tower.member_ids
        sectionGroups = self.tower.sectionGroups

        for member_id in member_ids:
            sgName = member_ids[member_id]
            sectionGroups[sgName].addMemberId(member_id)

    # def GenerateCombo(self):
    #     bracingGroups = self.tower.bracingGroups
    #     sectionGroups = self.tower.sectionGroups

    #     # create lists of variables
    #     bgs = list(bracingGroups.values())
    #     sgs = list(sectionGroups.values())

    #     # create lists for combinations (MUST BE IN THIS ORDER)
    #     variables = []
    #     for bg in bgs:
    #         variables.append([str(b) for b in bg.bracings])
    #     for sg in sgs:
    #         variables.append([str(s) for s in sg.sections])

    #     # create combinations
    #     self.combos = tuple(product(*variables))

    def GenerateInputTable(self):
        self.addPanelsToBracingGroups()
        self.addMemberIdsToSectionGroups()

        bracingGroups = self.tower.bracingGroups
        sectionGroups = self.tower.sectionGroups

        dict_of_combos = {}

        for key in bracingGroups:
            for panel in bracingGroups[key].panelAssignments:
                dict_of_combos[str(panel)] = []
                for bracing in bracingGroups[key].bracings:
                    dict_of_combos[str(panel)].append(str(bracing))

        for key in sectionGroups:
            for member in sectionGroups[key].memberIdAssignments:
                dict_of_combos['Member '+ member] = []
                for section in sectionGroups[key].sections:
                    dict_of_combos['Member '+ member].append(str(section))

        list_of_combos = [dict(zip(dict_of_combos.keys(),v)) for v in product(*dict_of_combos.values())]

        # reset dict
        for key in dict_of_combos:
            dict_of_combos[key] = []
        
        # add to dict
        for combo in list_of_combos:
            for key in combo:
                dict_of_combos[key].append(combo[key])

        # Convert list of dicts
        tower_enum = [i for i in range(1,len(list_of_combos)+1)]
        self.tower.inputTable['towerNumber'] = tower_enum

        # for var in dict_of_combos:
        self.tower.inputTable.update(dict_of_combos)

        # Update inputTable in tower
        self.tower.updateInputTable(self.tower.inputTable)

        # Save inputTable
        filewriter = FileWriter(self.fileLoc, self.tower)
        filewriter.writeInputTable(self.tower.inputTable)
   
    # def GenerateInputTable(self):
    #     self.addPanelsToBracingGroups()
    #     self.addMemberIdsToSectionGroups()
    #     self.GenerateCombo()

    #     bracingGroups = self.tower.bracingGroups
    #     sectionGroups = self.tower.sectionGroups

    #     # create lists of variables
    #     bgs = list(bracingGroups.values())
    #     sgs = list(sectionGroups.values())

    #     # create a list of dicts (MUST BE IN THIS ORDER)
    #     towerVariations = []

    #     for bg in bgs:
    #         panels = bg.panelAssignments
    #         var = {}
    #         for panel in panels:
    #             var[str(panel)] = []
    #         towerVariations.append(var)

    #     for sg in sgs:
    #         member_ids = sg.memberIdAssignments
    #         var = {}
    #         for member_id in member_ids:
    #             var['Member ' + member_id] = []
    #         towerVariations.append(var)

    #     # Apply combinations
    #     for combo in self.combos:
    #         for i, dVar in enumerate(towerVariations):
    #             param = combo[i]
    #             for assignName in dVar:
    #                 dVar[assignName].append(param)

    #     # Convert list of dicts
    #     tower_enum = [i for i in range(1,len(self.combos)+1)]
    #     self.inputTable['towerNumber'] = tower_enum

    #     for var in towerVariations:
    #        self.inputTable.update(var)

    #     # Update inputTable in tower
    #     self.tower.updateInputTable(self.inputTable)

    #     # Save inputTable
    #     filewriter = FileWriter(self.fileLoc, self.tower)
    #     filewriter.writeInputTable(self.inputTable)

    def addProgress(self):
        self.counter += 1
        self.progressBar.setValue(self.counter)