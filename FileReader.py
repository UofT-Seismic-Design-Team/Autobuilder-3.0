from Model import * # contains tower design components
import ProjectSettings  # contains data in project settings
import AssignBracingDesign

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
                elif fileType == 'Bracings':
                    self.readBracings(path)

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
        with open(path, 'r') as pFile:
            header = pFile.readline()
            numPanels = int(pFile.readline().split(',')[1])

            # add panels to tower
            for i in range(numPanels):
                junk = pFile.readline()

                panelName = pFile.readline().split(',')[1]
                panel = Panel(panelName)

                corners = []

                for i in range(4):
                    corner = pFile.readline().split(',')[1:-1]
                    x, y, z = [float(i) for i in corner]
                    corners.append(Node(x, y, z))

                lLeft, uLeft, uRight, lRight = corners
                panel.definePanelWithNodes(lLeft, uLeft, uRight,lRight)

                self.tower.addPanel(panel)

    def readFloorPlans(self, path):
        with open(path, 'r') as fpFile:
            header = fpFile.readline()
            numFPlans = int(fpFile.readline().split(',')[1])

            # add floor plans to tower
            for i in range(numFPlans):
                junk = fpFile.readline()

                planName = fpFile.readline().split(',')[1]
                floorPlan = FloorPlan(planName)

                elevs = fpFile.readline().split(',')[1]
                elevs = elevs.split(' ')[:-1] # remove the last empty element
                for elev in elevs:
                    floorPlan.addElevation(float(elev))

                numNodes = int(fpFile.readline().split(',')[1])

                for j in range(numNodes):
                    nodeInfo = fpFile.readline().split(',')[1:]

                    x = float(nodeInfo[0])
                    y = float(nodeInfo[1])

                    node = Node(x, y)
                    floorPlan.addNode(node)

                floorPlan.generateMemebersfromNodes()

                self.tower.addFloorPlan(floorPlan)

    def readBracings(self, path):
        with open(path, 'r') as brFile:
            header = brFile.readline()
            numBracings = int(brFile.readline().split(',')[1])

            # add possible bracing schemes
            for i in range(numBracings):
                junk = brFile.readline()

                bracingName = brFile.readline().split(',')[1]
                bracing = Bracing(bracingName)

                numMembers = int(brFile.readline().split(',')[1])

                for j in range(numMembers):
                    memberInfo = brFile.readline().split(',')[1:]
                    
                    x1 = float(memberInfo[0])
                    y1 = float(memberInfo[1])
                    x2 = float(memberInfo[2])
                    y2 = float(memberInfo[3])

                    node1 = Node(x1,y1)
                    node2 = Node(x2,y2)

                    bracing.addNodes(node1,node2)
                
                bracing.generateMembersfromNodes()

                self.tower.addBracings(bracing)
