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
import sys

# Create splash window
if __name__ == '__main__':
    root = QtWidgets.QApplication(sys.argv)
    root.setWindowIcon(QtGui.QIcon(os.path.dirname(os.path.realpath(__file__)) + '/Icons/Logo.png'))
    splash_pix = QtGui.QPixmap(os.path.dirname(os.path.realpath(__file__)) + '/Icons/Splash.png')
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.show()

import re
import widgetClasses as wc
import ImageViewer as ImgV
import TextEditor as TextV
import unicodedata as uni
import HtmlViewer as HtmlV
import HtmlEditor as HtmlE
import glyphs
import distance


IMG_TYPES = ('.png','.bmp','.tif','.tiff','.jpg','.jpeg','.pbm','.pgm','.ppm','.xbm','.xpm')

VERSION = 'v0.0'

class MainProgram(QtWidgets.QMainWindow):

    def __init__(self, root):
        super(MainProgram, self).__init__()
        self.setAcceptDrops(True)
        self.main_widget = QtWidgets.QSplitter(self)
        self.main_widget.setHandleWidth(10)
        self.splitterOrient = 'Horizontal'
        #self.main_widget.setOrientation(QtCore.Qt.Vertical)
        
        self.setCentralWidget(self.main_widget)

        #viewers
        self.viewTabs = QtWidgets.QTabWidget(self)
        self.viewTabs.setMovable(False)
        #self.tabs.tabBar().tabMoved.connect(self.moveWorkspace)
        self.viewTabs.setTabsClosable(True)
        #self.tabs.currentChanged.connect(self.changeMainWindow)
        self.viewTabs.tabCloseRequested.connect(self.removeViewTab)
        self.main_widget.addWidget(self.viewTabs)
        self.viewTabs.setVisible(False)
        self.viewerList = []
        self.currentViewer = None

        #Text files
        self.editTabs = QtWidgets.QTabWidget(self)
        self.editTabs.setMovable(False)
        self.editTabs.setTabsClosable(True)
        self.editTabs.tabCloseRequested.connect(self.removeEditTab)
        self.main_widget.addWidget(self.editTabs)
        self.editTabs.setVisible(False)
        self.editorList = []
        self.currentEditor = None

        # Settings
        self.initMenu()
        self.initToolbar()
        self.statusBar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusBar)


        self.lastLocation = os.path.expanduser('~')

        self.resize(1000, 1000)
        self.show()

    def addImageViewer(self,imageList):
        imageViewer = ImgV.multiImageFrame(self)
        self.viewTabs.addTab(imageViewer,'Images')
        self.viewerList.append(imageViewer)
        self.currentViewer = self.viewerList[-1]
        self.currentViewer.setImageList(imageList)

    def addHtmlViewer(self,loc):
        wid = HtmlV.HtmlViewer(self)
        self.viewTabs.addTab(wid,'HTML')
        self.viewerList.append(wid)
        self.currentViewer = self.viewerList[-1]
        self.currentViewer.setHtml(loc)
        self.viewTabs.setVisible(True)

    def addHtmlEditor(self,loc):
        htmlEdit = HtmlE.HtmlEditFrame(self)
        self.editTabs.addTab(htmlEdit,'Html')
        self.editorList.append(htmlEdit)
        self.currentEditor = self.editorList[-1]
        self.currentEditor.setTextList([loc])

    def addTextEdit(self,textList):
        textEdit = TextV.multiTextFrame(self)
        self.editTabs.addTab(textEdit,'Txt')
        self.editorList.append(textEdit)
        self.currentEditor = self.editorList[-1]
        self.currentEditor.setTextList(textList)

    def dispMsg(self, msg, color='black'):
        if color == 'red':
            self.statusBar.setStyleSheet("QStatusBar{padding-left:8px;color:red;}")
        else:
            self.statusBar.setStyleSheet("QStatusBar{padding-left:8px;}")
        self.statusBar.showMessage(msg, 10000)

    def removeViewTab(self,num):
        self.viewerList[num].clearReader() 
        self.viewTabs.removeTab(num)
        del self.viewerList[num]
        if num == self.viewTabs.currentIndex():
            if num == len(self.viewerList):
                num = num - 1
        elif num < self.viewTabs.currentIndex():
            num = self.viewTabs.currentIndex() - 1
        else:
            num = self.viewTabs.currentIndex()
        if len(self.viewerList) == 0:
            self.viewTabs.hide()
            self.currentViewer = None
        else:
            self.viewTabs.setCurrentIndex(num)
            self.currentViewer = self.viewerList[num]
        self.menuCheck()

    def removeEditTab(self,num):
        self.editorList[num].clearReader() 
        self.editTabs.removeTab(num)
        del self.editorList[num]
        if num == self.editTabs.currentIndex():
            if num == len(self.editorList):
                num = num - 1
        elif num < self.editTabs.currentIndex():
            num = self.editTabs.currentIndex() - 1
        else:
            num = self.editTabs.currentIndex()
        if len(self.editorList) == 0:
            self.editTabs.hide()
            self.currentEditor = None
        else:
            self.editTabs.setCurrentIndex(num)
            self.currentEditor = self.editorList[num]
        self.menuCheck()


    def initToolbar(self):
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.toggleViewAction().setEnabled(False)
        acts = [self.cleanOCRAct,self.headerDelAct,self.footerDelAct,self.emptyPagesAct,self.hyphenWordsAct,self.greekWidgetAct,self.formatWidgetAct]
        for act in acts:
            self.toolbar.addAction(act)


    def initMenu(self):
        IconDirectory = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'Icons' + os.path.sep
        self.menubar = self.menuBar()

        self.filemenu = QtWidgets.QMenu('File', self)
        self.menubar.addMenu(self.filemenu)
        self.openFileAct = self.filemenu.addAction('Add files', self.openFileDialog)
        self.openFolderAct = self.filemenu.addAction('Add folder', self.openFolderDialog)

        self.viewmenu = QtWidgets.QMenu('View', self)
        self.menubar.addMenu(self.viewmenu)
        self.splitterOrientAct = self.viewmenu.addAction('Toggle horizontal/vertical view', self.toggleSplitterOrient)

        self.imagemenu = QtWidgets.QMenu('Image viewer', self)
        self.menubar.addMenu(self.imagemenu)
        self.optimizePNGAct = self.imagemenu.addAction('Optimize png images', self.optimizePNG)


        self.textmenu = QtWidgets.QMenu('Text editor: pre', self)
        self.menubar.addMenu(self.textmenu)
        self.cleanOCRAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'clean.png'),'Clean OCR', self.cleanOCR)
        #self.greekTransAct = self.textmenu.addAction('Greek UTF8 --> Transliterated Greek', self.transliterateGreek)
        self.charCountAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'charcount.png'),'Get character count', self.charCount)
        self.wordListAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'wordcount.png'),'Get word list', self.wordList)
        self.hyphenWordsAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'corrhyphen.png'),'Correct EOL hyphens', self.hyphenCorrext)
        self.headerDelAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'head.png'),'Remove headers', self.headerDelWindow)
        self.footerDelAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'foot.png'),'Remove footers', self.footerDelWindow)
        self.emptyPagesAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'labelblank.png'),'Label blank pages', self.labelEmptyPages)
        self.greekWidgetAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'greek.png'),'Greek input window', self.textOpenGreek)
        self.copticWidgetAct = self.textmenu.addAction('Coptic input window', self.textOpenCoptic)
        self.cyrillicWidgetAct = self.textmenu.addAction('Cyrillic input window', self.textOpenCyrillic)
        self.hebrewWidgetAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'hebrew.png'),'Hebrew input window', self.textOpenHebrew)
        self.unicodeNormAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'uninorm.png'),'Unicode normalize', self.textUniNorm)
        self.unicodeWidgetAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'unicodeinput.png'),'Unicode input window', self.textOpenUnicode)
        self.searchWidgetAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'search.png'),'Search', self.textSearch, QtCore.Qt.CTRL + QtCore.Qt.Key_F)
        self.formatWidgetAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'format.png'),'Format tools', self.textFormat)
        
        self.textmenupost = QtWidgets.QMenu('Text editor: post', self)
        self.menubar.addMenu(self.textmenupost)
        self.searchDPmarksAct = self.textmenupost.addAction('Find DP markers', self.textDPSearch)
        self.tonos2OxiaAct = self.textmenupost.addAction('Convert Tonos to Oxia', self.textTonos2Oxia)
        self.starHyphenWidgetAct = self.textmenupost.addAction('Fix starred hyphens', self.textStarHyphen)

        self.textViewActs = [self.cleanOCRAct,self.charCountAct,self.wordListAct,
                            self.hyphenWordsAct,self.headerDelAct,self.footerDelAct,self.emptyPagesAct,
                            self.greekWidgetAct,self.hebrewWidgetAct,self.unicodeWidgetAct,
                            self.searchWidgetAct,self.searchDPmarksAct,self.tonos2OxiaAct,self.formatWidgetAct,self.starHyphenWidgetAct]

        self.helpmenu = QtWidgets.QMenu('Help', self)
        self.menubar.addMenu(self.helpmenu)
        self.aboutAction = self.helpmenu.addAction('&About', lambda: aboutWindow(self))

        self.menuCheck()


    def menuEnable(self,enable):
        self.textmenu.menuAction().setEnabled(enable)
        self.textmenupost.menuAction().setEnabled(enable) 
        self.imagemenu.menuAction().setEnabled(enable)
        self.helpmenu.menuAction().setEnabled(enable)

    def menuCheck(self):
        if self.currentEditor is not None:
            self.textmenu.menuAction().setEnabled(True)
            self.textmenupost.menuAction().setEnabled(True)
            for act in self.textViewActs:
                act.setEnabled(True)
        else:
            self.textmenu.menuAction().setEnabled(False)
            self.textmenupost.menuAction().setEnabled(False)
            for act in self.textViewActs:
                act.setEnabled(False)

        if  type(self.currentViewer) is ImgV.multiImageFrame:
            self.imagemenu.menuAction().setEnabled(True)
        else:
            self.imagemenu.menuAction().setEnabled(False)

    def toggleSplitterOrient(self):
        if self.splitterOrient == 'Horizontal':
            self.splitterOrient = 'Vertical'
        else:
            self.splitterOrient = 'Horizontal'

        if self.splitterOrient == 'Horizontal':
            self.main_widget.setOrientation(QtCore.Qt.Horizontal)
            self.viewTabs.setTabPosition(QtWidgets.QTabWidget.North)
            self.editTabs.setTabPosition(QtWidgets.QTabWidget.North)
        else:
            self.main_widget.setOrientation(QtCore.Qt.Vertical)
            self.viewTabs.setTabPosition(QtWidgets.QTabWidget.West)
            self.editTabs.setTabPosition(QtWidgets.QTabWidget.West)

    def optimizePNG(self):
        self.currentViewer.optimizePNG()

    def cleanOCR(self):
        CleanOCRWindow(self)

    def transliterateGreek(self):
        self.currentEditor.transliterateGreek()

    def hyphenCorrext(self):
        HyphenWindow(self)

    def charCount(self):
        CharCountWindow(self)

    def headerDelWindow(self):
        HeaderDelWindow(self)

    def footerDelWindow(self):
        FooterDelWindow(self)

    def labelEmptyPages(self):
        EmptyPagesWindow(self)

    def wordList(self):
        WordCountWindow(self)

    def textOpenGreek(self):
        self.currentEditor.openGreekWidget()

    def textOpenCoptic(self):
        self.currentEditor.openCopticWidget()

    def textOpenCyrillic(self):
        self.currentEditor.openCyrillicWidget()

    def textOpenHebrew(self):
        self.currentEditor.openHebrewWidget()

    def textUniNorm(self):
        self.currentEditor.normUni()

    def textOpenUnicode(self):
        self.currentEditor.openUnicodeWidget()

    def textSearch(self):
        self.currentEditor.openSearchWindow()

    def textFormat(self):
        self.currentEditor.openFormatWindow()

    def textStarHyphen(self):
        self.currentEditor.openStarHyphenFixWindow()


    def textDPSearch(self):
        self.currentEditor.openSearchDPWindow()

    def textTonos2Oxia(self):
        self.currentEditor.greekTonos2Oxia()

    def openFileDialog(self):
        fileList = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open File', self.lastLocation)
        if isinstance(fileList, tuple):
            fileList = fileList[0]
        if len(fileList) > 0:
            self.loadFiles(fileList)

    def openFolderDialog(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open File', self.lastLocation)
        if os.path.isdir(folder):
            # Get all files from this dir, and construct their absolute path.
            fileList = [os.path.join(folder,x) for x in os.listdir(folder) if os.path.isfile(os.path.join(folder,x))]
            if len(fileList) > 0:
                self.loadFiles(fileList)

    def loadFiles(self,fileList):
        self.lastLocation = os.path.dirname(fileList[-1])  # Save used path
        #Get all text files, sorted alphabetically
        textList = sorted([x for x in fileList if x.endswith('.txt')])
        htmlList = sorted([x for x in fileList if x.endswith('.html') or x.endswith('.htm')])

        #Get all image files, sorted alphabetically
        imageList = sorted([x for x in fileList if x.lower().endswith(IMG_TYPES)])
        if len(imageList):
            self.addImageViewer(imageList)
        if len(htmlList):
            for html in htmlList:
                self.addHtmlViewer(html)
                self.addHtmlEditor(html)
        if len(textList):
            self.addTextEdit(textList)

        self.menuCheck()

    def dropEvent(self, event):
        fileList = [url.toLocalFile() for url in event.mimeData().urls()]
        # Unpack folder if filelist has a single folder. 
        if len(fileList) == 1 and os.path.isdir(fileList[0]):
            dir = fileList[0]
            # Get all files from this dir, and construct their absolute path.
            fileList = [os.path.join(dir,x) for x in os.listdir(dir) if os.path.isfile(os.path.join(dir,x))]
        self.loadFiles(fileList)


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()


class HyphenWindow(wc.ToolWindow):
    NAME = 'Correct end of line hyphens'
    OKNAME = 'Apply'

    def __init__(self, parent):
        super(HyphenWindow, self).__init__(parent)
        self.checkText = QtWidgets.QCheckBox('Based on text')
        self.checkText.setChecked(True)
        self.grid.addWidget(self.checkText, 0, 0)
        self.checkDict = QtWidgets.QCheckBox('Based on dictionary')
        self.checkDict.setEnabled(False)
        self.grid.addWidget(self.checkDict, 1, 0)
        self.grid.addWidget(QtWidgets.QLabel('Otherwise:'),2,0)
        self.otherwiseDrop = QtWidgets.QComboBox()
        self.otherwiseDrop.addItems(['Do nothing','Join and keep hyphen','Join and remove hyphen'])
        self.grid.addWidget(self.otherwiseDrop, 3, 0)


    def applyFunc(self):
        useDict = self.checkDict.isChecked()
        useText = self.checkText.isChecked()
        otherwise = self.otherwiseDrop.currentIndex()
        self.father.currentEditor.delEOLHypenWords(useDict,useText,otherwise)


class EmptyPagesWindow(wc.ToolWindow):
    NAME = 'Label empty pages'
    OKNAME = 'Apply'

    def __init__(self, parent):
        super(EmptyPagesWindow, self).__init__(parent)
        self.grid.addWidget(QtWidgets.QLabel('Text to insert:'), 0, 0)
        self.text = QtWidgets.QLineEdit('[Blank Page]')
        self.grid.addWidget(self.text,1,0)

    def applyFunc(self):
        self.father.currentEditor.labelEmptyPage(self.text.text())



class CharCountWindow(wc.ToolWindow):
    NAME = 'Character Count'
    CANCELNAME = 'Close'
    OKNAME = 'Update'
    APPLYANDCLOSE = False
    RESIZABLE = True

    def __init__(self, parent):
        super(CharCountWindow, self).__init__(parent)
        self.grid.addWidget(QtWidgets.QLabel('Order:'), 0, 0)
        self.orderType = QtWidgets.QComboBox()
        self.orderType.addItems(['Alphabetically (Ascending)','Alphabetically (Descending)','Count (Ascending)',
            'Count (Descending)'])
        self.orderType.currentIndexChanged.connect(self.upd)
        self.grid.addWidget(self.orderType,0,1)
        self.table = QtWidgets.QTableWidget(1, 6)
        self.table.setHorizontalHeaderLabels(['Character', 'Code point', 'Name','Count','DP suite','Replace'])
        self.table.verticalHeader().hide()
        self.upd()
        self.grid.addWidget(self.table, 1, 0, 1, 6)
        self.resize(900, 800)
        #self.setGeometry(self.frameSize().width() - self.geometry().width(), self.frameSize().height(), 0, 0)

    def upd(self):
        ordType = self.orderType.currentIndex()
        counter = self.father.currentEditor.getCharCount()
        self.table.setRowCount(len(counter.keys()))

        if ordType == 0: #Alphabetical
            elements = sorted(counter.keys())
        elif ordType == 1: #Alphabetical, inverted
            elements = reversed(sorted(counter.keys()))
        elif ordType == 2: #By count
            vals = [counter[x] for x in counter.keys()]
            elements = [x for _,x in sorted(zip(vals,counter.keys()))] #Sort keys by counter values
        elif ordType == 3: #By count, inverted
            vals = [counter[x] for x in counter.keys()]
            elements = [x for _,x in reversed(sorted(zip(vals,counter.keys())))]

        for pos, val in enumerate(elements):
            char = val
            charOr = char
            code = "{0:#0{1}x}".format(ord(val),6) #Hex value of character
            count = str(counter[val])
            if ord(val) == 10:
                name = 'LINE FEED'
                char = '\\n'
            elif ord(val) == 12:
                name = 'FORM FEED'
                char = '\\f'
            else:
                try:
                    name = uni.name(val)
                except exception:
                    name = '?'
            # Get DP suite
            suite = '-'
            for key in glyphs.DPSuitesDict.keys():
                if char in glyphs.DPSuitesDict[key]:
                    suite = key
                    break

            item1 = QtWidgets.QTableWidgetItem(char)
            item1.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 0, item1)
            item2 = QtWidgets.QTableWidgetItem(code)
            item2.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 1, item2)
            item3 = QtWidgets.QTableWidgetItem(name)
            item3.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 2, item3)
            item4 = QtWidgets.QTableWidgetItem(count)
            item4.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 3, item4)
            item5 = QtWidgets.QTableWidgetItem(suite)
            item5.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 4, item5)
            item6 = QtWidgets.QPushButton('Replace')
            item6.clicked.connect(lambda arg, c=charOr: self.replaceChar(c))
            self.table.setCellWidget(pos, 5, item6)

        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.resizeColumnsToContents()

    def replaceChar(self,char):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Replace character by', 'Characters:')
        if ok:
            self.father.currentEditor.runRegexp([[re.escape(char),re.escape(text)]],all=True)
            self.upd()


    def applyFunc(self):
        self.father.currentEditor.saveCurrent()
        self.upd()


