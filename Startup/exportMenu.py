import hiero.exporters
import hiero.core
import hiero.ui
from PySide import QtGui, QtCore

class ExportPresetAction(QtGui.QAction):
  def __init__(self, title="Preset"):
    QtGui.QAction.__init__(self, title, None)

class ExportersMenu:

  def __init__(self):
    self.data = []
    # Preset Registry
    self._actions = []
    self.binProcessorsMenu = QtGui.QMenu("Process as Clips")
    self.timelineProcessorsMenu = QtGui.QMenu("Process as Sequence")
    self.shotProcessorsMenu = QtGui.QMenu("Process as Shots")
    
    self.rootMenu = self.createExportMenu()
    self.rootMenu.addMenu(self.timelineProcessorsMenu)
    self.rootMenu.addMenu(self.binProcessorsMenu)
    self.rootMenu.addMenu(self.shotProcessorsMenu)

  def _addAction(self, action, menu):
    self._actions.append(action)
    menu.addAction(action)

  def createExportMenu(self):
    rootMenu = QtGui.QMenu("Quick Export")
    self.reg = hiero.exporters.registry
    self.localPresets = self.reg.localPresets()
    #print 'Local Presets are: ' + str(self.localPresets)

    projects = hiero.core.projects()
    self.projectPresets = []
    for proj in projects:
      self.projectPresets+=[self.reg.projectPresets(proj)]

    self.presets = self.projectPresets+self.localPresets

    for preset in self.presets:
      if isinstance(preset,hiero.exporters.FnBinProcessor.BinProcessorPreset):
        #print 'Adding Bin Processor with name: ' + preset._name
        self._addAction(ExportPresetAction(title=preset._name), self.binProcessorsMenu)
      elif isinstance(preset,hiero.exporters.FnTimelineProcessor.TimelineProcessorPreset):
        #print 'Adding Timeline Processor with name: ' + preset._name
        self._addAction(ExportPresetAction(title=preset._name), self.timelineProcessorsMenu)
      elif isinstance(preset,hiero.exporters.FnShotProcessor.ShotProcessorPreset):
        #print 'Adding shotProcessorsMenu Processor with name: ' + preset._name
        self._addAction(ExportPresetAction(title=preset._name), self.shotProcessorsMenu)
    
    return rootMenu


def addExportMenu(event):
  #print 'Adding ExportersMenu to Edit menu'  
  exportersMenu = ExportersMenu()
  fileMenu = hiero.ui.findMenuAction("foundry.menu.edit")
  fileMenu.menu().addMenu(exportersMenu.rootMenu)

hiero.core.events.registerInterest('kStartup',addExportMenu)