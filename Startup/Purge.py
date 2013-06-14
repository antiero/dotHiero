# Purge Menu
# Adds a Purge Menu to the right-click Menu of the Project view with the following actions:
# 1) Purge > Unused Clips - removes any Clips from a Project, not used in a Sequence
# 2) Purge > Offline Clips - removes any Clips whose MediaSource is currently oFfline
# 3) Purge > Empty Bins - removes any Bins that contain no Clips or Sequences
# Usage: Copy to ~/.hiero/Python/StartupUI
# Demonstrates the use of hiero.core.find_items module.
# Requires Hiero 1.5v1 or later.

import hiero.core
import hiero.ui
import PySide.QtGui
import PySide.QtCore

# Method to return whether a Bin is empty...
def binIsEmpty(b):
  numBinItems = 0
  bItems = b.items()
  empty = False

  if len(bItems) == 0:
    empty = True
    return empty
  else:
    for b in bItems:
      if isinstance(b,hiero.core.BinItem) or isinstance(b,hiero.core.Bin):
        numBinItems+=1
    if numBinItems == 0:
      empty = True

  return empty


# This is just a convenience method for returning QActions with a title, triggered method and icon.
def createMenuAction(title, method, icon = None ):
  action = PySide.QtGui.QAction(title,None)
  if icon:
    action.setIcon(QIcon(icon))
  action.triggered.connect( method )
  return action

class PurgeMenu:

  def __init__(self):
      self._purgeMenu =  PySide.QtGui.QMenu("Purge")
      self._purgeMenu.setIcon(PySide.QtGui.QIcon('icons:TagDelete.png'))
      self._removeUnusedAction = createMenuAction("Unused Clips...", self.removeUnusedClips)
      self._removeOfflineMediaAction = createMenuAction("Offline Clips...", self.removeOfflineClips)
      self._removeEmptyBinsAction = createMenuAction("Empty Bins...", self.removeEmptyBins)
      self._purgeMenu.addAction(self._removeUnusedAction)
      self._purgeMenu.addAction(self._removeOfflineMediaAction)
      self._purgeMenu.addAction(self._removeEmptyBinsAction)      
      hiero.core.events.registerInterest("kShowContextMenu/kBin", self.eventHandler)

  # Method to remove Clips which are unused in any Sequences in the active Project
  def removeUnusedClips(self) :
  
    #Get selected items
    item = self.selectedItem
    proj = item.project() 
    
    # Build a list of Projects
    SEQS = hiero.core.findItems(proj,"Sequences")
    # Build a list of Clips
    CLIPSTOREMOVE = hiero.core.findItems(proj,"Clips")
    
    # For each sequence, iterate through each track Item, see if the Clip is in the CLIPS list.
    # Remaining items in CLIPS will be removed
        
    for seq in SEQS:
      #Loop through selected and make folders
      for track in seq:
        for trackitem in track:
          if trackitem.source() in CLIPSTOREMOVE:
            CLIPSTOREMOVE.remove(trackitem.source())
    
    # If there are no Clips to remove, return
    if len(CLIPSTOREMOVE)==0:
      return
  
    # Present Dialog Asking if User wants to remove Clips
    msgBox = PySide.QtGui.QMessageBox()
    msgBox.setWindowTitle("Remove Unused Clips");
    msgBox.setText("Remove %i unused Clips from Project %s?" % (len(CLIPSTOREMOVE),proj.name()));
    msgBox.setDetailedText("Remove:\n %s" % (str(CLIPSTOREMOVE)));
    msgBox.setStandardButtons(PySide.QtGui.QMessageBox.Ok | PySide.QtGui.QMessageBox.Cancel);
    msgBox.setDefaultButton(PySide.QtGui.QMessageBox.Ok);
    ret = msgBox.exec_()
  
    if ret == PySide.QtGui.QMessageBox.Cancel:
       return
    elif ret == PySide.QtGui.QMessageBox.Ok:
      BINS = []
      with proj.beginUndo('Remove Unused Clips'):
        # Delete the rest of the Clips
        for clip in CLIPSTOREMOVE:
          BI = clip.binItem()
          B = BI.parentBin()
          BINS+=[B]
          B.removeItem(BI)

    return
    
  # Removes any Empty Bins from a Project
  def removeEmptyBins(self) :
  
    #Get selected items
    item = self.selectedItem
    proj = item.project()
    allBinsEmpty = 0
    while allBinsEmpty == 0:
      BINS = hiero.core.findItems(proj,hiero.core.Bin)
      numEmpty = 0
      for b in BINS:
        if binIsEmpty(b):
          B = b.parentBin()
          B.removeItem(b)
          numEmpty=+1
      if numEmpty == 0:
        allBinsEmpty = 1
      else:
        allBinsEmpty = 0
    return
     
  # Removes any Clips whose MediaSource is offline
  def removeOfflineClips(self) :
  
    #Get selected items
    item = self.selectedItem
    proj = item.project() 
    
    # Build a list of Projects
    SEQS = hiero.core.findItems(proj,"Sequences")
    # Build a list of Clips
    CLIPSTOREMOVE = hiero.core.findItems(proj,"Clips")
    
    # For each sequence, iterate through each track Item, see if the Clip is in the CLIPS list.
    # Remaining items in CLIPS will be removed
    
    for clip in CLIPSTOREMOVE:
      if clip.mediaSource().isMediaPresent():
        CLIPSTOREMOVE.remove(clip)
  
    # If there are no Clips to remove, return
    if len(CLIPSTOREMOVE)==0:
      return
      
    # Present Dialog Asking if User wants to remove Clips
    msgBox = PySide.QtGui.QMessageBox()
    msgBox.setWindowTitle("Remove Offline Clips");
    msgBox.setText("Remove %i Offline Clips from Project %s?" % (len(CLIPSTOREMOVE),proj.name()));
    msgBox.setDetailedText("Remove:\n %s" % (str(CLIPSTOREMOVE)));
    msgBox.setStandardButtons(PySide.QtGui.QMessageBox.Ok | PySide.QtGui.QMessageBox.Cancel);
    msgBox.setDefaultButton(PySide.QtGui.QMessageBox.Ok);
    ret = msgBox.exec_()
  
    if ret == PySide.QtGui.QMessageBox.Cancel:
       return
    elif ret == PySide.QtGui.QMessageBox.Ok:
      BINS = []
      with proj.beginUndo('Remove Offline Clips'):
        # Delete the rest of the Clips
        for clip in CLIPSTOREMOVE:
          BI = clip.binItem()
          B = BI.parentBin()
          BINS+=[B]
          B.removeItem(BI)
      
    return

  def eventHandler(self, event):
    if not hasattr(event.sender, 'selection'):
        # Something has gone wrong, we shouldn't only be here if raised
        # by the Bin view which will give a selection.
        return
    
    self.selectedItem = None
    s = event.sender.selection()
    
    if len(s)>=1:
      self.selectedItem = s[0]
      
      # Only add the menu if the Item has a 'project()' method to return its project
      if hasattr(self.selectedItem,'project'):
        hiero.ui.insertMenuAction(self._purgeMenu.menuAction(), event.menu)
        
    return

# Add the Purge Menu
PurgeUnusedAction = PurgeMenu()
