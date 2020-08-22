from PyQt5.QtCore import *    # core Qt functionality
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *       # extends QtCore with GUI functionality
from PyQt5.QtOpenGL import *    # provides QGLWidget, a special OpenGL QWidget

from OpenGL.GL import *       # python wrapping of OpenGL
from OpenGL.GLU import *      # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo

from Model import * # geometry of the tower model

import numpy as np
import math as m

import sys


class View3DGLWidget(QGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.tower = Tower()

        # Member variables to control the states of the render
        self.rotMultiplier_x = -90 # show the XZ Plane in the beginning
        self.rotMultiplier_y = 0
        self.rotMultiplier_z = 0

        # TESTING
        self.scalingFactor_x = 5/21
        self.scalingFactor_y = 5/21
        self.scalingFactor_z = 5/21

        # TESTING
        self.translation_x = 0
        self.translation_y = 0
        self.translation_z = -30

        # Save the previous location of the cursor
        self.last_x, self.last_y = None, None

    def initializeGL(self): # this is the init type of thing
        self.qglClearColor(QColor('black'))     # initialize the screen to black
        
        glEnable(GL_DEPTH_TEST)           # enable depth testing

    def resizeGL(self, width, height):       
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / float(height)

        # Sample: gluPerspective(field_of_view, aspect_ratio, z_near, z_far)
        gluPerspective(45.0, aspect, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        # pre-rendering housekeeping

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()    # push the current matrix to the current stack

        # Note: tranlate the object before rotating it
        # Note: need to get this '-30' 
        glTranslate(0, 0, -30)    # third, translate cube to specified depth

        glRotate(self.rotMultiplier_x, 1, 0, 0)
        glRotate(self.rotMultiplier_y, 0, 1, 0)
        glRotate(self.rotMultiplier_z, 0, 0, 1)

        glScale(self.scalingFactor_x, self.scalingFactor_y, self.scalingFactor_z)

        self.renderTowerSkeleton()

        glPopMatrix()    # restore the previous modelview matrix

    def setTower(self, tower):
        # Tower model
        self.tower = tower

    def renderTowerSkeleton(self):
        glLineWidth(2)
        glBegin(GL_LINES)

        # Render the floor plan
        for elev in self.tower.floors:
            floor = self.tower.floors[elev]
            # will draw lines between the two points
            for floorPlan_name in floor.floorPlans:
                floorPlan = floor.floorPlans[floorPlan_name]
                for member in floorPlan.members:
                    start_node = member.start_node
                    end_node = member.end_node
                    
                    vertex1 = (start_node.x-2, start_node.y-4, elev + self.translation_z)
                    glColor3fv((1,1,1))
                    glVertex3fv(vertex1)

                    vertex2 = (end_node.x-2, end_node.y-4, elev + self.translation_z)
                    glColor3fv((1,1,1))
                    glVertex3fv(vertex2)

        # Render the columns
        for column_id in self.tower.columns:
            column = self.tower.columns[column_id]
            start_node = column.start_node
            end_node = column.end_node
            
            vertex1 = (start_node.x-2, start_node.y-4, start_node.z + self.translation_z)
            glColor3fv((1,0,0))
            glVertex3fv(vertex1)

            vertex2 = (end_node.x-2, end_node.y-4, end_node.z + self.translation_z)
            glColor3fv((1,0,0))
            glVertex3fv(vertex2)

        glEnd()

    def rotate(self, delta_x, delta_y):

        sumOfChange = abs(delta_x) + abs(delta_y)

        self.rotMultiplier_z += delta_x / sumOfChange * 5

        self.rotMultiplier_x += delta_y / sumOfChange * 5

    def mouseMoveEvent(self, e):
        if self.last_x is None:
            self.last_x = e.x()
            self.last_y = e.y()
            return # Ignore the first time.
        
        change_x = e.x() - self.last_x
        change_y = e.y() - self.last_y

        self.rotate(change_x, change_y)

        # Update the origin for next time.
        self.last_x = e.x()
        self.last_y = e.y()

        self.update()

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None
    
    def wheelEvent(self, e):
        scrollDirection = e.angleDelta().y()/120
        # if u scroll up upward, magnify
        if scrollDirection > 0:
            factor = 1.1
        else:
        # otherwise, minimize 
            factor = 1/1.1

        self.scalingFactor_x *= factor
        self.scalingFactor_y *= factor
        self.scalingFactor_z *= factor

    def mouseDoubleClickEvent(self, e):
        self.scalingFactor_x = 1
        self.scalingFactor_y = 1
        self.scalingFactor_z = 1


