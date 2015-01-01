# Looks Menu - Conveniently allow grade node presets to be saved/reused in a Project
# Allow Effects to be saved/restored within a Studio Project
# Right-click Effect > Save Look 
from PySide.QtGui import *
import hiero.core
import nuke
import re
import os
import uuid
import ast

class LookNameDialog(QDialog):
  def __init__(self):
    QDialog.__init__(self, parent=hiero.ui.mainWindow())

    self.setWindowTitle("Set Look Name")
    layout = QFormLayout()

    self._lookNameTextEdit = QLineEdit()
    self._lookNameTextEdit.setText("Grade")
    self._lookNameTextEdit.setToolTip('Enter name for Look.')
    layout.addRow("Enter Look Name: ", self._lookNameTextEdit)

    self._buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    self._buttonbox.button(QDialogButtonBox.Ok).setText("Save")
    self._buttonbox.accepted.connect(self.accept)
    self._buttonbox.rejected.connect(self.reject)
    layout.addRow("",self._buttonbox)

    self.setLayout(layout)
    
    # Set the focus to be the Note field
    self._lookNameTextEdit.setFocus()
    self._lookNameTextEdit.selectAll()

class LooksMenu(object):
  def __init__(self):
    self._saveLookAction = hiero.ui.createMenuAction("Save...", self.saveGradeAsLook, QIcon("File.png"))
    self._clearLooksAction = hiero.ui.createMenuAction("Clear Looks", self.clearLooksFromProject, QIcon("Delete.png"))
    self._lookNameDialog = LookNameDialog()

    # Get the .nuke Plugin path for saving thumbnails of Looks
    rootPluginPath = nuke.pluginPath()[0]
    self._thumbnailPath = os.path.join(rootPluginPath, "Looks", "thumbnails")

    hiero.core.events.registerInterest((hiero.core.events.EventType.kShowContextMenu, hiero.core.events.EventType.kTimeline), self.eventHandler)

  def getActiveProject(self):
    project = hiero.ui.activeSequence().project()
    return project

  def saveLookThumbnailToDisk(self):
    """Saves a Thumbnail of the look as shown in the Viewer at time of saving the look.
    Returns thumbnail .png name for use as Icon"""
    im = hiero.ui.currentViewer().image()

    # Get the .nuke Plugin path..
    rootPluginPath = nuke.pluginPath()[0]
    lookThumbnailPath = os.path.join(rootPluginPath, "Looks", "thumbnails")
    if not os.path.isdir(lookThumbnailPath):
      os.makedirs(lookThumbnailPath)

    thumbFileName = str(uuid.uuid4()) + ".png"

    pngSavePath = os.path.join(lookThumbnailPath, thumbFileName)
    if im.save( pngSavePath ):
      return thumbFileName
    else:
      return None

  def _buildLookMenu(self):
    """Builds a list of looks that can be restored, based on the 'Looks' Bin in the tags Project"""
    # Locate the 'Looks' tag Bin
    self._looksMenu = QMenu("Looks")
    self._looksMenu.addAction(self._saveLookAction)
    self._looksMenu.addAction(self._clearLooksAction)

    project = self.getActiveProject()
    self._restoreLookSubMenu = QMenu("Restore")
    looksTagBin = self.getLooksTagBinForProject(project)    
    tags = looksTagBin.items()

    self._tagActions = []
    for tag in tags:
      action = QAction(tag.name(), None)
      action.triggered.connect( lambda: self.addLookToActiveSelectionFromTag(tag) )
      self._tagActions+=[action]
    
    for act in self._tagActions:
      self._restoreLookSubMenu.addAction(act)

    self._looksMenu.addMenu(self._restoreLookSubMenu)
    
    return self._looksMenu    

  def addLookToActiveSelectionFromTag(self, lookTag):
    """Applies a Grade Look to the current selection"""
    
    selection = hiero.ui.activeView().selection()
    if len(selection)<1:
      return

    tagMetadata = lookTag.metadata()

    # We can only handle the following cases.. either:
    # 1 - Simple Case - Selection is a Grade node -> just reset the node and restore values
    gradeSoftEffects = self.getGradeEffectsFromSelection(selection)

    for grade in gradeSoftEffects:
      # For each soft effect, reset knobs to default, then set them...
      gradeNode = grade.node()
      gradeNode.resetKnobsToDefault()
    
      for key in tagMetadata.keys():
        # Get a literal eval value as this is stored as a string in the Tag...
        if key.startswith("tag.Grade."):
          knobName = key.replace("tag.Grade.", "")
          stringValue = ast.literal_eval(str(tagMetadata.value(key)))
          floatValues = map(float, stringValue)
          if len(floatValues)==1:
            floatValues=floatValues[0]

          gradeNode[knobName].setValue( floatValues )

  def showLookTextDialogForSoftEffect(self, effect):
    if self._lookNameDialog.exec_():
      tagName = self._lookNameDialog._lookNameTextEdit.text()
      nodeTag = self.createTagObjectForNode(effect.node(), tagName)
      self.addTagToProjectLooksBin(nodeTag, effect.project())

  def createTagObjectForNode(self, node, name):
    """Extracts node knob values and stores in metadata of a Tag"""
    tag = hiero.core.Tag(name)
    tagMetadata = tag.metadata()

    # Add a Metadata key to define this Tag as a Look Tag
    tagMetadata.setValue("tag.nodeClass", "Grade")
    knobValues = node.writeKnobs(nuke.WRITE_NON_DEFAULT_ONLY | nuke.TO_VALUE)

    # [knob1, value1, knob2, {value2}...]
    knobValueRawList = knobValues.split('\n')[1:]
    for knobPair in knobValueRawList:
      knobName = knobPair.split()[0]

      # raw = ['whitepoint {2 2 1.1 1}', 'white 0.55']
      values = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", knobPair)

      # Set this as a key in the Tag metadata collection prefix with tag.Grade.
      tagMetadata.setValue("tag.Grade."+knobName, str(values))

    # Save a Thumbnail of the Current Viewer - this 
    thumbnail = self.saveLookThumbnailToDisk()
    tag.setIcon(thumbnail)
    return tag

  def getGradeEffectsFromSelection(self, selection):
    gradeEffects = [item for item in selection if isinstance(item, hiero.core.SubTrackItem) and item.node().Class()=="Grade"]
    return gradeEffects

  def getLooksTagBinForProject(self, project):
    """Returns the 'Looks' Bin in which Look Tags are stored"""
    tagsBin = project.tagsBin()
    looksBin = hiero.core.findItemsInBin(tagsBin, hiero.core.Bin, "Looks")
    if len(looksBin)>=1:
      looksBin = looksBin[0]
    else:
      looksBin = hiero.core.Bin("Looks")
      tagsBin.addItem(looksBin)

    return looksBin

  def clearLooksFromProject(self):
    """Removes Looks from Project and thumbnails from ~/.nuke/Looks/thumbnail dir"""

    clearYesNo = nuke.ask("Are you sure you wish to clear all Project Looks and thumbnails?")

    if clearYesNo:
      project = hiero.ui.activeSequence().project()
      tagsBin = self.getLooksTagBinForProject(project)
      tagItems = tagsBin.items()
      for tag in tagItems:
        tagsBin.removeItem(tag)
        thumbnailPath = tag.icon()
        try:
          os.remove(thumbnailPath)
        except OSError:
          pass

  def addTagToProjectLooksBin(self, tag, project):
    looksBin = self.getLooksTagBinForProject(project)
    looksBin.addItem(tag)
    self.showTagsBin()

  def showTagsBin(self):
    # Show the Tags Panel
    tagsAction = hiero.ui.findMenuAction("Tags")
    tagsAction.trigger()

  def saveGradeAsLook(self):
    # Only support saving of a single Look
    view = hiero.ui.activeView()
    if not hasattr(view, "selection"):
      return

    selection = view.selection()
    gradeEffects = self.getGradeEffectsFromSelection(selection)

    if len(gradeEffects)==1:
      gradeEffects[0].node() 
      softEffect = gradeEffects[0]
      self.showLookTextDialogForSoftEffect(softEffect)
    else:
      return

  def eventHandler(self, event):
    view = hiero.ui.activeView()
    if not hasattr(view, "selection"):
      return

    selection = view.selection()
    # Only add the Menu if Bins or Sequences are selected (this ensures menu isn't added in the Tags Pane)
    if len(selection) > 0: 
      lookMenu = self._buildLookMenu()
      event.menu.addMenu(lookMenu)

lm = LooksMenu()