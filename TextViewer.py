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
import unicodedata as uni
import re
import collections as col
import math
import greek
import coptic
import widgetClasses as wc
import unicode as unicode

#QtGui.QFontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + '/DPSansMono.ttf')

class multiTextFrame(QtWidgets.QSplitter):
    def __init__(self,parent):
        QtWidgets.QWidget.__init__(self)
        self.father = parent
        self.font = 'DPSansMono'

        self.setHandleWidth(2)
        self.setOrientation(QtCore.Qt.Vertical)
        self.setStyleSheet("QSplitter::handle{background: gray;}")


        self.textWidget = QtWidgets.QWidget()
        self.textFrame = QtWidgets.QGridLayout(self.textWidget)
        self.addWidget(self.textWidget)

        self.textViewer = QtTextEdit(self)

        #Force LTR text
        #doc = self.textViewer.document()
        #textOption = doc.defaultTextOption()
        #textOption.setTextDirection(QtCore.Qt.LeftToRight)
        #doc.setDefaultTextOption(textOption)
        #self.textViewer.setDocument(doc)


        self.textFrame.addWidget(self.textViewer, 0, 0, 1, 11)
        self.textViewer.setAcceptRichText(False)
        self.textViewer.cursorPositionChanged.connect(self.cursorPositionChanged)
        self.textViewer.leave.connect(self.saveCurrent)

        self.textPageSpin = QtWidgets.QSpinBox(self)
        self.textPageSpin.setMinimum(1)
        self.textPageSpin.valueChanged.connect(self.changeTextIndex)
        self.textPageSpin.setEnabled(False)
        self.textFrame.addWidget(self.textPageSpin,1,1)
        self.textPageName = QtWidgets.QLabel('')
        self.textFrame.addWidget(self.textPageName,1,2)
        self.deleteButton = QtWidgets.QPushButton('X')
        self.deleteButton.clicked.connect(self.clearReader)
        self.textFrame.addWidget(self.deleteButton,1,0)
        self.textFrame.setColumnStretch(9,1)

        self.unicodeLabel = QtWidgets.QLabel('')
        self.textFrame.addWidget(self.unicodeLabel,1,10)
        self.textLocs = None
        self.textIndex = None
        self.inputWindowWidget = None

        self.lastSearch = ''
        self.setAcceptDrops(True)
        self.setStretchFactor(0, 1)

    def numberOfFiles(self):
        if self.textLocs is None:
            return 0
        else:
            return len(self.textLocs)

    def removeInputWindow(self):
        self.inputWindowWidget.deleteLater()
        self.inputWindowWidget = None

    def openGreekWidget(self):
        self.openInputWidget(GreekInputWindow(self))

    def openCopticWidget(self):
        self.openInputWidget(CopticInputWindow(self))

    def openHebrewWidget(self):
        self.openInputWidget(HebrewInputWindow(self))

    def openUnicodeWidget(self):
        self.openInputWidget(UnicodeInputWindow(self))

    def openSearchWindow(self):
        self.openInputWidget(SearchWindow(self,self.lastSearch))
        self.inputWindowWidget.input.setFocus()

    def openSearchDPWindow(self):
        self.openInputWidget(SearchDPWindow(self))

    def openInputWidget(self,widget):
        if self.inputWindowWidget is not None:
            self.removeInputWindow()
        self.inputWindowWidget = widget
        self.addWidget(self.inputWindowWidget)
        self.setStretchFactor(1, 0) # set stretch factor to 0, at least for greek

    def normUni(self):
        self.saveCurrent()
        index = self.textIndex
        self.saveText(index)
        if not all:
            locations = [self.textLocs[index - 1]]
        else:
            locations = self.textLocs


        for loc in locations:
            with open(loc,'r') as f:
                text = f.read()
            text = uni.normalize('NFC',text)

            with open(loc,'w') as f:
                f.write(text)

        self.reload()

    def setReadOnly(self,readOnly):
        self.textViewer.setReadOnly(readOnly)

    def changeTextIndex(self,index,save=True):
        if save:
            self.saveText(self.textIndex)
        self.textIndex = index
        self.reload()

    def reload(self):
        index = self.textIndex
        with open(self.textLocs[index - 1],'r') as f:
            text = f.read()
        self.textViewer.setCurrentFont(QtGui.QFont(self.font))
        self.textViewer.setPlainText(text)
        self.textPageName.setText(self.textNames[index - 1])
        self.textPageSpin.setValue(index)
        self.father.editTabs.setVisible(True)

    def indexIncrement(self, step = 'f'):
        if step == 'f':
            self.textIndex = min(self.textIndex + 1, len(self.textLocs))
        elif step == 'b':
            self.textIndex = max(self.textIndex - 1, 1)
        self.reload()
        if self.textIndex == 1 or self.textIndex == len(self.textLocs):
            return False
        else:
            return True


    def search(self,sstr,side,regex,loop):
        """
        Search the text files for a pattern. Move the cursor selection
        to the found match (if any).

        Input
        -----
        sstr: string, search pattern or regex
        side: string, 'f' or 'b', forwards or backwards
        regex: bool, True if regex search should be used
        loop: bool, if True, loop pages by incrementing index.
        """
        self.lastSearch = sstr
        cursor = self.textViewer.textCursor()
        text = self.textViewer.toPlainText()
        if regex is True:
            if side == 'f': #forward search
                tmp = text[cursor.selectionEnd():]
                m = re.search(sstr,tmp)
                pos = cursor.selectionEnd() + m.start()
            else:
                #Backwards search slow, as we need to find all elements first.
                #Is there a better solution?
                tmp = text[:cursor.selectionStart()]
                m = [x for x in re.finditer(sstr,tmp)][-1]
                pos = m.start()
            matchlen = len(m.group(0))
        else:
            if side == 'f': #forward search
                pos = text.find(sstr,cursor.selectionEnd())
            elif side == 'b': #backwards
                pos = text.rfind(sstr,0,cursor.selectionStart())
            matchlen = len(sstr)
            

        if pos != -1:
            cursor.setPosition(pos)
            cursor.setPosition(pos, QtGui.QTextCursor.MoveAnchor);
            cursor.setPosition(pos + matchlen, QtGui.QTextCursor.KeepAnchor);
            self.textViewer.setTextCursor(cursor)
        else: # not found, increment file index en search again. Improve by doing this on file
              # without loading it.
            if loop:
                check = self.indexIncrement(side)
                if side == 'b':
                    # If backwards, reset cursor to end of page.
                    cursor.movePosition(QtGui.QTextCursor.End)
                    self.textViewer.setTextCursor(cursor)
                if check:
                    self.search(sstr,side,regex,loop)
                else:
                    self.father.dispMsg('TextEdit: Reached file limits')


    def setTextList(self,pathList,reset=True):
        if len(pathList) > 0:
            self.clearReader()
            self.textLocs = pathList
            self.textNames = [os.path.basename(x) for x in pathList]
            self.textPageSpin.setValue(1)
            self.textPageSpin.setMaximum(len(self.textLocs))
            self.textPageSpin.setEnabled(True)
            if reset:
                self.changeTextIndex(1,save=False)

            self.father.editTabs.setVisible(True)

    def saveText(self,index):
        with open(self.textLocs[index - 1],'w') as f:
            f.write(self.textViewer.toPlainText())

    def saveCurrent(self):
        if self.textLocs is not None:
            self.saveText(self.textPageSpin.value())

    def clearReader(self):
        self.saveCurrent()
        self.textLocs = None
        self.textIndex = None
        self.textPageName.setText('')
        #self.setVisible(False)
        self.father.menuCheck()

    def dropEvent(self, event):
        self.father.dropEvent(event)

    def dragMoveEvent(self, event):
        pass
        
    def dragEnterEvent(self, event):   
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def cursorPositionChanged(self):
        Select = self.textViewer.textCursor().selectedText()

        if len(Select) == 1:
            self.unicodeLabel.setText(uni.name(Select[0]))
        else:
            self.unicodeLabel.setText('')

        #tc = self.textViewer.textCursor()
        #tbf = tc.blockFormat()
        #tbf.setLayoutDirection( QtCore.Qt.LeftToRight )
        #tc.setBlockFormat(tbf)
        #self.textViewer.setTextCursor(tc)


    def runRegexp(self,regexps,all=False):
        self.saveCurrent()
        index = self.textIndex
        self.saveText(index)
        if not all:
            locations = [self.textLocs[index - 1]]
        else:
            locations = self.textLocs

        for loc in locations:
            with open(loc,'r') as f:
                text = f.read()
            for elem in regexps:
                text = re.sub(elem[0],elem[1],text)

            with open(loc,'w') as f:
                f.write(text)

        self.reload()


    def cleanOCR(self,nameslist):
        """
        Creates and runs a series of regexp based an a list of input names.
        The names relate for the options that can be selected from an input window in the main program.
        Unused names are ignored.
        """
        RegExps = [] #Start of ther reagexp list.


        if 'formfeed' in nameslist:
            RegExps.append(['\f','']) #Remove form feed character
        if 'tabtospace' in nameslist:
            RegExps.append(['\t',' ']) #Tab to white space

        if 'multiwhite' in nameslist:
            RegExps.append([' +',' ']) #Replace multiple white spaces with one
        if 'fixscolon' in nameslist:
            RegExps.append([' +;',';']) #Remove white spaces before semi-colon
        if 'fixcolon' in nameslist:
            RegExps.append([' +:',':']) #Remove white spaces before colon
        if 'fixexlam' in nameslist:
            RegExps.append([' +!','!']) #Remove white spaces before exclamation mark
        if 'fixquestion' in nameslist:
            RegExps.append([' +\?','?']) #Remove white spaces before question mark
        if 'fixperiod' in nameslist:
            RegExps.append([' +\.','.']) #Remove white spaces before period
        if 'fixcomma' in nameslist:
            RegExps.append([' +,','.']) #Remove white spaces before comma


        if 'underscoreconv':
            RegExps.append(['_','-']) #Replace underscore with dash
        if 'emdashconv' in nameslist:
            RegExps.append(['—','--']) #Replace em-dash with --
        if 'emspace' in nameslist:
            RegExps.append([' *-- *','--']) #Remove white spaces around double-dash
        if 'emdashEOL' in nameslist:
            RegExps.append(['--\n(\S+) *','--\g<1>\n' ]) #Combine em-dash at EOL.
        if 'emdashSOL' in nameslist:
            RegExps.append(['(\S)\n--(\S+) *','\g<1>--\g<2>\n' ]) #Combine em-dash at SOL.

        if 'curlysingle' in nameslist:
            RegExps.append(['[’‘]',"'"]) #Convert curly single quotes to the easy one
        if 'stodquote' in nameslist:
            RegExps.append(["''",'"']) #Convert two single apostrophe signs to a double apostrophe

        #Correct white space around quotes
        if 'curlyquotespace' in nameslist:
            RegExps.append([' +”','”'])
            RegExps.append(['“ +','“']) 

        if 'guillespace1' in nameslist:
            RegExps.append([' +»','»'])
            RegExps.append(['« +','«']) 
        if 'guillespace2' in nameslist:
            RegExps.append([' +«','«'])
            RegExps.append(['» +','»']) 
        if 'quilletoquote' in nameslist:
            RegExps.append(['[«»]','"']) #Convert some other signs to quote marks

        if 'curlydouble' in nameslist:
            RegExps.append(['[”“]','"']) #Convert curly quotes to straight

        #Dutch lower quote conversions
        if 'lowdquote' in nameslist:
            RegExps.append(['„','"'])
        if 'lowsquote' in nameslist:
            RegExps.append(['‚',"'"])


        if 'bracesconv' in nameslist:
            RegExps.append(['{','('])
            RegExps.append(['}',')'])
        
        if 'fixopenbrack' in nameslist:
            RegExps.append(['\( +','(']) #Remove spaces after opening brackets
        if 'fixclosebrack' in nameslist:
            RegExps.append([' +\)',')']) #Remove spaces before closing brackets
        if 'commatoquote' in nameslist:
            RegExps.append([',,','"']) #Convert double comma to double quote
        if 'convellip' in nameslist:
            RegExps.append(['…',"..."]) #Convert ellipsis


        if 'ijligature' in nameslist:
            RegExps.append(['ĳ',"ij"]) #Convert ij ligature
            RegExps.append(['Ĳ',"IJ"]) #Convert IJ ligature
        if 'greekTPK' in nameslist:
            RegExps.append(['[͵᾿᾽΄̓͂]',"'"]) # convert Tonos Psili and Koronis to single quote
        if 'greekTheta' in nameslist:
            RegExps.append(['ϑ',"θ"]) #Normalize theta symbol to normal theta
            RegExps.append(['ϴ',"Θ"]) #Normalize theta symbol to normal thet


        if 'leadingwhite' in nameslist:
            RegExps.append([re.compile('^ +',re.MULTILINE),'']) #Leading whitespaces
        if 'trailingwhite' in nameslist:
            RegExps.append([re.compile(' +$',re.MULTILINE),'']) #End whitespaces

        if 'multilines' in nameslist:
            RegExps.append(['\n\n+','\n\n']) #Convert >1 empty line to 1 empty line
        if 'startlines' in nameslist:
            RegExps.append(['^\n+','']) #Remove starting white lines
        if 'endlines' in nameslist:
            RegExps.append(['\n+$','']) #Remove ending white lines

        #Some guiprep things for quotes and spaces
        #      $line =~ s/^" /"/;  # start of line doublequote	      
        #      $line =~ s/ "$/"/;  #  end of line doublequote
        #      $line =~s/\s"-/"-/g;
        #      $line =~s/the\s"\s/the\s"/g;
        #      $line =~s/([.,!]) (["'] )/$1$2/g;      # punctuation, space, quote, space

        self.runRegexp(RegExps,all=True)


    def labelEmptyPage(self,label='[Blank Page]'):
        """
        Insert a label on empty pages.
        """
        self.saveCurrent()
        for loc in self.textLocs:
            with open(loc,'r') as f:
                text = f.read().splitlines()
            if len(text) == 0:
                with open(loc,'w') as f:
                    f.write(label)
        self.reload()


    def transliterateGreek(self):
        regexp = []
        for elem in greek.GREEK_REMOVE_DIA:
            regexp.append(['[' + elem[0] + ']',elem[1]])

        regexp = regexp + greek.GREEK_TRANSLITERATE

        self.runRegexp(regexp,all=True)

    def greekTonos2Oxia(self):
        self.runRegexp(greek.GREEK_TONOS2OXIA,all=True)
        


    def getCharCount(self,all=True):
        self.saveCurrent()
        if not all:
            locations = [self.textLocs[self.textIndex - 1]]
        else:
            locations = self.textLocs
        text = ''
        for loc in locations:
            with open(loc,'r') as f:
                text = text + f.read()
        outDict = col.Counter(text)
        return outDict

    def getWordList(self,all=True):
        self.saveCurrent()
        if not all:
            locations = [self.textLocs[self.textIndex - 1]]
        else:
            locations = self.textLocs
        text = ''
        for loc in locations:
            with open(loc,'r') as f:
                text = text + f.read()
        outDict = getWordCount(text)
        return outDict

    def getLines(self,pos):
        """
        Returns a list with all lines of index 'pos' for all opened files.

        TODO: add check that index is ok.
        """
        lines = []
        for loc in self.textLocs:
            with open(loc,'r') as f:
                text = f.read().splitlines()
                if len(text) > 0:
                    lines.append(text[pos])
                else:
                    lines.append(None)

        return lines

    def getHeaders(self):
        return self.getLines(0)

    def getFooters(self):
        return self.getLines(-1)


    def delHeaders(self,checkList,cleanStart=True):
        """
        Remove the headers from the files.

        Input
        checkList: List with booleans, True if first line needs to be removed
        cleanStart: Boolean. If True, remove possible empty line after header.
        """
        self.saveCurrent()
        for pos, loc in enumerate(self.textLocs):
            if checkList[pos]:
                with open(loc,'r') as f:
                    text = f.read().splitlines()
                
                with open(loc,'w') as f:
                    if cleanStart and len(text) > 1 and text[1] == '':
                        f.writelines('\n'.join(text[2:]))
                    else:
                        f.writelines('\n'.join(text[1:]))
        self.reload()

    def delFooters(self,checkList,cleanStart=True):
        """
        Remove the footers from the files.

        Input
        checkList: List with booleans, True if first line needs to be removed
        cleanStart: Boolean. If True, remove possible empty line after header.
        """
        self.saveCurrent()
        for pos, loc in enumerate(self.textLocs):
            if checkList[pos]:
                with open(loc,'r') as f:
                    text = f.read().splitlines()
                
                with open(loc,'w') as f:
                    if cleanStart and len(text) > 1 and text[-2] == '':
                        f.writelines('\n'.join(text[:-2]))
                    else:
                        f.writelines('\n'.join(text[:-1]))
        self.reload()


    def delEOLHypenWords(self,useDict=False,useText=True,otherwise=0):
        self.saveCurrent()
        if not all:
            locations = [self.textLocs[self.textIndex - 1]]
        else:
            locations = self.textLocs
        if useText:
            wordDict = self.getWordList() #Get all words in the text

        for loc in locations:
            with open(loc,'r') as f:
                text = f.read()
            
            #Get all EOL hyphen words. Select also all non-whitespace characters
            #after, as well as a series of white spaces (excluding line endings).
            #After hyphen and EOL, at least 1 word character must be there.
            hyphenWords = re.findall('\w+-\n\w\S+[\s^\r\n]*', text)
            for w in hyphenWords:
                # Get the word
                usew = re.match('\w+-\n\w+',w).group(0)
                #Make the two options
                whyphen = usew.replace('\n','')
                wohyphen = usew.replace('-\n','')

                whFull = w.replace('\n','').rstrip()
                wohFull = w.replace('-\n','').rstrip()
                if useText:
                    wcount = wordDict[whyphen]
                    wocount = wordDict[wohyphen]
                    if wocount > wcount:
                        text = text.replace(w,wohFull+'\n',1)
                        continue
                    elif wcount > wocount:
                        text = text.replace(w,wohFull+'\n',1)
                        continue

                if useDict:
                    #Needs to be implemented
                    pass

                if otherwise == 1: #Keep hyphens
                    text = text.replace(w,whFull+'\n',1)
                elif otherwise == 2:
                    text = text.replace(w,wohFull+'\n',1)

            with open(loc,'w') as f:
                f.write(text)

        self.reload()

    def insertStr(self,string):
        self.textViewer.insertPlainText(string)

        

