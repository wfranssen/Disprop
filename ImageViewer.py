#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2020 Wouter Franssen

# This file is part of Disprop.
#
# Disprop is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Disprop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Disprop. If not, see <http://www.gnu.org/licenses/>.import os.path

from PyQt5 import QtGui, QtCore, QtWidgets
import os.path
import multiprocessing as mp
from PIL import Image


def optImage(loc):
    im = Image.open(loc)
    im.save(loc,optimize=True)

class multiImageFrame(QtWidgets.QWidget):
    def __init__(self,parent):
        super(multiImageFrame, self).__init__(parent)
        self.father = parent
        self.imageFrame = QtWidgets.QGridLayout(self)

        self.imageViewer = ImageViewer(self)
        self.imageFrame.addWidget(self.imageViewer, 0, 0, 1, 11)

        self.pageSpin = QtWidgets.QSpinBox(self)
        self.pageSpin.setMinimum(1)
        self.pageSpin.valueChanged.connect(self.changeIndex)
        self.pageSpin.setEnabled(False)
        self.imageFrame.addWidget(self.pageSpin,1,1)
        self.pageName = QtWidgets.QLabel('')
        self.imageFrame.addWidget(self.pageName,1,2)
        self.deleteButton = QtWidgets.QPushButton('X')
        self.deleteButton.clicked.connect(self.clearReader)
        self.imageFrame.addWidget(self.deleteButton,1,0)
        self.imageFrame.setRowStretch(0,1)

        self.imageLocs = None
        self.imageIndex = None
        self.setAcceptDrops(True)

    def numberOfFiles(self):
        if self.imageLocs is None:
            return 0
        else:
            return len(self.imageLocs)

    def changeIndex(self,index):
        image = QtGui.QImage(self.imageLocs[index - 1])
        #image.invertPixels()
        self.imageViewer.setImage(image)
        self.pageName.setText(self.imageNames[index - 1])
        self.imageViewer.setVisible(True)

    def setImageList(self,pathList,reset=True):
        if len(pathList) > 0:
            self.clearReader()
            self.imageLocs = pathList
            self.imageNames = [os.path.basename(x) for x in pathList]
            self.pageSpin.setValue(1)
            self.pageSpin.setMaximum(len(self.imageLocs))
            self.pageName.setText(self.imageNames[0])
            self.pageSpin.setEnabled(True)
            if reset:
                self.changeIndex(1)
            self.setVisible(True)


    def optimizePNG(self):
        if self.imageLocs is not None:
            locs = [x for x in self.imageLocs if x.lower().endswith('.png')]
            with mp.Pool(max(mp.cpu_count()-1,1)) as p:
                p.map(optImage, locs)

    def clearReader(self):
        self.imageLocs = None
        self.imageIndex = None
        self.pageName.setText('')
        self.setVisible(False)

    def dropEvent(self, event):
        self.father.dropEvent(event)

    def dragMoveEvent(self, event):
        pass
        
    def dragEnterEvent(self, event):   
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()


class ImageViewer(QtWidgets.QGraphicsView):

    def __init__(self,parent):
        super(ImageViewer, self).__init__(parent)
        self.father = parent
        self.setAcceptDrops(True)

        self.graphScene = QtWidgets.QGraphicsScene()
        self.setScene(self.graphScene)

        self.currentPixmapItem = None

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # Zoom box coordinates as a list of fractional positions in the image.
        self.zoomBox = None


    def setImage(self, image):
        pixmap = QtGui.QPixmap.fromImage(image)
        self.pixmapBackup = pixmap
        if self.currentPixmapItem is None:
            self.currentPixmapItem = self.graphScene.addPixmap(pixmap)
        else:
            self.currentPixmapItem.setPixmap(pixmap)
        self.setSceneRect(QtCore.QRectF(pixmap.rect()))  # Set scene size to image size.
        self.zoomBox = None
        self.updateScene()


    def updateScene(self):
        if self.currentPixmapItem is None:
            return
        if self.zoomBox is not None:
            x,y,w,h = self.zoomBox
            xzoom = 1/(w-x)
            yzoom = 1/(h-y)
            zoom = min(xzoom,yzoom)
            if zoom > 4:
                zmode = QtCore.Qt.FastTransformation
            else:
                zmode = QtCore.Qt.SmoothTransformation

            width = int(self.geometry().width() * zoom)
            height = int(self.geometry().height() * zoom)
            Pixmap = self.pixmapBackup.scaled(width,height,transformMode=zmode,
                    aspectRatioMode=QtCore.Qt.KeepAspectRatioByExpanding)
            self.currentPixmapItem.setPixmap(Pixmap)
            self.setSceneRect(QtCore.QRectF(Pixmap.rect()))  # Set scene size to image size.
            x, y, w, h = self.frac2coords(x,y,w,h)
            self.fitInView(x,y,w-x,h-y, QtCore.Qt.KeepAspectRatio)
        else:
            self.zoomBox = None  
            Pixmap = self.pixmapBackup.scaledToHeight(self.geometry().height(),mode = QtCore.Qt.SmoothTransformation)
            self.currentPixmapItem.setPixmap(Pixmap)
            self.setSceneRect(QtCore.QRectF(Pixmap.rect()))  # Set scene size to image size.
            self.fitInView(self.sceneRect(),QtCore.Qt.KeepAspectRatio)  

    def resizeEvent(self, event):
        self.updateScene()

    def mousePressEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        elif event.button() == QtCore.Qt.RightButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif event.button() == QtCore.Qt.RightButton:
            viewBBox = self.sceneRect()
            selectionBBox = self.graphScene.selectionArea().boundingRect().intersected(viewBBox)
            self.graphScene.setSelectionArea(QtGui.QPainterPath())  # Clear current selection area.
            if selectionBBox.isValid() and (selectionBBox != viewBBox):
                coords = selectionBBox.getCoords()
                self.zoomBox = self.coords2frac(coords)
                self.updateScene()
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def coords2frac(self,coords):
        """
        Converts a series of scene coordinates to fractions of the
        full image width or height.
        """
        x = coords[0]/self.currentPixmapItem.pixmap().width()
        w = coords[2]/self.currentPixmapItem.pixmap().width()
        y = coords[1]/self.currentPixmapItem.pixmap().height()
        h = coords[3]/self.currentPixmapItem.pixmap().height()
        return [x,y,w,h]

    def frac2coords(self,x,y,w,h):
        """
        Converts fractions to pixel positions (scene coords).
        """
        x *= self.currentPixmapItem.pixmap().width()
        y *= self.currentPixmapItem.pixmap().height()
        w *= self.currentPixmapItem.pixmap().width()
        h *= self.currentPixmapItem.pixmap().height()
        newc1 = self.mapToScene(int(x),int(y))
        newc2 = self.mapToScene(int(w),int(h))
        return newc1.x(),newc1.y(),newc2.x(),newc2.y()

    def mouseDoubleClickEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.RightButton:
            self.zoomBox = None
            self.updateScene()
        QtWidgets.QGraphicsView.mouseDoubleClickEvent(self, event)

    def dropEvent(self, event):
        self.father.dropEvent(event)

    def dragMoveEvent(self, event):
        pass
        
    def dragEnterEvent(self, event):   
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()


