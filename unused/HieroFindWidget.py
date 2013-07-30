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

  class FindDialog(QWidget):
    def __init__(self):
      QWidget.__init__( self )

      self.setObjectName( "uk.co.thefoundry.finddialog" )
      self.setWindowTitle( "Find" )
      self.setWindowIcon(QIcon("icons:Search-icon.png"))
      self.setContentsMargins( 20, 15, 5, 2 )

      self.gridLayout = QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      self.horizontalSearchFieldLayout = QHBoxLayout()
      self.horizontalSearchFieldLayout.setObjectName("horizontalSearchFieldLayout")

      self.label = QLabel("Find:")
      self.label.setObjectName("findLabel")
      self.horizontalSearchFieldLayout.addWidget(self.label)

      self.searchTextField = SearchTextField()
      self.searchTextField.setObjectName("searchTextField")
      self.searchTextField.setToolTip("Enter Text to Search For")
      self.horizontalSearchFieldLayout.addWidget(self.searchTextField)
      self.searchTextField.returnPressed.connect(self.findMatches)
      self.searchTextList = []

      self.searchOptionsComboBox = QComboBox(self)
      self.searchOptionsComboBox.setObjectName("searchOptionsComboBox")
      self.searchOptionsComboBox.setToolTip("Search for Text in Shot Names, Metadata, Tag Notes, or All")
      self.searchOptionsComboBox.addItem("Search All")
      self.searchOptionsComboBox.addItem("Search Names")
      self.searchOptionsComboBox.addItem("Search Metadata")
      self.searchOptionsComboBox.addItem("Search Tag Notes")

      self.horizontalSearchFieldLayout.addWidget(self.searchOptionsComboBox)
      self.gridLayout.addLayout(self.horizontalSearchFieldLayout, 0, 0, 1, 1)
      self.horizontalOptionsLayout = QHBoxLayout()
      self.horizontalOptionsLayout.setObjectName("horizontalOptionsLayout")
      spacerItem = QSpacerItem(35, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
      self.horizontalOptionsLayout.addItem(spacerItem)

      self.verticalLayout = QVBoxLayout()
      self.verticalLayout.setObjectName("verticalLayout")

      self.topLeftVerticalLayout = QVBoxLayout()
      self.topLeftVerticalLayout.setObjectName("topLeftVerticalLayout")

      self.topRightVerticalLayout = QVBoxLayout()
      self.topRightVerticalLayout.setObjectName("topRightVerticalLayout")

      self.ignoreCase = QCheckBox("Ignore case", self)
      self.ignoreCase.setObjectName("ignoreCase")
      self.ignoreCase.setToolTip("Case Insensitive Search.")
      self.ignoreCase.toggled.connect(self.saveDialogState)
      self.topLeftVerticalLayout.addWidget(self.ignoreCase)
      self.useRegex = QCheckBox("Use Regular Expressions", self)
      self.useRegex.setObjectName("useRegex")
      self.useRegex.setToolTip("Use Regular Expressions to Search.")
      self.useRegex.toggled.connect(self.saveDialogState)
      self.topLeftVerticalLayout.addWidget(self.useRegex)
      self.useTagFilter = QCheckBox("Filter Results by Tags", self)
      self.useTagFilter.setObjectName("useTagFilter")
      self.useTagFilter.setToolTip("Select tags in the tag filter box to narrow the search by only looking at shots with the selected tags.")
      self.useTagFilter.stateChanged.connect(self.saveDialogState)
      self.useTagFilter.toggled.connect(self.findMatches)
      self.topLeftVerticalLayout.addWidget(self.useTagFilter)

      self.radioGroupBox = QGroupBox("Search Scope")

      self.searchCurrent = QRadioButton("Current Sequence")
      self.searchCurrent.clicked.connect(self.saveDialogState)
      self.searchCurrent.setToolTip("Only search the currently active Sequence.")
      self.searchCurrent.setChecked(True)
      self.searchAllOpen = QRadioButton("All Open Sequences")
      self.searchAllOpen.setToolTip("Search All Open Sequences.\nThis will search shots in any sequences open in a Viewer.")
      self.searchAllOpen.clicked.connect(self.saveDialogState)
      self.searchAllInProject = QRadioButton("All Sequences in Open Projects")
      self.searchAllInProject.setToolTip("Search All Sequences in all open projects whether they are open in a Viewer or not.\
                                         \nIf matches are found in an unopened sequence it will be opened to display the results.")
      self.searchAllInProject.clicked.connect(self.saveDialogState)

      self.radioLayout = QVBoxLayout()
      self.radioLayout.setSpacing(-1)
      self.radioLayout.addWidget(self.searchCurrent)
      self.radioLayout.addWidget(self.searchAllOpen)
      self.radioLayout.addWidget(self.searchAllInProject)
      self.radioGroupBox.setLayout(self.radioLayout)

      self.topLeftVerticalLayout.addWidget(self.radioGroupBox)
      topLeftSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
      self.topLeftVerticalLayout.addItem(topLeftSpacer)

      self.middleHorizontalLayout = QHBoxLayout()
      self.middleHorizontalLayout.addLayout(self.topLeftVerticalLayout)
      groupSpacer = QSpacerItem(100, 20, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
      self.middleHorizontalLayout.addItem(groupSpacer)

      self.splitter = QSplitter(self)
      self.tagbox = TagSplitterWidget(self, self.splitter)
      self.tagbox.setObjectName("tagfilterbox")
      self.topRightVerticalLayout.addWidget(self.tagbox)
      self.middleHorizontalLayout.addLayout(self.topRightVerticalLayout)

      self.verticalLayout.addLayout(self.middleHorizontalLayout)

      self.dividerline = QFrame(self)
      self.dividerline.setFrameShape(QFrame.HLine)
      self.dividerline.setFrameShadow(QFrame.Plain)
      self.dividerline.setObjectName("dividerline")
      self.dividerline.setStyleSheet("QFrame {color: black}")


      self.horizontalOptionsLayout.addLayout(self.verticalLayout)
      self.gridLayout.addLayout(self.horizontalOptionsLayout, 1, 0, 1, 1)
      self.horizontalLayout = QHBoxLayout()
      self.horizontalLayout.setObjectName("horizontalLayout")
      spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
      self.horizontalLayout.addItem(spacerItem1)
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

      self.horizontalLayout.addWidget(self.previousButton)
      self.horizontalLayout.addWidget(self.nextButton)
      self.gridLayout.addWidget(self.dividerline, 2, 0, 1, 1)
      self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)

      self.horizontalStatus = QHBoxLayout()
      self.horizontalStatus.setObjectName("horizontalStatus")

      self.tableWidget = QTableWidget(self)
      self.tableWidget.setObjectName("tableWidget")
      self.tableWidget.setToolTip("Double click a result or press Return/Enter to jump to the shot in the Timeline.\
                                  \nSelect one or more clips and right click to:\
                                  \n   -Open in Nuke\
                                  \n   -Build Track\
                                  \n   -Create New Sequence from Selection")
      self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.tableWidget.setAlternatingRowColors(True)
      self.tableWidget.setSortingEnabled(True)
      self.tableWidget.doubleClicked.connect(self.goToResult)
      #self.tableWidget.itemSelectionChanged.connect(self.resultSelectionChanged)
      self.tableWidget.clicked.connect(self.resultSelectionChanged)
      self.tableWidget.verticalHeader().hide()
      self.tableWidget.horizontalHeader().sectionClicked.connect(self.sortResultColumn)
      self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
      self.tableWidget.connect(self.tableWidget, SIGNAL("customContextMenuRequested(QPoint)"), self.resultsListContextMenu)
      self.tableHeader = self.tableWidget.horizontalHeader()

      keyPressRedirect = FindResultsKeyPressRedirect(self)
      self.tableWidget.installEventFilter(keyPressRedirect)

      self.horizontalTableLayout = QHBoxLayout()
      self.horizontalTableLayout.setObjectName("horizontalTableLayout")
      self.horizontalTableLayout.addWidget(self.tableWidget)

      self.statusbar = QLabel()
      self.statusbar.setText("Ready")

      self.horizontalStatus.addWidget(self.statusbar)

      self.gridLayout.addLayout(self.horizontalStatus, 4, 0, 1, 1)
      self.gridLayout.addLayout(self.horizontalTableLayout, 5, 0, 1, 1)

      self.setWindowTitle("Find")
      self.searchTextField.setFocus()

      self.currentMatchNumber = 0
      self.matchList = []

      self.retranslateUI()
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

    def retranslateUI(self):
      '''Populate the UI from saved settings.
         Must be done outside of the init to set focus correctly.
      '''
      settings = hiero.core.ApplicationSettings()
      self.kLastFindDialogText = "FindDialog/lastFindDialogText"
      self.kIgnoreCase = "FindDialog/ignoreCase"
      self.kUseRegex = "FindDialog/useRegex"
      self.kSearchParams = "FindDialog/searchParams"
      self.kSearchScope = "FindDialog/searchScope"
      self.kUseTagFilter = "FindDialog/tagFilter"

      lastSearch = settings.value(self.kLastFindDialogText, "").decode("utf-8")
      if lastSearch:
        self.searchTextList = ast.literal_eval(lastSearch)
        self.searchTextField.setText(self.searchTextList[-1])

      # Check boxes that were checked on last use
      ignoreCase = settings.value(self.kIgnoreCase, "")
      useRegex = settings.value(self.kUseRegex, "")
      searchParams = settings.value(self.kSearchParams, "")
      searchScope = settings.value(self.kSearchScope, "")
      useTagFilter = settings.value(self.kUseTagFilter, "")

      if ignoreCase:
        self.ignoreCase.setChecked(eval(ignoreCase.title()))
      if useRegex:
        self.useRegex.setChecked(eval(useRegex.title()))
      if useTagFilter:
        self.useTagFilter.setChecked(eval(useTagFilter.title()))

      if searchScope == "1":
        self.searchCurrent.setChecked(True)
      elif searchScope == "2":
        self.searchAllOpen.setChecked(True)
      elif searchScope == "3":
        self.searchAllInProject.setChecked(True)

      if searchParams:
        self.searchOptionsComboBox.setCurrentIndex(int(searchParams))
      else:
        self.searchOptionsComboBox.setCurrentIndex(0)

      self.loadAutocompleter()
      self.searchTextField.setFocus()

    def closeEvent(self, event):
      '''Save the current layout state when widget is closed.
      '''
      self.saveDialogState()
      event.accept()

    def resultsListContextMenu(self):
      hieroState = HieroState()
      # Create a menu
      openInNuke = OpenInNukeAction(self, hieroState)
      buildFromTags = BuildTrackFromExportTag(self)
      buildFromStructure = BuildTrackCustom(self)
      newSequence = CreateNewSequence(self)
      menu = QMenu("Menu", self)
      menu.addAction(openInNuke, title="Open in Nuke...")
      submenu = menu.addMenu("Build Track")
      if not len(self.tableWidget.selectedIndexes()):
        submenu.setEnabled(False)

      submenu.addAction(buildFromStructure, title="From Export Structure")
      submenu.addAction(buildFromTags, title="From Export Tag")
      menu.addAction(newSequence, title="New Sequence from Selection")
      # Show the context menu.
      menu.exec_(QCursor.pos())

    def loadAutocompleter(self):
      '''Save some recent searches like Google
      '''
      searchmodel = QStandardItemModel()
      for i, word in enumerate(set(self.searchTextList)):
        item = QStandardItem(word)
        searchmodel.setItem(i, 0, item)

      self.searchTextField.setModel(searchmodel)
      self.searchTextField.setModelColumn(0)

    def saveDialogState(self):
      '''Save the current state of the widget so it
         can be reopened where it was left.
      '''
      self.kLastFindDialogText = "FindDialog/lastFindDialogText"
      self.kIgnoreCase = "FindDialog/ignoreCase"
      self.kUseRegex = "FindDialog/useRegex"
      self.kSearchParams = "FindDialog/searchParams"
      self.kSearchScope = "FindDialog/searchScope"
      self.kUseTagFilter = "FindDialog/tagFilter"

      if self.searchCurrent.isChecked():
        searchScope = 1
      elif self.searchAllOpen.isChecked():
        searchScope = 2
      elif self.searchAllInProject.isChecked():
        searchScope = 3
      else:
        searchScope = 1

      settings = hiero.core.ApplicationSettings()
      settings.setValue(self.kIgnoreCase, bool(self.ignoreCase.checkState()))
      settings.setValue(self.kUseRegex, bool(self.useRegex.checkState()))
      settings.setValue(self.kUseTagFilter, bool(self.useTagFilter.checkState()))
      settings.setValue(self.kSearchParams, self.searchOptionsComboBox.currentIndex())
      settings.setValue(self.kSearchScope, searchScope)

    def updateStatusBar(self, message):
      '''Update the widget status bar with @message
      '''
      #self.statusbar.showMessage(message)
      self.statusbar.setText(message)

    def findMatches(self):
      '''Find track items based on the given search string.
         Options: search by regular expressions, case-insensitive search,
         filter search results by tags.
      '''
      # TODO: Exact matches with quotes and Boolean search (Google style)
      # example: "colorspace : Gamma1.8" and "Resolution : 1920x1080"
      if not self.useTagFilter.isChecked() and isinstance(self.sender(), QCheckBox):
        if self.sender().objectName() != "useTagFilter":
          return
      self.updateStatusBar("Searching...")
      self.matchList = []
      self.currentMatchNumber = 0

      if self.searchCurrent.isChecked():
        trackItemList = []
        cv = hiero.ui.currentViewer()
        player = cv.player()
        sequence = player.sequence()
        if isinstance(sequence, hiero.core.Sequence):
          trackItemList = self.trackItems(sequence)

      if self.searchAllOpen.isChecked():
        trackItemList = self.allTrackItems(onlyOpen=True)
      if self.searchAllInProject.isChecked():
        trackItemList = self.allTrackItems()

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
        if self.useTagFilter.isChecked():
          self.matchList = self.tagbox.filterSelection(self.matchList)
          if not self.matchList:
            for row in sorted(range(self.tableWidget.rowCount()+1), reverse=True):
              self.tableWidget.removeRow(row)
            for column in sorted(range(self.tableWidget.columnCount()+1), reverse=True):
              self.tableWidget.removeColumn(column)
            self.updateStatusBar("No matches found")
            self.searchTextField.setFocus()
            return

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

# Tag filter widget to optionally search by tag combination presets
class TagSplitterWidget(QWidget):
  def __init__(self, mainLayout, parent):
    super(TagSplitterWidget, self).__init__(parent)

    self.mainLayout = mainLayout

    self.tagBoxVertical = QVBoxLayout(self)
    self.tagBoxVertical.setSizeConstraint(QLayout.SetDefaultConstraint)
    self.tagBoxVertical.setContentsMargins(0, 0, 0, 0)
    self.tagBoxVertical.setObjectName("tagBoxVertical")

    self.tagScrollArea = QScrollArea(self)
    self.tagScrollArea.setEnabled(True)
    sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.tagScrollArea.sizePolicy().hasHeightForWidth())
    self.tagScrollArea.setSizePolicy(sizePolicy)
    self.tagScrollArea.setMinimumSize(QSize(150, 40))
    self.tagScrollArea.setAutoFillBackground(True)
    self.tagScrollArea.setWidgetResizable(True)
    self.tagScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.tagScrollArea.setObjectName("tagScrollArea")

    self.tagListBox = QFrame()
    self.tagListBox.setGeometry(QRect(0, 0, 150, 200))
    sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.tagListBox.sizePolicy().hasHeightForWidth())
    self.tagListBox.setSizePolicy(sizePolicy)
    self.tagListBox.setMinimumSize(QSize(150, 200))
    # The background color doesn't get set to the color we want by default so we set it here
    self.tagListBox.setBackgroundRole(QPalette.Base)
    self.tagListBox.setAcceptDrops(True)
    self.tagListBox.setObjectName("tagListBox")

    self.verticalLayoutWidget = QWidget(self.tagListBox)
    self.verticalLayoutWidget.setGeometry(QRect(-1, -1, 150, 200))
    self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

    self.tagBoxVertical.addWidget(self.tagScrollArea)

    ########## Horizontal Layout for tag box filter and presets ##########
    self.tagButtonHorizontal = QHBoxLayout()
    self.tagButtonHorizontal.setObjectName("tagButtonHorizontal")

    self.tagPresetComboBox = QComboBox(self.mainLayout)
    self.tagPresetComboBox.setObjectName("tagPresetComboBox")
    self.tagPresetComboBox.setParent(self.tagListBox)
    self.tagPresetComboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
    self.tagPresetComboBox.setToolTip("Choose a Tag Combination Preset or Save the Currently Selected Combination.\
                                      \nTo Delete a Preset select it and then right click and choose Delete.")
    self.tagPresetComboBox.addItem("Save Preset...")
    self.tagPresetComboBox.addItem("None")
    self.italicFont = QFont(self.tagPresetComboBox.font())
    self.italicFont.setStyle(QFont.Style.StyleItalic)
    self.tagPresetComboBox.setItemData(1, self.italicFont, Qt.FontRole)
    self.tagPresetComboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
    self.tagPresetComboBox.currentIndexChanged.connect(self.tagPresetChanged)
    self.tagPresetComboBox.activated.connect(self.tagPresetChanged)
    self.tagPresetComboBox.setMinimumHeight(22)

    self.tagPresetComboBox.setContextMenuPolicy(Qt.CustomContextMenu)
    self.tagPresetComboBox.connect(self.tagPresetComboBox, SIGNAL("customContextMenuRequested(QPoint)"), self.tagPresetContextMenu)

    self.tagFilter = QCheckBox("Filter Excluded", self.mainLayout)
    self.tagFilter.setToolTip("Check this to only show shots with tags marked [+]\
                               \nand exclude those with tags marked [-].\
                               \nIf unchecked all shots with tags marked [+] will be displayed\
                               \neven if they also contain tags marked [-].")
    self.tagFilter.setChecked(True)
    #self.tagFilter.clicked.connect(self.filterSelection)
    self.tagFilter.clicked.connect(self.mainLayout.findMatches)
    self.tagFilter.setObjectName("tagFilter")

    self.tagBoxVertical.addLayout(self.tagButtonHorizontal)
    self.emptyFrame = QFrame()
    self.emptyFrame.setObjectName("emptyFrame")
    self.emptyFrame.setMaximumHeight(2)
    self.emptyFrame.setMinimumHeight(2)
    self.tagBoxVertical.addWidget(self.emptyFrame)

    self.tagScrollArea.setWidget(self.tagListBox)

    self.tagVBoxLayout = QVBoxLayout(self.verticalLayoutWidget)

    self.tagVBoxLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
    self.tagVBoxLayout.setObjectName("tagVBoxLayout")

    self.populateFromTags()

    # We have to put the Checkbox here because otherwise it won't appear.
    # This is only an issue if we have a class. If we put this code in the
    # main widget without instantiating it from a class then it's fine to
    # put it above after we create the objects

    self.tagButtonHorizontal.addWidget(self.tagPresetComboBox)
    self.tagButtonHorizontal.addWidget(self.tagFilter)
    spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
    self.tagButtonHorizontal.addItem(spacerItem)

    self.loadTagPresets()

  def tagPresetContextMenu(self):
    '''Context Menu for the Tag Combination Preset box
    '''
    sender = self.sender()
    # Create a menu
    deletePreset = self.DeleteTagPreset(sender)
    menu = QMenu("Menu", self)
    menu.addAction(deletePreset, title="Delete")

    # Show the context menu.
    menu.exec_(QCursor.pos())

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

  def getUsedTagNames(self):
    '''Search the project for all track item tags.
    '''
    # Only track item tags are searched for. Tags
    # on bin items, sequences, or tracks are ignored
    tagsUsed = {}
    projectList = hiero.core.projects()

    for project in projectList:
      bin = project.clipsBin()
      clips, sequences = self.findAllItems(bin.items(), [], [])
      for sequence in sequences:
        for track in sequence.activeItem():
          for ti in track:
            if ti.tags():
              tagsUsed[ti] = []
              for tag in ti.tags():
                tagsUsed[ti].append(tag)

    return tagsUsed

  def filterSelection(self, selection):
    '''Filter the selection based on checked and partially checked tags
    '''
    checkedTags = []
    ignoredTags = []
    excludedTags = []
    tagnames = {}

    filteredTrackItems = []
    ignoredTrackItems = []

    if not self.mainLayout.useTagFilter.isChecked():
      return selection

    usedTags = self.getUsedTagNames()
    anyChecked = False

    for box in self.tagListBox.findChildren(QCheckBox):
      # We reverse the use of Checked and PartiallyChecked because it's annoying that the first click
      # of a tristate checkbox gives you the PartiallyChecked state.
      if box.checkState() == Qt.PartiallyChecked: # We really mean Fully Checked
        checkedTags.append(box.text())
        anyChecked = True

      if box.checkState() == Qt.Checked: # We really mean Partially Checked
        ignoredTags.append(box.text())
        anyChecked = True

      if box.checkState() == Qt.Unchecked:
        excludedTags.append(box.text())

    if anyChecked:
      if self.tagFilter.checkState() == Qt.Checked:
        if checkedTags:
          for trackItem in usedTags:
            checkedMatch = False
            ignoredMatch = False
            currentTagList = [tag.name() for tag in usedTags[trackItem]]

            # Look at the list of trackitems and their tags
            # If a tag is checked we have a match
            if set(checkedTags).issubset(set(currentTagList)):
              checkedMatch = True

            # We have a match so make sure the tag isn't checked [-] to be ignored
            if checkedMatch:
              for ignored in ignoredTags:
                if ignored in currentTagList:
                  ignoredMatch = True
                  break

            if checkedMatch and not ignoredMatch:
              if trackItem in selection:
                if not trackItem in filteredTrackItems:
                  filteredTrackItems.append(trackItem)

      if self.tagFilter.checkState() == Qt.Unchecked:
        for trackItem in usedTags:
          currentTagList = [tag.name() for tag in usedTags[trackItem]]

          for checked in checkedTags:
            if checked in currentTagList:
              if trackItem in selection:
                if not trackItem in filteredTrackItems:
                  filteredTrackItems.append(trackItem)

    else:
      return []

    return filteredTrackItems

  def populateFromTags(self):

    for index in range(self.tagVBoxLayout.count()):
      self.tagVBoxLayout.takeAt(index)

    for tag in self.tagListBox.findChildren(QCheckBox):
      tag.deleteLater()

    tagnames = {}
    usedTags = self.getUsedTagNames()
    for trackItem in usedTags:
      for tag in usedTags[trackItem]:

        if tag.name() not in tagnames:
          tagnames[tag.name()] = [trackItem]
        else:
          tagnames[tag.name()].append(trackItem)

    tagCount = []
    for tname in sorted(tagnames, reverse=True):
      transcodematch = re.search("(Transcode)", tname)
      nukematch = re.search("(Nuke Project)", tname)
      if not nukematch and not transcodematch:
        tagCount.append(tname)

        tag = [t for t in tagnames[tname][0].tags() if t.name() == tname][0]
        iconPath = QIcon(tag.icon())

        tagBox = QCheckBox(tname)
        tagBox.setStyleSheet("::indicator {width:12px; height:12px;} ::indicator:indeterminate {image: url(icons:Checkbox_plus.png);} ::indicator:checked { image: url(icons:Checkbox_minus.png); }")
        tagBox.setTristate(True)
        tagBox.setIcon(iconPath)
        #tagBox.stateChanged.connect(self.filterSelection)
        tagBox.stateChanged.connect(self.mainLayout.findMatches)
        tagBox.setParent(self.tagListBox)
        self.tagVBoxLayout.insertWidget(0, tagBox)


    self.tagListBox.updateGeometry()
    self.tagListBox.adjustSize()

    count = self.tagVBoxLayout.count()
    newY = (18 * len(tagCount)) + 10 # Height of each checkbox * number of boxes plus total top/bottom padding
    self.tagListBox.setMinimumSize(QSize(self.tagListBox.x(), newY))

  def loadTagPresets(self):
    '''Load tag presets from the user's uistate.ini and populate
       the tag preset combo box.
    '''
    settings = hiero.core.ApplicationSettings()

    self.kTagCombinationPreset = "tagCombinationPresets"
    presets = settings.value(self.kTagCombinationPreset, "")
    if presets:
      presets = ast.literal_eval(presets)
      for presetName in sorted(presets, key=lambda s: s.lower()):
        self.tagPresetComboBox.addItem(presetName)
        for index in range(self.tagPresetComboBox.count()):
          if self.tagPresetComboBox.itemText(index) == presetName:
            self.tagPresetComboBox.setItemData(index, presets[presetName])

  def deleteTagPreset(self, index):
    '''Delete a tag combination preset
    '''
    settings = hiero.core.ApplicationSettings()
    self.kTagCombinationPreset = "tagCombinationPresets"

    savedPresets = settings.value(self.kTagCombinationPreset, "")
    if savedPresets:
      savedPresets = ast.literal_eval(savedPresets)
    else:
      savedPresets = {}

    currentPreset = self.tagPresetComboBox.itemText(index)
    if currentPreset == "Save Preset..." or currentPreset == "None":
      pass
    else:
      del savedPresets[currentPreset]
      self.tagPresetComboBox.removeItem(index)
      settings.setValue(self.kTagCombinationPreset, savedPresets)

  def saveTagPreset(self):
    '''Save a tag combination preset.
    '''
    currentState = self.currentTagSelectionState()
    settings = hiero.core.ApplicationSettings()

    self.kTagCombinationPreset = "tagCombinationPresets"

    savedPresets = settings.value(self.kTagCombinationPreset, "")
    if savedPresets:
      savedPresets = ast.literal_eval(savedPresets)
    else:
      savedPresets = {}

    dialog = PresetDialog()
    if dialog.exec_():
      text = dialog.lineEdit.text()
      if text:
        newPreset = {text: currentState}

        savedPresets.update(newPreset)
        settings.setValue(self.kTagCombinationPreset, savedPresets)

        loadedPresets = list(savedPresets.keys())
        sortedPresets = list(loadedPresets)
        sortedPresets.append(text)
        sortedIndex = sorted(sortedPresets, key=lambda s: s.lower()).index(text)

        # Add 2 to the sort index because we skip over "Save Preset..." and "None"
        self.tagPresetComboBox.insertItem(sortedIndex+2, text)

        for index in range(self.tagPresetComboBox.count()):
          if self.tagPresetComboBox.itemText(index) == text:
            self.tagPresetComboBox.setCurrentIndex(index)
            self.tagPresetComboBox.setItemData(index, currentState)
      else:
        dialog.close()

  def tagPresetChanged(self):
    '''Change the tag filter preset combo box.
    '''
    currentTagPreset = self.tagPresetComboBox.currentText()

    if currentTagPreset == "None":
      self.clearTagSelection()

    if currentTagPreset == "Save Preset...":
      currentState = self.currentTagSelectionState()
      self.saveTagPreset()

    else:
      for index in range(self.tagPresetComboBox.count()):
        if self.tagPresetComboBox.itemText(index) == currentTagPreset:
          itemdata = self.tagPresetComboBox.itemData(index)

      if itemdata:
        checked = itemdata['checked']
        ignored = itemdata['ignored']
        for box in self.tagListBox.findChildren(QCheckBox):
          if box.text() in checked:
            box.setCheckState(Qt.PartiallyChecked)
          elif box.text() in ignored:
            box.setCheckState(Qt.Checked)
          else:
            box.setCheckState(Qt.Unchecked)

  def tagSelectionStateChanged(self):

    currentState = self.currentTagSelectionState()
    currentPreset = self.tagPresetComboBox.currentIndex()
    presetData = self.tagPresetComboBox.itemData(currentPreset)
    if presetData != currentState:
      self.tagPresetComboBox.setCurrentIndex(1)

  def currentTagSelectionState(self):
    checkedTags = []
    ignoredTags = []

    for box in self.tagListBox.findChildren(QCheckBox):
      if box.checkState() == Qt.PartiallyChecked: # We really mean Fully Checked
        checkedTags.append(box.text())

      if box.checkState() == Qt.Checked: # We really mean Partially Checked
        ignoredTags.append(box.text())

    return {'checked': checkedTags, 'ignored': ignoredTags}

  def clearTagSelection(self):
    currentTagBox = self.sender().parent()

    for box in self.tagListBox.findChildren(QCheckBox):
      if box.checkState() == Qt.PartiallyChecked: # We really mean Fully Checked
        box.setCheckState(Qt.Unchecked)
      if box.checkState() == Qt.Checked: # We really mean Partially Checked
        box.setCheckState(Qt.Unchecked)

  class DeleteTagPreset(QAction):
    def __init__(self, sender, title="Delete"):
      QAction.__init__(self, title, None)

      self.sender = sender
      self.triggered.connect(self.deletePreset)

    def deletePreset(self):
      current = self.sender.currentIndex()
      self.sender.parent().deleteTagPreset(current)

