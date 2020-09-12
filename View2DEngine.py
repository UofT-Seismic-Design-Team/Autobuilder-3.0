from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality

from Model import *

import math as m

COLORS_FLOOR_PLAN = ['blue', 'violet']
COLORS_PANEL = ['orange']
COLORS_NODE = ['green']

class ViewSectionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.tower = Tower()
        self.elevation_index = 0
        self.elevation = 0

        self.last_x, self.last_y = None, None
        self.pen_color = QColor('#000000')

        self.dimension_x = self.size().width()
        self.dimension_y = self.size().height()

        self.panel_direction = 1

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        self.drawPanels(painter)
        self.drawFloorPlan(painter)

        painter.end()

    def setTower(self, tower):
        self.tower = tower
        self.elevation = self.tower.elevations[self.elevation_index]
    
    def elevationUp(self):
        self.elevation_index += 1
        # prevent list to go out of range
        self.elevation_index = min(len(self.tower.elevations)-1, self.elevation_index)

        self.elevation = self.tower.elevations[self.elevation_index]

    def elevationDown(self):
        self.elevation_index -= 1
        # prevent list to go out of range
        self.elevation_index = max(0, self.elevation_index)

        self.elevation = self.tower.elevations[self.elevation_index]

    def changePanelDirection(self):
        self.panel_direction *= -1

    # need to be fixed in the future
    def drawFloorPlan(self, painter):

        p = painter.pen()

        floor = self.tower.floors[self.elevation]

        colorIndex = 0
        for floorPlan_name in floor.floorPlans:

            p.setColor(QColor(COLORS_FLOOR_PLAN[colorIndex]))
            painter.setPen(p)

            floorPlan = floor.floorPlans[floorPlan_name]

            for member in floorPlan.members:
                start = member.start_node
                end = member.end_node

                # Determine the reference length
                refLength = min(self.dimension_x, self.dimension_y)

                # object to view ratio
                ratio = 0.6

                # Note: 12 is only for testing purposes; will be set by user in project settings
                view_factor = refLength * ratio / 12

                # translation required to center the object
                center_x = self.dimension_x/2 - view_factor*12/2
                center_y = view_factor*12  + max(self.dimension_y/12*0.6 - view_factor, 0)*12/2 + self.dimension_y*0.2

                # Draw the members of the floor plan-------------------
                p.setColor(QColor(COLORS_FLOOR_PLAN[colorIndex]))
                p.setWidth(5)
                painter.setPen(p)

                # y coordinates are negative since the y direction in the widget is downwards
                painter.drawLine(start.x*view_factor+center_x, -start.y*view_factor+center_y, end.x*view_factor+center_x, -end.y*view_factor+center_y)
                
                # Draw the nodes of the floor plan-------------------
                p.setColor(QColor(COLORS_NODE[0]))
                p.setWidth(15)
                painter.setPen(p)

                painter.drawPoint(start.x*view_factor+center_x, -start.y*view_factor+center_y)
                painter.drawPoint(end.x*view_factor+center_x, -end.y*view_factor+center_y)

            colorIndex += 1

    def drawPanels(self, painter):

        p = painter.pen()
        p.setWidth(5)

        floor = self.tower.floors[self.elevation]

        colorIndex = 0
        index = 0
        for panel in floor.panels:

            p.setColor(QColor(COLORS_PANEL[colorIndex]))
            painter.setPen(p)

            lowerLeft = panel.lowerLeft
            lowerRight = panel.lowerRight

            # Get slope of base member
            baseSlope = (lowerRight.y - lowerLeft.y) / (lowerRight.x - lowerLeft.x + 0.0000000001)# tolerance to avoid divison by zero
            
            orientationX = lowerRight.x - lowerLeft.x
            orientationY = lowerRight.y - lowerLeft.y

            angle = abs(m.atan(baseSlope))
            
            # First quadrant
            if orientationX >= 0 and orientationY >= 0:
                angle = angle
            # Second quadrant
            elif orientationX < 0 and orientationY > 0:
                angle += m.pi/2
            # Third quadrant
            elif orientationX <= 0 and orientationY <= 0:
                angle += m.pi
            # Fourth quardant
            elif orientationX < 0 and orientationY < 0:
                angle += m.pi * 3/2

            panel_orientation = self.panel_direction * m.pi/2

            dx = m.cos(angle - panel_orientation)
            dy = m.sin(angle - panel_orientation)

            upperLeft = Node(lowerLeft.x + dx, lowerLeft.y + dy)
            upperRight = Node(lowerRight.x + dx, lowerRight.y + dy)

            idLocation = Node((lowerLeft.x + lowerRight.x + dx)/2, (lowerLeft.y + lowerRight.y + dy)/2)

            # Determine the reference length
            refLength = min(self.dimension_x, self.dimension_y)

            # object to view ratio
            ratio = 0.6

            # Note: 12 is only for testing purposes; will be set by user in project settings
            view_factor = refLength * ratio / 12

            # translation required to center the object
            center_x = self.dimension_x/2 - view_factor*12/2
            center_y = view_factor*12  + max(self.dimension_y/12*0.6 - view_factor, 0)*12/2 + self.dimension_y*0.2

            nodes = [lowerRight, upperRight, upperLeft, lowerLeft]

            for i in range(len(nodes)-1):
                # y coordinates are negative since the y direction in the widget is downwards
                painter.drawLine(nodes[i].x*view_factor+center_x, -nodes[i].y*view_factor+center_y, nodes[i+1].x*view_factor+center_x, -nodes[i+1].y*view_factor+center_y)
            
            painter.drawText(idLocation.x*view_factor+center_x, -idLocation.y*view_factor+center_y, str(panel.name))

            index += 1