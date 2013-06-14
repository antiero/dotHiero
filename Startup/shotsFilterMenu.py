import hiero
import PySide

class Test(PySide.QtGui.QDialog):
    def __init__(self, parent=None):
        super(Test, self).__init__(parent)
        
        self._sequence = 0
        self._doingRefresh = 0

        #Add layouts/widgets
        self._mainLayout = PySide.QtGui.QVBoxLayout()
        
        self._mainSplitter = PySide.QtGui.QSplitter()
        self._mainSplitter.setOrientation(PySide.QtCore.Qt.Vertical)
        
        self._topFrame = PySide.QtGui.QFrame()
        self._topLayout = PySide.QtGui.QVBoxLayout()
        
        self._contextComboLayout = PySide.QtGui.QHBoxLayout()
        self._contextCombo = PySide.QtGui.QComboBox()
        self._contextCombo.addItem('Active Viewer')
        self._contextCombo.addItem('Fake Sequence 1')
        self._contextCombo.addItem('Fake Sequence 2')
        self._contextCombo.addItem('Fake Clip')
        
        self._contextRefresh = PySide.QtGui.QPushButton()
        self._contextRefresh.setText('Refresh')

        self._filterOptionsLayout = PySide.QtGui.QHBoxLayout()
        self._filterText = PySide.QtGui.QLabel()
        self._filterText.setText('Filter :')
        self._filterCombo = PySide.QtGui.QComboBox()
        self._filterCombo.addItem('All Shots')
        #self._filterCombo.addItem('Specific Shot')
        self._filterCombo.addItem('Specific Tag')
        #self._shotOptionsCombo = PySide.QtGui.QComboBox()
        #self._shotOptionsCombo.addItem('Shot0010')
        #self._shotOptionsCombo.addItem('Shot0020')
        #self._shotOptionsCombo.addItem('Shot0030')
        #self._shotOptionsCombo.setSizeAdjustPolicy(PySide.QtGui.QComboBox.AdjustToContents)
        self._tagOptionsCombo = PySide.QtGui.QComboBox()
        self._tagOptionsCombo.addItem('Tag1')
        self._tagOptionsCombo.addItem('Tag2')
        self._tagOptionsCombo.addItem('Tag3')
        self._tagOptionsCombo.setSizeAdjustPolicy(PySide.QtGui.QComboBox.AdjustToContents)
        
        self._tagsTable = PySide.QtGui.QTableWidget()
        self._tagsTable.setColumnCount(2)
        self._tagsTable.setRowCount(1)
        self._tagsTable.horizontalHeader().setVisible(True)
        self._tagsTable.verticalHeader().setVisible(False)
        self._tagsTable.setHorizontalHeaderLabels(('Frame','Note'))
        
        self._bottomFrame = PySide.QtGui.QFrame()
        self._bottomLayout = PySide.QtGui.QVBoxLayout()
        
        self._noteText = PySide.QtGui.QTextEdit()
        self._noteOptionsLayout = PySide.QtGui.QHBoxLayout()
        
        self._frameMode = PySide.QtGui.QComboBox()
        self._frameMode.addItem('Current Frame')
        self._frameMode.addItem('Custom Frame')
        self._frameMode.addItem('Current Sequence')
        #self._frameMode.addItem('Current Shot')
        self._frameInput = PySide.QtGui.QLineEdit()
        self._frameInput.setText("0")
        self._frameInput.setInputMask("000000")
        
        
        self._addNoteButton = PySide.QtGui.QPushButton()
        self._addNoteButton.setText('Add New Note')

        #Add widgets to layouts
        self._mainLayout.addWidget(self._mainSplitter)
        self._mainSplitter.addWidget(self._topFrame)
        self._topFrame.setLayout(self._topLayout)
        
        self._topLayout.addLayout(self._contextComboLayout)
        self._contextComboLayout.addWidget(self._contextCombo)
        self._contextComboLayout.addWidget(self._contextRefresh)
        self._contextComboLayout.addStretch()
        self._topLayout.addLayout(self._filterOptionsLayout)
        self._filterOptionsLayout.addWidget(self._filterText)
        self._filterOptionsLayout.addWidget(self._filterCombo)
        #self._filterOptionsLayout.addWidget(self._shotOptionsCombo)
        self._filterOptionsLayout.addWidget(self._tagOptionsCombo)
        self._filterOptionsLayout.addStretch()
        self._topLayout.addWidget(self._tagsTable)
        
        self._mainSplitter.addWidget(self._bottomFrame)
        self._bottomFrame.setLayout(self._bottomLayout)
        
        self._bottomLayout.addWidget(self._noteText)
        self._bottomLayout.addLayout(self._noteOptionsLayout)
        self._noteOptionsLayout.addWidget(self._frameMode)
        self._noteOptionsLayout.addWidget(self._frameInput)
        self._noteOptionsLayout.addStretch()
        self._noteOptionsLayout.addWidget(self._addNoteButton)
        
        self.setLayout(self._mainLayout)

        #Set sizes/initial states
        self._mainSplitter.setSizes([450, 100]) 
        self._frameInput.setMinimumSize(60,20) 
        self._tagsTable.setSelectionBehavior(PySide.QtGui.QAbstractItemView.SelectRows)
        self._tagsTable.horizontalHeader().resizeSection(0,50)
        self._tagsTable.horizontalHeader().setResizeMode(PySide.QtGui.QHeaderView.Stretch)
        self._tagsTable.horizontalHeader().setResizeMode(0, PySide.QtGui.QHeaderView.Fixed)
        self._tagsTable.horizontalHeader().setHighlightSections(False)
        
        #self._shotOptionsCombo.setVisible(False)
        self._tagOptionsCombo.setVisible(False)
        self._frameInput.setEnabled(False)
        self._addNoteButton.setEnabled(False)
        
        #Set Signals
        self._contextCombo.currentIndexChanged.connect(self.contextChanged)
        self._contextRefresh.clicked.connect(self.contextRefresh)
        self._filterCombo.currentIndexChanged.connect(self.filterTypeChanged)
        #self._shotOptionsCombo.currentIndexChanged.connect(self.shotOptionChanged)
        self._tagOptionsCombo.currentIndexChanged.connect(self.tagOptionChanged)
        self._tagsTable.cellClicked.connect(self.tableCellClicked)
        self._tagsTable.cellChanged.connect(self.tableCellChanged)
        self._noteText.textChanged.connect(self.noteTextChanged)
        self._frameMode.currentIndexChanged.connect(self.frameModeChanged)
        self._frameInput.textChanged.connect(self.frameNumberChanged)
        self._addNoteButton.clicked.connect(self.addNote)
        
        #Do Refresh
        self.refreshPanel()
        
    def getFrameAndSeqTagsOnSeq(self, seq) :
        if isinstance(seq, hiero.core.Sequence):
            return [tag for tag in seq.tags() if tag.metadata()['applieswhole'] == "0"], [tag for tag in seq.tags() if tag.metadata()['applieswhole'] == "1"]
        else : 
            return [], []
        
    def makeFrameTagItem(self, tag, index, table) :
    
        #Get vars
        if tag.metadata().hasKey('start') :
            frame = tag.metadata()['start']
        else : 
            frame = "Seq"
        label = tag.metadata()['label']
        note = tag.metadata()['note'] if tag.metadata().hasKey('note') else ""
        
        #Populate Item
        #print "Populating!\n\tIndex :", index, "\n\tFrame :", frame, "\n\tNote :", note
        self._tagsTable.setItem(index, 0, PySide.QtGui.QTableWidgetItem(frame))
        self._tagsTable.setItem(index, 1, PySide.QtGui.QTableWidgetItem(note))
        
    def setSequenceVar(self) :
        context = self._contextCombo.currentText()
        #Only Active Viewer currently works, as we can't query all open viewers through python
        if context == "Active Viewer" :
            self._sequence = hiero.ui.currentViewer().player().sequence().binItem().activeItem()
        else :
            self._sequence = None
            
    def refreshPanel(self) :
        print "Refreshing contents of table!"
        self._doingRefresh = 1

        #Get sequence tags
        self.setSequenceVar()
        if self._sequence and isinstance(self._sequence, hiero.core.Sequence) :
            frameTags, sequenceTags = self.getFrameAndSeqTagsOnSeq(self._sequence)
        else : 
            frameTags = []
            sequenceTags = []
        
        #Get filter type and filter
        validTags = []
        if self._filterCombo.currentText() == "All Shots" :
            validTags = (frameTags + sequenceTags)
        elif self._filterCombo.currentText() == "Specific Tag" :
            validTags = [x for x in (sequenceTags + frameTags) if x.name() == str(self._tagOptionsCombo.currentText())]
        #elif self._filterCombo.currentText() == "Specific Shot" :
        #   shotToCheck = self._shotOptionsCombo.currentText()
        
        #Set table column/row count
        self._tagsTable.setRowCount(len(validTags))
        
        #Populate table
        #For each, print frame, label and note
        for x, tag in enumerate(validTags) : 
            self.makeFrameTagItem(tag, x, self._tagsTable)
            
        self._doingRefresh = 0
        
    def returnShotsInSequenceByTrack(self, seq) :
        items = []
        videoTracks = seq.videoTracks()
        for track in videoTracks : 
            items.append([track.name(), track.items()])

        return items

    def contextChanged(self, newIndex) :
        print "Context changed. New Index is :", newIndex
        
        #Set Sequence, update filters and refresh panel.
        self.setSequenceVar()
        self.filterTypeChanged(self._filterCombo.currentIndex())
        self.refreshPanel()

    def contextRefresh(self) :
        print "Context refresh button clicked."
        
    def filterTypeChanged(self, newIndex) :
        print "Filter type changed. New Index is :", newIndex
        
        self._doingRefresh = 1
        
        if newIndex == 0 :
            #self._shotOptionsCombo.setVisible(False)
            self._tagOptionsCombo.setVisible(False)
            
