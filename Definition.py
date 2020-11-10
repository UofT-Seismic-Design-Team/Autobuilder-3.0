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
        'MainMenu': 'orange'
    }

    Member = {
        'Bracing': 'grey'
    }

    Text = {
        'MainMenu': 'orange'
    }

       
class View2DConstants:
    RATIO = 0.6 # constant for view to object ratio

    # Size constants --------------------
    MEMBER_SIZE = 5.0
    NODE_SIZE = 15.0
    TEXT_SIZE = 7.0
