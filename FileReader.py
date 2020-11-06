from Model import * # contains tower design components
import ProjectSettings  # contains data in project settings
from Definition import StringToEnum  # StringToEnum conversion
import pandas as pd  # use data frame to read files

class FileReader:
    def __init__(self, fileLoc, tower, psData):
        self.mainFileLoc = fileLoc
        self.tower = tower
        self.psData = psData

    def readMainFile(self):
        with open(self.mainFileLoc, 'r') as mainFile:
            lines = mainFile.readlines()

            # Find header
            pSettings_index = lines.index('#Project_Settings\n')
            fPlans_index = lines.index('#Floor_Plans\n')
            panels_index = lines.index('#Panels\n')

            # Group data
            pSettings_data = lines[pSettings_index+1:fPlans_index-1]
            fPlans_data = lines[fPlans_index+1:panels_index-1]
            panels_data = lines[panels_index+1:-1]

            self.readProjectSettings(pSettings_data)
            self.readFloorPlans(fPlans_data)
            self.readPanels(panels_data)

    def readProjectSettings(self, data):
        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            var = line[0]
            val = line[1]
            
            if var == 'tower_elevs':
                elevs = val.split()
                for elev in elevs:
                    self.psData.floorElevs.append(float(elev)) # will update floor elevations in tower object simultaneously (pointer)

            elif var == 'sect_props':
                self.psData.sectionProps = val.split()

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

    def readPanels(self, data):
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
        floorPlans = self.tower.floorPlans

        for line in data[1:]: # skip header
            line = line.rstrip('\n').split(',') # remove trailing newline 

            fpName = line[0]
            elevation = line[1]
            x = float(line[2])
            y = float(line[3])

            if not (fpName in floorPlans):
                elevs = elevation.split()
                newFloorPlan = FloorPlan(fpName)
                for elev in elevs:
                    newFloorPlan.addElevation(float(elev))
                self.tower.addFloorPlan(newFloorPlan)

            floorPlan = floorPlans[fpName]
            floorPlan.addNode(Node(x,y))

        # Make sure members are generated
        for fpName in floorPlans:
            floorPlan = floorPlans[fpName]
            floorPlan.generateMembersfromNodes()
