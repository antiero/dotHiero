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

  # These are a set of action names we can use for operating on multiple Clip/TrackItems
  eMaxVersion = "Max Version"
  eMinVersion = "Min Version"
  eNextVersion = "Next Version"
  ePreviousVersion = "Previous Version"

  def __init__(self):
      self._versionEverywhereMenu = None
      self._versionActions = []

      hiero.core.events.registerInterest("kShowContextMenu/kBin", self.binViewEventHandler)

  def makeVersionActionForSingleClip(self, version):
    """This is used to populate the list of Versions when a single Clip is selected"""
    action = QAction(version.name(),None)
    action.setData(lambda: version)

    def updateAllTrackItems():
      currentClip = version.item()
      trackItems = currentClip.whereAmI()
      proj = currentClip.project()

      # Make this all undo-able in a single Group undo
      with proj.beginUndo("Update All Versions for %s" % currentClip.name()):
        for ti in trackItems:
          print 'Setting TrackItem %s to be this version: %s ' % (str(ti), str(version))
          ti.setCurrentVersion(version)

        # We also should update the current Version of the selected Clip for completeness...
        currentClip.binItem().setActiveVersion(version)
    
    action.triggered.connect( updateAllTrackItems )
    return action

  # This is just a convenience method for returning QActions with a title, triggered method and icon.
  def makeAction(self,title, method, icon = None):
    action = QAction(title,None)
    action.setIcon(QIcon(icon))
    
    # We do this magic, so that the title string from the action is used to set the frame rate!
    def methodWrapper():
      method(title)
    
    action.triggered.connect( methodWrapper )
    return action     

  def clipSelectionForActiveView(self):
    """Helper method to return a list of Clips in the Active View"""
    selection = hiero.ui.activeView().selection()

    if len(selection)==0:
      return None

    clipItems = [item.activeItem() for item in selection if isinstance(item.activeItem(),hiero.core.Clip)]

    bins = [item for item in selection if isinstance(item,hiero.core.Bin)]

    # We search inside of a Bin for a Clip which is not already in clipBinItems
    if len(bins)>0:
      # Grab the Clips inside of a Bin and append them to a list
      for bin in bins:
        clips = hiero.core.findItemsInBin(bin,'Clip')
        for clip in clips:
          if clip not in clipItems:
            clipItems.append(clip)

    return clipItems

  # This generates the Version Up Everywhere menu
  def createVersionEveryWhereMenuForView(self, viewName):

    # We look to the activeView for a selection of Clips
    clips = self.clipSelectionForActiveView()
    versionEverywhereMenu = QMenu("Version Up Everywhere")
    self._versionActions = []
    
    # And bail if nothing is found
    if len(clips)==0:
      return versionEverywhereMenu

    # Now, if we have just one Clip selected, we'll form a special menu, which lists all versions
    if len(clips)==1:
      versions = clips[0].binItem().items()
      for version in versions:
        self._versionActions+=[self.makeVersionActionForSingleClip(version)]

    elif len(clips)>1:
      # We will add Max/Min/Prev/Next options, which can be called on a TrackItem, without the need for a Version object
      self._versionActions+=[self.makeAction(self.eMaxVersion,self.setTrackItemVersionForClipSelection, icon=None)]
      self._versionActions+=[self.makeAction(self.eMinVersion,self.setTrackItemVersionForClipSelection, icon=None)]
      self._versionActions+=[self.makeAction(self.eNextVersion,self.setTrackItemVersionForClipSelection, icon=None)]
      self._versionActions+=[self.makeAction(self.ePreviousVersion,self.setTrackItemVersionForClipSelection, icon=None)]

    for act in self._versionActions:
      versionEverywhereMenu.addAction(act)

    return versionEverywhereMenu

  def setTrackItemVersionForClipSelection(self,versionOption):

    clipSelection = self.clipSelectionForActiveView()

    if len(clipSelection)==0:
      return

    proj = clipSelection[0].project()

    with proj.beginUndo("Update All Clip Versions"):
      for clip in clipSelection:
        # Look to see if it exists in a TrackItem somewhere...
        clipUsage = clip.whereAmI('TrackItem')

        # Next, depending on the versionOption, make the appropriate update
        # There's probably a more neat/compact way of doing this...
        for shot in clipUsage:
          if versionOption == self.eMaxVersion:
            shot.maxVersion()
          elif versionOption == self.eMinVersion:
            shot.minVersion()
          elif versionOption == self.eNextVersion:
            shot.nextVersion()
          elif versionOption == self.ePrevVersion:
            shot.prevVersion()

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