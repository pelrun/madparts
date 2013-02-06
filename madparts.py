#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtOpenGL import *

from OpenGL.GL import *
import OpenGL.arrays.vbo as glvbo

import FTGL

import numpy as np
import math

import jydjs
from jydjssyntax import JSHighlighter
from jydcoffeesyntax import CoffeeHighlighter
from jydgldraw import GLDraw

gldx = 200
gldy = 200

font_file = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"

class MyGLWidget(QGLWidget):
    def __init__(self, parent = None):
        super(MyGLWidget, self).__init__(parent)
        self.data = np.array(
          [[x,y] for x in range(-gldx/2, gldx/2) for y in range(-gldy/2, gldy/2)],
          dtype=np.float32)
        self.zoomfactor = 50
        self.zoom_changed = False
        self.shapes = []
        self.font = FTGL.BitmapFont(font_file)
        self.gldraw = GLDraw(self.font)
        self.font.FaceSize(24, 72)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(0.5, 0.5, 0.5)
        self.vbo.bind() # make this vbo the active one
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, self.vbo)
        glDrawArrays(GL_POINTS, 0, gldx*gldy)

        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(-100, 0, 0)
        glVertex3f(100, 0, 0)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(0, -100, 0)
        glVertex3f(0, 100, 0)
        glEnd()
        
        i = 1
        if self.shapes != None:
            for shape in self.shapes:
                if shape['shape'] == 'rect': self.gldraw.rect(shape, i)
                if shape['shape'] == 'circle': self.gldraw.circle(shape)
                i = i + 1
        if self.zoom_changed:
            self.zoom_changed = False
            self.resizeGL(self.width(), self.height())

    def resizeGL(self, w, h):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # every 'zoomfactor' pixels is one mm
        mm_visible_x = float(w)/self.zoomfactor
        if mm_visible_x < 1: mm_visible_x = 1.0
        mm_visible_y = float(h)/self.zoomfactor
        if mm_visible_y < 1: mm_visible_y = 1.0
        glOrtho(-mm_visible_x/2, mm_visible_x/2, -mm_visible_y/2, mm_visible_y/2, -1, 1)
        glViewport(0, 0, w, h)

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.vbo = glvbo.VBO(self.data)
  
    def set_shapes(self, s):
        self.shapes = s
        self.updateGL()


class MainWin(QtGui.QMainWindow):

  def zoom(self):
      self.glw.zoomfactor = int(self.zoom_selector.text())
      self.glw.zoom_changed = True
      self.glw.updateGL()

  def compile(self):
      code = self.te1.toPlainText()
      try:
          #result = jydjs.eval_js_footprint(code)
          result = jydjs.eval_coffee_footprint(code)
          self.te2.setPlainText(str(result))
          self.glw.set_shapes(result)
      except Exception as ex:
          self.te2.setPlainText(str(ex))
          

  def __init__(self):
    super(MainWin, self).__init__()
    lsplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
    self.te1 = QtGui.QTextEdit()
    self.te1.setAcceptRichText(False)
    #self.te1.setPlainText(jydjs.js_example)
    self.te1.setPlainText(jydjs.coffee_example)
    #self.highlighter1 = JSHighlighter(self.te1.document())
    self.highlighter1 = CoffeeHighlighter(self.te1.document())
    self.connect(self.te1, QtCore.SIGNAL('textChanged()'), self.compile)
    self.te2 = QtGui.QTextEdit()
    self.te2.setReadOnly(True)
    self.highlighter2 = JSHighlighter(self.te2.document())
    lsplitter.addWidget(self.te1)
    lsplitter.addWidget(self.te2)
    rvbox = QtGui.QVBoxLayout()
    rhbox = QtGui.QHBoxLayout()
    self.glw = MyGLWidget()
    self.zoom_selector = QtGui.QLineEdit(str(self.glw.zoomfactor))
    self.zoom_selector.setValidator(QtGui.QIntValidator(1, 250))
    self.connect(self.zoom_selector, QtCore.SIGNAL('editingFinished()'), self.zoom)
    self.connect(self.zoom_selector, QtCore.SIGNAL('returnPressed()'), self.zoom)
    rhbox.addWidget(QtGui.QLabel("Zoom: "))
    rhbox.addWidget(self.zoom_selector)
    rvbox.addLayout(rhbox)
    rvbox.addWidget(self.glw)

    right = QtGui.QWidget()
    right.setLayout(rvbox)
    splitter = QtGui.QSplitter(self, QtCore.Qt.Horizontal)
    splitter.addWidget(lsplitter)
    splitter.addWidget(right)
    self.setCentralWidget(splitter)

    self.statusBar().showMessage("Ready.")

    self.exitAction = QtGui.QAction('Quit', self)
    self.exitAction.setShortcut('Ctrl+Q')
    self.exitAction.setStatusTip('Exit application')
    self.connect(self.exitAction, QtCore.SIGNAL('triggered()'), self.close)

    menuBar = self.menuBar()
    fileMenu = menuBar.addMenu('&File')
    fileMenu.addAction(self.exitAction)

    def close(self):
        QtGui.qApp.quit()
    
if __name__ == '__main__':
    app = QtGui.QApplication(["madparts"])
    widget = MainWin()
    widget.show()
    app.exec_()