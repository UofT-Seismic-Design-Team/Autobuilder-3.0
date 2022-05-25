import Model    # contains tower design components
import ProjectSettings  # contains data in project settings
import DisplaySettings  # contains data in display settings
from Definition import *    # file extensions, EnumToString conversion
import pandas as pd  # use data frame to write files
from Performance import * # tower performance data
from Message import *    # pop up window for illegal entries

import os   # create new directory

class FileWriter:
    def __init__(self, fileLoc, tower=None, psData=None):
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
        self.writeDisplaySettings()
        self.writeFloorPlans()
        self.writeFloors()
        self.writePanels()
        self.writeBracings()
        self.writeBracingGroups()
        self.writeSectionGroups()
        self.writeAreaSectionGroups()
        self.writeBracingAssignments()
        self.writeSectionAssignments()
        self.writeAreaSectionAssignments()

        self.writeMainFile()

    def writeMainFile(self):
        psettings = ''
        projectSettingsLoc = self.folderLoc + FileExtension.projectSettings
        with open(projectSettingsLoc, 'r') as f:
            psettings = f.read()

        dsettings = ''
        displaySettingsLoc = self.folderLoc + FileExtension.displaySettings
        with open(displaySettingsLoc, 'r') as f:
            dsettings = f.read()

        floorPlan = ''
        floorPlanLoc = self.folderLoc + FileExtension.floorPlan
        with open(floorPlanLoc, 'r') as f:
            floorPlan = f.read()

        floor = ''
        floorLoc = self.folderLoc + FileExtension.floor
        with open(floorLoc, 'r') as f:
            floor = f.read()

        panel = ''
        panelLoc = self.folderLoc + FileExtension.panel
        with open(panelLoc, 'r') as f:
            panel = f.read()

        bracings = ''
        bracingsLoc = self.folderLoc + FileExtension.bracings
        with open(bracingsLoc, 'r') as f:
            bracings = f.read()

        bGroups = ''
        bGroupsLoc = self.folderLoc + FileExtension.bracingGroups
        with open(bGroupsLoc, 'r') as f:
            bGroups = f.read()

        sGroups = ''
        sGroupsLoc = self.folderLoc + FileExtension.sectionGroups
        with open(sGroupsLoc, 'r') as f:
            sGroups = f.read()

        asGroups = ''
        asGroupsLoc = self.folderLoc + FileExtension.areaSectionGroups
        with open(asGroupsLoc, 'r') as f:
            asGroups = f.read()

        bAssignments = ''
        bAssignmentsLoc = self.folderLoc + FileExtension.bracingAssignments
        with open(bAssignmentsLoc, 'r') as f:
            bAssignments = f.read()
        
        sAssignments = ''
        sAssignmentsLoc = self.folderLoc + FileExtension.sectionAssignments
        with open(sAssignmentsLoc, 'r') as f:
            sAssignments = f.read()

        asAssignments = ''
        asAssignmentsLoc = self.folderLoc + FileExtension.areaSectionAssignments
        with open(asAssignmentsLoc, 'r') as f:
            asAssignments = f.read()

        headers = [
            MFHeader.projectSettings,
            MFHeader.displaySettings,
            MFHeader.floorPlans,
            MFHeader.floors,
            MFHeader.panels,
            MFHeader.bracings,
            MFHeader.bracingGroups,
            MFHeader.sectionGroups,
            MFHeader.areaSectionGroups,
            MFHeader.bracingAssignments,
            MFHeader.sectionAssignments,
            MFHeader.areaSectionAssignments,
        ]

        datasets = [
            psettings,
            dsettings,
            floorPlan,
            floor,
            panel,
            bracings,
            bGroups,
            sGroups,
            asGroups,
            bAssignments,
            sAssignments,
            asAssignments,
        ]

        with open(self.mainFileLoc, 'w') as mainFile:
            for i, header in enumerate(headers):
                 mainFile.write(header)
                 mainFile.write('\n')
                 mainFile.write(datasets[i])

                 if i == len(headers)-1: # avoid the unnecessary new line at the end
                     break

                 mainFile.write('\n')

    # TODO: move all strings to Definition module
    def writeProjectSettings(self):
        ''' Write project settings data to file '''

        projectSettingsLoc = self.folderLoc + FileExtension.projectSettings
        psData = self.psData

        psData_dict = {
            'setting':[],
            'value':[],
        }

        # Convert to string
        # elevations
        elevs = ' '.join([str(elev) for elev in psData.floorElevs])
        psData_dict['setting'].append('tower_elevs')
        psData_dict['value'].append(elevs)

        # sections
        for key in psData.sections:
            sect = psData.sections[key]
            psData_dict['setting'].append('sect_props')
            val = str(sect.name) + ' ' + str(sect.rank)
            psData_dict['value'].append(val)

        # area sections
        for key in psData.areaSections:
            sect = psData.areaSections[key]
            psData_dict['setting'].append('area_sect_props')
            val = str(sect.name) + ' ' + str(sect.rank)
            psData_dict['value'].append(val)

        # Other settings
        psKeys = [
            # Project Settings
            'gm',
            'analysis',
            'modelLoc',
            'modelName',
            'renderX',
            'renderY',
            'renderZ',
            'tensileStrength',
            'compressiveStrength',
            'shearStrength',

            # Run Towers
            'SAPPath',
            'nodesList',
            'footprint',
            'totalHeight',
            'totalMass',
            'forceReductionFactor',
            'gmIdentifier',
            'memberUtilizationId',
            'keepExistingMembers',
            'divideAllMembersAtIntersections',
            'toRun',
            'centreOfRigidity',
        ]
        
        values = [
            psData.groundMotion,
            EnumToString.ATYPE[psData.analysisType],
            psData.SAPModelLoc,
            psData.modelName,
            psData.renderX,
            psData.renderY,
            psData.renderZ,
            psData.tensileStrength,
            psData.compressiveStrength,
            psData.shearStrength,

            psData.SAPPath,
            ' '.join(psData.nodesList),
            psData.footprint,
            psData.totalHeight,
            psData.totalMass,
            psData.forceReductionFactor,
            psData.gmIdentifier,
            psData.memberUtilizationId,
            psData.keepExistingMembers,
            psData.divideAllMembersAtIntersections,
            psData.toRun,
            EnumToString.CRTYPE[psData.centreOfRigidity],
        ]

        for i, psKey in enumerate(psKeys):
            psData_dict['setting'].append(psKey)
            psData_dict['value'].append(values[i])

        df = pd.DataFrame(psData_dict)
        df.to_csv(projectSettingsLoc, index=False)

        try:
            df.to_csv(projectSettingsLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to create project settings')

    def writeDisplaySettings(self):
        ''' Write display settings to file '''
        displaySettingsLoc = self.folderLoc + FileExtension.displaySettings
        dSettings = self.tower.displaySettings

        dSettings_dict = {
            'setting':[],
            'value':[],
        }

        dsKeys = [
            '2D_pName',
            '2D_pLength',
        ]

        values = [
            dSettings.pName,
            dSettings.pLength,
        ]

        for i, dsKey in enumerate(dsKeys):
            dSettings_dict['setting'].append(dsKey)
            dSettings_dict['value'].append(values[i])

        df = pd.DataFrame(dSettings_dict)
        df.to_csv(displaySettingsLoc, index=False)

        try:
            df.to_csv(displaySettingsLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to create display settings')

    def writeFloorPlans(self):
        ''' Write floor plans to file '''
        floorPlanLoc = self.folderLoc + FileExtension.floorPlan
        tower = self.tower
        floorPlans = tower.floorPlans

        floorPlanData = {
            'floorPlanName':[],
            'x':[],
            'y':[],
            'bot':[],
            'top':[],
            'start':[],
            'end':[],
        }

        for fpName in floorPlans:
            floorPlan = floorPlans[fpName]

            botConnections = [0 for i in range(len(floorPlan.nodes))]
            for botLabel in floorPlan.bottomConnections:
                for index in floorPlan.bottomConnections[botLabel]:
                    botConnections[index] = botLabel

            topConnections = [0 for i in range(len(floorPlan.nodes))]
            for topLabel in floorPlan.topConnections:
                for index in floorPlan.topConnections[topLabel]:
                    topConnections[index] = topLabel

            for i, node in enumerate(floorPlan.nodes):
                floorPlanData['floorPlanName'].append(str(fpName))
                floorPlanData['x'].append(str(node.x))
                floorPlanData['y'].append(str(node.y))
                floorPlanData['bot'].append(str(botConnections[i]))
                floorPlanData['top'].append(str(topConnections[i]))
                floorPlanData['start'].append(Constants.filler)
                floorPlanData['end'].append(Constants.filler)

            for start, end in floorPlan.nodePairs:
                floorPlanData['floorPlanName'].append(str(fpName))
                floorPlanData['x'].append(Constants.filler)
                floorPlanData['y'].append(Constants.filler)
                floorPlanData['bot'].append(Constants.filler)
                floorPlanData['top'].append(Constants.filler)
                floorPlanData['start'].append(str(start))
                floorPlanData['end'].append(str(end))

        df = pd.DataFrame(floorPlanData)

        try:
            df.to_csv(floorPlanLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to create floor plan')

    def writeFloors(self):
        ''' Write floors to file '''
        floorLoc = self.folderLoc + FileExtension.floor
        floors = self.tower.floors

        floorData = {
            'elevation':[],
            'floorPlans':[],
            'comX':[],
            'comY':[],
        }

        for elev in floors:
            floor = floors[elev]
            fpNames = ' '.join([str(fp.name) for fp in floor.floorPlans])
            comX = floor.comX
            comY = floor.comY

            floorData['elevation'].append(str(elev))
            floorData['floorPlans'].append(fpNames)
            floorData['comX'].append(str(comX))
            floorData['comY'].append(str(comY))

        df = pd.DataFrame(floorData)

        try:
            df.to_csv(floorLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to save floor')

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

        try:
            df.to_csv(panelLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to save panels')

    def writeBracings(self):
        ''' Write Bracings to file '''
        bracingsLoc = self.folderLoc + FileExtension.bracings
        tower = self.tower
        bracings = tower.bracings

        bracingsData = {
            'bracingName':[],
            'x1':[],
            'y1':[],
            'x2':[],
            'y2':[],
            'material':[],
        }

        for bName in bracings:
            bracing = bracings[bName]
            for member in bracing.members:
                x1 = member.start_node.x
                y1 = member.start_node.y
                x2 = member.end_node.x
                y2 = member.end_node.y

                mat = member.material

                bracingsData['bracingName'].append(bName)
                bracingsData['x1'].append(str(x1))
                bracingsData['y1'].append(str(y1))
                bracingsData['x2'].append(str(x2))
                bracingsData['y2'].append(str(y2))
                bracingsData['material'].append(mat)

        df = pd.DataFrame(bracingsData)

        try:
            df.to_csv(bracingsLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to save bracings')

    def writeBracingGroups(self):
        ''' Write Bracing Groups to file '''
        bGroupsLoc = self.folderLoc + FileExtension.bracingGroups
        tower = self.tower
        bGroups = tower.bracingGroups
        print('bgroups', bGroups)

        bGroupsData = {
            'bracingGroup':[],
            'bracing':[],
        }

        for bGroupName in bGroups:
            bGroup = bGroups[bGroupName]

            for bName in bGroup.variables:
                bGroupsData['bracingGroup'].append(bGroupName)
                bGroupsData['bracing'].append(bName)

        df = pd.DataFrame(bGroupsData)

        try:
            df.to_csv(bGroupsLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to save bracing groups')

    def writeSectionGroups(self):
        ''' Write Section Groups to file '''
        sGroupsLoc = self.folderLoc + FileExtension.sectionGroups
        tower = self.tower
        sGroups = tower.sectionGroups

        sGroupsData = {
            'sectionGroup':[],
            'section':[],
        }

        for sGroupName in sGroups:
            sGroup = sGroups[sGroupName]

            for sName in sGroup.variables:
                sGroupsData['sectionGroup'].append(sGroupName)
                sGroupsData['section'].append(sName)

        df = pd.DataFrame(sGroupsData)

        try:
            df.to_csv(sGroupsLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to save section groups')

    def writeAreaSectionGroups(self):
        ''' Write Section Groups to file '''
        asGroupsLoc = self.folderLoc + FileExtension.areaSectionGroups
        tower = self.tower
        asGroups = tower.areaSectionGroups

        asGroupsData = {
            'areaSectionGroup':[],
            'areaSection':[],
        }

        for asGroupName in asGroups:
            asGroup = asGroups[asGroupName]

            for asName in asGroup.variables:
                asGroupsData['areaSectionGroup'].append(asGroupName)
                asGroupsData['areaSection'].append(asName)

        df = pd.DataFrame(asGroupsData)

        try:
            df.to_csv(asGroupsLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to save area section groups')

    def writeBracingAssignments(self):
        ''' Write Bracing Assignments to file '''
        bAssignmentsLoc = self.folderLoc + FileExtension.bracingAssignments
        tower = self.tower
        panels = tower.panels

        bAssignmentsData = {
            'panelName':[],
            'bracingGroup':[],
        }

        for pName in panels:
            panel = panels[pName]
            bGroup = panel.bracingGroup

            if bGroup:
                bAssignmentsData['panelName'].append(pName)
                bAssignmentsData['bracingGroup'].append(bGroup)

        df = pd.DataFrame(bAssignmentsData)

        try:
            df.to_csv(bAssignmentsLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to save bracing assignments')

    def writeSectionAssignments(self):
        ''' Write Section Assignments to file '''
        sAssignmentsLoc = self.folderLoc + FileExtension.sectionAssignments
        tower = self.tower
        member_ids = tower.member_ids

        sAssignmentsData = {
            'memberid':[],
            'sectionGroup':[],
        }

        for member_id in member_ids:
            sGroup = member_ids[member_id]

            sAssignmentsData['memberid'].append(member_id)
            sAssignmentsData['sectionGroup'].append(sGroup)

        df = pd.DataFrame(sAssignmentsData)

        try:
            df.to_csv(sAssignmentsLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to save section assignments')

    def writeAreaSectionAssignments(self):
        ''' Write Area Section Assignments to file '''
        asAssignmentsLoc = self.folderLoc + FileExtension.areaSectionAssignments
        tower = self.tower
        panels = tower.panels

        asAssignmentsData = {
            'panelName':[],
            'areaSectionGroup':[],
        }

        for pName in panels:
            panel = panels[pName]
            asGroup = panel.areaSectionGroup

            if asGroup:
                asAssignmentsData['panelName'].append(pName)
                asAssignmentsData['areaSectionGroup'].append(asGroup)

        df = pd.DataFrame(asAssignmentsData)

        try:
            df.to_csv(asAssignmentsLoc, index=False)

        except:
            warning = WarningMessage()
            warning.popUpErrorBox('Unable to save area section assignments')

    def writeInputTable(self, inputTable):
        ''' Write Input Table to file '''
        inputTableLoc = self.folderLoc + FileExtension.inputTable

        df = pd.DataFrame(inputTable)
        df.to_csv(inputTableLoc, index=False)

    def writeOutputTable(self, towerPerformances, logSignal=None):
        ''' Write tower performances to output file '''
        outputTableLoc = self.folderLoc + FileExtension.outputTable

        outputTable = {
            'towerNum': [],
        }
        towerAttrConst = [
            'totalWeight', 'period', 'maxEcc', 'avgEcc',
        ]

        towerAttrVarCombo = [
            'maxAcc','maxDisp','basesh', 'buildingCost', 'seismicCost',
        ]

        towerAttrVarFloor = [
            'CR',
        ]

        towerDCRs = [
            'tensionDCR', 'compDCR', 'shearDCR',
        ]

        for towerNum in towerPerformances:
            outputTable['towerNum'].append(towerNum)
            towerPerformance = towerPerformances[towerNum]

            for var in towerPerformance.variables:
                value = towerPerformance.variables[var]
                if var in outputTable:
                    outputTable[var].append(value)
                else:
                    outputTable[var] = [value]

            for attr in towerAttrConst:
                result = getattr(towerPerformance, attr)

                if attr in outputTable:
                    # column name for this result
                    outputTable[attr].append(result)
                else:
                    outputTable[attr] = [result]
                
            for attr in towerAttrVarCombo:
                results = getattr(towerPerformance, attr)

                for combo in results:
                    # column name for this result
                    resultName = combo + '-' + attr
                    result = results[combo]

                    if resultName in outputTable:
                        outputTable[resultName].append(result)

                    else:
                        outputTable[resultName] = [result]

            for attr in towerAttrVarFloor:
                results = getattr(towerPerformance, attr)

                for floor in results:
                    crX = str(results[floor][0])
                    crY = str(results[floor][1])
                
                    # column name for this result
                    crXName = str(floor) + ' - CRx'
                    crYName = str(floor) + ' - CRy'

                    if crXName in outputTable:
                        outputTable[crXName].append(crX)
                    else:
                        outputTable[crXName] = [crX]

                    if crYName in outputTable:
                        outputTable[crYName].append(crY)
                    else:
                        outputTable[crYName] = [crY]

            for attr in towerDCRs:
                result = getattr(towerPerformance, attr)

                if attr in outputTable:
                    # column name for this result
                    outputTable[attr].append(result)
                else:
                    outputTable[attr] = [result]

                

        df = pd.DataFrame(outputTable)

        try:
            df.to_csv(outputTableLoc, index=False)

        except:
            if logSignal:
                logSignal.emit('Fail to generate output table')
            else:
                # NOTE: no warning message for SAPModelCreation due to thread safety issues
                warning = WarningMessage()
                warning.popUpErrorBox('Unable to save output table')