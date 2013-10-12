# Copyright (c) 2011 The Foundry Visionmongers Ltd.  All Rights Reserved.

import os.path
import os
import sys

from hiero.core import *


class ThumbnailExportTask(TaskBase):
  def __init__( self, initDict ):
    """Initialize"""
    TaskBase.__init__( self, initDict )

  kFirstFrame = "First Frame"
  kMiddleFrame = "Middle Frame"
  kLastFrame = "Last Frame"
  kFirstMidLastFrame = "First, Middle, Last Frames"

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

  def getFreezeFrameInfoFromTrackItemAtTime(self, trackItem,T):
    """This does the convoluted magic to get the necessaries to produce a Still from a TrackItem at time T"""
    # File Source
    clip = trackItem.source()
    file_knob = clip.mediaSource().fileinfos()[0].filename()

    clip = trackItem.source()

    first_last_frame = int(mapRetime(trackItem,T)+clip.sourceIn())
    return file_knob, first_last_frame, trackItem

  def getThumbnailForItemAtPosition(self, trackItem, kPosition):
    """This is the action to generate a QImage for an item at the given kPosition"""

    if kPosition == self.kFirstFrame:
      FreezeFrame = trackItem.sourceIn()
    elif kPosition == self.kMiddleFrame:
      FreezeFrame = int((trackItem.sourceOut()-trackItem.sourceIn())/2)
    elif kPosition == self.kLastFrame:
      FreezeFrame = trackItem.sourceOut()

    # The Colour Transform of the TrackItem
    colourTransform = trackItem.sourceMediaColourTransform()

    # This is the (convoluted) magic to create a single Frame Clip in the Bin
    fileKnob,currentFrame,ti = self.getFreezeFrameInfoFromTrackItemAtTime(trackItem,FreezeFrame)

    # This is an adjustment for the Timeline time of the current TrackItem
    FreezeFrame = currentFrame+trackItem.timelineIn()

    # This creates a single Frame object
    FreezeFrameClip = hiero.core.Clip(hiero.core.MediaSource(fileKnob),FreezeFrame, FreezeFrame)
    FreezeFrameClip.sourceMediaColourTransform(colourTransform)
    FreezeFrameClip.editFinished()

    thumbnail = FreezeFrameClip.thumbnail()
    return thumbnail

    # This adds the FreezeFrameClip to the Bin and returns it with the appropriate TrackItem colourTransform applied
    #clip = self.addStillClipToStillsBin(proj,FreezeFrameClip,colourTransform)
     
  def taskStep(self):
    # Write out the thumbnail for each item
    if isinstance(self._item, (Sequence, Clip)):
        self._thumbFile = self.resolvedExportPath()
        print 'RESOLVED EXPORT PATH IS: ' + str(self._thumbFile)
        
        filename, ext = os.path.splitext(self._thumbFile)
        
        if isinstance(self._item, (Clip,Sequence)):
          # In and out points of the Sequence
          start, end = self.sequenceInOutPoints(self._item, 0, self._item.duration() - 1)

          print "SEQUENCE START, END is: %i, %i" % (int(start), int(end))

          # Get the frame type
          frameType = self._preset.properties()['frameType']
          if frameType == self.kFirstFrame:
            thumb = self._item.thumbnail(start)
          if frameType == self.kMiddleFrame:
            thumb = self._item.thumbnail(start+((end-start)/2))
          if frameType == self.kLastFrame:
            thumb = self._item.thumbnail(end)

          print 'SAVING %s TO: self._thumbFile' % str(thumb)

          thumbSize = self._preset.properties()['thumbSize']
          if thumbSize != "Default":
            thumb = thumb.scaledToHeight(int(thumbSize))
          thumb.save(self._thumbFile)
        
        elif isinstance(self._item, TrackItem):
          handles = self._cutHandles if self._cutHandles is not None else 0
          start, end = (self._item.timelineIn() - handles), (self._item.timelineOut() + handles) + 1
          # If trackitem write out just the audio within the cut
          self._sequence.writeAudioToFile(self._audioFile, start, end)
        
    self._finished = True
    
    return False

class ThumbnailExportPreset(TaskPresetBase):
  def __init__(self, name, properties):
    TaskPresetBase.__init__(self, ThumbnailExportTask, name)
    # Set any preset defaults here
    # self._properties["SomeProperty"] = "SomeValue"
    # Set any preset defaults here
    self.properties()["format"] = "png"
    self.properties()["frameType"] = "First Frame"
    self.properties()["customFrameOffset"] = 0
    self.properties()["thumbSize"] = "Default"

    # Update preset with loaded data
    self.properties().update(properties)

  def addCustomResolveEntries(self, resolver):
    resolver.addResolver("{ext}", "File format extension of the thumbnail", lambda keyword, task: self.properties()["format"])
    resolver.addResolver("{frame}", "Frame type (first/middle/last)", lambda keyword, task: self.properties()["frameType"].split(' Frame')[0].lower())
  
  def supportedItems(self):
    return TaskPresetBase.kAllItems

taskRegistry.registerTask(ThumbnailExportPreset, ThumbnailExportTask)