import hiero.core
from PySide.QtGui import *

def whereAmI(self, searchType='TrackItem'):
  """returns a list of objects which contain this Clip. 
  By default this will return a list of TrackItems where the Clip is used in its project.
  You can also return a list of Sequences by specifying the searchType to be 'Sequence'

  Example usage:

  shotsForClip = clip.whereAmI('TrackItem')
  sequencesForClip = clip.whereAmI('Sequence')
  """
  proj = self.project()

  if ('TrackItem' not in searchType) and ('Sequence' not in searchType):
    print "searchType argument must be 'TrackItem' or 'Sequence'"
    return None

  # If user specifies a TrackItem, then it will return 
  searches = hiero.core.findItemsInProject(proj, searchType)

  if len(searches)==0:
    print 'Unable to find %s in any items of type: %s' % (str(self),str(searchType)) 
    return None
  
  # Case 1: Looking for Shots (trackItems)
  clipUsedIn = []
  if isinstance(searches[0],hiero.core.TrackItem):
    for shot in searches:
      if shot.source().binItem() == self.binItem():
        clipUsedIn.append(shot)

  # Case 1: Looking for Shots (trackItems)
  elif isinstance(searches[0],hiero.core.Sequence):
      for seq in searches:
        # Iterate tracks > shots...
        tracks = seq.items()
        for track in tracks:
          shots = track.items()
          for shot in shots:
            if shot.source().binItem() == self.binItem():
              clipUsedIn.append(seq)

  return clipUsedIn

# Add new method to Clip object
hiero.core.Clip.whereAmI = whereAmI

# Menu which adds a Tags Menu to the Viewer, Project Bin and Timeline/Spreadsheet
class VersionAllMenu:

  def __init__(self):
      self._versionEverywhereMenu = None
      self._versionActions = []

      hiero.core.events.registerInterest("kShowContextMenu/kBin", self.binViewEventHandler)

  def makeActionFromVersion(self, version):
    action = QAction(version.name(),None)
    action.setData(lambda: version)

    # We do this magic, so that the title string from the action is used to set the frame rate!
    def methodWrapper():
      print 'METHOD WRAPPER CALLED'
      currentClip = version.item()
      trackItems = currentClip.whereAmI()
      for ti in trackItems:
        print 'Setting TrackItem %s to be this version: %s ' % (str(ti), str(version))
        ti.setCurrentVersion(version)
    
    action.triggered.connect( methodWrapper )
    return action  

  # This generates the Version Up Everywhere menu
  def createVersionEveryWhereMenuForView(self, viewName):

    selection = hiero.ui.activeView().selection()
    self._versionActions = []
    if len(selection)==0:
      return

    versionEverywhereMenu = QMenu("Version Up Everywhere")

    # If we're in the Bin, we could have a Sequence, Bin(s), or Clip(s) selected.
    # We must ignore the Sequence case, and treat the other cases.
    if viewName == 'kBin':
      # If we've selected one Clip, we'll present a unique list of all available versions to pick form

      clipBinItems = [item for item in selection if isinstance(item.activeItem(),hiero.core.Clip)]

      print 'Got this many Clips: ' + str(clipBinItems)
      bins = [item for item in selection if isinstance(item,hiero.core.Bin)]

      # We search inside of a Bin for a Clip which is not already in clipBinItems
      if len(bins)>0:
        # Grab the Clips inside of a Bin and append them to a list
        for bin in bins:
          clips = hiero.core.findItemsInBin(bin,'Clip')
          for clip in clips:
            if clip not in clipBinItems:
              clipBinItems.append(clip)

      # Now, if we have just one Clip selected, we'll form a special menu, which lists all versions
      if len(clipBinItems)==1:
        versions = clipBinItems[0].items()
        for version in versions:
          self._versionActions+=[self.makeActionFromVersion(version)]
          

      for act in self._versionActions:
        versionEverywhereMenu.addAction(act)

        # We have a mixture of Clips, so we can't pick a Version, offer options for Prev/Next/Min/Max
    return versionEverywhereMenu


  # This handles events from the Project Bin View
  def binViewEventHandler(self,event):

    if not hasattr(event.sender, 'selection'):
      # Something has gone wrong, we should only be here if raised
      # by the Bin view which gives a selection.
      return
    selection = event.sender.selection()

    # Return if there's no Selection. We won't add the Localise Menu.
    if selection == None:
      return

    # Only add the Menu if Bins or Sequences are selected (this ensures menu isn't added in the Tags Pane)
    if len(selection) > 0:
      self._versionEverywhereMenu = self.createVersionEveryWhereMenuForView('kBin')
      
      # Insert the Tags menu with the Localisation Menu
      hiero.ui.insertMenuAction(self._versionEverywhereMenu.menuAction(), event.menu)
    return

# Instantiate the Menu to get it to register itself.
VersionAllMenu = VersionAllMenu()