# Copyright (c) 2011 The Foundry Visionmongers Ltd.  All Rights Reserved.

import re
import os
import os.path
import math
import csv

import hiero.core

class ShotListExportTrackTask:
  def __init__(self, parent, track, trackItems):
    self._parent = parent
    self._track = track
    self._trackItems = trackItems
    self._trackItemIndex = 0
    # Note EDL event indexes start at 1. In the future we may want to skip some track items so
    # keeping these counters separate to make sure EDL events will still increment sequentially.
    self._eventIndex = 1
    self._fps = parent._fps
    self._preset = parent._preset
    self._edits = []
    self._dropFrame = False
  
  def edits(self):
    return self._edits


  #### Shot Methods ####
  def getStatus(self, trackItem):
    status = 'OK'
    if not trackItem.isMediaPresent():
      status = 'OFF'
    return status

  def timecodePrefCheck(self):
    # We need to check the user Preference for 'Timecode > EDL-Style Spreadsheet Timecodes'
    return int(hiero.core.ApplicationSettings().boolValue('useVideoEDLTimecodes'))

  def getReelName(self,trackItem):
    reelName = ""
    M = trackItem.metadata()
    if M.hasKey('foundry.edl.sourceReel'):
      reelName = M.value('foundry.edl.sourceReel')
    return reelName

  def getSrcIn(self,trackItem):
    fps = trackItem.parent().parent().framerate()
    clip = trackItem.source()
    clipstartTimeCode = clip.timecodeStart()
    srcIn = hiero.core.Timecode.timeToString(clipstartTimeCode+trackItem.sourceIn(), fps, hiero.core.Timecode.kDisplayTimecode)
    return srcIn

  def getSrcOut(self,trackItem):

    fps = trackItem.parent().parent().framerate()
    clip = trackItem.source()
    clipstartTimeCode = clip.timecodeStart()
    srcOut = hiero.core.Timecode.timeToString(clipstartTimeCode+trackItem.sourceOut()+self.timecodePrefCheck(), fps, hiero.core.Timecode.kDisplayTimecode)
    return srcOut

  def getDstIn(self,trackItem):
    seq = trackItem.parent().parent()
    tStart = seq.timecodeStart()
    fps = seq.framerate()
    dstIn = hiero.core.Timecode.timeToString(tStart+trackItem.timelineIn(),fps,hiero.core.Timecode.kDisplayTimecode)
    return dstIn

  def getDstOut(self,trackItem):
    seq = trackItem.parent().parent()
    tStart = seq.timecodeStart()
    fps = seq.framerate()
    dstOut = hiero.core.Timecode.timeToString(tStart+trackItem.timelineOut()+self.timecodePrefCheck(), fps, hiero.core.Timecode.kDisplayTimecode)
    return dstOut

  # Get a Nuke Read node style file path
  def getNukeStyleFilePath(self,trackItem):
    fi = trackItem.source().mediaSource().fileinfos()[0]
    filename = fi.filename()
    first = fi.startFrame()
    last = fi.endFrame()
    if trackItem.source().mediaSource().singleFile():
      return filename
    else:
      return "%s %i-%i" % (filename,first,last)


  def trackItemFilename(self, trackItem):
    filename = None
    source = None
    if isinstance(trackItem.source(), hiero.core.Clip):
      source = trackItem.source().mediaSource()
    if source is not None and source.fileinfos() is not None:
      fileinfo = source.fileinfos()[0]
      if fileinfo is not None:
        filename = fileinfo.filename()
        if not self._preset.properties()["abspath"]:
          filename = os.path.basename(filename)
    return filename

  def trackItemEditName(self, trackItem):
    editName = trackItem.name()
    editName = re.sub(r'[\W_]+', '', editName) 
    if self._preset.properties()["truncate"]:
      editName = editName [:8]
    return editName


  # Create a basic EDL cut
  def createShotListRow(self, trackItem):
  
    # Get all Tracks in the Sequence...
    if isinstance(trackItem,hiero.core.TrackItem):
      #M = trackItem.metadata()

      shotRow = [str(trackItem.eventNumber()),
                    str(self.getStatus(trackItem)),
                    str(trackItem.name()),
                    str(self.getReelName(trackItem)),
                    str(trackItem.parent().name()),
                    "%.1f" % (100.0*float(trackItem.playbackSpeed())),
                    str(self.getSrcIn(trackItem)),
                    str(self.getSrcOut(trackItem)),
                    str(math.floor(trackItem.sourceDuration())),
                    str(self.getDstIn(trackItem)),
                    str(self.getDstOut(trackItem)),
                    str(trackItem.duration()),
                    str(trackItem.source().name()),
                    str(self.getNukeStyleFilePath(trackItem))]

    self._edits.append( shotRow )    

  def taskStep(self):
    if len(self._trackItems) == 0:
      return False
    trackItem = self._trackItems[self._trackItemIndex]

    self.createShotListRow(trackItem)

    self._eventIndex += 1
    self._trackItemIndex += 1
    
    return self._trackItemIndex < len(self._trackItems)

