import Model    # contains tower design components
import ProjectSettings  # contains data in project settings
from Definition import *    # file extensions, EnumToString conversion
import pandas as pd  # use data frame to write files

import json # testing

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

        self.writeProjectSettings()
        self.writeFloorPlans()
        self.writePanels()

        self.writeMainFile()

    def writeMainFile(self):
        psettings = ''
        projectSettingsLoc = self.folderLoc + FileExtension.projectSettings
        with open(projectSettingsLoc, 'r') as f:
            psettings = f.read()

        floorPlan = ''
        floorPlanLoc = self.folderLoc + FileExtension.floorPlan
        with open(floorPlanLoc, 'r') as f:
            floorPlan = f.read()

        panel = ''
        panelLoc = self.folderLoc + FileExtension.panel
        with open(panelLoc, 'r') as f:
            panel = f.read()

        with open(self.mainFileLoc, 'w') as mainFile:
            mainFile.write('#Project_Settings')
            mainFile.write('\n')
            mainFile.write(psettings)

            mainFile.write('\n')
            mainFile.write('#Floor_Plans')
            mainFile.write('\n')
            mainFile.write(floorPlan)

            mainFile.write('\n')
            mainFile.write('#Panels')
            mainFile.write('\n')
            mainFile.write(panel)


    def writeProjectSettings(self):
        ''' Write project settings data to file '''
        projectSettingsLoc = self.folderLoc + FileExtension.projectSettings
        psData = self.psData

        psData_dict = {
            'setting':[],
            'value':[],
        }

        psData_dict['setting'] = [
            'tower_elevs',
            'sect_props',
            'gm',
            'analysis',
            'modelLoc',
            'modelName',
            'renderX',
            'renderY',
            'renderZ',
        ]

        # Convert to string
        elevs = ' '.join([str(elev) for elev in psData.floorElevs])
        sectProps = ' '.join([str(sect) for sect in psData.sectionProps])
        aType = EnumToString.ATYPE[psData.analysisType]
        
        values = [
            elevs,
            sectProps,
            psData.groundMotion,
            aType,
            psData.SAPModelLoc,
            psData.modelName,
            psData.renderX,
            psData.renderY,
            psData.renderZ,
        ]

        psData_dict['value'] = [str(i) for i in values] # convert values into string

        df = pd.DataFrame(psData_dict)
        df.to_csv(projectSettingsLoc, index=False)

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
                elevs = ' '.join([str(elev) for elev in floorPlan.elevations])

                floorPlanData['floorPlanName'].append(str(fpName))
                floorPlanData['elevation'].append(elevs)
                floorPlanData['x'].append(str(node.x))
                floorPlanData['y'].append(str(node.y))

        df = pd.DataFrame(floorPlanData)
        df.to_csv(floorPlanLoc, index=False)

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
        df.to_csv(panelLoc, index=False)