class QtTextEdit(QtWidgets.QTextEdit):
    
    leave = QtCore.pyqtSignal()

    def __init__(self,father):
        QtWidgets.QTextEdit.__init__(self)
        self.father = father
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.setAcceptDrops(True)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.setFont(font)
        doc = self.document()
        doc.setDefaultCursorMoveStyle(QtCore.Qt.VisualMoveStyle)
        # Adds extra line ends?
        #options= QtGui.QTextOption()
        #options.setTextDirection(QtCore.Qt.LeftToRight)
        #doc.setDefaultTextOption(options)


    def dropEvent(self, event):
        self.father.dropEvent(event)

    def dragMoveEvent(self, event):
        pass
        
    def dragEnterEvent(self, event):   
        self.father.dragEnterEvent(event)

    def leaveEvent(self, QEvent):
        self.leave.emit()




class SearchWindow(QtWidgets.QWidget):
    def __init__(self,parent,lastSearch):
        QtWidgets.QWidget.__init__(self)
        self.father = parent
        layout = QtWidgets.QGridLayout(self)
        layout.setColumnStretch(1,1)
        self.tabs = QtWidgets.QTabWidget(self)
        layout.addWidget(QtWidgets.QLabel('<b>Search window</b>'), 0, 0)
        self.closeButton = QtWidgets.QPushButton('Close')
        layout.addWidget(self.closeButton, 0, 2)
        self.frame = QtWidgets.QGridLayout()
        layout.addLayout(self.frame, 2, 0, 1, 3)
        self.closeButton.clicked.connect(self.father.removeInputWindow)
        self.input = QtWidgets.QLineEdit(lastSearch)
        self.input.returnPressed.connect(lambda: self.search('f'))
        self.frame.addWidget(self.input, 0, 0)
        self.leftSearch = QtWidgets.QPushButton('<--')
        self.leftSearch.clicked.connect(lambda: self.search('b'))
        self.frame.addWidget(self.leftSearch, 0, 1)
        self.rightSearch = QtWidgets.QPushButton('-->')
        self.rightSearch.clicked.connect(lambda: self.search('f'))
        self.frame.addWidget(self.rightSearch, 0, 2)
        self.regex = QtWidgets.QCheckBox('regex')
        self.frame.addWidget(self.regex, 0, 3)
        self.loopPages = QtWidgets.QCheckBox('Loop pages')
        self.frame.addWidget(self.loopPages, 1, 0)


    def search(self,side):
        text = self.input.text()
        regex = bool(self.regex.checkState())
        loop = bool(self.loopPages.checkState())
        if len(text) > 0:
            self.father.search(text,side,regex,loop)


