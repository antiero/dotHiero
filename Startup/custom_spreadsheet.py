# Adds custom columns to the Spreadsheet view
import hiero.core
import hiero.ui
from PySide import QtGui, QtCore

# Adds custom spreadsheet columns and right-click menu for setting the Shot Status, allowing status to be set on a selection of Shots
# gStatusTags is a global dictionary of key(status)-value(icon) pairs, which can be overridden with custom icons if required
# Python methods are added to hiero.core.TrackItem.status() and .getStatus() for setting and getting the Shot Status.

# Uncomment this if you don't want the Set Status right-click menu
kAddStatusMenu = True

class CustomSpreadsheetColumns(QtCore.QObject):
  """
    A class defining custom columns for Hiero's spreadsheet view. This has a similar, but
    slightly simplified, interface to the QAbstractItemModel and QItemDelegate classes.
  """
  global gStatusTags
  gColourSpaces = ['linear', 'sRGB', 'rec709', 'Cineon','Gamma1.8', 'Gamma2.2','Panalog', 'REDLog','ViperLog']
  currentView = hiero.ui.activeView()
  gCustomColumnList = [
    { 'name' : 'Tags', 'cellType' : 'readonly'},
    { 'name' : 'Colourspace',  'cellType' : 'dropdown'},
    { 'name' : 'Notes', 'cellType' : 'textedit' },
    { 'name' : 'FileType', 'cellType' : 'readonly' },
    { 'name' : 'Shot Status', 'cellType' : 'dropdown' },
    { 'name' : 'Thumbnail', 'cellType' : 'readonly' },
    { 'name' : 'MediaType', 'cellType' : 'readonly' },
    { 'name' : 'Width', 'cellType' : 'readonly' },
    { 'name' : 'Height', 'cellType' : 'readonly' },
    { 'name' : 'Pixel Aspect', 'cellType' : 'readonly' }
  ]

  def numColumns(self):
    """
      Return the number of custom columns in the spreadsheet view
    """
    return len( self.gCustomColumnList )

  def columnName(self, column):
    """
      Return the name of a custom column
    """
    return self.gCustomColumnList[column]['name']

  def getTagsString(self,item):
    """
      Convenience method for returning all the Notes in a Tag as a string
    """    
    tagNames = []
    tags = item.tags()
    for tag in tags:
      tagNames+=[tag.name()]
    tagNameString = ','.join(tagNames)
    return tagNameString

  def getNotes(self,item):
    """
      Convenience method for returning all the Notes in a Tag as a string
    """        
    notes = ''
    tags = item.tags()
    for tag in tags:
      note = tag.note()
      if len(note)>0:
        notes+=tag.note()+', '
    return notes[:-2]
    
  def getData(self, row, column, item):
    """
      Return the data in a cell
    """
    currentColumn = self.gCustomColumnList[column]
    if currentColumn['name'] == 'Tags':
      return self.getTagsString(item)

    if currentColumn['name'] == 'Colourspace':
      try:
        colTransform = item.sourceMediaColourTransform()
      except:
        colTransform = '--'
      return colTransform

    if currentColumn['name'] == 'Notes':
      try:
        note = self.getNotes(item)
      except:
        note = ''
      return note

    if currentColumn['name'] == 'FileType':
      fileType = '--'
      M = item.source().mediaSource().metadata()
      if M.hasKey('foundry.source.type'):
        fileType = M.value('foundry.source.type')
      elif M.hasKey('media.input.filereader'):
        fileType = M.value('media.input.filereader')
      return fileType

    if currentColumn['name'] == 'Shot Status':
      status = item.status()
      return str(status)

    if currentColumn['name'] == 'MediaType':
      M = item.mediaType()
      return str(M).split('MediaType')[-1].replace('.k','')

    if currentColumn['name'] == 'Thumbnail':
      return str(item.eventNumber())

    if currentColumn['name'] == 'Width':
      return str(item.source().format().width())

    if currentColumn['name'] == 'Height':
      return str(item.source().format().height())

    if currentColumn['name'] == 'Pixel Aspect':
      return str(item.source().format().pixelAspect())                                

    return ""

  def setData(self, row, column, item, data):
    """
      Set the data in a cell
    """
    currentColumn = self.gCustomColumnList[column]

    if currentColumn['name'] == 'Notes':
      if len(data)>0:
        tag = hiero.core.Tag('Note')
        tag.setIcon("icons:TagNote.png")
        tag.setNote(unicode(data))
        selection = self.currentView.selection()
        for trackItem in selection:
          trackItem.addTag(tag)

    if currentColumn['name'] == 'Shot Status':
      return item.status()

  def getTooltip(self, row, column, item):
    """
      Return the tooltip for a cell
    """
    currentColumn = self.gCustomColumnList[column]
    if currentColumn['name'] == 'Tags':
      return unicode([item.name() for item in item.tags()])

    if currentColumn['name'] == 'Notes':
      return str(self.getNotes(item))
    return ""

  def getFont(self, row, column, item):
    """
      Return the tooltip for a cell
    """
    return None

  def getBackground(self, row, column, item):
    """
      Return the background colour for a cell
    """
    if not item.source().mediaSource().isMediaPresent():
      return QtGui.QColor(80, 20, 20)
    return None

  def getForeground(self, row, column, item):
    """
      Return the text colour for a cell
    """
    #if column == 1:
    #  return QtGui.QColor(255, 64, 64)
    return None

  def getIcon(self, row, column, item):
    """
      Return the icon for a cell
    """
    currentColumn = self.gCustomColumnList[column]
    if currentColumn['name'] == 'Colourspace':
      return QtGui.QIcon("icons:LUT.png")
    if currentColumn['name'] == 'MediaType':
      mediaType = item.mediaType()
      if mediaType == hiero.core.TrackItem.kVideo:
        return QtGui.QIcon("icons:VideoOnly.png")
      elif mediaType == hiero.core.TrackItem.kAudio:
        return QtGui.QIcon("icons:AudioOnly.png")

    return None

  def getSizeHint(self, row, column, item):
    """
      Return the size hint for a cell
    """
    currentColumnName = self.gCustomColumnList[column]['name']
    if currentColumnName== 'Tags':
      return QtCore.QSize(120, 50)      

    if currentColumnName== 'Thumbnail':
      return QtCore.QSize(90, 50)      

    return None

  def paintCell(self, row, column, item, painter, option):
    """
      Paint a custom cell. Return True if the cell was painted, or False to continue
      with the default cell painting.
    """
    currentColumn = self.gCustomColumnList[column]
    if currentColumn['name'] == 'Tags':
      if option.state & QtGui.QStyle.State_Selected:
        painter.fillRect(option.rect, option.palette.highlight())
      iconSize = 20
      r = QtCore.QRect(option.rect.x(), option.rect.y()+(option.rect.height()-iconSize)/2, iconSize, iconSize)
      tags = item.tags()
      if len(tags) > 0:
        painter.save()
        painter.setClipRect(option.rect)
        for tag in item.tags():
          QtGui.QIcon(tag.icon()).paint(painter, r, QtCore.Qt.AlignLeft)
          r.translate(r.width()+2, 0)
        painter.restore()
        return True
    
    if currentColumn['name'] == 'Thumbnail':
      imageView = None
      pen = QtGui.QPen()
      r = QtCore.QRect(option.rect.x()+2, (option.rect.y()+(option.rect.height()-46)/2), 85, 46)
      if not item.source().mediaSource().isMediaPresent():
        imageView = QtGui.QImage("icons:Offline.png")
        pen.setColor(QtGui.QColor(QtCore.Qt.red))

      if item.mediaType() == hiero.core.TrackItem.MediaType.kAudio:
        imageView = QtGui.QImage("icons:AudioOnly.png")
        #pen.setColor(QtGui.QColor(QtCore.Qt.green))
        painter.fillRect(r, QtGui.QColor(45, 59,45))

      if option.state & QtGui.QStyle.State_Selected:
        painter.fillRect(option.rect, option.palette.highlight())

      
      tags = item.tags()
      painter.save()
      painter.setClipRect(option.rect)
      
      if not imageView:
        try:
          imageView = item.thumbnail(item.sourceIn())
          pen.setColor(QtGui.QColor(20,20,20))
        # If we're here, we probably have a TC error, no thumbnail, so get it from the source Clip...
        except:
          pen.setColor(QtGui.QColor(QtCore.Qt.red))
      
      if not imageView:
        try:
          imageView = item.source().thumbnail()
          pen.setColor(QtGui.QColor(QtCore.Qt.yellow))
        except:
          imageView  = QtGui.QImage("icons:Offline.png")
          pen.setColor(QtGui.QColor(QtCore.Qt.red))
          

      QtGui.QIcon(QtGui.QPixmap.fromImage(imageView)).paint(painter, r, QtCore.Qt.AlignCenter)
      painter.setPen(pen)
      painter.drawRoundedRect(r,1,1)
      painter.restore()
      return True      
      
    return False

  def createEditor(self, row, column, item, view):
    """
      Create an editing widget for a custom cell
    """
    self.currentView = view

    currentColumn = self.gCustomColumnList[column]
    if currentColumn['cellType'] == 'readonly':
      cle = QtGui.QLabel()
      cle.setEnabled(False)
      cle.setVisible(False)
      return cle

    if currentColumn['name']=='Colourspace':
      cb = QtGui.QComboBox()
      for colourspace in self.gColourSpaces:
        cb.addItem(colourspace)
      cb.currentIndexChanged.connect(self.colourspaceChanged)
      return cb

    if currentColumn['name']=='Shot Status':
      cb = QtGui.QComboBox()
      for key in gStatusTags.keys():
        cb.addItem(QtGui.QIcon(gStatusTags[key]), key)
      cb.currentIndexChanged.connect(self.statusChanged);
      return cb

    return None

  def setModelData(self, row, column, item, editor):
    return False


  def dropMimeData(self, row, column, item, data, items):
    """
      Handle a drag and drop operation
    """
    for thing in items:
      if isinstance(thing,hiero.core.Tag):
        item.addTag(thing)
    return None

  def colourspaceChanged(self,index):
    """
      This method is called when colourspace widget changes index.
    """
    index = self.sender().currentIndex()
    colourspace = self.gColourSpaces[index]
    selection = self.currentView.selection()
    items = [item for item in selection if (item.mediaType()==hiero.core.TrackItem.MediaType.kVideo)]
    for trackItem in items:
      trackItem.setSourceMediaColourTransform(colourspace)


  def statusChanged(self, arg):
    """
      This method is called when status widget changes index.
    """
    view = hiero.ui.activeView()
    selection = view.selection()
    status = self.sender().currentText()
    for trackItem in selection:
      trackItem.setStatus(status)