class CSVFileWriter():
  def __init__(self, parent, columnHeaderList):
    self._parent = parent
    
    # This is a list of the selected Column Header titles, specified via the UI
    self._csvHeaderRow = columnHeaderList
    print 'THIS LIST:',self._csvHeaderRow
    self._edits = []

  def addEdits(self, edits):
    self._edits += edits

  def write(self, filePath):
    
    
    try:
      # check export root exists
      dir = os.path.dirname(filePath)
      if not os.path.exists(dir):
        os.makedirs(dir)
      # Write the Header row to the CSV file
      self._writer = csv.writer(open(filePath, 'w'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
      self._writer.writerow(self._csvHeaderRow)
    except IOError:
      error( "CSVFileWriter.write failed %s" % exportPath )
      raise
    
    eventIndex = 1
    for shotRow in self._edits:
      self._writer.writerow(shotRow)



class ShotListExportTask(hiero.core.TaskBase):
  
  def __init__(self, initDict):
    """Initialize"""
    self._currentTrack = None
    hiero.core.TaskBase.__init__(self, initDict)
    self._fps = self._sequence.framerate().toInt()
    self._trackTasks = []
    self._trackTaskIndex = 0
    self._audioTask = None

    self._stepTotal = 0
    self._stepCount = 0
  
    csvColumnHeaders = self.getColumnHeaderTitleList()
    # Initialise a CSV File Writer with selected column headers
    self._fileWriter = CSVFileWriter(self,csvColumnHeaders)

  def getColumnHeaderTitleList(self):
    # Here, we construct a list of column headers, based on csvData Dict for checkboxes which are True
    columnHeaders = []
    for data in ShotListExportTask.csvPropertyData:
      key = data['knobName']
      value = self._preset.properties()["csvData"][key]
      if value==True:
        columnHeaders+=[key]
    
    print 'CSV Column headers:',columnHeaders
    return columnHeaders

  def currentTrackName(self):
    if self._currentTrack:
      return self._currentTrack.name()
    else:
      return self._sequence.videoTracks()[0].name()
    
  def startTask (self):

    """if self._preset.supportsAudio():
      audioTracks = []
      for track in self._sequence.audioTracks():
        audioTracks.append( track )
      self._audioTask = ShotListExportAudioTrackTask(self, audioTracks)
      while self._audioTask.taskStep():
        pass"""

    # Build list of items from sequence to be added added to the CSV
    for track in self._sequence.videoTracks():
      trackItems = []
      for trackitem in track:
        trackItems.append(trackitem)
        self._stepTotal += 1
      task = ShotListExportTrackTask(self, track, trackItems)
      self._trackTasks.append( task )


  def exportFilePath(self):
    exportPath = self.resolvedExportPath()
    # Check file extension
    if not exportPath.lower().endswith(".csv"):
      exportPath += ".csv"
    return exportPath

  def taskStep(self):
    trackTask = self._trackTasks[self._trackTaskIndex]
    self._currentTrack = trackTask._track
    if not trackTask.taskStep():
      path = self.exportFilePath()

      self._fileWriter.addEdits( trackTask.edits() )

      """if self._audioTask:
        self._fileWriter.addEdits( self._audioTask.edits() )
        self._audioTask = None"""

      self._fileWriter.write( path )
      self._trackTaskIndex += 1

    self._stepCount += 1
    return self._stepCount < self._stepTotal
  
  def finishTask(self):
    hiero.core.TaskBase.finishTask(self)

  def progress(self):
    if self._stepTotal == 0:
      return 0.0
    else:
      return float(self._stepCount / self._stepTotal)


ShotListExportTask.csvPropertyData = (
                          {'title':"Event", 'knobName':"event", 'value' : True },
                          {'title':"Status", 'knobName':"status", 'value' : True},
                          {'title':"Shot Name", 'knobName':"shotName", 'value' : True},
                          {'title':"Reel", 'knobName':"reel", 'value' : True},
                          {'title':"Track", 'knobName':"track", 'value' : True},
                          {'title':"Speed", 'knobName':"speed", 'value' : True},
                          {'title':"Src In", 'knobName':"srcIn", 'value' :  True},
                          {'title':"Src Out", 'knobName':"srcOut", 'value' : True},
                          {'title':"Src Duration", 'knobName':"srcDuration", 'value' : True},
                          {'title':"Dst In", 'knobName':"dstIn", 'value' : True},
                          {'title':"Dst Out", 'knobName':"dstOut", 'value' : True},
                          {'title':"Dst Duration", 'knobName':"dstDuration", 'value' : True},
                          {'title':"Clip Name", 'knobName':"clip", 'value' : True},
                          {'title':"Clip Media", 'knobName':"clipMedia", 'value' : True})

class ShotListExportPreset(hiero.core.TaskPresetBase):
  def __init__(self, name, properties):
    """Initialise presets to default values"""
    hiero.core.TaskPresetBase.__init__(self, ShotListExportTask, name)
    self._properties = {}
    self._name = name
    
    self.properties()["csvData"] = dict([(subdict['knobName'],subdict['value']) for subdict in ShotListExportTask.csvPropertyData])
    
    # Update preset with loaded data
    self.properties().update(properties)

  def supportedItems(self):
    return hiero.core.TaskPreset.kSequence
    
  def addCustomResolveEntries(self, resolver):
    resolver.addResolver("{ext}", "Extension of the file to be output", lambda keyword, task: "csv")

  def supportsAudio(self):
    return True

 

hiero.core.log.debug( "Registering ShotListExportTask" )
hiero.core.taskRegistry.registerTask(ShotListExportPreset, ShotListExportTask)

  
