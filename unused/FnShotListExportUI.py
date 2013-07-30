# Copyright (c) 2011 The Foundry Visionmongers Ltd.  All Rights Reserved.

import PySide.QtCore
import PySide.QtGui

import hiero.ui
import FnShotListExportTask


class ShotListExportUI(hiero.ui.TaskUIBase):
  def __init__(self, preset):
    """Initialize"""
    hiero.ui.TaskUIBase.__init__(self, FnShotListExportTask.ShotListExportTask, preset, "Spreadsheet CSV Exporter")

  def populateUI(self, widget, exportTemplate):
    if exportTemplate:
      self._exportTemplate = exportTemplate
      self._uiProperties = []
      
      self._layout = PySide.QtGui.QFormLayout()
      
      # create checkbox for each Spreadsheet Column
      for datadict in FnShotListExportTask.ShotListExportTask.csvPropertyData:
        uiProperty = hiero.ui.UIPropertyFactory.create(type(datadict["value"]), key=datadict["knobName"], value=datadict["value"], dictionary=self._preset.properties()["csvData"], label=datadict["title"])
        self._uiProperties.append(uiProperty)
        self._layout.addRow(datadict["title"], uiProperty)

      widget.setLayout(self._layout)

hiero.ui.taskUIRegistry.registerTaskUI(FnShotListExportTask.ShotListExportPreset, ShotListExportUI)
