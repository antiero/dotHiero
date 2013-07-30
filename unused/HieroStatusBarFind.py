# HieroFindWidget.py by Zachary Scheuren
# v1.1 30/04/13
# Adds a Find submenu to the main Edit menu with the standard
# actions "Find...", "Find Next", and "Find Previous"
# Dock the widget and then use the hotkeys (Alt+Cmd+F, Cmd+G, Shift+Cmd+G)
# to search for track items by text in shot names, metadata, or tag notes.
# Search using either plain text or regular expressions.
# Optionally filter the results using tag combination presets.

import hiero
from PySide.QtGui import *
from PySide.QtCore import *
from hiero.ui.BuildExternalMediaTrack import *
from hiero.ui.nuke_bridge.send_to_nuke import *
from hiero.ui.nuke_bridge.hiero_state import *
import re
import ast

class FindAction(QAction):
  def __init__(self):
    QAction.__init__(self, "Find...", None)
    self.triggered.connect(self.openDialog)
    self.setShortcut(QKeySequence('Alt+Ctrl+F'))

  def openDialog(self):
    '''Open the Find panel
    '''
    # Open the Find pane if it's not already open. Then set focus on it.
    for action in hiero.ui.mainWindow().menuBar().actions():
      if action.text() == "&Window":
        for sub in action.menu().actions():
          if sub.text() == "Find":
            sub.trigger()

    for widget in QApplication.allWidgets():
      try:
        if widget.windowTitle() == "Find":
          widget.setFocus()
          for child in widget.findChildren(QWidget):
            if child.objectName() == "tagfilterbox":
              child.populateFromTags()
          for child in widget.findChildren(QLineEdit):
            if child.objectName() == "searchTextField":
              child.setFocus()
          break
      except:
        pass

  class FindBar(QWidget):
    def __init__(self):
      QWidget.__init__( self )

      self.setObjectName( "uk.co.thefoundry.findbar" )

      self.mainWidget = hiero.ui.mainWindow().statusBar()

      self.label = QLabel("Find:")
      self.label.setObjectName("findLabel")
      self.mainWidget.addWidget(self.label)

      self.searchTextField = SearchTextField()
      self.searchTextField.setObjectName("searchTextField")
      self.searchTextField.setToolTip("Enter Text to Search For")
      self.mainWidget.addWidget(self.searchTextField)
      self.searchTextField.returnPressed.connect(self.findMatches)
      self.searchTextList = []

      self.searchOptionsComboBox = QComboBox()
      self.searchOptionsComboBox.setObjectName("searchOptionsComboBox")
      self.searchOptionsComboBox.setToolTip("Search for Text in Shot Names, Metadata, Tag Notes, or All")
      self.searchOptionsComboBox.addItem("Search All")
      self.searchOptionsComboBox.addItem("Search Names")
      self.searchOptionsComboBox.addItem("Search Metadata")
      self.searchOptionsComboBox.addItem("Search Tag Notes")

      self.nextButton = QPushButton("Find Next", self)
      self.nextButton.setToolTip("Go to the Next Result.")
      self.nextButton.setAutoDefault(False)
      self.nextButton.setObjectName("nextButton")
      self.nextButton.clicked.connect(self.findNext)

      self.previousButton = QPushButton("Find Previous", self)
      self.previousButton.setToolTip("Go to the Previous Result.")
      self.previousButton.setAutoDefault(False)
      self.previousButton.setObjectName("previousButton")
      self.previousButton.clicked.connect(self.findPrevious)

      self.ignoreCase = QCheckBox("Ignore case") # Unused
      self.ignoreCase.setToolTip("Toggle case-(in)sensitive Search.")
      self.useRegex = QCheckBox("regex")
      self.useRegex.setToolTip("Use Regular Expressions to Search.")      
      
      self.statusLabel = QLabel("Ready")
      self.statusLabel.setTextFormat(PySide.QtCore.Qt.TextFormat.LogText)
      #self.horizontalSearchFieldLayout.addWidget(self.searchOptionsComboBox)
      #self.horizontalSearchFieldLayout.addWidget(self.ignoreCase)
      self.mainWidget.addWidget(self.useRegex)
      self.mainWidget.addWidget(self.statusLabel)
      self.mainWidget.addWidget(self.previousButton)
      self.mainWidget.addWidget(self.nextButton)

      #self.searchAllInProject = QRadioButton("All Sequences in Open Projects")
      #self.searchAllInProject.setToolTip("Search All Sequences in all open projects whether they are open in a Viewer or not.\
      #                                   \nIf matches are found in an unopened sequence it will be opened to display the results.")

      self.tableWidget = QTableWidget()
      self.tableWidget.setObjectName("tableWidget")
      self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.tableWidget.setAlternatingRowColors(True)
      self.tableWidget.setSortingEnabled(True)
      self.tableWidget.doubleClicked.connect(self.goToResult)
      self.tableWidget.itemSelectionChanged.connect(self.resultSelectionChanged)
      self.tableWidget.clicked.connect(self.resultSelectionChanged)
      self.tableWidget.verticalHeader().hide()
      self.tableWidget.horizontalHeader().sectionClicked.connect(self.sortResultColumn)
      self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
      self.tableHeader = self.tableWidget.horizontalHeader()

      keyPressRedirect = FindResultsKeyPressRedirect(self)
      self.tableWidget.installEventFilter(keyPressRedirect)

      self.statusbar = QLabel()
      self.statusbar.setText("Ready")

      self.searchTextField.setFocus()

      self.currentMatchNumber = 0
      self.matchList = []

      self.nextTabAction = hiero.ui.findMenuAction("Next Tab")

      for widget in QApplication.allWidgets():
        try:
          if widget.windowTitle() == "Project":
            self.projectWindow = widget
            break
        except:
          pass

      self.findNextAction = FindNextAction(self)
      self.findPreviousAction = FindPreviousAction(self)
      self.findNextAction.setEnabled(False)
      self.findPreviousAction.setEnabled(False)

    def loadAutocompleter(self):
      '''Save some recent searches like Google
      '''
      searchmodel = QStandardItemModel()
      for i, word in enumerate(set(self.searchTextList)):
        item = QStandardItem(word)
        searchmodel.setItem(i, 0, item)

      self.searchTextField.setModel(searchmodel)
      self.searchTextField.setModelColumn(0)

    def updateStatusBar(self, message):
      '''Update the widget status bar with @message
      '''
      #self.statusbar.showMessage(message)
      self.statusLabel.setText(message)

    def findMatches(self):
      '''Find track items based on the given search string.
         Options: search by regular expressions, case-insensitive search,
         filter search results by tags.
      '''
      self.updateStatusBar("Searching...")
      self.matchList = []
      self.currentMatchNumber = 0

      trackItemList = self.allTrackItems(onlyOpen=True)

      searchText = self.searchTextField.text().encode("utf-8")
      if searchText:
        if len(self.searchTextList) == 10:
          self.searchTextList.pop(0)
        if searchText not in self.searchTextList:
          self.searchTextList.append(searchText)
        else:
          self.searchTextList.pop(self.searchTextList.index(searchText))
          self.searchTextList.append(searchText)
        self.loadAutocompleter()

      settings = hiero.core.ApplicationSettings()
      try:
        # We use a try/except here because you might enter some weird stuff
        # and it will fail. Without correct encoding Unicode broke this.
        # Seems ok now, but leaving the try in to be safe.
        settings.setValue(self.kLastFindDialogText, self.searchTextList)
      except:
        pass

      for trackItem in trackItemList:
        matchName = trackItem.name()
        matchSourceName = trackItem.source().name()
        matchMetadata = trackItem.metadata()
        matchSourceMetadata = trackItem.source().metadata()
        tagText = [item.note() for item in trackItem.tags()]

        if self.ignoreCase.isChecked() and self.useRegex.isChecked():
          try:
            regex = re.compile(searchText, re.IGNORECASE)
          except Exception as e:
            self.updateStatusBar("Invalid regex: %s" % str(e))
            regex = None

        if not self.ignoreCase.isChecked() and self.useRegex.isChecked():
          try:
            regex = re.compile(searchText)
          except Exception as e:
            self.updateStatusBar("Invalid regex: %s" % str(e))
            regex = None

        if self.searchOptionsComboBox.currentText() == "Search Names":
          if self.ignoreCase.checkState() == Qt.Checked:
            if self.useRegex.isChecked():
              if regex:
                nameMatch = regex.search(trackItem.name().lower())
                sourceNameMatch = regex.search(trackItem.source().name().lower())
                if nameMatch or sourceNameMatch:
                  self.matchList.append(trackItem)
              else:
                self.updateStatusBar("Invalid regex")
            else:
              for ref in [matchName, matchSourceName]:
                if searchText.lower() in ref.lower():
                  self.matchList.append(trackItem)
                  break
          else:
            if self.useRegex.isChecked():
              if regex:
                nameMatch = regex.search(trackItem.name())
                sourceNameMatch = regex.search(trackItem.source().name())
                if nameMatch or sourceNameMatch:
                  self.matchList.append(trackItem)
              else:
                self.updateStatusBar("Invalid regex")
            else:
              for ref in [matchName, matchSourceName]:
                if searchText in ref:
                  self.matchList.append(trackItem)
                  break

        if self.searchOptionsComboBox.currentText() == "Search Metadata":
          if self.ignoreCase.isChecked():
            if self.useRegex.isChecked():
              if regex:
                metaMatch = regex.search(str(matchMetadata).lower())
                sourcemetaMatch = regex.search(str(matchSourceMetadata).lower())
                if metaMatch or sourcemetaMatch:
                  self.matchList.append(trackItem)
              else:
                self.updateStatusBar("Invalid regex")
            else:
              for ref in [str(matchMetadata), str(matchSourceMetadata)]:
                if searchText.lower() in ref.lower():
                  self.matchList.append(trackItem)
                  break
          else:
            if self.useRegex.isChecked():
              if regex:
                metaMatch = regex.search(str(matchMetadata))
                sourcemetaMatch = regex.search(str(matchSourceMetadata))
                if metaMatch or sourcemetaMatch:
                  self.matchList.append(trackItem)
              else:
                self.updateStatusBar("Invalid regex")
            else:
              for ref in [str(matchMetadata), str(matchSourceMetadata)]:
                if searchText in ref:
                  self.matchList.append(trackItem)
                  break

        if self.searchOptionsComboBox.currentText() == "Search All":
          if self.ignoreCase.isChecked():
            if self.useRegex.isChecked():
              if regex:
                nameMatch = regex.search(trackItem.name().lower())
                sourceNameMatch = regex.search(trackItem.source().name().lower())
                metaMatch = regex.search(str(matchMetadata).lower())
                sourcemetaMatch = regex.search(str(matchSourceMetadata).lower())
                tagMatch = None
                for tag in trackItem.tags():
                  tagMatch = regex.search(tag.note().lower())
                  if tagMatch:
                    break
                if nameMatch or sourceNameMatch or metaMatch or sourcemetaMatch or tagMatch:
                  self.matchList.append(trackItem)
              else:
                self.updateStatusBar("Invalid regex")
            else:
              for ref in [matchName, matchSourceName, str(matchMetadata), str(matchSourceMetadata)]:
                if searchText.lower() in ref.lower():
                  self.matchList.append(trackItem)
                  matchFound = True
                  break
                else:
                  matchFound = False
              if not matchFound:
                for tag in trackItem.tags():
                  if searchText.lower() in tag.note().lower():
                    self.matchList.append(trackItem)
                    break
          else:
            if self.useRegex.isChecked():
              if regex:
                nameMatch = regex.search(trackItem.name())
                sourceNameMatch = regex.search(trackItem.source().name())
                metaMatch = regex.search(str(matchMetadata))
                sourcemetaMatch = regex.search(str(matchSourceMetadata))
                tagMatch = None
                for tag in trackItem.tags():
                  tagMatch = regex.search(tag.note())
                  if tagMatch:
                    break
                if nameMatch or sourceNameMatch or metaMatch or sourcemetaMatch or tagMatch:
                  self.matchList.append(trackItem)
              else:
                self.updateStatusBar("Invalid regex")
            else:
              for ref in [matchName, matchSourceName, str(matchMetadata), str(matchSourceMetadata)]:
                if searchText in ref:
                  self.matchList.append(trackItem)
                  matchFound = True
                  break
                else:
                  matchFound = False
              if not matchFound:
                for tag in trackItem.tags():
                  if searchText in tag.note():
                    self.matchList.append(trackItem)
                    break

        if self.searchOptionsComboBox.currentText() == "Search Tag Notes":
          if self.ignoreCase.isChecked():
            if self.useRegex.isChecked():
              if regex:
                for tag in trackItem.tags():
                  tagMatch = regex.search(tag.note().lower())
                  if tagMatch:
                    self.matchList.append(trackItem)
                    break
              else:
                self.updateStatusBar("Invalid regex")
            else:
                for tag in trackItem.tags():
                  if searchText in tag.note().lower():
                    self.matchList.append(trackItem)
                    break
          else:
            if self.useRegex.isChecked():
              if regex:
                for tag in trackItem.tags():
                  tagMatch = regex.search(tag.note())
                  if tagMatch:
                    self.matchList.append(trackItem)
                    break
              else:
                self.updateStatusBar("Invalid regex")
            else:
              for tag in trackItem.tags():
                if searchText in tag.note():
                  self.matchList.append(trackItem)
                  break

      if self.matchList:

        self.findNextAction.setEnabled(True)
        self.findPreviousAction.setEnabled(True)

        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(["#", "Name", "Track", "Sequence", "Project", "In", "Out"])
        # Set a reasonable default width based on the current size of the widget
        defaultWidth = (self.width()-145 + len(str(len(self.matchList)))*1 ) / 4
        self.tableHeader.setDefaultSectionSize( defaultWidth )# (self.width()-125) / 4)
        self.tableHeader.setStretchLastSection(True)
        self.tableHeader.setMinimumSectionSize(20)
        self.tableHeader.resizeSection(0, 30)
        self.tableHeader.resizeSection(5, 30)
        self.tableHeader.resizeSection(6, 30)
        self.tableHeader.setSortIndicatorShown(True)
        self.tableWidget.setRowCount(len(self.matchList))

        self.matchDict = {}
        for item in self.matchList:
          self.matchDict[self.matchList.index(item)] = item

        for i in self.matchDict:
          matchNumber = QTableWidgetItem()
          matchNumber.setData(Qt.DisplayRole, i+1)
          trackItem = self.matchList[i]
          trackItemName = QTableWidgetItem("%s (%s)" % (trackItem.name(), trackItem.source().name()))
          trackItemName.setData(Qt.UserRole, trackItem)
          trackItemName.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)

          trackItemSourceName = QTableWidgetItem(trackItem.source().name())
          trackItemSourceName.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)

          trackItemParentTrack = QTableWidgetItem(trackItem.parentTrack().name())
          trackItemParentTrack.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
          trackItemSequence = QTableWidgetItem(trackItem.sequence().name())
          trackItemSequence.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
          trackItemProject = QTableWidgetItem(trackItem.project().name())
          trackItemProject.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)

          timelineIn = QTableWidgetItem(str(trackItem.timelineIn()))
          timelineOut = QTableWidgetItem(str(trackItem.timelineOut()))
          self.tableWidget.setRowHeight(i, 16)
          self.tableWidget.setItem(i, 0, matchNumber)
          self.tableWidget.setItem(i, 1, trackItemName)
          self.tableWidget.setItem(i, 2, trackItemParentTrack)
          self.tableWidget.setItem(i, 3, trackItemSequence)
          self.tableWidget.setItem(i, 4, trackItemProject)
          self.tableWidget.setItem(i, 5, timelineIn)
          self.tableWidget.setItem(i, 6, timelineOut)
          self.update()

          trackRange = QTableWidgetSelectionRange(0, 0, 0, 6)
          self.tableWidget.setRangeSelected(trackRange, True)

        currentTrackItem = self.matchList[0]
        self.goToShot(currentTrackItem)
        self.updateStatusBar("%i of %i matches:\n%s / %s / %s" % (1, len(self.matchList), currentTrackItem.name(), currentTrackItem.parentTrack().name(), currentTrackItem.sequence().name()))
      else:
        for row in sorted(range(self.tableWidget.rowCount()+1), reverse=True):
          self.tableWidget.removeRow(row)
        for column in sorted(range(self.tableWidget.columnCount()+1), reverse=True):
          self.tableWidget.removeColumn(column)

        self.updateStatusBar("No matches found")
        self.searchTextField.setFocus()

    def findNext(self):
      '''Go to the Next match
      '''
      if self.matchList:
        if self.currentMatchNumber != -1:
          if self.currentMatchNumber+1 == len(self.matchList):
            self.currentMatchNumber = 0
          else:
            self.currentMatchNumber +=1
        elif self.currentMatchNumber == -1:
          self.currentMatchNumber = 0

        trackItem = self.updateCurrentResult()
        self.goToShot(trackItem)

      else:
        self.findMatches()

    def findPrevious(self):
      '''Go to the Previous match
      '''
      if self.matchList:
        if self.currentMatchNumber != -1:
          if self.currentMatchNumber == 0:
            self.currentMatchNumber = len(self.matchList)-1
          else:
            self.currentMatchNumber -=1
        elif self.currentMatchNumber == -1:
          self.currentMatchNumber = 0

        trackItem = self.updateCurrentResult()
        self.goToShot(trackItem)

      else:
        self.findMatches()

    def updateCurrentResult(self):
      '''Update the currently selected result and jump to the shot
      '''
      if self.currentMatchNumber == -1:
        self.currentMatchNumber = 0

      originalRowNumber = self.tableWidget.item(self.currentMatchNumber, 0).data(Qt.DisplayRole)
      currentItem = self.tableWidget.item(self.currentMatchNumber, 1)
      trackItem = currentItem.data(Qt.UserRole)
      activeView = hiero.ui.activeView()

      # Make sure the trackItem exists on a track before we try to select it
      itemExists = False
      try:
        if trackItem.parentTrack():
          itemExists = True
      except:
        itemExists = False

      if itemExists:
        self.updateStatusBar("%i of %i matches:\n%s / %s / %s" % (originalRowNumber, len(self.matchList), trackItem.name(), trackItem.parentTrack().name(), trackItem.sequence().name()))

      if isinstance(activeView, hiero.ui.TimelineEditor):
        activeView.selectNone()

      maxVal = len(self.matchList)
      trackRange = QTableWidgetSelectionRange(self.currentMatchNumber, 0, self.currentMatchNumber, 6)
      for selectedRange in self.tableWidget.selectedRanges():
        self.tableWidget.setRangeSelected(selectedRange, False)
      self.tableWidget.setRangeSelected(trackRange, True)
      self.tableWidget.scrollToItem(currentItem)

      return trackItem

    def findAllItems(self, rootbin, clips, sequences):
      '''Recursively find all clips and sequences in a bin.
         If started from the root bin of a project it will return
         all clips and sequences in the entire project.
      '''
      for s in rootbin:
        if isinstance(s, hiero.core.Bin):
          for item in s.items():
            if isinstance(item, hiero.core.BinItem) and hasattr(item, "activeItem"):
              if isinstance(item.activeItem(), hiero.core.Clip):
                clips.append(item.activeItem())
              if isinstance(item.activeItem(), hiero.core.Sequence):
                sequences.append(item.activeItem())
            elif isinstance(item, hiero.core.Bin):
                self.findAllItems([item], clips, sequences)
        elif isinstance(s, hiero.core.BinItem) and hasattr(s, "activeItem"):
          if isinstance(s.activeItem(), hiero.core.Clip):
            clips.append(s.activeItem())
          if isinstance(s.activeItem(), hiero.core.Sequence):
            sequences.append(s.activeItem())

      return clips, sequences

    def openViewers(self):
      '''Find all open Viewers
      '''
      allViewers = []
      for widget in QApplication.allWidgets():
        if "viewer" in widget.objectName():
          widget.setFocus()
          view = hiero.ui.activeView()
          allViewers.append(view)

      return allViewers

    def findViewer(self, sequence, start=None):
      '''Find a specific Viewer
      '''
      for widget in QApplication.allWidgets():
        try:
          if widget.windowTitle() == sequence.name() and "viewer" in widget.objectName():
            widget.setFocus()
            if hiero.ui.activeView().player().sequence() == sequence:
              return hiero.ui.activeView()
            else:
              continue
        except:
          pass

      return None

    def allTrackItems(self, onlyOpen=False):
      '''Search projects for all track items in all sequences.
         Optionally, only search sequences that are opened in a Viewer.
      '''
      trackItems = []
      if not onlyOpen:
        for project in hiero.core.projects():
          bin = project.clipsBin()
          clips, sequences = self.findAllItems(bin.items(), [], [])
          for sequence in sequences:
            items = self.trackItems(sequence)
            trackItems += items
      else:
        openViewers = self.openViewers()
        for viewer in openViewers:
          sequence = viewer.player().sequence()
          if isinstance(sequence, hiero.core.Sequence):
            items = self.trackItems(sequence)
            trackItems += items

      return trackItems

    def trackItems(self, sequence):
      '''Get all track items from a sequence
      '''
      trackItems = []
      for track in sequence:
        for ti in track:
          link = False
          if ti not in trackItems:
            for item in trackItems:
              if ti in item.linkedItems():
                link = True
            if not link:
              trackItems.append(ti)
            else:
              pass

      return trackItems

    def FindOrCreateTrack(self, sequence, trackName):
      track = None
      isNewTrack = False
      # Look for existing track
      for existingtrack in sequence.videoTracks():
        if existingtrack.trackName() == trackName:
          track = existingtrack
          break

      # No existing track. Create new video track
      if track is None:
        track = hiero.core.VideoTrack(str(trackName))
        sequence.addTrack(track)
        isNewTrack = True

      return track, isNewTrack

    def selectedResults(self):
      '''Return a list of the currently selected TrackItems in the Results Spreadsheet
      '''
      selectedRows = []
      selectedResults = []

      for selectedRange in self.tableWidget.selectedRanges():
        topRow = selectedRange.topRow()
        bottomRow = selectedRange.bottomRow()
        selectedRows = sorted(selectedRows + range(topRow, bottomRow+1))

      for i in selectedRows:
        trackItem = self.tableWidget.item(i, 1).data(Qt.UserRole)
        selectedResults.append(trackItem)

      return selectedResults

    def sortResultColumn(self, column):
      '''Sort the search results based on column clicked
      '''
      try:
        currentItem = self.tableWidget.selectedItems()[0]
      except:
        currentItem = None

      currentOrder = self.tableHeader.sortIndicatorOrder()

      self.tableWidget.sortItems(column)
      self.tableHeader.setSortIndicator(column, currentOrder)

      if currentItem:
        currentRow = self.tableWidget.currentRow()
        self.currentMatchNumber = currentRow

    def resultSelectionChanged(self):
      '''Handle change in the result selection
      '''
      currentRow = self.tableWidget.currentRow()
      if currentRow != -1:
        originalRowNumber = self.tableWidget.item(currentRow, 0).data(Qt.DisplayRole)
        currentTrackItem = self.tableWidget.item(currentRow, 1).data(Qt.UserRole)
        self.currentMatchNumber = currentRow
      else:
        try:
          self.currentMatchNumber = self.tableWidget.selectedRanges()[0].topRow()
        except:
          self.currentMatchNumber = 0
        originalRowNumber = self.tableWidget.item(self.currentMatchNumber, 0).data(Qt.DisplayRole)
        currentTrackItem = self.tableWidget.item(self.currentMatchNumber, 1).data(Qt.UserRole)

      # Make sure the trackItem exists on a track before we try to select it
      itemExists = False
      try:
        if currentTrackItem.parentTrack():
          itemExists = True
      except:
        itemExists = False

      if itemExists:
        self.updateStatusBar("%i of %i matches:\n%s / %s / %s" % (originalRowNumber, len(self.matchList), currentTrackItem.name(), currentTrackItem.parentTrack().name(), currentTrackItem.sequence().name()))
        return currentTrackItem
      else:
        self.findMatches()

    def goToResult(self):
      currentTrackItem = self.resultSelectionChanged()
      self.goToShot(currentTrackItem)

    def goToShot(self, trackItem):
      '''Go to the track item in the sequence.
      '''
      if not trackItem:
        return
      sequence = trackItem.parentSequence()

      cv = self.findViewer(sequence)
      if not cv:
        cv = hiero.ui.currentViewer()
        p = cv.player()
        p.setSequence(sequence)
      tIn = trackItem.timelineIn()
      cv.setTime(tIn)
      tl = hiero.ui.findMenuAction("Show Timeline Editor")
      settings = hiero.core.ApplicationSettings()
      tl.trigger()

      startView = hiero.ui.activeView()
      np = hiero.ui.findMenuAction("Next Pane")
      while not isinstance(hiero.ui.activeView(), hiero.ui.TimelineEditor):
        np.trigger()
        if hiero.ui.activeView() == startView:
          return None

      activeView = hiero.ui.activeView()
      if isinstance(activeView, hiero.ui.TimelineEditor):
        activeView.selectNone()
      if isinstance(activeView, hiero.ui.TimelineEditor) and activeView.sequence() == trackItem.sequence():
        activeView.setSelection(trackItem.linkedItems())
      QApplication.processEvents()
      sequence.editFinished()

      # Return focus to the search text field
      # Comment this out if you want focus to stay on the track item
      self.searchTextField.setFocus()

