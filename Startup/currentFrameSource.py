import hiero.core as hc
import hiero.ui as hi

# Method to return a file source and frame range a Nuke friendly Read node way
def getFrameSourceFromCurrentViewer():
  # Current Viewer and Player
  cv = hi.currentViewer()
  cp = cv.player()

  # Current Sequence
  seq = cp.sequence().binItem().activeItem()

  # Current time of the Player
  T = cp.time()
  # Current TrackItem of the
  trackItem = seq.trackItemAt(T)

  d = T-trackItem.timelineIn()
  frame = trackItem.sourceIn()+d

  # Source Clip
  fileIn = trackItem.source().mediaSource().firstpath()
  # Now we have to calculate the Source frame of the TrackItem
  return fileIn, frame
