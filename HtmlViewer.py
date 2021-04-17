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
# along with Disprop. If not, see <http://www.gnu.org/licenses/>.

import os.path
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWebKitWidgets import QWebView



class HtmlViewer(QtWidgets.QSplitter):
    def __init__(self,parent):
        QtWidgets.QWidget.__init__(self)
        self.father = parent

        self.setHandleWidth(2)
        self.setOrientation(QtCore.Qt.Vertical)
        self.setStyleSheet("QSplitter::handle{background: gray;}")


        self.browser = Browser(self)

        self.addWidget(self.browser)

        self.setAcceptDrops(True)
        self.setStretchFactor(0, 1)

    def setHtml(self,file):
        url = QtCore.QUrl().fromLocalFile(file)
        self.browser.load(url)

    def clearReader(self):
        pass

    def dropEvent(self, event):
        self.father.dropEvent(event)

    def dragMoveEvent(self, event):
        pass
        
    def dragEnterEvent(self, event):   
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()


class Browser(QWebView):
    def __init__(self,parent):
        QWebView.__init__(self)
        self.father = parent

    def dropEvent(self, event):
        self.father.dropEvent(event)

    def dragMoveEvent(self, event):
        pass
        
    def dragEnterEvent(self, event):   
        self.father.dragEnterEvent(event)
