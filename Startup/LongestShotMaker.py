import hiero.core
from PySide.QtGui import *
from PySide.QtGui import *

# Longest Shot from Sequence
# Workflow:
# 1) Select a bunch of Sequences > Right-click > Create Longest Shot Sequnece
# 2) Longest Shot Maker asks what kind of Sequence you want:
# Create a new Sequence with identical Shot names? (default behaviour)
# Long Shot maker analyses EDLs (Sequences) for identical Shot

# Context menu option to create new sequences from selected Clips in the Bin View.
# If Clips are named as Stereo left and right then one sequence will be created with left and right tagged tracks.

class LongestSequenceFromSelectionAction(QAction):
  
  def __init__(self):
    QAction.__init__(self, "Create Longest Shot Sequence", None)
    self.triggered.connect(self.doit)
    hiero.core.events.registerInterest((hiero.core.events.EventType.kShowContextMenu, hiero.core.events.EventType.kBin), self.eventHandler)
  
  def newSequence(self, selection):
    '''Create a new sequence from a selection of clips
      @return hiero.core.Sequence, hiero.core.Bin
      '''
    if isinstance(selection[0], hiero.core.BinItem):
      clip = selection[0].activeItem()
    elif isinstance(selection[0], hiero.core.Clip):
      clip = selection[0]
    
    bin = clip.binItem().parentBin()
    sequence = hiero.core.Sequence(selection[0].name())
    
    if clip.mediaSource().hasVideo():
      if clip.mediaSource().metadata()["foundry.source.framerate"]:
        fps = clip.mediaSource().metadata()["foundry.source.framerate"]
      else:
        fps = clip.framerate()
      sequence.setFramerate(hiero.core.TimeBase.fromString(str(fps)))
      sequence.setFormat(clip.format())
      
      for i in range(clip.numVideoTracks()):
        sequence.addTrack(hiero.core.VideoTrack("Video " + str(i+1)))
        try:
          videoClip = sequence.videoTrack(i).addTrackItem(clip, 0)
        except:
          print "Failed to add clip"
    else:
      videoClip = None
    
    if clip.mediaSource().hasAudio():
      linkItems = []
      for i in range(clip.numAudioTracks()):
        audioTrackName = "Audio " + str( i+1 )
        if not self.trackNameExists(sequence, audioTrackName):
          newAudioTrack = sequence.addTrack(hiero.core.AudioTrack(audioTrackName))
        else:
          newAudioTrack = self.trackNameExists(sequence, audioTrackName)
        audioClip = newAudioTrack.addTrackItem(clip, i, 0)
        linkItems.append(audioClip)
        if videoClip:
          audioClip.link(videoClip)
        else:
          if len(linkItems) > 0:
            audioClip.link(linkItems[0])
    
    return sequence, bin

  
  def doit(self):
    selection = list(hiero.ui.activeView().selection())
    sequences = [item.activeItem() for item in selection if isinstance(item.activeItem(),hiero.core.Sequence)]
  
    # For every Sequence, we need to build a list of shots
    # This will assume that the first track is the master track, as if it were from the original EDL
    all_shots = []
    for seq in sequences:
      try:
        track = seq[0]
      except:
        print "A Sequnece must contain at least one Video Track. Check Sequence:  %s" % str(seq)
        return
      
      shots = list(track.items())
      all_shots.extend(shots)

    # We now must determine sets of shots which have the same Shot name and Source Clip name
    shotMatches = {}
    for shot in all_shots:
      print str(shot)
      shotName = shot.name()
      if shotName in shotMatches.keys():
        shotMatches[shotName]+=[{'trackItem':shot,
                                 'clip':shot.source(),
                                 'duration':shot.duration(),
                                 'sourceIn':shot.sourceIn(),
                                 'sourceOut':shot.sourceOut()
                                 }]
      else:
        shotMatches[shotName]=[{'trackItem':shot,
                                 'clip':shot.source(),
                                 'duration':shot.duration(),
                                 'sourceIn':shot.sourceIn(),
                                 'sourceOut':shot.sourceOut()
                                 }]
    hiero.core.shots=shotMatches

    longestShots = []
    for shotName in shotMatches.keys():
      MAX = max([item['duration'] for item in shotMatches[shotName]])
      print 'Max duration for Shot: %s is %i' % (str(shotName),MAX)
      
      # Now find the dict inside shotMatches which has this duration
      longestShot = [item['trackItem'] for item in shotMatches[shotName] if item['duration']==MAX]
      longestShots.extend(longestShot)

    print 'LONGEST SHOTS WERE: ' + str(longestShots)
    # Create a new Sequence
    seq2 = hiero.core.Sequence("Longest Shots")
    t0 = 0
    for shot in longestShots:
      print 'ADDING SHOT: ' + str(shot)
      seq2.addClip(shot.source(),t0)
      t0 = seq.duration()
    proj = seq.project()
    root = proj.clipsBin()
    root.addItem(hiero.core.BinItem(seq2))

  def eventHandler(self, event):
    if not hasattr(event.sender, 'selection'):
      return
    
    # Disable if nothing is selected
    selection = event.sender.selection()
    
    selectedSequences = [item for item in selection if isinstance(item.activeItem(),hiero.core.Sequence)]

    self.setEnabled( len(selectedSequences) > 1 )
    event.menu.addAction(self)

action = LongestSequenceFromSelectionAction()