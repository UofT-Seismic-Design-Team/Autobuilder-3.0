import os
import win32com.client
import random
from openpyxl import *
from openpyxl.utils.cell import get_column_letter, column_index_from_string
import string
import numpy
import shapely
import pandas
import sys
import comtypes.client
import comtypes.gen

from backend_classes import Tower, BracingScheme, Panel

# Read in csv files and save them to the objects
# Input strings for the locations of the csv files
def read_input_files(project_settings_path, input_table_path, bracing_schemes_path, panels_path):
    # Read csv into dataframes
    project_settings_df = pandas.read_csv(project_settings_path, header=0)
    project_settings_dict = project_settings_df.set_index("propertyName").T.to_dict('list')
    for key in project_settings_dict.keys():
        project_settings_dict[key] = project_settings_dict[key][0]
    input_table_df = pandas.read_csv(input_table_path, header=0)
    bracing_schemes_df = pandas.read_csv(bracing_schemes_path, header=0)
    panels_df = pandas.read_csv(panels_path, header=0)

    # Read dataframes into python classes
    # input tables to tower class
    all_towers = []
    panel_cols = [col for col in input_table_df.columns if "Panel" in col]
    member_cols = [col for col in input_table_df.columns if "Member" in col]
    input_table_df_panels = input_table_df[panel_cols]
    input_table_df_members = input_table_df[member_cols]

    input_table_list_panels = input_table_df_panels.values.tolist()
    input_table_list_members = input_table_df_members.values.tolist()

    num_towers = len(input_table_df.index)

    for tower_num in range(num_towers):
        # read panels
        panel_schemes = input_table_list_panels[tower_num]
        panel_schemes = {panel_cols[i]: panel_schemes[i] for i in range(len(panel_cols))}
        # read members
        member_secs = input_table_list_members[tower_num]
        member_secs = {member_cols[i]: member_secs[i] for i in range(len(member_cols))}
        all_towers.append(Tower(panel_schemes, member_secs))

    # bracing schemes to bracing schemes class
    all_bracing_schemes = {}
    bracing_schemes_names = bracing_schemes_df.bracingName.unique().tolist()
    for name in bracing_schemes_names:
        bracing_schemes_df_filtered = bracing_schemes_df[bracing_schemes_df["bracingName"] == name]
        bracing_elements = bracing_schemes_df_filtered[["x1", "y1", "x2", "y2"]].values.tolist()
        bracing_sections = bracing_schemes_df_filtered[["section"]].values.tolist()
        bracing_sections = [bracing_sections[i][0] for i in range(len(bracing_sections))]
        all_bracing_schemes[name] = BracingScheme(bracing_elements, bracing_sections)

    # panels to panel class
    all_panels = {}
    panel_names = panels_df.panelName.unique().tolist()
    ll_points_df = panels_df[panels_df["nodeLocation"] == "lowerLeft"]
    ul_points_df = panels_df[panels_df["nodeLocation"] == "upperLeft"]
    ur_points_df = panels_df[panels_df["nodeLocation"] == "upperRight"]
    lr_points_df = panels_df[panels_df["nodeLocation"] == "lowerRight"]

    for name in panel_names:
        ll_points_df_filtered = ll_points_df[ll_points_df["panelName"] == name]
        ul_points_df_filtered = ul_points_df[ul_points_df["panelName"] == name]
        ur_points_df_filtered = ur_points_df[ur_points_df["panelName"] == name]
        lr_points_df_filtered = lr_points_df[lr_points_df["panelName"] == name]
        ll_points = [ll_points_df_filtered["x"].values[0], ll_points_df_filtered["y"].values[0], ll_points_df_filtered["z"].values[0]]
        ul_points = [ul_points_df_filtered["x"].values[0], ul_points_df_filtered["y"].values[0], ul_points_df_filtered["z"].values[0]]
        ur_points = [ur_points_df_filtered["x"].values[0], ur_points_df_filtered["y"].values[0], ur_points_df_filtered["z"].values[0]]
        lr_points = [lr_points_df_filtered["x"].values[0], lr_points_df_filtered["y"].values[0], lr_points_df_filtered["z"].values[0]]
        all_panels[name] = Panel(ll_points, ul_points, ur_points, lr_points)

    return project_settings_dict, all_towers, all_bracing_schemes, all_panels

def start_sap2000(model_filepath, attach_to_instance=False, specify_path=False, program_path='C:\Program Files\Computers and Structures\SAP2000 22\SAP2000.exe'):
    # Start SAP2000
    # set the attach_to_instance flag to True to attach to an existing instance of the program
    # otherwise a new instance of the program will be started

    # set the specify_path flag to True to manually specify the path to SAP2000.exe
    # this allows for a connection to a version of SAP2000 other than the latest installation
    # otherwise the latest installed version of SAP2000 will be launched

    if attach_to_instance:
        # attach to a running instance of SAP2000
        try:
            # get the active SapObject
            mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
        except (OSError, comtypes.COMError):
            print("No running instance of the program found or failed to attach.")
            sys.exit(-1)
    else:
        # create API helper object
        helper = comtypes.client.CreateObject('SAP2000v1.Helper')
        helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
        if specify_path:
            try:
                # 'create an instance of the SAPObject from the specified path
                mySapObject = helper.CreateObject(ProgramPath)
            except (OSError, comtypes.COMError):
                print("Cannot start a new instance of the program from " + ProgramPath)
                sys.exit(-1)
        else:
            try:
                # create an instance of the SAPObject from the latest installed SAP2000
                mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
            except (OSError, comtypes.COMError):
                print("Cannot start a new instance of the program.")
                sys.exit(-1)
        # start SAP2000 application
        mySapObject.ApplicationStart()
        # create SapModel Object
        SapModel = mySapObject.SapModel
        # initialize model
        SapModel.InitializeNewModel()

        # open model
        ret = SapModel.File.OpenFile(model_filepath)
    return SapModel

#TESTING
projectSettingsPath = r"C:\Users\kotab\OneDrive - University of Toronto\Seismic\Autobuilder\projectSettings.csv"
inputTablePath = r"C:\Users\kotab\OneDrive - University of Toronto\Seismic\Autobuilder\inputTable.csv"
bracingSchemesPath = r"C:\Users\kotab\OneDrive - University of Toronto\Seismic\Autobuilder\bracing.csv"
panelsPath = r"C:\Users\kotab\OneDrive - University of Toronto\Seismic\Autobuilder\panels.csv"
inputData = read_input_files(projectSettingsPath, inputTablePath, bracingSchemesPath, panelsPath)
projectSettings = inputData[0]
allTowers = inputData[1]
allBracing = inputData[2]
allPanels = inputData[3]

i = 1
for tower in allTowers:
    print(i)
    print(tower.panel_bracing_schemes)
    print(tower.member_sections)
    i += 1

for panel in allPanels.keys():
    print(panel)
    '''
    print(allPanels[panel].lower_left)
    '''
    print(allPanels[panel].upper_left)
    print(allPanels[panel].upper_right)
    print(allPanels[panel].lower_right)

for bracing in allBracing.keys():
    print(bracing)
    print(allBracing[bracing].elements)
    print(allBracing[bracing].section_props)

ModelFilepath = r"C:\Users\kotab\Documents\Seismic\AB2 test\Tower 1 - Copy.sdb"
SapModel = start_sap2000(ModelFilepath)
