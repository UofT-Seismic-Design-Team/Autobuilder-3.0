from Model import * # contains tower design components
import ProjectSettings  # contains data in project settings
import pandas as pd  # use data frame to write files

class FileReader:
    def __init__(self, fileLoc, tower, psData):
        self.mainFileLoc = fileLoc
        self.tower = tower
        self.psData = psData

    def readMainFile(self):
        with open(self.mainFileLoc, 'r') as mainFile:
            header = mainFile.readline()
            lines = mainFile.readlines()

            for line in lines:
                line = line.split(',')
                fileType = line[0]
                path = line[1]

                if fileType == 'Project_settings':
                    self.readProjectSettings(path)
                elif fileType == 'Floor_plans':
                    self.readFloorPlans(path)
                elif fileType == 'Panels':
                    self.readPanels(path)

                else:
                    pass
    
    def readProjectSettings(self, path):
        with open(path, 'r') as psFile:
            header = psFile.readline()
            lines = psFile.readlines()

            for line in lines:
                line = line.split(',')
                var = line[0]
                val = line[1]

                if var == 'tower_elevs':
                    elevs = val.split()

                    for elev in elevs:
                        self.psData.floorElevs.append(float(elev)) # will update floor elevations in tower object simultaneously (pointer)

                elif var == 'sect_props':
                    self.psData.sectionProps = val.split()

                elif var == 'gm':
                    if val == 'True':
                        gm = True
                    else:
                        gm = False

                    self.psData.groundMotion = gm

                elif var == 'analysis':
                    self.psData.analysisType = int(val)

                elif var == 'modelLoc':
                    self.psData.modelLoc = val

                elif var == 'modelName':
                    self.psData.modelName = val
                
                elif var == 'renderX':
                    self.psData.renderX = float(val)

                elif var == 'renderY':
                    self.psData.renderY = float(val)

                elif var == 'renderZ':
                    self.psData.renderZ = float(val)
    
    def readPanels(self, path):
        df = pd.read_csv(path)
        panelData = df.to_dict()

        panels = self.tower.panels

        for row in panelData['panelName']:
            pName = panelData['panelName'][row]
            nodeLoc = panelData['nodeLocation'][row]
            x = float(panelData['x'][row])
            y = float(panelData['y'][row])
            z = float(panelData['z'][row])

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

    def readFloorPlans(self, path):
        df = pd.read_csv(path)
        floorPlanData = df.to_dict()

        floorPlans = self.tower.floorPlans

        floorPlans = self.tower.floorPlans
        for row in floorPlanData['floorPlanName']:
            fpName = floorPlanData['floorPlanName'][row]
            elevation = floorPlanData['elevation'][row]
            x = float(floorPlanData['x'][row])
            y = float(floorPlanData['y'][row])

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