class WordCountWindow(wc.ToolWindow):
    NAME = 'Word Count'
    CANCELNAME = 'Close'
    OKNAME = 'Update'
    APPLYANDCLOSE = False
    RESIZABLE = True

    def __init__(self, parent):
        super(WordCountWindow, self).__init__(parent)
        self.grid.addWidget(QtWidgets.QLabel('Order:'), 0, 0)
        self.orderType = QtWidgets.QComboBox()
        self.orderType.addItems(['Alphabetically (Ascending)','Alphabetically (Descending)','Count (Ascending)',
            'Count (Descending)'])
        self.orderType.currentIndexChanged.connect(self.upd)
        self.grid.addWidget(self.orderType,0,1)
        self.harmonic = QtWidgets.QPushButton('Harmonic')
        self.grid.addWidget(self.harmonic,0,2)
        self.harmonic.setEnabled(False)
        self.harmonic.clicked.connect(self.popupHarmonics)
        self.table = QtWidgets.QTableWidget(1, 2)
        self.table.setHorizontalHeaderLabels(['Word','Count'])
        self.table.verticalHeader().hide()
        self.table.currentCellChanged.connect(self.selectChanged)
        self.wordList = None
        self.upd()
        self.grid.addWidget(self.table, 1, 0, 1, 6)
        self.resize(1, 800)

    def selectChanged(self,currentRow, currentColumn, previousRow, previousColumn):
        if self.table.currentRow() is None:
            self.harmonic.setEnabled(False)
        else:
            self.harmonic.setEnabled(True)

    def upd(self):
        ordType = self.orderType.currentIndex()
        self.wordList = self.father.currentEditor.getWordList()
        self.table.setRowCount(len(self.wordList.keys()))
        keys = self.wordList.keys()

        if ordType == 0 or ordType == 1: #Alphabetical
            lwr = [x.lower() for x in keys]
            # Remove diacritics for sorting
            nfkd = [uni.normalize('NFKD', x) for x in lwr]
            for pos, word in enumerate(nfkd):
                nfkd[pos] = ''.join([c for c in word if not uni.combining(c)])

            elements = [x for _,x in sorted(zip(nfkd,keys))]
            if ordType == 1:
                elements = reversed(elements)
        elif ordType == 2 or ordType == 3: #By count
            vals = [self.wordList[x] for x in keys]
            elements = [x for _,x in sorted(zip(vals,keys))] #Sort keys by counter values
            if ordType == 3: #By count, inverted
                elements = reversed(elements)

        for pos, val in enumerate(elements):
            word = val
            count = str(self.wordList[val])
            item1 = QtWidgets.QTableWidgetItem(word)
            item1.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 0, item1)
            item2 = QtWidgets.QTableWidgetItem(count)
            item2.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 1, item2)

        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.resizeColumnsToContents()

    def popupHarmonics(self):
        word = self.table.item(self.table.currentRow(), 0).text()
        HarmonicWindow(self,word)

    def applyFunc(self):
        self.father.currentEditor.saveCurrent()
        self.upd()