class SearchDPWindow(QtWidgets.QWidget):
    def __init__(self,parent):
        QtWidgets.QWidget.__init__(self)
        self.father = parent
        layout = QtWidgets.QGridLayout(self)
        layout.setColumnStretch(1,1)
        self.tabs = QtWidgets.QTabWidget(self)
        layout.addWidget(QtWidgets.QLabel('<b>Search DP window</b>'), 0, 0)
        self.closeButton = QtWidgets.QPushButton('Close')
        layout.addWidget(self.closeButton, 0, 2)
        self.frame = QtWidgets.QGridLayout()
        layout.addLayout(self.frame, 2, 0, 1, 3)
        self.closeButton.clicked.connect(self.father.removeInputWindow)
        self.frame.addWidget(QtWidgets.QLabel('Backward:'), 0, 0)
        self.frame.addWidget(QtWidgets.QLabel('Forward:'), 1, 0)


        types = ['**','/*','*/','/#','#/']
        backBut = []
        forBut = []
        for pos, s in enumerate(types):
            backBut.append(QtWidgets.QPushButton(s))
            backBut[-1].clicked.connect(lambda arg, input=s: self.search(input,'b'))
            self.frame.addWidget(backBut[-1],0, pos + 1)
            forBut.append(QtWidgets.QPushButton(s))
            forBut[-1].clicked.connect(lambda arg, input=s: self.search(input,'f'))
            self.frame.addWidget(forBut[-1],1, pos + 1)


    def search(self,text,side):
        self.father.search(text,side,False,loop=True)


