# fields for creating new clip names and updates the selected track items.

import hiero.core
import hiero.ui
from PySide.QtGui import *
from PySide.QtCore import *
import tempfile

def mapRetime(ti, timelineTime):
  return ti.sourceIn() + int((timelineTime - ti.timelineIn()) * ti.playbackSpeed())

def openCurrentViewerFrameWithNuke():
  # Get current Viewer Frame
  cv = hiero.ui.currentViewer()

  # Get the Current Player Object
  p = cv.player()

  # Get the current Time in the Player
  T = p.time()

  # Get the current Sequence in the Viewer
  seq = p.sequence().binItem().activeItem()

  # Get the TrackItem at Time T
  trackItem = seq.trackItemAt(T)

  # File Source
  clip = trackItem.source()
  file_knob = clip.mediaSource().fileinfos()[0].filename()

  clip = trackItem.source()

  first_last_frame = int(mapRetime(trackItem,T)+clip.sourceIn())
  return file_knob, first_last_frame, trackItem

# Shows how to add a right-click menu item and act upon a selection of Track items

# This example opens the selected TrackItem in Nuke (if a valid Nuke path is specified in
# Hiero's preferences

import os.path
import hiero.core
import hiero.ui
import hiero.core.nuke
import tempfile

from PySide.QtGui import *
from PySide.QtCore import *

class GrabThisFrameAction(QAction):

  def __init__(self):
      QAction.__init__(self, "Grab Still", None)
      #self.triggered.connect(self.generateNukeScriptFromTrackItem)
      self.triggered.connect(self.createStillFromCurrentViewerFrame)
      hiero.core.events.registerInterest("kShowContextMenu/kViewer", self.eventHandler)

  def createStillFromCurrentViewerFrame(self):
    fileKnob,first_last_frame,trackItem = openCurrentViewerFrameWithNuke()
    
    # Create a 'Stills' Bin, and add the Still Frame as a new Clip
    proj = trackItem.project()
    rt = proj.clipsBin()
    try:
      b = rt['Stills']
    except:
      b = rt.addItem(hiero.core.Bin('Stills'))
    print fileKnob,first_last_frame
    clip = Clip(MediaSource(fileKnob),first_last_frame, first_last_frame)
    b.addItem(BinItem(clip))

  def eventHandler(self, event):
    enabled = True
    title = "Grab Still"
    self.setText(title)
    event.menu.addAction( self )

# Instantiate the action to get it to register itself.
GrabThisFrameAction = GrabThisFrameAction()

