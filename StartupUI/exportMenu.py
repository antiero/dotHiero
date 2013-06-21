import hiero.exporters
import hiero.core
import hiero.ui
from PySide import QtGui, QtCore

# This is just a convenience method for returning QActions with a title, triggered method and icon.
def createMenuAction(title, method, icon = None ):
  action = QtGui.QAction(title,None)
  action.setIcon(QtGui.QIcon(icon))
  action.triggered.connect( method )
  return action

class ExportersMenu:

  def __init__(self):
    self.data = []
    # Preset Registry
    self.reg = hiero.exporters.registry
    self.localPresets = self.reg.localPresets()

    projects = hiero.core.projects()
    self.projectPresets = []
    for proj in projects:
      self.projectPresets+=[self.reg.projectPresets(proj)]

    self.presets = self.projectPresets+self.localPresets
    self._actions = []
    self.rootMenu = self.createExportMenu()

  def _addAction(self, action, menu):
    self._actions.append(action)
    menu.addAction(action)

  def createExportMenu(self):
    rootMenu = QtGui.QMenu("Quick Export")
    binProcessorsMenu = QtGui.QMenu("Process as Clips")
    timelineProcessorsMenu = QtGui.QMenu("Process as Sequence")
    shotProcessorsMenu = QtGui.QMenu("Process as Shots")

    for preset in self.presets:
      if isinstance(preset,hiero.exporters.FnBinProcessor.BinProcessorPreset):
        
        act = QtGui.QAction(QtGui.QIcon('icons:Bin.png'),unicode(preset._name),None)
        print 'Adding Bin Processor with name: ' + preset._name
        self._addAction(act,binProcessorsMenu)
      elif isinstance(preset,hiero.exporters.FnTimelineProcessor.TimelineProcessorPreset):
        print 'Adding Timeline Processor with name: ' + preset._name
        act = QtGui.QAction(QtGui.QIcon('icons:TimelineStroked.png'),unicode(preset._name),None)
        self._addAction(act,timelineProcessorsMenu)
      elif isinstance(preset,hiero.exporters.FnShotProcessor.ShotProcessorPreset):
        print 'Adding shotProcessorsMenu Processor with name: ' + preset._name
        act = QtGui.QAction(QtGui.QIcon('icons:CompareSideBySide.png'),unicode(preset._name),None)
        self._addAction(act,shotProcessorsMenu)

    rootMenu.addMenu(timelineProcessorsMenu)
    rootMenu.addMenu(binProcessorsMenu)
    rootMenu.addMenu(shotProcessorsMenu)    
    return rootMenu


print 'Adding ExportersMenu to Edit menu'
exportersMenu = ExportersMenu()
fileMenu = hiero.ui.findMenuAction("foundry.menu.edit")
fileMenu.menu().addMenu(exportersMenu.rootMenu)