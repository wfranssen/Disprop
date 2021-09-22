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

from PyQt5 import QtGui, QtCore, QtWidgets
import unicodedata as uni

class ToolWindow(QtWidgets.QWidget):
    """
    The base class of the toolwindows.
    Implements the basic features shared by all toolwindows.
    Toolwindows inherit this class and alter its behaviour by the constants or by reimplementing functions.
    """

    NAME = ""              # The name displayed in the title of the window
    RESIZABLE = False      # should the window be resizable
    MENUDISABLE = True     # Should the window disable the menu of the main window
    APPLYANDCLOSE = True   # Should the window close after the ok button is pressed
    CANCELNAME = "&Cancel" # The name on the cancel button
    OKNAME = "&Ok"         # The name on the ok button

    def __init__(self, parent):
        """
        Initializes the ToolWindow.

        Parameters
        ----------
        parent : Main1DWindow or AbstractParamFrame
            Parent of the toolwindow.
        """
        super(ToolWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.Tool)
        self.father = parent
        self.setWindowTitle(self.NAME)
        self.layout = QtWidgets.QGridLayout(self)
        self.grid = QtWidgets.QGridLayout()
        self.box = QtWidgets.QDialogButtonBox()
        self.layout.addLayout(self.grid, 0, 0, 1, 2)
        self.cancelButton = QtWidgets.QPushButton(self.CANCELNAME)
        self.cancelButton.clicked.connect(self.closeEvent)
        self.okButton = QtWidgets.QPushButton(self.OKNAME)
        self.okButton.clicked.connect(self.applyAndClose)
        self.okButton.setFocus()
        self.box.addButton(self.cancelButton, QtWidgets.QDialogButtonBox.RejectRole)
        self.box.addButton(self.okButton, QtWidgets.QDialogButtonBox.AcceptRole)
        self.show()
        self.layout.addWidget(self.box, 3, 0)
        if not self.RESIZABLE:
            self.setFixedSize(self.size())
        if self.MENUDISABLE:
            self.father.menuEnable(False)
        self.setGeometry(self.frameSize().width() - self.geometry().width(), self.frameSize().height(), 0, 0)


    def applyFunc(self):
        """
        Dummy function for the apply function.
        Should be reimplemented by the toolwindows.
        """
        pass

    def applyAndClose(self):
        """
        Runs the apply function and when APPLYANDCLOSE is set, closes the window.
        """
        self.applyFunc()
        if self.APPLYANDCLOSE:
            self.closeEvent()

    def closeEvent(self, *args):
        """
        Updates the view and closes the toolwindow.

        Parameters
        ----------
        *args
            Any arguments are ignored.
        """
        if self.MENUDISABLE:
            self.father.menuEnable(True)
        self.deleteLater()



class CharInputWindow(QtWidgets.QWidget):
    """
    Provides a general window for alphabetic inputs in the text editor.
    """
    TITLE = ''
    def __init__(self,parent):
        QtWidgets.QWidget.__init__(self)
        self.father = parent
        layout = QtWidgets.QGridLayout(self)
        layout.setColumnStretch(1,1)
        self.tabs = QtWidgets.QTabWidget(self)
        layout.addWidget(QtWidgets.QLabel(self.TITLE), 0, 0)
        self.closeButton = QtWidgets.QPushButton('Close')
        layout.addWidget(self.closeButton, 0, 2)
        self.closeButton.clicked.connect(self.father.removeInputWindow)
        layout.addWidget(self.tabs, 1, 0, 1, 3)

    def addTab(self,title, charLists):
        """
        Add a tab with name 'title'. It has a a number of rows equal to len(charLists).
        Each row is populetd with the elements in each list inside charLists.
        By default, a preview box is put on the left.
        """
        mainWidget = QtWidgets.QWidget()
        frame = QtWidgets.QGridLayout()
        frame.setHorizontalSpacing(0) #Keep horizontal spacing as close as possible
        frame.setVerticalSpacing(0) #Keep vertical spacing as close as possible
        mainWidget.setLayout(frame)

        self.tabs.addTab(mainWidget, title)
        # PreviewLabel
        previewLabel = QtWidgets.QLabel('')
        previewLabel.setAlignment(QtCore.Qt.AlignCenter)
        previewLabel.setStyleSheet("border: 1px solid gray;") 
        font = QtGui.QFont()
        font.setPointSize(30)
        previewLabel.setFont(font) 
        previewLabel.setMinimumWidth(60)
        previewLabel.setMaximumWidth(60)
        frame.addWidget(previewLabel,0,0,2,1)

 	# Create all buttons
        buttons = []
        for row, lst in enumerate(charLists):
            buttons.append([])
            for column, char in enumerate(lst):
                buttons[-1].append(specialButton(char))
                buttons[-1][-1].setMinimumWidth(16)
                buttons[-1][-1].clicked.connect(lambda arg, char=char: self.buttonPush(char))
                buttons[-1][-1].enter.connect(lambda char=char: previewLabel.setText(char))
                buttons[-1][-1].leave.connect(lambda char='': previewLabel.setText(char))
                hexname = 'U+' + "{0:#0{1}x}".format(ord(char),6)[2:].upper()
                buttons[-1][-1].setToolTip(uni.name(char) + ' (' + hexname + ')')
                frame.addWidget(buttons[-1][-1],row,column + 1)

        return frame, buttons, previewLabel

    def buttonPush(self,char):
        self.father.insertStr(char)
        self.father.textViewer.setFocus()

class specialButton(QtWidgets.QPushButton):
    """ 
    Button with enter and leave signals.
    """
    
    enter = QtCore.pyqtSignal()
    leave = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(specialButton, self).__init__(parent)

    def enterEvent(self, QEvent):
        self.enter.emit()

    def leaveEvent(self, QEvent):
        self.leave.emit()
