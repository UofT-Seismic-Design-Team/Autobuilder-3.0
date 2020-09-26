import Model    # contains tower design components
import ProjectSettings  # contains data in project settings
from Definition import *    # file extensions

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
        ''' Wrapper method to write all files '''
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

        with open(floorPlanLoc, 'w') as fpFile:
            floorPlans = tower.floorPlans
            fpFile.write('#FLOOR_PLANS\n')
            fpFile.write('numFPlans,' + str(len(floorPlans)) + ',\n')
            fpFile.write('\n')

            for fpName in floorPlans:
                floorPlan = floorPlans[fpName]
                numNodes = len(floorPlan.nodes)
                fpFile.write('planName,' + str(fpName) + ',\n')

                # Write elevations for the floor plan
                fpFile.write('elevs,')
                for elev in floorPlan.elevations:
                    fpFile.write(str(elev) + ' ')
                fpFile.write(',\n')

                fpFile.write('numNodes,' + str(numNodes) + ',\n')
                
                # Write nodes in floor plan
                i = 1
                for node in floorPlan.nodes:
                    fpFile.write(str(i) + ',' + str(node.x)+ ',' + str(node.y) + ',\n')
                    i += 1
                
                fpFile.write('\n')

    def writePanels(self):
        ''' Write panels to file '''
        panelLoc = self.folderLoc + FileExtension.panel
        tower = self.tower
        
        with open(panelLoc, 'w') as pFile:
            panels = tower.panels
            pFile.write('#PANELS\n')
            pFile.write('numPanels,' + str(len(panels)) + ',\n')
            pFile.write('\n')

            for pName in panels:
                panel = panels[pName]
                pFile.write('panelName,' + str(pName) + ',\n')

                # Write corners of panel to file
                pFile.write('lowerLeft,' + str(panel.lowerLeft.x) + ',' + str(panel.lowerLeft.y) + ',' + str(panel.lowerLeft.z) + ',\n')
                pFile.write('upperLeft,' + str(panel.upperLeft.x) + ',' + str(panel.upperLeft.y) + ',' + str(panel.upperLeft.z) + ',\n')
                pFile.write('upperRight,' + str(panel.upperRight.x) + ',' + str(panel.upperRight.y) + ',' + str(panel.upperRight.z) + ',\n')
                pFile.write('lowerRight,' + str(panel.lowerRight.x) + ',' + str(panel.lowerRight.y) + ',' + str(panel.lowerRight.z) + ',\n')

                pFile.write('\n')