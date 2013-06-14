# Copyright (c) 2011 The Foundry Visionmongers Ltd.  All Rights Reserved.

import PySide.QtCore
import PySide.QtGui

import hiero.ui
import FnShotListExportTask


class ShotListExportUI(hiero.ui.TaskUIBase):
  def __init__(self, preset):
    """Initialize"""
    hiero.ui.TaskUIBase.__init__(self, FnShotListExportTask.ShotListExportTask, preset, "ShotList Exporter")
    
  def absPathCheckboxChanged(self, state):
    # Slot to handle change of checkbox state
    self._preset.properties()["abspath"] = state == PySide.QtCore.Qt.Checked
  
  def truncateCheckboxChanged(self, state):
    # Slot to handle change of checkbox state
    self._preset.properties()["truncate"] = state == PySide.QtCore.Qt.Checked
  
  def populateUI(self, widget, exportTemplate):
    layout = PySide.QtGui.QFormLayout()
    widget.setLayout(layout)

    # create checkbox for whether the ShotList task should add Absolute Paths
    absPathCheckbox = PySide.QtGui.QCheckBox()
    absPathCheckbox.setCheckState(PySide.QtCore.Qt.Unchecked)
    if self._preset.properties()["abspath"]:
      absPathCheckbox.setCheckState(PySide.QtCore.Qt.Checked)    
    absPathCheckbox.stateChanged.connect(self.absPathCheckboxChanged)
    
    truncateCheckBox = PySide.QtGui.QCheckBox()
    truncateCheckBox.setCheckState(PySide.QtCore.Qt.Unchecked)
    if self._preset.properties()["truncate"]:
      truncateCheckBox.setCheckState(PySide.QtCore.Qt.Checked)    
    truncateCheckBox.stateChanged.connect(self.truncateCheckboxChanged)
    
    # Add Checkbox to layout
    layout.addRow("Include Absolute Path", absPathCheckbox)
    layout.addRow("Truncate Reel Name", truncateCheckBox)
 
    
hiero.ui.taskUIRegistry.registerTaskUI(FnShotListExportTask.ShotListExportPreset, ShotListExportUI)