class PresetDialog(QDialog):
  def __init__(self, parent=None):
    super(PresetDialog, self).__init__(parent)

    self.setWindowTitle("Tag Preset")
    self.setSizeGripEnabled(True)

    layout = QFormLayout()
    self.lineEdit = QLineEdit()

    layout.addRow("Preset Name:", self.lineEdit)

    # Add the standard ok/cancel buttons, default to ok.
    self._buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    self._buttonbox.button(QDialogButtonBox.Ok).setText("Save")
    self._buttonbox.accepted.connect(self.accept)
    self._buttonbox.rejected.connect(self.reject)
    layout.addWidget(self._buttonbox)

    self.setLayout(layout)
    self.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )

class BuildTrackCustom(BuildExternalMediaTrackAction):
  def __init__(self, selection):
    super(BuildExternalMediaTrackAction, self).__init__("From Export Structure")
    self.selection = selection
    if not len(self.selection.tableWidget.selectedIndexes()):
      self.setEnabled(False)

  def configure(self, project, selection):
    dialog = self.BuildExternalMediaTrack(selection)
    if dialog.exec_():
      self._trackName = dialog.trackName()

      # Determine the exported file paths
      self._exportTemplate = dialog._exportTemplate
      structureElement = dialog._exportTemplateViewer.selection()
      self._processorPreset = dialog._preset
      if structureElement is not None:
        # Grab the elements relative path
        self._elementPath = structureElement.path()
        self._elementPreset = structureElement.preset()

        resolver = hiero.core.ResolveTable()
        resolver.merge(dialog._resolver)
        resolver.merge(self._elementPreset.createResolver())
        self._resolver = resolver
        self._project = project

        return True

    return False

  def doit(self):
    selection = {}

    for trackItem in self.selection.selectedResults():
      sequence = trackItem.parentSequence()
      project = sequence.project()
      try:
        selection[project]
      except:
        selection[project] = {}
        selection[project]['sequences'] = {}

      if not sequence in selection[project]['sequences']:
        selection[project]['sequences'][sequence] = []

      if not trackItem in selection[project]['sequences'][sequence]:
        selection[project]['sequences'][sequence].append(trackItem)

    for key,value in selection.iteritems():
      for sequence, items in selection[key]['sequences'].iteritems():
        project = sequence.project()

        if not self.configure(project, items):
          return

        self._buildTrack(items, sequence, project)

        if self._errors:
          msgBox = QMessageBox(hiero.ui.mainWindow())
          msgBox.setWindowTitle("Build Media Track")
          msgBox.setText("There were problems building the track.")
          msgBox.setDetailedText( '\n'.join(self._errors) )
          msgBox.exec_()
          self._errors = []

  def _buildTrack(self, selection, sequence, project):
    # Begin undo group
    project.beginUndo("Build external media track")

    try:
      #Loop waiting for either a collision handling option or a blank track
      readyToBuild = 0
      trackName = self.trackName()
      while readyToBuild == 0 :
        #Get the destination track
        track, isNewTrack = BuildTrack.FindOrCreateTrack(sequence, trackName)

        if not isNewTrack :

          #Look for collisions
          newSelection, returnedTrack = self.checkTrackItemCollisions(selection, track)

          #Check if the user cancelled
          if returnedTrack == None:
            return False

          #If user choose to deal with collisions then we do build
          if newSelection != None :
            selection = newSelection
            track = returnedTrack
            readyToBuild = 1

          #Else user wants to make a new track
          else :
            trackName = returnedTrack
            readyToBuild = 0

        else :
          readyToBuild = 1

      #If there's nothing to do, stop doing things.
      if len(selection) == 0 :
        project.endUndo()
        return True

      # TODO: Allow the user to choose a destination in the bin
      bin = BuildTrack.FindOrCreateBin(project, track.name())

      # Collision handling: store collided items in sets, to be removed at the end (preventing from removing the same item twice)
      collidedTransitions = set()

      for originalTrackItem in selection:
        # TrackItems
        if isinstance(originalTrackItem, hiero.core.TrackItem):
          if isinstance(originalTrackItem.source(), hiero.core.Clip):

            files = self.getExternalFilePaths(originalTrackItem)
            if self._useMaxVersions:
              files = BuildTrackActionBase.findFiles( files )
            start, duration, handles, offset = self.getExpectedRange( originalTrackItem )
            self.buildShotFromFiles(files, originalTrackItem.name(), sequence, track, bin, originalTrackItem, start, duration, handles, offset)
        elif isinstance(originalTrackItem, hiero.core.Transition):
          # Check for colliding transitions
          BuildTrack.CheckForTransitionCollisions(originalTrackItem, track, isNewTrack, collidedTransitions)
          track.addTransition(originalTrackItem.clone())

      # Remove collided transitions
      for item in collidedTransitions:
        track.removeTransition(item)

      return True
    # Ensure the undo gets closed even if there's an exception
    finally:
      # End undo group (this does the actual editing, hence BEFORE sequence.editFinished())
      project.endUndo()
      # Send signal to update viewers (TimelineEditor, SpreadsheetView, Viewer)
      sequence.editFinished()


  class BuildExternalMediaTrack(QDialog):
    def __init__(self,  selection,  parent=None):
      super(BuildTrackCustom.BuildExternalMediaTrack, self).__init__(parent)
      self.setWindowTitle("Build Track From Export Structure")
      self.setSizeGripEnabled(True)

      self._exportTemplate = None
      self._selection = selection
      layout = QVBoxLayout()
      formLayout = QFormLayout()

      self._tracknameField = QLineEdit(BuildTrack.ProjectTrackNameDefault(selection))
      self._tracknameField.setToolTip("Name of new track")
      namepatternrx = QRegExp("[a-z A-Z 0-9]*")
      nameval = QRegExpValidator(namepatternrx, self)
      self._tracknameField.setValidator(nameval)
      formLayout.addRow("Track Name:", self._tracknameField)

      project = None
      if self._selection:
        project = self.itemProject(self._selection[0])
      presetNames = [ preset.name() for preset in hiero.core.taskRegistry.localPresets() + hiero.core.taskRegistry.projectPresets(project) ]
      presetCombo = QComboBox()
      for name in sorted(presetNames):
        presetCombo.addItem(name)
      presetCombo.currentIndexChanged.connect(self.presetChanged)
      self._presetCombo = presetCombo
      formLayout.addRow("Export Preset:", presetCombo)

      layout.addLayout(formLayout)

      self._exportTemplate = hiero.core.ExportStructure2()
      self._exportTemplateViewer = hiero.ui.ExportStructureViewer(self._exportTemplate, hiero.ui.ExportStructureViewer.ReadOnly)

      layout.addWidget(self._exportTemplateViewer)

      # Add the standard ok/cancel buttons, default to ok.
      self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
      self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("Build")
      self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
      self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Builds the selected entry in the export template. Only enabled if an entry is selected in the view above.")
      self._buttonbox.accepted.connect(self.acceptTest)
      self._buttonbox.rejected.connect(self.reject)
      layout.addWidget(self._buttonbox)

      if presetNames:
        self.presetChanged(presetNames[0])

      self.setLayout(layout)

    def itemProject(self, item):
      if hasattr(item, 'project'):
        return item.project()
      elif hasattr(item, 'parent'):
        return self.itemProject(item.parent())
      else:
        return None

    def acceptTest(self):

      validSelection = self._exportTemplateViewer.selection() is not None
      if validSelection:
        self.accept()
      else:
        QMessageBox.warning(self, "Build External Media Track", "Please select an entry in the export template and press Build again.", QMessageBox.Ok)

    def presetChanged(self, index):

      project = None
      if self._selection:
        project = self.itemProject(self._selection[0])
      presetsDict = dict([ (preset.name(), preset) for preset in hiero.core.taskRegistry.localPresets() + hiero.core.taskRegistry.projectPresets(project) ])

      value = self._presetCombo.currentText()
      if value in presetsDict:
        self._preset = presetsDict[value]
        self._exportTemplate.restore(self._preset._properties["exportTemplate"])
        if self._preset._properties["exportRoot"] != "None":
          self._exportTemplate.setExportRootPath(self._preset._properties["exportRoot"])
        self._exportTemplateViewer.setExportStructure(self._exportTemplate)
        self._resolver = self._preset.createResolver()
        self._resolver.addEntriesToExportStructureViewer(self._exportTemplateViewer)

        # force the first item to be selected, if there is only one
        self._exportTemplateViewer.selectFileIfOnlyOne()

    def trackName(self):
      return str(self._tracknameField.text())

