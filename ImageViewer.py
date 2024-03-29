#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021 Wouter Franssen

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

        self.zoomLevel = QtWidgets.QDoubleSpinBox(self)
        self.zoomLevel.setMinimum(0.001)
        self.zoomLevel.setMaximum(1000)
        self.zoomLevel.setValue(100)
        self.zoomLevel.editingFinished.connect(self.changeZoom)
        self.zoomDrop = QtWidgets.QComboBox()
        self.zoomDrop.addItems(['Zoom [%]:','Fit width','Fit page'])
        self.zoomDrop.currentIndexChanged.connect(self.zoomTypeChanged)
        self.imageFrame.addWidget(self.zoomDrop,1,9)
        self.imageFrame.addWidget(self.zoomLevel,1,10)

        self.imageFrame.setRowStretch(0,1)
        self.imageFrame.setColumnStretch(8,1)


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
        self.imageViewer.scrollUp()
        self.pageName.setText(self.imageNames[index - 1])
        self.father.viewTabs.setVisible(True)

    def changeZoom(self):
        value = self.zoomLevel.value()
        self.imageViewer.setZoomSpinbox(value)
        self.zoomDrop.setCurrentIndex(0)

    def zoomTypeChanged(self,index):
        if index == 1:
            self.imageViewer.fitWidth()
        elif index == 2:
            self.imageViewer.fitPage()


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
            self.father.viewTabs.setVisible(True)


    def optimizePNG(self):
        if self.imageLocs is not None:
            locs = [x for x in self.imageLocs if x.lower().endswith('.png')]
            with mp.Pool(max(mp.cpu_count()-1,1)) as p:
                p.map(optImage, locs)

    def clearReader(self):
        self.imageLocs = None
        self.imageIndex = None
        self.pageName.setText('')
        #self.setVisible(False)

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
        self.zoom = 1

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

    def setZoomSpinbox(self,zoom):
        self.zoom = zoom/100
        self.updateScene()

    def setZoom(self,zoom):
        zoom = max(zoom,self.father.zoomLevel.minimum()/100)
        zoom = min(zoom,self.father.zoomLevel.maximum()/100)
        self.zoom = zoom
        self.updateScene()

    def scrollZoom(self,step):
        zoom = self.zoom * 1.1**(step/120)

        zoom = max(zoom,self.father.zoomLevel.minimum()/100)
        zoom = min(zoom,self.father.zoomLevel.maximum()/100)
        self.zoom = zoom
        self.father.zoomLevel.setValue(self.zoom*100)
        self.updateScene()
        self.father.zoomDrop.setCurrentIndex(0)

    def fitWidth(self):
        width = self.viewport().width()
        imageWidth = self.pixmapBackup.width()
        zoom = width/imageWidth
        self.setZoom(zoom)
        self.father.zoomLevel.setValue(self.zoom*100)

    def fitPage(self):
        width = self.viewport().width()
        height = self.viewport().height()
        imageWidth = self.pixmapBackup.width()
        imageHeight = self.pixmapBackup.height()

        widthZoom = width/imageWidth
        heightZoom = height/imageHeight
        
        zoom = min(widthZoom,heightZoom)
        
        self.setZoom(zoom)
        self.father.zoomLevel.setValue(self.zoom*100)

    def updateScene(self):
        if self.zoom > 2: # If high zoom, don't do antialiasing
            zmode = QtCore.Qt.FastTransformation
        else:
            zmode = QtCore.Qt.SmoothTransformation
        width = int(self.pixmapBackup.width() * self.zoom)
        Pixmap = self.pixmapBackup.scaledToWidth(width,mode=zmode)
        self.currentPixmapItem.setPixmap(Pixmap)
        self.setSceneRect(QtCore.QRectF(Pixmap.rect()))  # Set scene size to image size.

    def scrollUp(self):
        self.verticalScrollBar().setValue(0)

    def resizeEvent(self, event):
        if self.father.zoomDrop.currentIndex() == 1:
            self.fitWidth()
        elif self.father.zoomDrop.currentIndex() == 2:
            self.fitPage()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        elif event.button() == QtCore.Qt.RightButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
        if event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif event.button() == QtCore.Qt.RightButton:
            selectionBBox = self.graphScene.selectionArea().boundingRect()
            self.graphScene.setSelectionArea(QtGui.QPainterPath())  # Clear current selection area.
            if selectionBBox.isValid():
                coords = selectionBBox.getCoords() #points in scene
                
                xdiff = abs(coords[0] - coords[2])/self.currentPixmapItem.pixmap().width()
                ydiff = abs(coords[1] - coords[3])/self.currentPixmapItem.pixmap().height()
                # now we have the fraction to have in view.
                # devide view size by this, to get the full size, and get the zoom levels
                zoomx = self.viewport().width()/xdiff/self.pixmapBackup.width()
                zoomy = self.viewport().height()/ydiff/self.pixmapBackup.height()
                zoom = min(zoomx,zoomy)

                oldx = min(coords[0],coords[2])/self.currentPixmapItem.pixmap().width()
                oldy = min(coords[1],coords[3])/self.currentPixmapItem.pixmap().height()

                self.setZoom(zoom)
                # Find new position of the upper left point.
                newx = oldx*self.currentPixmapItem.pixmap().width()
                newy = oldy*self.currentPixmapItem.pixmap().height()

                # Scroll with these values
                self.horizontalScrollBar().setValue(int(newx))
                self.verticalScrollBar().setValue(int(newy))
                self.father.zoomDrop.setCurrentIndex(0) # set view type to 'zoom'
                self.father.zoomLevel.setValue(self.zoom*100)

            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.father.zoomDrop.setCurrentIndex(2)
            self.fitPage()
            self.zoomBox = None
            self.updateScene()
        QtWidgets.QGraphicsView.mouseDoubleClickEvent(self, event)

    def wheelEvent(self,event):
        if event.modifiers() & QtCore.Qt.ControlModifier or event.buttons() == QtCore.Qt.RightButton:
            """
            Update the view to new zoom. Scroll the area to keep the same
            absolute image position under the cursor.
            """
            x, y = event.pos().x(), event.pos().y() # The cursor pos in the frame
            scenePos = self.mapToScene(x,y)
            oldx = scenePos.x()/self.currentPixmapItem.pixmap().width()
            oldy = scenePos.y()/self.currentPixmapItem.pixmap().height()
            # Now zoom to new zoom setting.
            self.scrollZoom(event.angleDelta().y() + event.angleDelta().x())
            scenePosNew = self.mapToScene(x,y)
            newx = scenePosNew.x()
            newy = scenePosNew.y()
            xscroll = oldx * self.currentPixmapItem.pixmap().width() - newx 
            yscroll = oldy * self.currentPixmapItem.pixmap().height() - newy
            # Scroll with these values
            self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() + xscroll))
            self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() + yscroll))
        else:
            QtWidgets.QGraphicsView.wheelEvent(self, event)

    def dropEvent(self, event):
        self.father.dropEvent(event)

    def dragMoveEvent(self, event):
        pass
        
    def dragEnterEvent(self, event):   
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()