#        elif newIndex == 1 : 
#            self._shotOptionsCombo.setVisible(True)
#            self._tagOptionsCombo.setVisible(False)
#            
#            #Clear combo and add new items
#            self._shotOptionsCombo.clear()
#            seqItems = self.returnShotsInSequenceByTrack(self._sequence)
#            for track in seqItems :
#                for item in track[1] :
#                    self._shotOptionsCombo.addItem(str(item.name()))
                   
        else : 
            #self._shotOptionsCombo.setVisible(False)
            self._tagOptionsCombo.setVisible(True)
            
            #Clear combo and add new items
            self._tagOptionsCombo.clear()
            frameTags, seqTags = self.getFrameAndSeqTagsOnSeq(self._sequence)
            
            #Get different tag types and sort
            tagNames = set()
            for tag in (frameTags + seqTags) :
                tagNames.add(str(tag.name()))
            
            tagNamesSorted = [tag for tag in tagNames]
            tagNamesSorted.sort()
            
            for tag in tagNamesSorted :
                self._tagOptionsCombo.addItem(tag)
            
            
        self._doingRefresh = 0
            
        self.refreshPanel()

#    def shotOptionChanged(self, newIndex) :
#        if self._doingRefresh == 0 :
#            print "Shots option changed. New Index is :", newIndex
#            self.refreshPanel()
        
    def tagOptionChanged(self, newIndex) :
        if self._doingRefresh == 0 :
            print "Tags option changed. New Index is :", newIndex
            self.refreshPanel()
        
    def tableCellClicked(self, row, column) :
        print "You clicked table row index :", row
        
    def tableCellChanged(self, row, column) :
        if self._doingRefresh == 0 :
            print "You changed text in table row :", row, "and column :", column
        
    def noteTextChanged(self) :
        text = self._noteText.toPlainText()
        print "Note text has changed. New text is :", text
        
        if len(text) < 1 :
            self._addNoteButton.setEnabled(False)
        else : 
            self._addNoteButton.setEnabled(True)
        
    def frameModeChanged(self, newIndex) :
        print "Frame mode changed. New Index is :", newIndex
        if newIndex == 1 :
            self._frameInput.setEnabled(True)
        else : 
            self._frameInput.setEnabled(False)

    def frameNumberChanged(self, newFrame) :
        print "Frame number changed. New Number is :", self._newFrame
        
    def addNote(self) :
        print "Add Note button clicked."
        
t = Test()
t.show()