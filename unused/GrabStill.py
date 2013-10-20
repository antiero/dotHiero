# GrabStill.py - Adds a right-click menu action for creating still frame clips from the active Viewer frame
# To install, copy to ~/.hiero/Python/StartupUI/
# Requires Hiero 1.5v1 or later.

import hiero.core
import hiero.ui
import os.path
from PySide.QtGui import *
from PySide.QtCore import *

def mapRetime(ti, timelineTime):
  return ti.sourceIn() + int((timelineTime - ti.timelineIn()) * ti.playbackSpeed())

# Method to return the visible TrackItem in the Current Viewer for a Sequence, seq, used for Tagging Shots in the Viewer
def visibleShotAtTime(seq,time):
  shot = seq.trackItemAt(time)
  if shot == None:
    return shot
    
  elif shot.isMediaPresent() and shot.isEnabled():
    return shot

def getFrameInfoFromTrackItemAtTime(trackItem,T):
  
  # File Source
  clip = trackItem.source()
  file_knob = clip.mediaSource().fileinfos()[0].filename()

  clip = trackItem.source()

  first_last_frame = int(mapRetime(trackItem,T)+clip.sourceIn())
  return file_knob, first_last_frame, trackItem

class GrabThisFrameAction(QAction):

  def __init__(self):
      QAction.__init__(self, "Grab Still Frame", None)
      self.triggered.connect(self.createStillFromCurrentViewerFrame)
      hiero.core.events.registerInterest("kShowContextMenu/kViewer", self.eventHandler)

  def createStillFromCurrentViewerFrame(self):
  
    currentShot = []
    cTransform = None
    # Current Time of the Current Viewer
    T = self.currentViewer.time()
    if self.currentClipSequence == None:
      self.currentClipSequence = hiero.ui.activeView().player().sequence()
    else:
      sequence = self.currentClipSequence.binItem().activeItem()
      if isinstance(sequence,hiero.core.Clip):
        cTransform = sequence.sourceMediaColourTransform()
        currentFrame = int(sequence.mediaSource().startTime()) + int(T)
        clip = hiero.core.Clip(sequence.mediaSource().fileinfos()[0].filename(),currentFrame, currentFrame)
      elif isinstance(sequence,hiero.core.Sequence):
        
        # Check that Media is Online - we won't add a Tag to Offline Media
        currentShot = visibleShotAtTime(sequence,T)
        if not currentShot:
          QMessageBox.warning(None, "Grab Frame", "Unable to Grab a Still Frame.", QMessageBox.Ok)
          return
        else:
          fileKnob,currentFrame,trackItem = getFrameInfoFromTrackItemAtTime(currentShot,T)
          clip = hiero.core.Clip(hiero.core.MediaSource(fileKnob),currentFrame, currentFrame)
          cTransform = currentShot.sourceMediaColourTransform()
          
      # Create a 'Stills' Bin, and add the Still Frame as a new Clip
      proj = self.currentClipSequence.project()
      rt = proj.clipsBin()
      try:
        b = rt['Stills']
      except:
        b = rt.addItem(hiero.core.Bin('Stills'))
      
      # This adds the Clip to the Stills Bin
      try:
        bi = hiero.core.BinItem(clip)
        clip.setName(bi.name()+'_frame%i' % currentFrame)
        b.addItem(bi)
        
        # Make sure the Clip has the correct Source Media Colour Transform applied...
        bi.activeItem().setSourceMediaColourTransform(cTransform)

      except:
        print 'Unable to create Still frame'

  def eventHandler(self, event):
    if hiero.ui.currentViewer().layoutMode() != hiero.ui.Viewer.LayoutMode.eLayoutStack:
      return
    else:
      self.currentClipSequence = None
      self.currentViewer = None
      self.currentPlayer = None
      
      self.currentViewer = event.sender
      self.currentPlayer = self.currentViewer.player()
      self.currentClipSequence = self.currentPlayer.sequence()

      if not self.currentClipSequence:
        return
      else:
        title = "Grab still Frame"
        self.setText(title)
        event.menu.addAction( self )

# Instantiate the action to get it to register itself.
GrabThisFrameAction = GrabThisFrameAction()