class BuildTrackFromExportTag(BuildTrackFromExportTagAction):
  def __init__(self, selection):
    super(BuildTrackFromExportTagAction, self).__init__("From Export Tag")
    self.selection = selection

    if not len(self.selection.tableWidget.selectedIndexes()):
      self.setEnabled(False)

  def doit(self):
    selection = {}

    for trackItem in self.selection.selectedResults():
      sequence = trackItem.parentSequence()
      project = sequence.project()
      try:
        selection[project]
      except:
        selection[project] = {}
        selection[project]['sequences'] = {}

      if not sequence in selection[project]['sequences']:
        selection[project]['sequences'][sequence] = []

      if not trackItem in selection[project]['sequences'][sequence]:
        selection[project]['sequences'][sequence].append(trackItem)


    for key,value in selection.iteritems():
      for sequence, items in selection[key]['sequences'].iteritems():
        project = sequence.project()

        if not self.configure(project, items):
          return

        self._buildTrack(items, sequence, project)

        if self._errors:
          msgBox = QMessageBox(hiero.ui.mainWindow())
          msgBox.setWindowTitle("Build Media Track")
          msgBox.setText("There were problems building the track.")
          msgBox.setDetailedText( '\n'.join(self._errors) )
          msgBox.exec_()
          self._errors = []