class HarmonicWindow(wc.ToolWindow):
    NAME = 'Harmonics'
    CANCELNAME = 'Close'
    APPLYANDCLOSE = False
    RESIZABLE = True
    MENUDISABLE = False

    def __init__(self, parent,word):
        super(HarmonicWindow, self).__init__(parent)
        self.word = word
        self.okButton.hide()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.grid.addWidget(QtWidgets.QLabel(f'<b>Harmonics for: {word}</b>'),0,0,1,2)

        self.table = QtWidgets.QTableWidget(1, 2)
        self.table.setHorizontalHeaderLabels(['Word','Count'])
        self.table.verticalHeader().hide()
        self.table.currentCellChanged.connect(self.selectChanged)
        self.grid.addWidget(self.table, 3, 0, 1, 2)
        self.grid.addWidget(QtWidgets.QLabel('Order:'),2,0)
        self.harmSpin = QtWidgets.QSpinBox()
        self.harmSpin.setMinimum(1)
        self.harmSpin.setMaximum(2)
        self.harmSpin.valueChanged.connect(self.upd)
        self.grid.addWidget(self.harmSpin,2,1)
        self.replacePush = QtWidgets.QPushButton('Replace with')
        self.replacePush.clicked.connect(self.replace)
        self.replacePush.setEnabled(False)
        self.grid.addWidget(self.replacePush,4,0,1,2)
        self.upd(1)
        self.resize(200, 600)

    def selectChanged(self):
        if self.table.currentRow() is None:
            self.replacePush.setEnabled(False)
        else:
            self.replacePush.setEnabled(True)

    def upd(self,order):
        if order == 1:
            harm = [x for x in self.father.wordList.keys() if distance.distanceIsOne(self.word,x)]
        elif order == 2:
            harm = [x for x in self.father.wordList.keys() if distance.distanceIsTwo(self.word,x)]
        self.table.setRowCount(len(harm))

        for pos, val in enumerate(harm):
            item1 = QtWidgets.QTableWidgetItem(val)
            item1.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 0, item1)
            item2 = QtWidgets.QTableWidgetItem(str(self.father.wordList[val]))
            item2.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 1, item2)

        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.resizeColumnsToContents()

    def replace(self):
        word = self.table.item(self.table.currentRow(), 0).text()
        print(word)


