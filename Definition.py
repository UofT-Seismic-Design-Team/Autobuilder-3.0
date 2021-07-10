# Module to store constants

class Algebra:
    EPSILON = 0.00001

class FileExtension:
    projectSettings = '/projectSettings.csv'
    displaySettings = '/displaySettings.csv'
    floorPlan = '/floorPlan.csv'
    floor = '/floor.csv'
    panel = '/panel.csv'
    bracings = '/bracings.csv'
    bracingGroups = '/bracingGroups.csv'
    sectionGroups = '/sectionGroups.csv'
    bracingAssignments = '/bracingAssignments.csv'
    sectionAssignments = '/sectionAssignments.csv'
    inputTable = '/inputTable.csv'
    SAPModels = '/SAP Models'

class MFHeader:
    ''' Main file header '''
    projectSettings = '#Project_Settings'
    displaySettings = '#Display_Settings'
    floorPlans = '#Floor_Plans'
    floors = '#Floors'
    panels = '#Panels'
    bracings = '#Bracings'
    bracingGroups = '#Bracing_Groups'
    sectionGroups = '#Section_Groups'
    bracingAssignments = '#Bracing_Assignments'
    sectionAssignments = '#Section_Assignments'

class EnumToString:
    ATYPE = {
        0: 'Time_History',
        1: 'RSA',
    }

class StringToEnum:
    ATYPE = {
        'Time_History': 0,
        'RSA': 1,
    }

class Color:
    Node = {
        'MainMenu': 'green',
        'Bracing': 'green'
    }

    FloorPlan = { 
        'MainMenu': (
            'blue',
            'violet',
            'red',
            'pink',
            'purple',
        ),
    }

    Panel = {
        'MainMenu': 'orange',
    }

    Member = {
        'Bracing': 'grey',
    }

    Text = {
        'MainMenu': 'black',
    }

class SAP2000Constants:
    Units = {
        'kip_in_F': 3,
        'N_m_C': 10,
        'N_mm_C': 9,
    }

    MaxDecimalPlaces = 6

class Constants:
    g = 9.81 # in m/s^2

class UnitConversion:

    # relative to kg 
    # from xxx to kg
    # e.g. 1 lb = 0.453592 kg
    Mass = {
        'lb': 0.453592
    }
       
class View2DConstants:
    RATIO = 0.6 # constant for view to object ratio

    # Size constants --------------------
    MEMBER_SIZE = 5.0
    NODE_SIZE = 15.0
    TEXT_SIZE = 7.0
