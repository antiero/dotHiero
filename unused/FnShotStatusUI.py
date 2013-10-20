# FnShotStatusUI - adds a Custom Column and Right-click menu to the Spreadsheet/Timeline view, allowing status to be set on a selection of Shots
# gStatusTags is a global dictionary of key(status)-value(icon) pairs, which can be overridden with custom status/icons if required
# Copyright (c) 2013 The Foundry Visionmongers Ltd.  All Rights Reserved.

import hiero.core
import hiero.ui
from PySide.QtGui import QMenu, QAction, QIcon, QComboBox
from PySide.QtCore import QSize

# Global Dictionary of Status Tags. 
# Note: This can be overwritten if you want to add a new status type or custom icon
# Override the gStatusTags dictionary by adding your own 'Status':'Icon.png' key-value pairs.
# Add new custom keys like so: gStatusTags['For Client'] = 'forClient.png'
gStatusTags = {'Bid':'icons:status/TagBid.png',
  'Planned':'icons:status/TagPlanned.png',
  'Not Started':'icons:status/TagNotStarted.png',
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
  tags = self.tags()
  for tag in tags:
    if tag.metadata().hasKey('tag.status'):
      hiero.core.log.debug('A Tag with a Status exists on this Shot')
      tag.setIcon(gStatusTags[status])
      tag.metadata().setValue('tag.status',status)
      self.sequence().editFinished()
      return

  # If we're here, we could not find a Tag with tag.status metadata, so create one
  hiero.core.log.debug('No Tag found. Creating a new one')
  statusTag = hiero.core.Tag(status)
  statusTag.setIcon(gStatusTags[status])
  statusTag.metadata().setValue('tag.status', status)
  self.addTag(statusTag)
  self.sequence().editFinished()
  return

# Inject status getter and setter methods into hiero.core.TrackItem
hiero.core.TrackItem.setStatus = _setStatus
hiero.core.TrackItem.status = _status

# This is a convenience method for returning QActions with a triggered method based on the title string
def titleStringTriggeredAction(title, method, icon = None):
  action = QAction(title,None)
  action.setIcon(QIcon(icon))
  
  # We do this magic, so that the title string from the action is used to set the status
  def methodWrapper():
    method(title)
  
  action.triggered.connect( methodWrapper )
  return action

# Menu which adds a Set Status Menu to Timeline and Spreadsheet Views
class SetStatusMenu(QMenu):

  def __init__(self):
      QMenu.__init__(self, "Set Status", None)

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

# Add a Custom Column to display the Status in the Spreadsheet
class StatusSpreadsheetColumn(object):
  """
    A custom column for Hiero's spreadsheet view. 
    This allows Shot Status state to be updated
  """

  global gStatusTags

  def numColumns(self):
    """
      Return the number of custom columns in the spreadsheet view
    """
    return 1

  def columnName(self, column):
    """
      Return the name of a custom column
    """
    if column == 0:
      return "Shot Status"

  def getData(self, row, column, item):
    """
      Return the data in a cell
    """

    if column == 0:
      status = item.status()
      return str(status)

  def setData(self, row, column, item, data):
    """
      Set the data in a cell
    """
    return item.status()

  def getSizeHint(self, row, column, item):
    """
      Return the size hint for a cell
    """
    if column == 0:
      return QSize(200, 26)
    return None

  def getTooltip(self, row, column, item):
    """
      Return the tooltip for a cell
    """
    return "Shot Status: " + str(item.status())

  def getIcon(self, row, column, item):
    """
      Return the icon for a cell
    """
    if column == 0:
      status = item.status()
      if status in gStatusTags.keys():
        return QIcon(gStatusTags[status])
    return None

  def createEditor(self, row, column, item, view):
    """
      Creates the ComboBox for setting the Status
    """
    cb = QComboBox()
    for key in gStatusTags.keys():
      cb.addItem(QIcon(gStatusTags[key]), key)
    return cb

  def setModelData(self, row, column, item, editor):
    """
      Update the model data from the custom editor. Return True if this was done.
    """
    item.setStatus(editor.currentText())
    return False

# Add the 'Set Status' context menu to Timeline and Spreadsheet
SetStatusMenu = SetStatusMenu()

# Register the Shot Status column
hiero.ui.customColumn = StatusSpreadsheetColumn()