class HeaderDelWindow(wc.ToolWindow):
    NAME = 'Remove Headers'
    OKNAME = 'Apply'
    RESIZABLE = True
    R_NAME = 'Remove possible empty line after header'

    def __init__(self, parent):
        super(HeaderDelWindow, self).__init__(parent)
        self.table = QtWidgets.QTableWidget(1, 4)
        self.table.setHorizontalHeaderLabels(['Remove','Page #','Page name','Header'])
        self.table.verticalHeader().hide()
        self.table.itemClicked.connect(self.itemClicked)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.upd()
        self.grid.addWidget(self.table, 1, 0, 1, 6)
        self.cleanCheck = QtWidgets.QCheckBox(self.R_NAME)
        self.cleanCheck.setChecked(True)
        self.grid.addWidget(self.cleanCheck, 2, 0)
        self.resize(900, 800)
        self.father.currentEditor.setReadOnly(True)


    def itemClicked(self,item):
        if self.table.column(item) == 0:
            return
        row = self.table.row(item)
        check = self.checkList[row]
        if check is not None:
            state = check.checkState()
            if state:
                check.setCheckState(0)
            else:
                check.setCheckState(2)

    def getLines(self):
        return self.father.currentEditor.getHeaders()


    def upd(self):
        pagenames = self.father.currentEditor.textNames 
        self.table.setRowCount(len(pagenames))
        headers =  self.getLines()
        self.checkList = []
        for pos in range(len(pagenames)):


            item1 = QtWidgets.QTableWidgetItem(str(pos))
            item1.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 1, item1)
            item2 = QtWidgets.QTableWidgetItem(pagenames[pos])
            item2.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(pos, 2, item2)
            if headers[pos] is not None:
                item3 = QtWidgets.QTableWidgetItem(headers[pos])
                item3.setFlags(QtCore.Qt.ItemIsEnabled)
                self.table.setItem(pos, 3, item3)
                item0 = QtWidgets.QTableWidgetItem()
                item0.setCheckState(2)
                item0.setTextAlignment( QtCore.Qt.AlignCenter )
                self.table.setItem(pos, 0, item0)
                self.checkList.append(item0)
            else:
                self.checkList.append(None)


        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.resizeColumnsToContents()

    def closeEvent(self, *args):
        self.father.currentEditor.setReadOnly(False)
        wc.ToolWindow.closeEvent(self)

    def applyFunc(self):
        checks = [x.checkState() if x is not None else False for x in self.checkList]
        self.father.currentEditor.delHeaders(checks,self.cleanCheck.isChecked()) 


