# version_up_everywhere.py 
# Adds action to Bin View to enable a Clip to be Min/Max/Next/Prev versioned in all shots used in a Project.
#
# Usage: 
# 1) Copy file to ~/.hiero/Python/Startup
# 2) Right-click on Clip(s) or Bins containin Clips in in the Bin View
# 3) Select Version Everywhere > OPTION to update the version in all shots where the Clip is used in the Project.
import hiero.core
from PySide.QtGui import *

def whereAmI(self, searchType='TrackItem'):
  """returns a list of TrackItem or Sequnece objects in the Project which contain this Clip. 
  By default this will return a list of TrackItems where the Clip is used in its project.
  You can also return a list of Sequences by specifying the searchType to be 'Sequence'.
  Should consider putting this into hiero.core.Clip by default?

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
      # We have to wrap this in a try/except because it's possible through the Python API for a Shot to exist without a Clip in the Bin
      try:

        # For versioning to be work, we must look to the BinItem that a Clip is wrapped in.
        if shot.source().binItem() == self.binItem():
          clipUsedIn.append(shot)

      # If we throw an exception here its because the Shot did not have a Source Clip in the Bin.
      except RuntimeError:
        #print 'Unable to find Parent Clip BinItem for Shot: %s, Source:%s' % (shot, shot.source())
        pass

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

# Add whereAmI method to Clip object
hiero.core.Clip.whereAmI = whereAmI

#### MAIN VERSION EVERYWHERE GUBBINS #####
class VersionAllMenu(object):

  # These are a set of action names we can use for operating on multiple Clip/TrackItems
  eMaxVersion = "Max Version"
  eMinVersion = "Min Version"
  eNextVersion = "Next Version"
  ePreviousVersion = "Previous Version"

  # This is the title used for the Version Menu title. It's long isn't it?
  actionTitle = "Set Version For All Shots"

  def __init__(self):
      self._versionEverywhereMenu = None
      self._versionActions = []

      hiero.core.events.registerInterest("kShowContextMenu/kBin", self.binViewEventHandler)
      hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.binViewEventHandler)

  def showVersionUpdateReportFromShotManifest(self,sequenceShotManifest):
      """This just displays an info Message box, based on a Sequence[Shot] manifest dictionary"""

      # Now present an info dialog, explaining where shots were updated
      updateReportString = "The following Versions were updated:\n"
      for seq in sequenceShotManifest.keys():
        updateReportString+="%s:\n  Shots:\n" % (seq.name())
        for shot in sequenceShotManifest[seq]:
          updateReportString+='  %s\n    (New Version: %s)\n' % (shot.name(), shot.currentVersion().name())
        updateReportString+='\n'

      infoBox = QMessageBox(hiero.ui.mainWindow())
      infoBox.setIcon(QMessageBox.Information)

      if len(sequenceShotManifest)<=0:
        infoBox.setText("No Shot Versions were updated")
        infoBox.setInformativeText("Clip could not be found in any Shots in this Project")
      else:
        infoBox.setText("Versions were updated in %i Sequences of this Project." % (len(sequenceShotManifest)))
        infoBox.setInformativeText("Show Details for more info.")
        infoBox.setDetailedText(updateReportString)

      infoBox.exec_()     

  def makeVersionActionForSingleClip(self, version):
    """This is used to populate the QAction list of Versions when a single Clip is selected in the BinView. 
    It also triggers the Version Update action based on the version passed to it. 
    (Not sure if this is good design practice, but it's compact!)"""
    action = QAction(version.name(),None)
    action.setData(lambda: version)

    def updateAllTrackItems():
      currentClip = version.item()
      trackItems = currentClip.whereAmI()
      proj = currentClip.project()

      # A Sequence-Shot manifest dictionary
      sequenceShotManifest = {}

      # Make this all undo-able in a single Group undo
      with proj.beginUndo("Update All Versions for %s" % currentClip.name()):
        for shot in trackItems:
          seq = shot.parentSequence()
          if seq not in sequenceShotManifest.keys():
            sequenceShotManifest[seq] = [shot]
          else:
            sequenceShotManifest[seq]+=[shot]                    
          shot.setCurrentVersion(version)

        # We also should update the current Version of the selected Clip for completeness...
        currentClip.binItem().setActiveVersion(version)

      # Now disaplay a Dialog which informs the user of where and what was changed
      self.showVersionUpdateReportFromShotManifest(sequenceShotManifest)
    
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

    # We could have a mixture of Bins and Clips selected, so s
    clipItems = [item.activeItem() for item in selection if hasattr(item, "activeItem") and isinstance(item.activeItem(),hiero.core.Clip)]

    # We'll also append Bins here, and see if can find Clips inside
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
  def createVersionEveryWhereMenuForView(self, view):

    versionEverywhereMenu = QMenu(self.actionTitle)
    self._versionActions = []
    if isinstance(view,hiero.ui.BinView):
      # We look to the activeView for a selection of Clips
      clips = self.clipSelectionForActiveView()

      
      # And bail if nothing is found
      if len(clips)==0:
        return versionEverywhereMenu

      # Now, if we have just one Clip selected, we'll form a special menu, which lists all versions
      if len(clips)==1:

        # Get a reversed list of Versions, so that bigger ones appear at top
        versions = list(reversed(clips[0].binItem().items()))
        for version in versions:
          self._versionActions+=[self.makeVersionActionForSingleClip(version)]

      elif len(clips)>1:
        # We will add Max/Min/Prev/Next options, which can be called on a TrackItem, without the need for a Version object
        self._versionActions+=[self.makeAction(self.eMaxVersion,self.setTrackItemVersionForClipSelection, icon=None)]
        self._versionActions+=[self.makeAction(self.eMinVersion,self.setTrackItemVersionForClipSelection, icon=None)]
        self._versionActions+=[self.makeAction(self.eNextVersion,self.setTrackItemVersionForClipSelection, icon=None)]
        self._versionActions+=[self.makeAction(self.ePreviousVersion,self.setTrackItemVersionForClipSelection, icon=None)]

    elif isinstance(view,hiero.ui.TimelineEditor):
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

    # Create a Sequence-Shot Manifest, to report to users where a Shot was updated
    sequenceShotManifest = {}

    with proj.beginUndo("Update multiple Versions"):
      for clip in clipSelection:
        
        # Look to see if it exists in a TrackItem somewhere...
        shotUsage = clip.whereAmI('TrackItem')
              
        # Next, depending on the versionOption, make the appropriate update
        # There's probably a more neat/compact way of doing this...
        for shot in shotUsage:

          # This step is done for reporting reasons
          seq = shot.parentSequence()
          if seq not in sequenceShotManifest.keys():
            sequenceShotManifest[seq] = [shot]
          else:
            sequenceShotManifest[seq]+=[shot]

          if versionOption == self.eMaxVersion:
            shot.maxVersion()
          elif versionOption == self.eMinVersion:
            shot.minVersion()
          elif versionOption == self.eNextVersion:
            shot.nextVersion()
          elif versionOption == self.ePreviousVersion:
            shot.prevVersion()

      # Finally, for completeness, set the Max/Min version of the Clip too (if chosen)
      # Note: It doesn't make sense to do Next/Prev on a Clip here because next/prev means different things for different Shots
      if versionOption == self.eMaxVersion:
        clip.binItem().maxVersion()
      elif versionOption == self.eMinVersion:
        clip.binItem().minVersion()

    # Now disaplay a Dialog which informs the user of where and what was changed
    self.showVersionUpdateReportFromShotManifest(sequenceShotManifest)

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

    view = hiero.ui.activeView()
    print 'VIEW IS: ' + str(view)
    # Only add the Menu if Bins or Sequences are selected (this ensures menu isn't added in the Tags Pane)
    # To-Do: Do the same for the Timeline and Spreadsheet Views...
    if len(selection) > 0:
      self._versionEverywhereMenu = self.createVersionEveryWhereMenuForView(view)
      
      # Insert the Tags menu with the Localisation Menu
      hiero.ui.insertMenuAction(self._versionEverywhereMenu.menuAction(), event.menu, after="foundry.menu.version")
    return


# Instantiate the Menu to get it to register itself.
VersionAllMenu = VersionAllMenu()