class SearchTextField(QLineEdit):
  def __init__(self, parent=None):
    super(SearchTextField, self).__init__(parent)

    self.completer = QCompleter(self)
    self.completer.setCompletionMode(QCompleter.PopupCompletion)
    self.pFilterModel = QSortFilterProxyModel(self)
    self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
    self.completer.setPopup(self.view())
    self.setCompleter(self.completer)
    self.textEdited[unicode].connect(self.pFilterModel.setFilterFixedString)

    self.setModelColumn(0)

  def setModel(self, model):
    self.pFilterModel.setSourceModel(model)
    self.completer.setModel(self.pFilterModel)

  def setModelColumn(self, column):
    self.completer.setCompletionColumn(column)
    self.pFilterModel.setFilterKeyColumn(column)

  def view(self):
    return self.completer.popup()

  def index(self):
    return self.currentIndex()

class FindResultsKeyPressRedirect(QObject):
  '''Redirects key presses inside the Find Results Spreadsheet
  '''
  def eventFilter(self, obj, event):
    if event.type() == QEvent.KeyPress and event.key() == Qt.Key(Qt.Key_Return):
      obj.parent().goToResult()
      return True
    if event.type() == QEvent.KeyPress and event.key() == Qt.Key(Qt.Key_Enter):
      obj.parent().goToResult()
      return True
    else:
      return False