class FooterDelWindow(HeaderDelWindow):
    NAME = 'Remove Footers'
    R_NAME = 'Remove possible empty line before footer'

    def __init__(self, parent):
        super(FooterDelWindow, self).__init__(parent)
        self.table.setHorizontalHeaderLabels(['Remove','Page #','Page name','Footer'])

    def getLines(self):
        return self.father.currentEditor.getFooters()

    def applyFunc(self):
        checks = [x.checkState() if x is not None else False for x in self.checkList]
        self.father.currentEditor.delFooters(checks,self.cleanCheck.isChecked()) 



class CleanOCRWindow(wc.ToolWindow):
    NAME = 'Clean OCR'
    OKNAME = 'Run'
    RESIZABLE = False

    PRESETS = ['English','Dutch','Empty']

    def __init__(self, parent):
        super(CleanOCRWindow, self).__init__(parent)

        self.grid.addWidget(QtWidgets.QLabel('Preset:'),0,0)

        self.presetDrop = QtWidgets.QComboBox()
        self.presetDrop.addItems(self.PRESETS)
        self.presetDrop.currentIndexChanged.connect(self.setBools)
        self.grid.addWidget(self.presetDrop,0,1)

        self.tabs = QtWidgets.QTabWidget(self)

        whiteWid = QtWidgets.QWidget(self)
        whiteGrid = QtWidgets.QGridLayout(whiteWid)
        self.whiteChecks = []
        whitelabels = ['Convert tab to space','Remove form feed character','Convert multiple white spaces to one',
        'Remove leading white spaces on each line','Remove trailing white spaces on each line',
        'Remove white lines at the start of each page','Remove white lines at the end of each page',
        'Merge multiple white lines to one']
        #A list with the names of each option.
        self.whiteCodeList = ['tabtospace','formfeed','multiwhite',
        'leadingwhite','trailingwhite',
        'startlines','endlines',
        'multilines']
        for pos, name in enumerate(whitelabels):
            self.whiteChecks.append(QtWidgets.QCheckBox(name))
            whiteGrid.addWidget(self.whiteChecks[-1],pos,0)
        whiteGrid.setRowStretch(20,1)
        self.tabs.addTab(whiteWid, 'White spaces')

        #Punctuation

        punctWid = QtWidgets.QWidget(self)
        punctGrid = QtWidgets.QGridLayout(punctWid)
        self.punctChecks = []
        punctGrid.addWidget(QtWidgets.QLabel('Remove white spaces before:'),0,0)
        labels = ['Colons','Semicolons','Periods','Commas','Questions marks',
        'Exclamation marks','Closing brackets )']
        self.punctCodeList = ['fixcolon','fixscolon','fixperiod','fixcomma','fixquestion',
        'fixexlam','fixclosebrack','fixopenbrack','convellip','emdashconv','emspace','emdashEOL',
        'emdashSOL','underscoreconv','bracesconv','commapara']
        for pos, name in enumerate(labels):
            self.punctChecks.append(QtWidgets.QCheckBox(name))
            punctGrid.addWidget(self.punctChecks[-1],pos + 1,0)

        punctGrid.addWidget(QtWidgets.QLabel('Remove white spaces after:'),20,0)
        punctAfterlabels = ['Opening brackets (']
        for pos, name in enumerate(punctAfterlabels):
            self.punctChecks.append(QtWidgets.QCheckBox(name))
            punctGrid.addWidget(self.punctChecks[-1],pos + 21,0)

        punctGrid.addWidget(QtWidgets.QLabel('Other:'),40,0)

        punctOtherlabels = ['Convert ellipsis to three periods','Convert em-dash to --',
        'Remove spaces on either side of --','Join EOL -- with next word',
        'Join start of line -- with previous word','Convert _ to -','Convert {} to ()',
        'Convert end of paragraph , to .']
        for pos, name in enumerate(punctOtherlabels):
            self.punctChecks.append(QtWidgets.QCheckBox(name))
            punctGrid.addWidget(self.punctChecks[-1],pos + 41,0)
        self.tabs.addTab(punctWid, '.,!?:;()—')

        #Quotes
        quotesWid = QtWidgets.QWidget(self)
        quotesGrid = QtWidgets.QGridLayout(quotesWid)
        self.quotesChecks = []


        quoteslabels = ['Correct white spaces around curly double quotes',
        'Convert two single quotes to a double quote','Convert two commas to a double quote',
        'Convert curly single quotes to straight',
        'Convert curly double quotes to straight']
        self.quotesCodeList = ['curlyquotespace','stodquote','commatoquote','curlysingle','curlydouble']
        for pos, name in enumerate(quoteslabels):
            self.quotesChecks.append(QtWidgets.QCheckBox(name))
            quotesGrid.addWidget(self.quotesChecks[-1],pos,0)
        quotesGrid.setRowStretch(20,1)
        self.tabs.addTab(quotesWid, 'Quotes')

        #LOTE
        loteWid = QtWidgets.QWidget(self)
        loteGrid = QtWidgets.QGridLayout(loteWid)
        self.loteChecks = []


        lotelabels = ['Correct spacing around « and »','Correct spacing around » and «',
        'Convert « and » to straight double quote','Covert lower single quote to straight upper',
        'Convert lower double quote to straight upper','Convert Ĳ/ĳ ligatures to I+J or i+j',
        'Convert several Greek characters to single quote','Convert Greek theta symbole to normal theta']
        self.loteCodeList = ['guillespace1','guillespace2',
        'quilletoquote','lowsquote','lowdquote','ijligature','greekTPK','greekTheta']
        for pos, name in enumerate(lotelabels):
            self.loteChecks.append(QtWidgets.QCheckBox(name))
            loteGrid.addWidget(self.loteChecks[-1],pos,0)
        loteGrid.setRowStretch(20,1)
        self.tabs.addTab(loteWid, 'LOTE')

        self.allChecks = self.whiteChecks + self.punctChecks + self.quotesChecks + self.loteChecks
        self.allCodeNames = self.whiteCodeList + self.punctCodeList + self.quotesCodeList + self.loteCodeList

        self.setBools()

        self.grid.addWidget(self.tabs, 1, 0, 1, 2)
        self.father.currentEditor.setReadOnly(True)

    def setBools(self):
        ind = self.presetDrop.currentIndex()
        if ind == 0: # English
            for elem in self.loteChecks:
                elem.setChecked(False)
            for elem in self.quotesChecks + self.punctChecks + self.whiteChecks:
                elem.setChecked(True)
        if ind == 1: # Dutch
            for elem in self.quotesChecks + self.punctChecks + self.whiteChecks:
                elem.setChecked(True)
            for elem in self.loteChecks: # first disable all LOTE
                elem.setChecked(False)
            for pos in [3,4,5]:
                self.loteChecks[pos].setChecked(True)
        elif ind == 2: # Empty
            for elem in self.loteChecks + self.quotesChecks + self.punctChecks + self.whiteChecks:
                elem.setChecked(False)


    def closeEvent(self, *args):
        self.father.currentEditor.setReadOnly(False)
        wc.ToolWindow.closeEvent(self)

    def applyFunc(self):
        names = [x[1] for x in zip(self.allChecks,self.allCodeNames) if x[0].isChecked()]
        self.father.currentEditor.cleanOCR(names)

