from Model import * # contains tower design components
import ProjectSettings  # contains data in project settings
import AssignBracingDesign
import pandas as pd  # use data frame to write files

class FileReader:
    def __init__(self, fileLoc, tower, psData, bracings, assignmentData):
        self.mainFileLoc = fileLoc
        self.tower = tower
        self.psData = psData
        self.bracings = bracings
        self.assignmentData = assignmentData

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
                elif fileType == 'Bracings':
                    self.readBracings(path)
                elif fileType == 'Panel_assignments':
                    self.readAssignments(path)

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

        for row in floorPlanData['floorPlanName']:
            fpName = str(floorPlanData['floorPlanName'][row])
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

            self.tower.addFloorPlan(floorPlan)

        # Make sure members are generated
        for fpName in floorPlans:
            floorPlan = floorPlans[fpName]
            floorPlan.generateMembersfromNodes()

    def readBracings(self, path):
        df = pd.read_csv(path)
        bracingData = df.to_dict()

        bracings = self.tower.bracings

        for row in bracingData['bracingName']:
            bcName = bracingData['bracingName'][row]
            x1 = float(bracingData['x1'][row])
            x2 = float(bracingData['x2'][row])
            y1 = float(bracingData['y1'][row])
            y2 = float(bracingData['y2'][row])
            material = bracingData['material'][row]

            if not (bcName in bracings):
                newBracing = Bracing(bcName)
                self.tower.addBracing(newBracing)

            node1 = Node(x1,y1)
            node2 = Node(x2,y2)

            bracing = bracings[bcName]
            bracing.addNodes(node1, node2)

            self.tower.addBracing(bracing)

        # Make sure members are generated
        for bcName in bracings:
            bracing = bracings[bcName]
            bracing.generateMembersfromNodes()

    def readAssignments(self, path):
        df = pd.read_csv(path)
        assignmentData = df.to_dict()
        
        assignments = self.tower.assignments

        for row in assignmentData['panelName']:
            amName = assignmentData['panelName'][row]
            bracingDesign = assignmentData['bracingDesign'][row]

            if not (amName in assignments):
                newAssignment = Assignment(amName)
                self.tower.addAssignment(newAssignment)

            assignment = assignments[amName]
            self.tower.addAssignment(assignment)