class CopticInputWindow(wc.CharInputWindow):
    TITLE = '<b>Coptic input window</b>'
    def __init__(self,parent):
        super(CopticInputWindow,self).__init__(parent)
        alChars = coptic.copticDict
        self.addTab('Alphabet', [alChars['u'],alChars['l']])
        self.addTab('Demotic Extensions', [alChars['du'],alChars['dl']])
  

class GreekInputWindow(QtWidgets.QWidget):
    def __init__(self,parent):
        QtWidgets.QWidget.__init__(self)
        self.father = parent
        layout = QtWidgets.QGridLayout(self)
        layout.setColumnStretch(1,1)
        self.tabs = QtWidgets.QTabWidget(self)
        layout.addWidget(QtWidgets.QLabel('<b>Greek input window</b>'), 0, 0)
        self.closeButton = QtWidgets.QPushButton('Close')
        layout.addWidget(self.closeButton, 0, 2)
        self.closeButton.clicked.connect(self.father.removeInputWindow)
        layout.addWidget(self.tabs, 1, 0, 1, 3)
        self.alphabet = QtWidgets.QWidget()
        self.frame = QtWidgets.QGridLayout()
        self.alphabet.setLayout(self.frame)

        self.tabs.addTab(self.alphabet, 'Alphabet')

        self.otherChars = QtWidgets.QWidget()
        self.frameChars = QtWidgets.QGridLayout()
        self.otherChars.setLayout(self.frameChars)
        self.tabs.addTab(self.otherChars, 'Other')

	#acute, tonos, grave, circum, smooth, rough, dia, macron, breve, iota
        # The labels we use for each modifier.
        self.diaNameList = ['A','T','G','C','S','R','D','M','B','I']
        # Here, we use dictionary with all possible characters. A separate list is made for upper/lower case.
        # Each combination of modifiers has a separate list. Each list is 25 positions, with None used to
        # signal that this character does not exist in unicode. We are very flexible in this way, and extra
        # modifiers (like var psi for example) can be easily included.
        self.charDict = greek.greekDiaDict

        # PreviewLabel
        self.previewLabel = QtWidgets.QLabel('')
        self.previewLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previewLabel.setStyleSheet("border: 1px solid gray;") 
        font = QtGui.QFont()
        font.setPointSize(30)
        self.previewLabel.setFont(font) 
        self.previewLabel.setMinimumWidth(60)
        self.previewLabel.setMaximumWidth(60)
        self.frame.addWidget(self.previewLabel,0,0,2,1)

 	# Create all buttons
        self.buttons = []
        letters = [self.charDict['u'],self.charDict['l']]
        for row, lst in enumerate(letters):
            for column, char in enumerate(lst):
                self.buttons.append(wc.specialButton(char))
                self.buttons[-1].setMinimumWidth(16)
                self.buttons[-1].clicked.connect(lambda arg, char=char: self.buttonPush(char))
                self.buttons[-1].enter.connect(lambda char=char: self.previewLabel.setText(char))
                self.buttons[-1].leave.connect(lambda char='': self.previewLabel.setText(char))
                # Lazy fix to not show capital end of word sigma
                if row == 0 and column == 18:
                    pass
                else:
                    self.frame.addWidget(self.buttons[-1],row,column + 1)



        # Create the frame and buttons for the modifiers.
        self.diaframe = QtWidgets.QGridLayout()
        self.frame.addLayout(self.diaframe, 3, 0, 1, 26)
        names = ['Acute','Tonos','Grave','Circumflex','Smooth','Rough','Diaeresis','Macron','Breve','Iota']
        tooltips = ['Acute (oxia)','Accent (tonos)','Grave (varia)','Circumflex (perispomeni)','Smooth breathing (psili)',
            'Rough breathing (dasia)','Diaeresis (dialytika)','Macron','Breve (vrachy)','Iota subscript (ypogegrammeni/prosgegrammeni)']
        self.modifierButtons = []
        modCharList = ['\u1FFD','\u0384','\u1FEF','\u1FC0','\u1FBF','\u1FFE','\u00A8',
        '\u0304','\u0306','\u037A']
        for pos, val in enumerate(names):
            self.modifierButtons.append(wc.specialButton(val))
            self.modifierButtons[-1].setCheckable(True)
            self.modifierButtons[-1].clicked.connect(self.refresh)
            self.modifierButtons[-1].setMinimumWidth(30)
            self.modifierButtons[-1].setToolTip(tooltips[pos])
            self.modifierButtons[-1].enter.connect(lambda char=modCharList[pos]: self.previewLabel.setText(char))
            self.modifierButtons[-1].leave.connect(lambda char='': self.previewLabel.setText(char))
            self.diaframe.addWidget(self.modifierButtons[-1],0,pos)

        # Create list of lists holding the modifier buttons that need to be deactivated
        # when a certain button is activated. This helps the user by disabling 'empty' options.
        self.modDeactive = []
        self.modDeactive.append([1,2,3,7,8])
        self.modDeactive.append([0,2,3,4,5,7,8,9])
        self.modDeactive.append([0,1,3,7,8])
        self.modDeactive.append([0,1,2,7,8])
        self.modDeactive.append([1,5,6,7,8])
        self.modDeactive.append([1,4,6,7,8])
        self.modDeactive.append([4,5,7,8,9])
        self.modDeactive.append([0,1,2,3,4,5,6,8,9])
        self.modDeactive.append([0,1,2,3,4,5,6,7,9])
        self.modDeactive.append([1,6,7,8])

        # Create the frame and buttons for the second tab.
        # PreviewLabel
        self.previewLabel2 = QtWidgets.QLabel('')
        self.previewLabel2.setAlignment(QtCore.Qt.AlignCenter)
        self.previewLabel2.setStyleSheet("border: 1px solid gray;") 
        self.previewLabel2.setFont(font) 
        self.previewLabel2.setMinimumWidth(60)
        self.previewLabel2.setMaximumWidth(60)
        self.frameChars.addWidget(self.previewLabel2,0,0,2,1)
        self.charButtons = []
        self.specialChar = greek.specialChars
                             
        for row, lst in enumerate(self.specialChar):
            for column, char in enumerate(lst):
                self.charButtons.append(wc.specialButton(char))
                self.charButtons[-1].setMinimumWidth(16)
                self.charButtons[-1].clicked.connect(lambda arg, char=char: self.buttonPush(char))
                self.charButtons[-1].setToolTip(uni.name(char))

                self.charButtons[-1].enter.connect(lambda char=char: self.previewLabel2.setText(char))
                self.charButtons[-1].leave.connect(lambda char='': self.previewLabel2.setText(char))
                self.frameChars.addWidget(self.charButtons[-1],row,column + 1)

        self.frameChars.setRowStretch(2,1)

        self.refresh()


    def refresh(self):
        """
        Refreshes the upper/lower button with changed diacritics.
        Activates/deactivates letters that do no exist with this combo
        and deactivates diacritics that cannot be added anymore.
        """
        lst = self.getCurrentChars()
        for pos, but in enumerate(self.buttons):
            if lst is None or lst[pos] is None:
                but.setEnabled(False)
            else:
                but.setEnabled(True)
                but.setText(lst[pos])
                hexname = 'U+' + "{0:#0{1}x}".format(ord(lst[pos]),6)[2:].upper()
                but.setToolTip(uni.name(lst[pos]) + ' (' + hexname + ')')
                # Is disconnect/connect the best way to reset the char?
                but.clicked.disconnect()
                but.clicked.connect(lambda arg, char=lst[pos]: self.buttonPush(char))
                but.enter.disconnect()
                but.enter.connect(lambda char=lst[pos]: self.previewLabel.setText(char))

        # Check button availability:
        states = [x.isChecked() for x in self.modifierButtons]
        #Turn all on to start with
        for button in self.modifierButtons:
            button.setEnabled(True)

        #Turn off all that is needed. Can be optimized by not deactivating multiple times.
        for pos, elem in enumerate(self.modDeactive):
            if states[pos]:
                for but in elem:
                    self.modifierButtons[but].setEnabled(False)


    def getCurrentChars(self):
        states = [x.isChecked() for x in self.modifierButtons]
        # Make key base on button states and the list of modifier keys. Join them to
        # get the key.
        key = ''.join([x[0] for x in zip(self.diaNameList,states) if x[1]])
        tmpkey = 'l' + key
        if tmpkey in self.charDict.keys():
             lower = self.charDict[tmpkey]
        else:
             lower = [None]*25 #If not in dict, no chars exist, so empty list
        tmpkey = 'u' + key
        if tmpkey in self.charDict.keys():
             upper = self.charDict[tmpkey]
        else:
             upper = [None]*25 #If not in dict, no chars exist, so empty list
        return upper + lower


    def buttonPush(self,char):
        self.father.insertStr(char)
        # Reset modifiers
        for button in self.modifierButtons:
            button.setChecked(False)
        self.refresh()