# Global Dictionary of Status Tags. 
# Note: This can be overwritten if you want to add a new status cellType or custom icon
# Override the gStatusTags dictionary by adding your own 'Status':'Icon.png' key-value pairs.
# Add new custom keys like so: gStatusTags['For Client'] = 'forClient.png'

gStatusTags = {'Approved':'icons:status/TagApproved.png',
  'Unapproved':'icons:status/TagUnapproved.png',
  'Ready To Start':'icons:status/TagReadyToStart.png',
  'Blocked':'icons:status/TagBlocked.png',
  'On Hold':'icons:status/TagOnHold.png',
  'In Progress':'icons:status/TagInProgress.png',
  'Awaiting Approval':'icons:status/TagAwaitingApproval.png',
  'Omitted':'icons:status/TagOmitted.png',
  'Final':'icons:status/TagFinal.png'}
  
def _status(self):
  """status -> Returns the Shot status. None if no Status is set."""

  status = None
  tags = self.tags()
  for tag in tags:
    if tag.metadata().hasKey('tag.status'):
      status = tag.metadata().value('tag.status')
  return status

def _setStatus(self, status):
  """setShotStatus(status) -> Method to set the Status of a Shot. 
  Adds a special kind of status Tag to a TrackItem
  Example: myTrackItem.setStatus('Final')

  @param status - a string, corresponding to the Status name
  """
  global gStatusTags

  # Get a valid Tag object from the Global list of statuses
  if not status in gStatusTags.keys():
    print 'Status requested was not a valid Status string.'
    return 

  # A shot should only have one status. Check if one exists and set accordingly 
  statusTag = None
  tags = self.tags()
  for tag in tags:
    if tag.metadata().hasKey('tag.status'):
      statusTag = tag
      break
  
  if not statusTag:
    statusTag = hiero.core.Tag('Status')
    statusTag.setIcon(gStatusTags[status])
    statusTag.metadata().setValue('tag.status', status) 
    self.addTag(statusTag)

  statusTag.setIcon(gStatusTags[status])
  statusTag.metadata().setValue('tag.status', status)
  
  self.sequence().editFinished()
  return