class aboutWindow(wc.ToolWindow):

    NAME = "About"
    RESIZABLE = True
    MENUDISABLE = False

    def __init__(self, parent):
        super(aboutWindow, self).__init__(parent)
        self.cancelButton.hide()
        self.logo = QtWidgets.QLabel(self)
        self.logo.setPixmap(QtGui.QPixmap(os.path.dirname(os.path.realpath(__file__)) + "/Icons/Splash.png"))
        self.tabs = QtWidgets.QTabWidget(self)
        self.text = QtWidgets.QTextBrowser(self)
        self.text.setOpenExternalLinks(True)
        self.license = QtWidgets.QTextBrowser(self)
        self.license.setOpenExternalLinks(True)
        licenseText = ''
        with open(os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'licenseHtml.txt') as f:
            licenseText = f.read()
        self.license.setHtml(licenseText)
        pythonVersion = sys.version
        pythonVersion = pythonVersion[:pythonVersion.index(' ')]
        self.text.setText('<p><b>Disprop ' + VERSION + '</b></p>' +
                          '<p>Copyright (&copy;) 2020-2021 Wouter Franssen.</p>'+
                          '<p><b>Inspired by:</b><br>guiprep, by Stephen Schultze.<br>guiguts, by Stephen Schulze.</p>' + 
                          '<b>Library versions</b>:<br>Python ' + pythonVersion +
                          '<br>PyQt ' + QtCore.PYQT_VERSION_STR +
                          '<br>Qt ' + QtCore.QT_VERSION_STR)
        self.thanks = QtWidgets.QTextEdit(self)
        self.thanks.setReadOnly(True)
        self.thanks.setHtml('<p></p>')
        self.tabs.addTab(self.text, 'Version')
        self.tabs.addTab(self.thanks, 'Thanks')
        self.tabs.addTab(self.license, 'License')
        self.grid.addWidget(self.logo, 0, 0, 1, 3, QtCore.Qt.AlignHCenter)
        self.grid.addWidget(self.tabs, 1, 0, 1, 3)
        self.resize(550, 700)

    def closeEvent(self, *args):
        self.deleteLater()


if __name__ == '__main__':
    mainProgram = MainProgram(root)
    mainProgram.setWindowTitle("Disprop - " + VERSION)
    mainProgram.show()
    splash.finish(mainProgram)
    sys.exit(root.exec_())