class HebrewInputWindow(QtWidgets.QWidget):
    def __init__(self,parent):
        QtWidgets.QWidget.__init__(self)
        self.father = parent
        layout = QtWidgets.QGridLayout(self)
        layout.setColumnStretch(1,1)
        self.tabs = QtWidgets.QTabWidget(self)
        layout.addWidget(QtWidgets.QLabel('<b>Hebrew input window</b>'), 0, 0)
        self.closeButton = QtWidgets.QPushButton('Close')
        layout.addWidget(self.closeButton, 0, 2)
        self.closeButton.clicked.connect(self.father.removeInputWindow)
        layout.addWidget(self.tabs, 1, 0, 1, 3)
        self.alphabet = QtWidgets.QWidget()
        self.frame = QtWidgets.QGridLayout()
        self.alphabet.setLayout(self.frame)

        self.tabs.addTab(self.alphabet, 'Alphabet')

        self.otherChars = QtWidgets.QWidget()
        self.frameChars = QtWidgets.QGridLayout()
        self.otherChars.setLayout(self.frameChars)
        self.tabs.addTab(self.otherChars, 'Other')


        # PreviewLabel
        self.previewLabel = QtWidgets.QLabel('')
        self.previewLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previewLabel.setStyleSheet("border: 1px solid gray;") 
        font = QtGui.QFont()
        font.setPointSize(30)
        self.previewLabel.setFont(font) 
        self.previewLabel.setMinimumWidth(60)
        self.previewLabel.setMaximumWidth(60)
        self.frame.addWidget(self.previewLabel,0,0,2,1)

        #'Dagesh','Sin','Shin','Hiriq','Sheva','Tsere','Segol','Patah','Qamats','Qubuts','Hataf Segol',
        # 'Hataf Patah','Hataf Qamats','Rafe'
        self.diaModList = ['\u05BC','\u05C2','\u05C1','\u05B4', '\u05B0', '\u05B5', '\u05B6',
        '\u05B7', '\u05B8','\u05C7', '\u05BB', '\u05B1', '\u05B2', '\u05B3', '\u05BF']

        self.alphabet = ['א','ב','ג','ד','ה','ו','ז','ח','ט','י','ך','כ','ל',
        'ם','מ','ן','נ','ס','ע','ף','פ','ץ','צ','ק','ר','ש','ת']

 	# Create all buttons
        self.buttons = []
        for column, char in enumerate(self.alphabet):
            self.buttons.append(wc.specialButton(char))
            self.buttons[-1].setMinimumWidth(16)
            self.buttons[-1].clicked.connect(lambda arg, char=char: self.buttonPush(char))
            self.buttons[-1].enter.connect(lambda char=char: self.previewLabel.setText(char))
            self.buttons[-1].leave.connect(lambda char='': self.previewLabel.setText(char))
            self.frame.addWidget(self.buttons[-1],0,column + 1)


        # Create the frame and buttons for the modifiers.
        self.diaframe = QtWidgets.QGridLayout()
        self.frame.addLayout(self.diaframe, 3, 0, 1, 28)
        names = self.diaModList
        self.modifierButtons = []

        modFont = QtGui.QFont()
        modFont.setPointSize(20)
        for pos, val in enumerate(names):
            self.modifierButtons.append(wc.specialButton(val))
            self.modifierButtons[-1].setCheckable(True)
            self.modifierButtons[-1].clicked.connect(self.refresh)
            self.modifierButtons[-1].setMinimumWidth(30)
            self.modifierButtons[-1].setFont(modFont)
            hexname = 'U+' + "{0:#0{1}x}".format(ord(val),6)[2:].upper()
            self.modifierButtons[-1].setToolTip(uni.name(val) + ' (' + hexname + ')')

            self.modifierButtons[-1].enter.connect(lambda char=val: self.previewLabel.setText(char))
            self.modifierButtons[-1].leave.connect(lambda char='': self.previewLabel.setText(char))
            self.diaframe.addWidget(self.modifierButtons[-1],0,pos)

        # Create list of lists holding the modifier buttons that need to be deactivated
        # when a certain button is activated. This helps the user by disabling 'empty' options.
        #self.modDeactive = []
        #self.modDeactive.append([1,2,3,7,8])
        #self.modDeactive.append([0,2,3,4,5,7,8,9])
        #self.modDeactive.append([0,1,3,7,8])
        #self.modDeactive.append([0,1,2,7,8])
        #self.modDeactive.append([1,5,6,7,8])
        #self.modDeactive.append([1,4,6,7,8])
        #self.modDeactive.append([4,5,7,8,9])
        #self.modDeactive.append([0,1,2,3,4,5,6,8,9])
        #self.modDeactive.append([0,1,2,3,4,5,6,7,9])
        #self.modDeactive.append([1,6,7,8])

        # Create the frame and buttons for the second tab.
        # PreviewLabel
        self.previewLabel2 = QtWidgets.QLabel('')
        self.previewLabel2.setAlignment(QtCore.Qt.AlignCenter)
        self.previewLabel2.setStyleSheet("border: 1px solid gray;") 
        self.previewLabel2.setFont(font) 
        self.previewLabel2.setMinimumWidth(60)
        self.previewLabel2.setMaximumWidth(60)
        self.frameChars.addWidget(self.previewLabel2,0,0,2,1)
        self.charButtons = []
        self.specialChar = ['׳','״','־','׀','־','׆']
                             
        for column, char in enumerate(self.specialChar):
            self.charButtons.append(wc.specialButton(char))
            self.charButtons[-1].setMinimumWidth(16)
            self.charButtons[-1].clicked.connect(lambda arg, char=char: self.buttonPush(char))
            self.charButtons[-1].enter.connect(lambda char=char: self.previewLabel2.setText(char))
            self.charButtons[-1].leave.connect(lambda char='': self.previewLabel2.setText(char))
            self.charButtons[-1].setToolTip(uni.name(char))
            self.frameChars.addWidget(self.charButtons[-1],0,column + 1)
        self.frameChars.setRowStretch(2,1)

        self.refresh()


    def refresh(self):
        """
        Refreshes the upper/lower button with changed diacritics.
        Activates/deactivates letters that do no exist with this combo
        and deactivates diacritics that cannot be added anymore.
        """
        lst = self.getCurrentChars()
        for pos, but in enumerate(self.buttons):
            if lst is None or lst[pos] is None:
                but.setEnabled(False)
            else:
                but.setEnabled(True)
                but.setText(lst[pos])
                hexnames = [' (U+' + "{0:#0{1}x}".format(ord(x),6)[2:].upper() + ')' for x in lst[pos]]
                name = ' + '.join([uni.name(x[0]) + x[1] for x in zip(lst[pos],hexnames)])
                but.setToolTip(name)
                # Is disconnect/connect the best way to reset the char?
                but.clicked.disconnect()
                but.clicked.connect(lambda arg, char=lst[pos]: self.buttonPush(char))
                but.enter.disconnect()
                but.enter.connect(lambda char=lst[pos]: self.previewLabel.setText(char))

        # Check button availability:
        states = [x.isChecked() for x in self.modifierButtons]
        #Turn all on to start with
        for button in self.modifierButtons:
            button.setEnabled(True)

        ##Turn off all that is needed. Can be optimized by not deactivating multiple times.
        #for pos, elem in enumerate(self.modDeactive):
        #    if states[pos]:
        #        for but in elem:
        #            self.modifierButtons[but].setEnabled(False)


    def getCurrentChars(self):
        states = [x.isChecked() for x in self.modifierButtons]
        #Get combining characters
        combine = ''.join([x[1] for x in zip(states,self.diaModList) if x[0]])
        out = [uni.normalize('NFKC',x + combine) for x in self.alphabet]
        return out

    def buttonPush(self,char):
        self.father.insertStr(char)
        # Reset modifiers
        for button in self.modifierButtons:
            button.setChecked(False)
        self.refresh()



