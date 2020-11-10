from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality

from Model import *
from ProjectSettings import *
from Definition import *

import math as m

COLORS_FLOOR_PLAN = ['blue', 'violet']
COLORS_PANEL = ['orange']
COLORS_NODE = ['green']
COLORS_BRACING = ['grey']

# New 2D view

# View Objects --------------------------------
class ViewObject:
    def __init__(self):
        self.color = ''
        self.size = 1.0
        self.dim_x = 1.0
        self.dim_y = 1.0

    def setColor(self, color):
        self.color = color

    def setSize(self, size):
        self.size = size

    def setDimX(self, x):
        self.dim_x = x

    def setDimY(self, y):
        self.dim_y = y

    def findDimX(self):
        # Assume x is positive
        x_all = []
        for member in self.members:
            x_all.append(member.start_node.x)
            x_all.append(member.end_node.x)
        return max(x_all)

    def findDimY(self):
        # Assume y is positive
        y_all = []
        for member in self.members:
            y_all.append(member.start_node.y)
            y_all.append(member.end_node.y)
        return max(y_all)

class ViewMember(ViewObject):
    def __init__(self):
        super().__init__()

        self.members = []

    def addMember(self, member):
        self.members.append(member)

class ViewNode(ViewObject):
    def __init__(self):
        super().__init__()

        self.nodes = []
    
    def addNode(self, node):
        self.nodes.append(node)

class ViewText(ViewObject):
    def __init__(self):
        super().__init__()

        self.texts = []
        self.members = []
        self.location = Node() # x and y range from 0 to 1
        # Note: make sure the text correpsonds to the right member
    
    def addText(self, text):
        self.texts.append(text)

    def addMember(self, member):
        self.members.append(member)

    def setLocation(self, location):
        self.location = location

# View2D Widget -------------------------------
class View2DWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.members = []
        self.nodes = []
        self.texts = []

        self.dimension_x = self.size().width()
        self.dimension_y = self.size().height()

        # display default bracing if no existing bracing is selected (i.e. initializing dialog)
        # DO NOT DELETE default bracing! TO DO: implement warning or alternative display (e.g. blank screen)
        self.displayed_bracing = 'default'

    def addMember(self, vMember):
        self.members.append(vMember)

    def addNode(self, vNode):
        self.nodes.append(vNode)

    def addText(self, vText):
        self.texts.append(vText)

    def reset(self):
        self.members.clear()
        self.nodes.clear()
        self.texts.clear()

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)

        for vMember in self.members:
            self.drawMember(painter, vMember)

        for vNode in self.nodes:
            self.drawNode(painter, vNode)

        for vText in self.texts:
            self.drawText(painter, vText)

        painter.end()

    def drawMember(self, painter, vMember):
        p = painter.pen()
        p.setColor(QColor(vMember.color))
        p.setWidth(vMember.size)
        painter.setPen(p)

        for member in vMember.members:
            start = member.start_node
            end = member.end_node

            x1, y1 = self.convertCoordinates(vMember, start.x, start.y)
            x2, y2 = self.convertCoordinates(vMember, end.x, end.y)

            painter.drawLine(x1, y1, x2, y2)

    def drawNode(self, painter, vNode):
        p = painter.pen()
        p.setColor(QColor(vNode.color))
        p.setWidth(vNode.size)
        painter.setPen(p)

        for node in vNode.nodes:
            x1, y1 = self.convertCoordinates(vNode, node.x, node.y)

            painter.drawPoint(x1, y1)

    def drawText(self, painter, vText):
        p = painter.pen()
        p.setColor(QColor(vText.color))
        painter.setPen(p)

        painter.setFont(QFont("Times", vText.size))
        
        location = vText.location

        for i in range(len(vText.texts)):
            text = vText.texts[i]
            member = vText.members[i]

            start = member.start_node
            end = member.end_node

            # translate text parallel to the member
            x = (start.x + end.x) * location.x
            y = (start.y + end.y) * location.x

            # translate text perpendicular to the member
            angle = member.angle()
            dx = m.cos(angle - m.pi/2) * location.y
            dy = m.sin(angle - m.pi/2) * location.y

            x1, y1 = self.convertCoordinates(vText, x + dx, y + dy)

            painter.drawText(x1, y1, text)

    # Methods to convert coordinates for objects to be displayed properly -----------------------------------
    def convertCoordinates(self, vObject, x, y):
        view_factor, dummy, view_factor_y = self.viewFactors(vObject)
        center_x, center_y = self.centerdxdy(vObject)

        # y coordinate is negative since y postive is downward in QPainter
        coordinates = (
            x * view_factor + center_x, 
            -y * view_factor + center_y, 
        )

        return coordinates
    
    def viewFactors(self, vObject):
        dim_x = vObject.dim_x
        dim_y = vObject.dim_y

        # Maximum length
        maxLength = max(dim_x, dim_y) + Algebra.EPSILON

        view_factor_x = self.dimension_x * View2DConstants.RATIO / maxLength
        view_factor_y = self.dimension_y * View2DConstants.RATIO / maxLength

        # Find the smallest view factor so that the object fits in the window
        view_factor = min(view_factor_x, view_factor_y)

        return view_factor, view_factor_x, view_factor_y

    def centerdxdy(self, vObject):
        ''' find the translations required to center the displayed object '''
        dim_x = vObject.dim_x
        dim_y = vObject.dim_y

        view_factor, dummy, view_factor_y = self.viewFactors(vObject)

        center_x = (self.dimension_x - view_factor*dim_x)/2

        # margin in the y direction
        margin_y = self.dimension_y*(1-View2DConstants.RATIO)/2
        # translation due to the difference of side lengths in x and y direction
        lengthDiff = max(dim_x - dim_y, 0)/2
        # translation due to the difference of the x and y dimensions of the view window
        dimDiff = max(view_factor_y - view_factor, 0)*dim_y/2

        center_y = view_factor*dim_y + margin_y + dimDiff + lengthDiff*view_factor

        return center_x, center_y