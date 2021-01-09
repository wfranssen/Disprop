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

import widgetClasses as wc
import ImageViewer as ImgV
import TextViewer as TextV
import unicodedata as uni


IMG_TYPES = ('.png','.bmp','.tif','.tiff','.jpg','.jpeg','.pbm','.pgm','.ppm','.xbm','.xpm')

VERSION = 'v0.0'

class MainProgram(QtWidgets.QMainWindow):

    def __init__(self, root):
        super(MainProgram, self).__init__()
        self.setAcceptDrops(True)
        self.main_widget = QtWidgets.QSplitter(self)
        self.main_widget.setHandleWidth(10)
        self.setCentralWidget(self.main_widget)


        self.imageViewer = ImgV.multiImageFrame(self)
        self.main_widget.addWidget(self.imageViewer)
        self.imageViewer.setVisible(False)
        self.currentViewer = self.imageViewer

        #Text files
        self.textViewer = TextV.multiTextFrame(self)
        self.main_widget.addWidget(self.textViewer)
        self.textViewer.setVisible(False)
        self.currentEditor = self.textViewer

        # Settings
        self.initMenu()
        self.initToolbar()


        self.lastLocation = os.path.expanduser('~')

        self.resize(1000, 1000)
        self.show()

    def initToolbar(self):
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.toggleViewAction().setEnabled(False)
        acts = [self.cleanOCRAct,self.headerDelAct,self.footerDelAct,self.emptyPagesAct,self.hyphenWordsAct,self.greekWidgetAct]
        for act in acts:
            self.toolbar.addAction(act)


    def initMenu(self):
        IconDirectory = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'Icons' + os.path.sep
        self.menubar = self.menuBar()

        self.filemenu = QtWidgets.QMenu('File', self)
        self.menubar.addMenu(self.filemenu)
        self.openFileAct = self.filemenu.addAction('Add files', self.openFileDialog)
        self.openFolderAct = self.filemenu.addAction('Add folder', self.openFolderDialog)


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
        self.hebrewWidgetAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'hebrew.png'),'Hebrew input window', self.textOpenHebrew)
        self.unicodeNormAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'uninorm.png'),'Unicode normalize', self.textUniNorm)
        self.unicodeWidgetAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'unicodeinput.png'),'Unicode input window', self.textOpenUnicode)
        self.searchWidgetAct = self.textmenu.addAction(QtGui.QIcon(IconDirectory + 'search.png'),'Search', self.textSearch, QtCore.Qt.CTRL + QtCore.Qt.Key_F)
        
        self.textmenupost = QtWidgets.QMenu('Text editor: post', self)
        self.menubar.addMenu(self.textmenupost)
        self.searchDPmarksAct = self.textmenupost.addAction('Find DP markers', self.textDPSearch)

        self.textViewActs = [self.cleanOCRAct,self.charCountAct,self.wordListAct,
                            self.hyphenWordsAct,self.headerDelAct,self.footerDelAct,self.emptyPagesAct,
                            self.greekWidgetAct,self.hebrewWidgetAct,self.unicodeWidgetAct,
                            self.searchWidgetAct,self.searchDPmarksAct]

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
        if self.currentEditor.numberOfFiles():
            self.textmenu.menuAction().setEnabled(True)
            self.textmenupost.menuAction().setEnabled(True)
            for act in self.textViewActs:
                act.setEnabled(True)
        else:
            self.textmenu.menuAction().setEnabled(False)
            self.textmenupost.menuAction().setEnabled(False)
            for act in self.textViewActs:
                act.setEnabled(False)

        if self.currentViewer.numberOfFiles():
            self.imagemenu.menuAction().setEnabled(True)
        else:
            self.imagemenu.menuAction().setEnabled(False)

    def optimizePNG(self):
        self.currentViewer.optimizePNG()

    def cleanOCR(self):
        CleanOCRWindow(self)
        #self.textViewer.cleanOCR()

    def transliterateGreek(self):
        self.textViewer.transliterateGreek()

    def hyphenCorrext(self):
        HyphenWindow(self)
        #self.textViewer.getEOLHypenWords()

    def charCount(self):
        CharCountWindow(self)

    def headerDelWindow(self):
        HeaderDelWindow(self)

    def footerDelWindow(self):
        FooterDelWindow(self)

    def labelEmptyPages(self):
        EmptyPagesWindow(self)
        #self.textViewer.labelEmptyPage()

    def wordList(self):
        self.textViewer.getWordList()

    def textOpenGreek(self):
        self.textViewer.openGreekWidget()

    def textOpenHebrew(self):
        self.textViewer.openHebrewWidget()

    def textUniNorm(self):
        self.textViewer.normUni()

    def textOpenUnicode(self):
        self.textViewer.openUnicodeWidget()

    def textSearch(self):
        self.textViewer.openSearchWindow()

    def textDPSearch(self):
        self.textViewer.openSearchDPWindow()


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

        #Get all image files, sorted alphabetically
        imageList = sorted([x for x in fileList if x.lower().endswith(IMG_TYPES)])
        if len(imageList):
            self.imageViewer.setImageList(imageList)
        if len(textList):
            self.textViewer.setTextList(textList)

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
        self.father.textViewer.delEOLHypenWords(useDict,useText,otherwise)


