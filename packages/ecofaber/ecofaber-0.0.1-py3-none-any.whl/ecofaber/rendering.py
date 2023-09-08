

import sys
import numpy as np


from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtOpenGL

import OpenGL.GL as gl
from OpenGL import GLU


from stl import mesh



class Shape3D:
    def __init__(self, filePath):
        self.mesh = mesh.Mesh.from_file(filePath)

        v, c, i = self.mesh.get_mass_properties()

        self.volume = v
        self.cog = c
        self.selRadius = self.getSelRadius(v)

    def getSelRadius(self, volume):
        return np.power(volume, 1/3)*0.6

    def getPoints(self):
        return self.mesh.points



class Camera:
    def __init__(self):
        self.action = None

        self.eye = np.array([100.,0.,0.])
        self.ctr = np.array([0.,0.,0.])
        self.up = np.array([0.,0.,1.])

    def getOrth(self):
        n = self.eye - self.ctr
        n = n / np.linalg.norm(n)
        j = self.up - np.dot(self.up, n)*n
        j = j / np.linalg.norm(j)
        i = np.cross(n, j)

        return n, i, j

    def getEulerAngles(self, v):
        v = v / np.linalg.norm(v)
        a = np.arctan2(v[1],v[0])
        b = np.arcsin(v[2])
        return a, b

    def getNormal(self, a, b):
        if b > 1.55:
            b = 1.55
        if b < -1.55:
            b = -1.55
        return np.array([
            np.cos(a)*np.cos(b),
            np.sin(a)*np.cos(b),
            np.sin(b)
        ])

    def setAction(self, action):
        self.action = action

    def setScroll(self, scroll):
        n, _ , _ = self.getOrth()
        self.eye -= + n*scroll

    def setMove(self, move):
        n, i, j = self.getOrth()

        if self.action == 'move':
            move = move / 10
            self.eye += (move[0]*i - move[1]*j)
            self.ctr += (move[0]*i - move[1]*j)

        if self.action == 'rotate':
            move = move / 100

            a, b = self.getEulerAngles(n)
            n = self.getNormal(a - move[0], b - move[1])

            dist = np.linalg.norm(self.eye - self.ctr)
            self.eye = self.ctr + n*dist

    def getState(self):
        return list(self.eye) + list(self.ctr) + list(self.up)

    def getRay(self, coord, angle):
        n, _ , _ = self.getOrth()
        a, b = self.getEulerAngles(-n)

        ar = np.arctan(coord[0]*np.tan(np.radians(angle[1]/2)))
        br = np.arctan(coord[1]*np.tan(np.radians(angle[0]/2)))

        a -= ar/np.cos(b)
        b += br

        ro = self.eye
        rn = self.getNormal(a, b)

        return ro, rn



class RayCasting:
    def __init__(self):
        pass

    def pick(self, ray, objects, shapes):
        ro, rn = ray
        matches = {}

        for obj in objects:
            if 'sel' not in obj.keys() or obj['sel'] == False:
                continue

            selSize = shapes[obj['name']].selRadius
            pos = np.array(obj['pos'])

            b = np.dot(rn, ro - pos)
            c = np.dot(ro - pos, ro - pos) - np.square(selSize)
            det = np.square(b) - c

            if det  <= 0:
                continue

            s = np.sqrt(det)
            t1, t2 = -b + s, -b -s

            for t in (t1, t2):
                if t > 0:
                    matches[t] = obj

        if len(matches.keys()):
            firstT = sorted(matches.keys())[0]
            return matches[firstT]
        else:
            return None



class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.shapes = {}
        self.camera = Camera()
        self.ray = None

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(155, 155, 155))
        gl.glEnable(gl.GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        self.size = [width, height]
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)
        GLU.gluPerspective(25.0, aspect, 1.0, 1000.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def addShape(self, name):
        if name not in self.shapes.keys():
            self.shapes[name] = Shape3D(f'shapes/{name}.stl')
        return self.shapes[name]

    def paintObject(self, obj, col, pos):
        gl.glPushMatrix()

        gl.glTranslate(*pos)
        gl.glTranslate(*[-i for i in obj.cog])

        gl.glColor3ub(*col)
        gl.glBegin(gl.GL_TRIANGLES)
        for p in obj.getPoints():
            gl.glVertex3f(*p[0:3])
            gl.glVertex3f(*p[3:6])
            gl.glVertex3f(*p[6:9])
        gl.glEnd()

        gl.glPopMatrix()

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()

        GLU.gluLookAt(*self.camera.getState())

        model = self.parent.model
        if model:
            for obj in model.getView():
                shape = self.addShape(obj['name'])
                self.paintObject(shape, obj['color'], obj['pos'])

        '''
        if self.ray:
            ro, rn = self.ray
            pos = list(ro + 100*rn)
            shape = self.addShape('b_tetra_1')
            self.paintObject(shape, [255,255,255], pos)
        '''


    def resetView(self):
        self.camera = Camera()
        self.updateGL()

    def selectObject(self):
        coord = [
            (2. * self.mousePos[0]) / self.size[0] - 1.,
            (2. * self.mousePos[1]) / self.size[1] + 1.
        ]

        angle = [
            25.,
            25.*self.size[0]/self.size[1]
        ]

        self.ray = self.camera.getRay(coord, angle)
        objects = self.parent.model.getView()

        raycasting = RayCasting()
        res = raycasting.pick(self.ray, objects, self.shapes)
        if res:
            return self.parent.model.getObj(res['pos'])
        else:
            return None

    def mousePressEvent(self, event):
        self.mousePos = np.array([event.x(), -event.y()])

        obj = self.selectObject()
        if obj:
            self.parent.setSelectElem(obj)

        btnNb = event.button()

        actions = {
            1: 'move',  # left click
            2: 'rotate' # right click
        }

        if btnNb in actions.keys():
            action = actions[btnNb]
            self.camera.setAction(action)
            self.updateGL()

    def mouseReleaseEvent(self, event):
        self.camera.setAction(None)

    def mouseMoveEvent(self, event):
        pos = np.array([event.x(), -event.y()])
        move = pos - self.mousePos
        self.mousePos = pos

        self.camera.setMove(move)
        self.updateGL()

    def wheelEvent(self, event):
        self.camera.setScroll(event.angleDelta().y()/120)
        self.updateGL()

