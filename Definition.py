# Module to store constants

class Algebra:
    EPSILON = 0.0001

class FileExtension:
    projectSettings = '/projectSettings.csv'
    floorPlan = '/floorPlan.csv'
    panel = '/panel.csv'
    bracings = '/bracings.csv'

class EnumToString:
    ATYPE = {
        0: 'Time_History',
        1: 'RSA'
    }

class StringToEnum:
    ATYPE = {
        'Time_History': 0,
        'RSA': 1,
    }