class FindNextAction(QAction):
  def __init__(self, parent):
    QAction.__init__(self, "Find Next", None)
    self.triggered.connect(self.findNextAction)
    self.setShortcut(QKeySequence('Ctrl+G'))
    self.parent = parent

  def findNextAction(self):
    self.parent.findNext()

class FindPreviousAction(QAction):
  def __init__(self, parent):
    QAction.__init__(self, "Find Previous", None)
    self.triggered.connect(self.findPreviousAction)
    self.setShortcut(QKeySequence('Shift+Ctrl+G'))
    self.parent = parent

  def findPreviousAction(self):
    self.parent.findPrevious()


  def findAllItems(self, rootbin, clips, sequences):
    '''Recursively find all clips and sequences in a bin.
       If started from the root bin of a project it will return
       all clips and sequences in the entire project.
    '''
    for s in rootbin:
      if isinstance(s, hiero.core.Bin):
        for item in s.items():
          if isinstance(item, hiero.core.BinItem) and hasattr(item, "activeItem"):
            if isinstance(item.activeItem(), hiero.core.Clip):
              clips.append(item)
            if isinstance(item.activeItem(), hiero.core.Sequence):
              sequences.append(item)
          elif isinstance(item, hiero.core.Bin):
              self.findAllItems([item], clips, sequences)
      elif isinstance(s, hiero.core.BinItem) and hasattr(s, "activeItem"):
        if isinstance(s.activeItem(), hiero.core.Clip):
          clips.append(s)
        if isinstance(s.activeItem(), hiero.core.Sequence):
          sequences.append(s)

    return clips, sequences

findBar = FindAction.FindBar()
hiero.ui.mainWindow().statusBar().addWidget(findBar)
