# Copyright (c) 2011 The Foundry Visionmongers Ltd.  All Rights Reserved.

import os.path
import os
import sys
import hiero.core
from hiero.core import *

def mapRetime(ti, timelineTime):
  """Maps the trackItem source in time to timeline in time, handling any retimes"""
  return ti.sourceIn() + int((timelineTime - ti.timelineIn()) * ti.playbackSpeed())

class ThumbnailExportTask(TaskBase):
  def __init__( self, initDict ):
    """Initialize"""
    TaskBase.__init__( self, initDict )

  kFirstFrame = "First"
  kMiddleFrame = "Middle"
  kLastFrame = "Last"
  kCustomFrame = "Custom"

  def startTask(self):
    TaskBase.startTask(self)
    
    pass
  
  def sequenceInOutPoints(self, sequence, indefault, outdefault):
    """Return tuple (start, end) of in/out points. If either in/out is not set, return in/outdefault in its place."""
    inTime, outTime = indefault, outdefault
    try:
      inTime = sequence.inTime()
    except:
      pass
    
    try:
      outTime = sequence.outTime()
    except:
      pass
    return inTime, outTime  

  def getthumbFrameInfoFromTrackItemAtTime(self, trackItem,T):
    """This does the convoluted magic to get the necessaries to produce a Still from a TrackItem at time T"""
    # File Source
    clip = trackItem.source()
    file_knob = clip.mediaSource().fileinfos()[0].filename()

    clip = trackItem.source()

    first_last_frame = int(mapRetime(trackItem,T)+clip.sourceIn())
    return file_knob, first_last_frame, trackItem
     
  def taskStep(self):
    # Write out the thumbnail for each item
    if isinstance(self._item, (Sequence, Clip, TrackItem)):

        # Get the frame type
        frameType = self._preset.properties()['frameType']

        # Grab the custom offset value, in case its needed
        customOffset = int(self._preset.properties()['customFrameOffset'])
        self._thumbFile = self.resolvedExportPath()

        filename, ext = os.path.splitext(self._thumbFile)
        
        if isinstance(self._item, (Clip,Sequence)):
          # In and out points of the Sequence
          start, end = self.sequenceInOutPoints(self._item, 0, self._item.duration() - 1)

          if frameType == self.kFirstFrame:
            thumbFrame = start
          if frameType == self.kMiddleFrame:
            thumbFrame = start+((end-start)/2)
          if frameType == self.kLastFrame:
            thumbFrame = end
          if frameType == self.kCustomFrame:
            if customOffset > end:
              # If the custom offset exceeds the last frame, clamp at the last frame
              hiero.core.log.info("Frame offset exceeds the source out frame. Clamping to the last frame")
              thumbFrame = end
            else:
              thumbFrame = start+customOffset
        
        elif isinstance(self._item, TrackItem):
          if frameType == self.kFirstFrame:
            thumbFrame = self._item.sourceIn()
          elif frameType == self.kMiddleFrame:
            thumbFrame = self._item.sourceIn()+int((self._item.sourceOut()-self._item.sourceIn())/2)
          elif frameType == self.kLastFrame:
            thumbFrame = self._item.sourceOut()
          elif frameType == self.kCustomFrame:
            thumbFrame = self._item.sourceIn()+customOffset
            if thumbFrame > self._item.sourceOut():
              # If the custom offset exceeds the last frame, clamp at the last frame 
              hiero.core.log.info("Frame offset exceeds the source out frame. Clamping to the last frame")
              thumbFrame = self._item.sourceOut()

        thumb = self._item.thumbnail(thumbFrame)

        # If we find a resolved path containing a special <SOURCE_FRAME_f#> string, replace the filepath with f#
        print 'RESOLVED PATH IS ' + str(self._thumbFile)
        if self._thumbFile.find("<SOURCE_FRAME_f#>") != -1:
          print 'FOUND THIS STRING MATCH: <SOURCE_FRAME_f#>'
          self._thumbFile = self._thumbFile.replace("<SOURCE_FRAME_f#>","f%i" % thumbFrame)
          print 'REPLACED, NOW THE PATH IS : %s' % self._thumbFile

        try:
          thumbSize = self._preset.properties()['thumbSize']
          if thumbSize != "Default":
            thumb = thumb.scaledToHeight(int(thumbSize))

          thumb.save(self._thumbFile)
        except:
          print 'Unable to save thumbnail for %s' % str(self._item)
  
    self._finished = True
    
    return False

class ThumbnailExportPreset(TaskPresetBase):
  def __init__(self, name, properties):
    TaskPresetBase.__init__(self, ThumbnailExportTask, name)

    # Set any preset defaults here
    self.properties()["format"] = "png"
    self.properties()["frameType"] = "First Frame"
    self.properties()["customFrameOffset"] = 12
    self.properties()["thumbSize"] = "Default"

    # Update preset with loaded data
    self.properties().update(properties)

  def addCustomResolveEntries(self, resolver):
    resolver.addResolver("{ext}", "File format extension of the thumbnail", lambda keyword, task: self.properties()["format"])
    resolver.addResolver("{sourceframe}", "The source frame number", lambda keyword, task: "<SOURCE_FRAME_f#>")    
    resolver.addResolver("{frame}", "Frame type (first/middle/last)", lambda keyword, task: self.properties()["frameType"].lower())
  
  def supportedItems(self):
    return TaskPresetBase.kAllItems

taskRegistry.registerTask(ThumbnailExportPreset, ThumbnailExportTask)