class OpenInNukeAction(OpenTrackItemsInNuke):
  def __init__(self, selection, hieroState, title="Open in Nuke..."):
    BuildTrackFromExportTagAction.__init__(self)
    self.setText(title)
    self.selection = selection

    trackItems = self.selection.selectedResults()

    if len(trackItems) > 1:
      self.setEnabled(False)

    # store the track name, currently hardcoded, for later
    self._trackName = BuildTrack.ProjectTrackNameDefault(trackItems)
    self._trackItems = trackItems
    self._hieroState = hieroState

    # check if we should be enabled
    enable = False
    for item in self._trackItems:
     tag = self.findTag(item)
     if tag:
       enable = True
       break

    # If taskRegistry is available, always enable because an export can be invoked to create the script
    self.setEnabled(enable or (hasattr(hiero.core, "taskRegistry") and (len(self._trackItems) > 0)))

class CreateNewSequence(QAction):
  def __init__(self, selection, title="New Sequence from Selection"):
    QAction.__init__(self, title, None)

    self.selection = selection
    self.triggered.connect(self.createNewSequence)

    if not len(self.selection.tableWidget.selectedIndexes()):
      self.setEnabled(False)

  def createNewSequence(self):
    '''Create a new sequence from the selected track items.
       The track item in/out and parent track will be retained
       unless you choose track items from different sequences
       with the same track names and the track items overlap.
    '''
    trackItemList = self.selection.selectedResults()

    if trackItemList:
      currentProject = trackItemList[0].parentTrack().project()
      if currentProject.isRestricted():
        project = hiero.core.newProject()
      else:
        project = currentProject

      bin = project.clipsBin()
      sequence = hiero.core.Sequence("TaggedShots")
      for item in trackItemList:
        itemrange = range(item.timelineIn(), item.timelineOut()+1)
        track, isNewTrack = self.selection.FindOrCreateTrack(sequence, item.parentTrack().name())
        for clip in track.items():
          cliprange = range(clip.timelineIn(), clip.timelineOut()+1)
          if list(set(cliprange) & set(itemrange)):
            # clips overlap so try to add the clip to the next track
            track, isNewTrack = self.selection.FindOrCreateTrack(sequence, item.parentTrack().name() + "_1")
        track.addTrackItem(item.clone())
      bin.addItem(hiero.core.BinItem(sequence))


# Create the widget and add to the Window menu
findWidget = FindAction.FindDialog()
wm = hiero.ui.windowManager()
wm.addWindow( findWidget )

# Create a submenu under Edit and populate it with Find Actions
#editMenuAction = hiero.ui.findMenuAction("hiero.menu.edit")
#editMenu = editMenuAction.menu()
#findMenu = QMenu("Find")
#editMenu.addMenu(findMenu)
#findDialog = FindAction()
#findMenu.addAction(findDialog)
#findMenu.addAction(findWidget.findNextAction)
#findMenu.addAction(findWidget.findPreviousAction)