# Inject status getter and setter methods into hiero.core.TrackItem
hiero.core.TrackItem.setStatus = _setStatus
hiero.core.TrackItem.status = _status

# This is a convenience method for returning QtGui.QActions with a triggered method based on the title string
def titleStringTriggeredAction(title, method, icon = None):
  action = QtGui.QAction(title,None)
  action.setIcon(QtGui.QIcon(icon))
  
  # We do this magic, so that the title string from the action is used to set the status
  def methodWrapper():
    method(title)
  
  action.triggered.connect( methodWrapper )
  return action

# Menu which adds a Set Status Menu to Timeline and Spreadsheet Views
class SetStatusMenu(QtGui.QMenu):

  def __init__(self):
      QtGui.QMenu.__init__(self, "Set Status", None)

      global gStatusTags
      # ant: Could use hiero.core.defaultFrameRates() here but messes up with string matching because we seem to mix decimal points
      self.statuses = gStatusTags
      self._statusActions = self.createStatusMenuActions()      

      # Add the Actions to the Menu.
      for act in self.menuActions:
        self.addAction(act)
      
      hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
      hiero.core.events.registerInterest("kShowContextMenu/kSpreadsheet", self.eventHandler)      

  def createStatusMenuActions(self):
    self.menuActions = []
    for status in self.statuses:
      self.menuActions+=[titleStringTriggeredAction(status,self.setStatusFromMenuSelection, icon=gStatusTags[status])]

  def setStatusFromMenuSelection(self, menuSelectionStatus):
    selectedShots  = [item for item in self._selection if (isinstance(item,hiero.core.TrackItem))]
    selectedTracks  = [item for item in self._selection if (isinstance(item,(hiero.core.VideoTrack,hiero.core.AudioTrack)))]

    # If we have a Track Header Selection, no shots could be selected, so create shotSelection list
    if len(selectedTracks)>=1:
      for track in selectedTracks:
        selectedShots+=[item for item in track.items() if (isinstance(item,hiero.core.TrackItem))]

    # It's possible no shots exist on the Track, in which case nothing is required
    if len(selectedShots)==0:
      return

    currentProject = selectedShots[0].project()

    with currentProject.beginUndo("Set Status"):
      # Shots selected
      for shot in selectedShots:
        shot.setStatus(menuSelectionStatus)

  # This handles events from the Project Bin View
  def eventHandler(self,event):
    if not hasattr(event.sender, 'selection'):
      # Something has gone wrong, we should only be here if raised
      # by the Timeline/Spreadsheet view which gives a selection.
      return
    
    # Set the current selection
    self._selection = event.sender.selection()

    # Return if there's no Selection. We won't add the Menu.
    if len(self._selection) == 0:
      return
    
    event.menu.addMenu(self)

# Add the 'Set Status' context menu to Timeline and Spreadsheet
if kAddStatusMenu:
  SetStatusMenu = SetStatusMenu()

# Register our custom columns
hiero.ui.customColumn = CustomSpreadsheetColumns()