class UnicodeInputWindow(QtWidgets.QWidget):
    def __init__(self,parent):
        QtWidgets.QWidget.__init__(self)
        self.father = parent
        layout = QtWidgets.QGridLayout(self)
        layout.setColumnStretch(1,1)
        layout.addWidget(QtWidgets.QLabel('<b>Unicode input window</b>'), 0, 0)
        self.closeButton = QtWidgets.QPushButton('Close')
        layout.addWidget(self.closeButton, 0, 2)
        self.closeButton.clicked.connect(self.father.removeInputWindow)

        self.buttonGroup = QtWidgets.QWidget()
        self.frame = QtWidgets.QGridLayout(self.buttonGroup)
        self.scrollFrame = QtWidgets.QScrollArea() 
        self.scrollFrame.setWidget(self.buttonGroup)
        self.scrollFrame.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollFrame.setWidgetResizable(True)


        bottomLayout = QtWidgets.QGridLayout()
        bottomLayout.addWidget(self.scrollFrame, 0, 1,2,1)
        bottomLayout.setRowStretch(1,1)
        layout.addLayout(bottomLayout,2,0,1,4)
        self.frame.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

        font = QtGui.QFont()
        font.setPointSize(30)
        self.previewLabel = QtWidgets.QLabel('')
        self.previewLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previewLabel.setStyleSheet("border: 1px solid gray;") 
        self.previewLabel.setFont(font) 
        self.previewLabel.setFixedSize(60,70)
        bottomLayout.addWidget(self.previewLabel,0,0)

     
        # Exclude all groups larger than 1000 chars. Quick fix to not run into
        # troubles with the 22000 Chinese characters. Perhaps just make a selection
        # ourselves, as guiguts does?

        self.uniBlocks = [x for x in unicode.uniBlocks if x[2]-x[1] < 2000]
        self.starts = []
        self.ends = []
        tmpnames = []
        self.minStr = []
        self.maxStr = []
        for name, start, end in self.uniBlocks:
            self.starts.append(start)
            self.ends.append(end)
            self.minStr.append("{0:#0{1}x}".format(start,6)[2:].upper())
            self.maxStr.append("{0:#0{1}x}".format(end,6)[2:].upper())
            tmpnames = [x[0] for x in self.uniBlocks]
        tmp = [x for x in sorted(zip(tmpnames,range(len(tmpnames))))]
        # Create list of the names on alphabetic order. Save the order change.
        self.namesOrder = [x[1] for x in tmp]
        self.names = [x[0] for x in tmp]

        self.ranges = [x[0] + '-' + x[1] for x in zip(self.minStr,self.maxStr)]
        #self.ranges = [x[0] + ': ' + x[1] for x in zip(ranges,tmpnames)]


        blockGrid = QtWidgets.QGridLayout()
        layout.addLayout(blockGrid,1,0,1,4)
        self.nameDrop = QtWidgets.QComboBox()
        self.nameDrop.addItems(self.names)
        self.nameDrop.activated.connect(self.namesUpdate)

        blockGrid.addWidget(QtWidgets.QLabel('Block range:'), 1, 0)
        blockGrid.addWidget(QtWidgets.QLabel('Block name:'), 1, 2)
        blockGrid.addWidget(self.nameDrop, 1, 3)
        blockGrid.setColumnStretch(4,1)

        self.rangeDrop = QtWidgets.QComboBox()
        self.rangeDrop.addItems(self.ranges)
        self.rangeDrop.activated.connect(self.rangesUpdate)
        blockGrid.addWidget(self.rangeDrop, 1, 1)

        self.lengths = [x[1] - x[0] + 1 for x in zip(self.starts,self.ends)]
        self.maxlength = max(self.lengths)
        self.buttons = []
        for pos in range(self.maxlength):
            self.buttons.append(wc.specialButton(''))
            self.buttons[-1].setMinimumWidth(16)
            self.buttons[-1].clicked.connect(lambda arg, char='': self.buttonPush(char))
            self.buttons[-1].enter.connect(lambda char='': self.previewLabel.setText(char))
            self.buttons[-1].leave.connect(lambda char='': self.previewLabel.setText(char))
            self.frame.addWidget(self.buttons[-1],math.floor(pos/20),pos%20)
        self.rangesUpdate(0)


    def namesUpdate(self,index):
        trueIndex = self.namesOrder[index]
        self.rangeDrop.setCurrentIndex(trueIndex)
        self.update(trueIndex)

    def rangesUpdate(self,index):
        self.nameDrop.setCurrentIndex(self.namesOrder.index(index))
        self.update(index)


    def update(self,index):
        start = self.starts[index]
        end = self.ends[index]
        length = self.lengths[index]
        for pos, val in enumerate(range(start, end + 1)):
            try:
                self.buttons[pos].clicked.disconnect()
            except:
                pass
            try:
                self.buttons[pos].enter.disconnect()
            except:
                pass



            char = chr(val)
            hexname = 'U+' + "{0:#0{1}x}".format(ord(char),6)[2:].upper()
            try:
                name = uni.name(char)
            except:
                self.buttons[pos].setText('')
                self.buttons[pos].setEnabled(False)
                self.buttons[pos].setToolTip(hexname)
                self.buttons[pos].enter.connect(lambda char='': self.previewLabel.setText(char))
            else:
                self.buttons[pos].setText(char)
                self.buttons[pos].clicked.connect(lambda arg, char=char: self.buttonPush(char))
                self.buttons[pos].enter.connect(lambda char=char: self.previewLabel.setText(char))
                self.buttons[pos].setToolTip(hexname + ': ' + name)
                self.buttons[pos].setEnabled(True)
            self.buttons[pos].setVisible(True)
        for pos in range(length,self.maxlength):
            self.buttons[pos].setVisible(False)


    def buttonPush(self,char):
        self.father.insertStr(char)

def getWordCount(text):
    text = re.sub('-----File: .+\.\w+-+',' ',text) #remove file headers
    text = re.sub('--+',' ',text) # remove long dashes
    text = re.sub('\*\*+',' ',text) # remove multiple stars
    text = re.sub('</?[ibf]>','',text) # remove i/b/f tags
    text = re.sub('</?sc>','',text) # remove <sc> tags
    text = re.sub('<tb>','',text) # remove <tb> tags
    # remove non-alphanumerical chars
    text = re.sub("[^\w,.'’\\-*]",' ',text)
    text = re.sub('[_]',' ',text) #Remove underscore that is in \w
    words = text.split() #split based on white chars
    # strip puntuation etc from left and right
    words = [w.strip('\'\.,') for w in words]
    # strip some chars from the left only
    words = [w.lstrip('-*') for w in words]

    # remove empty string
    words = [w for w in words if len(w) != 0]
        
    outDict = col.Counter(words)
    return outDict
