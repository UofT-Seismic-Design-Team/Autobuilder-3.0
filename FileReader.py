from Model import * # contains tower design components
import ProjectSettings  # contains data in project settings
from Definition import MFHeader, StringToEnum

class FileReader:
    def __init__(self, fileLoc, tower, psData):
        self.mainFileLoc = fileLoc
        self.tower = tower
        self.psData = psData

    def readMainFile(self):
        with open(self.mainFileLoc, 'r') as mainFile:
            lines = mainFile.readlines()
 
            # value: [header, location of header, data --> list]
            comps = {
                'pSettings':[MFHeader.projectSettings+'\n',-1],
                'dSettings':[MFHeader.displaySettings+'\n',-1],
                'fPlans':[MFHeader.floorPlans+'\n',-1],
                'floors':[MFHeader.floors+'\n',-1],
                'panels':[MFHeader.panels+'\n',-1],
                'bracings':[MFHeader.bracings+'\n',-1],
                'bracingGroups':[MFHeader.bracingGroups+'\n',-1],
                'sectionGroups':[MFHeader.sectionGroups+'\n',-1],
                'b_assignments':[MFHeader.bracingAssignments+'\n',-1],
                's_assignments':[MFHeader.sectionAssignments+'\n',-1],
            }

            sortedHeaderLoc = []

            # Find header
            for comp in comps.values():
                if comp[0] in lines:
                    comp[1] = lines.index(comp[0])
                    sortedHeaderLoc.append(comp[1])

            sortedHeaderLoc.sort()

            # Group data
            for comp in comps.values():
                if comp[1] == -1: # skip if comp is missing
                    comp.append(None)
                    continue

                start = comp[1]+1 # skip header
                if start < sortedHeaderLoc[-1]:
                    end = sortedHeaderLoc[sortedHeaderLoc.index(comp[1])+1]-1
                    comp.append(lines[start:end])
                else:
                    comp.append(lines[start:])
            
            self.readProjectSettings(comps['pSettings'][2])
            self.readDisplaySettings(comps['dSettings'][2])
            self.readFloorPlans(comps['fPlans'][2])
            self.readFloors(comps['floors'][2])
            self.readPanels(comps['panels'][2])
            self.readBracings(comps['bracings'][2])
            self.readBracingGroups(comps['bracingGroups'][2])
            self.readSectionGroups(comps['sectionGroups'][2])
            self.readBracingAssignments(comps['b_assignments'][2])
            self.readSectionAssignments(comps['s_assignments'][2])
            
    def readProjectSettings(self, data):
        if not data:
            return None
        
        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            var = line[0]
            val = line[1]
            
            if var == 'tower_elevs':
                elevs = val.split()
                for elev in elevs:
                    self.psData.floorElevs.append(float(elev)) # will update floor elevations in tower object simultaneously (pointer)

            elif var == 'sect_props':
                temp = val.split()

                name = temp[0]
                rank = int(temp[1])
                sect = Section(name, rank)

                self.psData.sections[name] = sect

            elif var == 'gm':
                self.psData.groundMotion = (val == 'True') # return True if the value is 'True'

            elif var == 'analysis':
                self.psData.analysisType = StringToEnum.ATYPE[val]

            elif var == 'modelLoc':
                self.psData.SAPModelLoc = val

            elif var == 'modelName':
                self.psData.modelName = val
            
            elif var == 'renderX':
                self.psData.renderX = float(val)

            elif var == 'renderY':
                self.psData.renderY = float(val)

            elif var == 'renderZ':
                self.psData.renderZ = float(val)

            elif var == 'SAPPath':
                self.psData.SAPPath = val

            elif var == 'nodesList':
                self.psData.nodesList = val.split()

            elif var == 'renderZ':
                self.psData.renderZ = float(val)

    def readDisplaySettings(self, data):
        if not data:
            return None

        dSettings = self.tower.displaySettings

        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline

            var = line[0]
            val = line[1]

            if var == '2D_pName':
                dSettings.pName = (val == 'True')

            elif var == '2D_pLength':
                dSettings.pLength = (val == 'True') 

    def readPanels(self, data):
        if not data:
            return None

        panels = self.tower.panels

        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            pName = line[0]
            nodeLoc = line[1]
            x = float(line[2])
            y = float(line[3])
            z = float(line[4])

            if not (pName in panels):
                newPanel = Panel(pName)
                self.tower.addPanel(newPanel)

            panel = panels[pName]
            
            if nodeLoc == 'lowerLeft':
                panel.lowerLeft.setLocation(x, y, z)
            elif nodeLoc == 'upperLeft':
                panel.upperLeft.setLocation(x, y, z)
            elif nodeLoc == 'upperRight':
                panel.upperRight.setLocation(x, y, z)
            elif nodeLoc == 'lowerRight':
                panel.lowerRight.setLocation(x, y, z)

    def readFloorPlans(self, data):
        if not data:
            return None

        floorPlans = self.tower.floorPlans
        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            fpName = line[0]

            if not (fpName in floorPlans):
                newFloorPlan = FloorPlan(fpName)
                self.tower.addFloorPlan(newFloorPlan)

            floorPlan = floorPlans[fpName]

            isNode = line[1] != Constants.filler
            if isNode:
                x = float(line[1])
                y = float(line[2])
                bot = line[3]
                top = line[4]
                floorPlan.addNode(Node(x,y))

                nodeIndex = len(floorPlan.nodes) - 1

                if bot in floorPlan.bottomConnections:
                    floorPlan.bottomConnections[bot].append(nodeIndex)
                else:
                    floorPlan.bottomConnections[bot] = [nodeIndex]

                if top in floorPlan.topConnections:
                    floorPlan.topConnections[top].append(nodeIndex)
                else:
                    floorPlan.topConnections[top] = [nodeIndex]

            # for floor plan members
            else:
                start = int(line[5])
                end = int(line[6])

                floorPlan.nodePairs.append([start, end])
                floorPlan.generateMemberFromNodePair(-1)

            self.tower.addFloorPlan(floorPlan)

    def readFloors(self, data):
        if not data:
            return None

        self.tower.defineFloors()

        floors = self.tower.floors
        floorPlans = self.tower.floorPlans
        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            elev = float(line[0])
            fpNames = line[1]
            comX = float(line[2])
            comY = float(line[3])

            floor = floors[elev]
            fpNames = fpNames.split()
            for fpName in fpNames:
                floor.addFloorPlan(floorPlans[fpName])

            floor.comX = comX
            floor.comY = comY

    def readBracings(self, data):
        if not data:
            return None

        bracings = self.tower.bracings
        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            bcName = line[0]
            x1 = float(line[1])
            y1 = float(line[2])
            x2 = float(line[3])
            y2 = float(line[4])
            material = str(line[5])

            if not (bcName in bracings):
                newBracing = Bracing(bcName)
                self.tower.addBracing(newBracing)

            bracing = bracings[bcName]

            node1 = Node(x1,y1)
            node2 = Node(x2,y2)
            bracing.addNodes(node1, node2)
            bracing.addMat(material)

            self.tower.addBracing(bracing)

        # Make sure members are generated
        for bcName in bracings:
            bracing = bracings[bcName]
            bracing.generateMembersfromNodes()

    def readBracingGroups(self, data):
        if not data:
            return None

        bracingGroups = self.tower.bracingGroups
        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            groupName = str(line[0])
            bracing = str(line[1])

            if not (groupName in bracingGroups):
                newGroup = BracingGroup(groupName)
                self.tower.addBracingGroup(newGroup)

            bracingGroup = bracingGroups[groupName]
            bracingGroup.addBracing(bracing)
            self.tower.addBracingGroup(bracingGroup)

    def readSectionGroups(self, data):
        if not data:
            return None

        sectionGroups = self.tower.sectionGroups
        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            groupName = str(line[0])
            section = str(line[1])

            if not (groupName in sectionGroups):
                newGroup = SectionGroup(groupName)
                self.tower.addSectionGroup(newGroup)

            sectionGroup = sectionGroups[groupName]
            sectionGroup.addSection(section)
            self.tower.addSectionGroup(sectionGroup)

    def readBracingAssignments(self, data):
        if not data:
            return None

        panels = self.tower.panels
        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            panelName = str(line[0])
            bGroup = str(line[1])

            for panel in panels:
                if panelName == panel:
                    panels[panel].addBracingAssignment(bGroup)

    def readSectionAssignments(self, data):
        if not data:
            return None

        member_ids = self.tower.member_ids
        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            member_id = str(line[0])
            sGroup = str(line[1])

            member_ids[member_id] = sGroup