class EmptyPagesWindow(wc.ToolWindow):
    NAME = 'Label empty pages'
    OKNAME = 'Apply'

    def __init__(self, parent):
        super(EmptyPagesWindow, self).__init__(parent)
        self.grid.addWidget(QtWidgets.QLabel('Text to insert:'), 0, 0)
        self.text = QtWidgets.QLineEdit('[Blank Page]')
        self.grid.addWidget(self.text,1,0)

    def applyFunc(self):
        self.father.textViewer.labelEmptyPage(self.text.text())



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
        self.table = QtWidgets.QTableWidget(1, 4)
        self.table.setHorizontalHeaderLabels(['Character', 'Code point', 'Name','Count'])
        self.table.verticalHeader().hide()
        self.upd()
        self.grid.addWidget(self.table, 1, 0, 1, 6)
        self.resize(900, 800)
        #self.setGeometry(self.frameSize().width() - self.geometry().width(), self.frameSize().height(), 0, 0)

    def upd(self):
        ordType = self.orderType.currentIndex()
        counter = self.father.textViewer.getCharCount()
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

        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.resizeColumnsToContents()

    def applyFunc(self):
        self.father.textViewer.saveCurrent()
        self.upd()




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
        self.father.textViewer.setReadOnly(True)


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
        return self.father.textViewer.getHeaders()


    def upd(self):
        pagenames = self.father.textViewer.textNames 
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
        self.father.textViewer.setReadOnly(False)
        wc.ToolWindow.closeEvent(self)

    def applyFunc(self):
        checks = [x.checkState() if x is not None else False for x in self.checkList]
        self.father.textViewer.delHeaders(checks,self.cleanCheck.isChecked()) 


class FooterDelWindow(HeaderDelWindow):
    NAME = 'Remove Footers'
    R_NAME = 'Remove possible empty line before footer'

    def __init__(self, parent):
        super(FooterDelWindow, self).__init__(parent)

    def getLines(self):
        return self.father.textViewer.getFooters()

    def applyFunc(self):
        checks = [x.checkState() if x is not None else False for x in self.checkList]
        self.father.textViewer.delFooters(checks,self.cleanCheck.isChecked()) 



class CleanOCRWindow(wc.ToolWindow):
    NAME = 'Clean OCR'
    OKNAME = 'Run'
    RESIZABLE = False

    def __init__(self, parent):
        super(CleanOCRWindow, self).__init__(parent)
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
            self.whiteChecks[-1].setChecked(True)
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
        'emdashSOL','underscoreconv','bracesconv']
        for pos, name in enumerate(labels):
            self.punctChecks.append(QtWidgets.QCheckBox(name))
            self.punctChecks[-1].setChecked(True)
            punctGrid.addWidget(self.punctChecks[-1],pos + 1,0)

        punctGrid.addWidget(QtWidgets.QLabel('Remove white spaces after:'),20,0)
        punctAfterlabels = ['Opening brackets (']
        for pos, name in enumerate(punctAfterlabels):
            self.punctChecks.append(QtWidgets.QCheckBox(name))
            self.punctChecks[-1].setChecked(True)
            punctGrid.addWidget(self.punctChecks[-1],pos + 21,0)

        punctGrid.addWidget(QtWidgets.QLabel('Other:'),40,0)

        punctOtherlabels = ['Convert ellipsis to three periods','Convert em-dash to --',
        'Remove spaces on either side of --','Join EOL -- with next word',
        'Join start of line -- with previous word','Convert _ to -','Convert {} to ()']
        for pos, name in enumerate(punctOtherlabels):
            self.punctChecks.append(QtWidgets.QCheckBox(name))
            self.punctChecks[-1].setChecked(True)
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
            self.quotesChecks[-1].setChecked(True)
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
            self.loteChecks[-1].setChecked(False)
            loteGrid.addWidget(self.loteChecks[-1],pos,0)
        loteGrid.setRowStretch(20,1)
        self.tabs.addTab(loteWid, 'LOTE')

        self.allChecks = self.whiteChecks + self.punctChecks + self.quotesChecks + self.loteChecks
        self.allCodeNames = self.whiteCodeList + self.punctCodeList + self.quotesCodeList + self.loteCodeList

        self.grid.addWidget(self.tabs, 1, 0, 1, 3)
        self.father.textViewer.setReadOnly(True)


    def closeEvent(self, *args):
        self.father.textViewer.setReadOnly(False)
        wc.ToolWindow.closeEvent(self)

    def applyFunc(self):
        names = [x[1] for x in zip(self.allChecks,self.allCodeNames) if x[0].isChecked()]
        self.father.textViewer.cleanOCR(names)

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
                          '<p>Copyright (&copy;) 2020 Wouter Franssen.</p>'+
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
