import Model    # contains tower design components
import ProjectSettings  # contains data in project settings
from Definition import *    # file extensions
import pandas as pd  # use data frame to write files

import os   # create new directory

class FileWriter:
    def __init__(self, fileLoc, tower, psData):
        self.mainFileLoc = fileLoc
        self.folderLoc = fileLoc.replace('.ab', '')

        self.tower = tower
        self.psData = psData

        # Create new directory for data
        try:
            os.mkdir(self.folderLoc)
        except:
            pass

    def writeFiles(self):
        ''' Wrapper function to write all files '''
        self.writeMainFile()

        self.writeProjectSettings()
        self.writeFloorPlans()
        self.writePanels()

    def writeMainFile(self):
        ''' Write paths for other files ''' 
        with open(self.mainFileLoc, 'w') as mainFile:
            mainFile.write('#PATHS')
            mainFile.write('\n')

            mainFile.write('Project_settings,')
            mainFile.write(self.folderLoc + FileExtension.projectSettings)
            mainFile.write(',\n')

            mainFile.write('Floor_plans,')
            mainFile.write(self.folderLoc + FileExtension.floorPlan)
            mainFile.write(',\n')

            mainFile.write('Panels,')
            mainFile.write(self.folderLoc + FileExtension.panel)
            mainFile.write(',\n')

    def writeProjectSettings(self):
        ''' Write project settings data to file '''
        projectSettingsLoc = self.folderLoc + FileExtension.projectSettings
        psData = self.psData

        with open(projectSettingsLoc, 'w') as psFile:

            psFile.write('#PROJECT_SETTINGS')
            psFile.write('\n')

            psFile.write('tower_elevs,')
            for elev in psData.floorElevs:
                psFile.write(str(elev) + ' ')
            psFile.write(',\n')

            psFile.write('sect_props,')
            for sect in psData.sectionProps:
                psFile.write(str(sect) + ' ')
            psFile.write(',\n')

            psFile.write('gm,' + str(psData.groundMotion))
            psFile.write(',\n')

            psFile.write('analyis,' + str(psData.analysisType))
            psFile.write(',\n')

            psFile.write('modelLoc,' + str(psData.SAPModelLoc))
            psFile.write(',\n')

            psFile.write('modelName,'+ str(psData.modelName))
            psFile.write(',\n')

            psFile.write('renderX,' + str(psData.renderX) + ',\n')
            psFile.write('renderY,' + str(psData.renderY) + ',\n')
            psFile.write('renderZ,' + str(psData.renderZ) + ',\n')

    def writeFloorPlans(self):
        ''' Write floor plans to file '''
        floorPlanLoc = self.folderLoc + FileExtension.floorPlan
        tower = self.tower
        floorPlans = tower.floorPlans

        floorPlanData = {
            'floorPlanName':[],
            'elevation':[],
            'x':[],
            'y':[],
        }

        for fpName in floorPlans:
            floorPlan = floorPlans[fpName]
            for node in floorPlan.nodes:
                # elevations
                elevs = ''
                for elev in floorPlan.elevations:
                    elevs = elevs + str(elev) + ' '

                floorPlanData['floorPlanName'].append(str(fpName))
                floorPlanData['elevation'].append(elevs)
                floorPlanData['x'].append(str(node.x))
                floorPlanData['y'].append(str(node.y))

        df = pd.DataFrame(floorPlanData)
        df.to_csv(floorPlanLoc)

    def writePanels(self):
        ''' Write panels to file '''
        panelLoc = self.folderLoc + FileExtension.panel
        tower = self.tower
        panels = tower.panels

        panelData = {
            'panelName':[],
            'nodeLocation':[],
            'x':[],
            'y':[],
            'z':[],
        }

        for pName in panels:
            panel = panels[pName]

            panelData['panelName'].append(str(pName))
            panelData['nodeLocation'].append('lowerLeft')
            panelData['x'].append(str(panel.lowerLeft.x))
            panelData['y'].append(str(panel.lowerLeft.y))
            panelData['z'].append(str(panel.lowerLeft.z))
            
            panelData['panelName'].append(str(pName))
            panelData['nodeLocation'].append('upperLeft')
            panelData['x'].append(str(panel.upperLeft.x))
            panelData['y'].append(str(panel.upperLeft.y))
            panelData['z'].append(str(panel.upperLeft.z))
            
            panelData['panelName'].append(str(pName))
            panelData['nodeLocation'].append('upperRight')
            panelData['x'].append(str(panel.upperRight.x))
            panelData['y'].append(str(panel.upperRight.y))
            panelData['z'].append(str(panel.upperRight.z))
            
            panelData['panelName'].append(str(pName))
            panelData['nodeLocation'].append('lowerRight')
            panelData['x'].append(str(panel.lowerRight.x))
            panelData['y'].append(str(panel.lowerRight.y))
            panelData['z'].append(str(panel.lowerRight.z))

        df = pd.DataFrame(panelData)
        df.to_csv(panelLoc)