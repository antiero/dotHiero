import os.path
import PySide.QtCore
import PySide.QtGui

import hiero.ui
import FnThumbnailExportTask


class ThumbnailExportUI(hiero.ui.TaskUIBase):

  kFirstFrame = "First"
  kMiddleFrame = "Middle"
  kLastFrame = "Last"
  kCustomFrame = "Custom"

  def __init__(self, preset):
    """Initialize"""
    hiero.ui.TaskUIBase.__init__(self, FnThumbnailExportTask.ThumbnailExportTask, preset, "Thumbnail Export")

  def formatComboBoxChanged(self):
    # Slot to handle change of thumbnail format combo change state
    value = self._formatComboBox.currentText()
    self._preset.properties()["format"] = unicode(value)
  
  def customOffsetTextChanged(self):
    # Slot to handle change of thumbnail format combo change state
    value = self._customFrameLineEdit.text()
    self._preset.properties()["customFrameOffset"] = unicode(value)

  def frameTypeComboBoxChanged(self, index):
    # Slot to handle change of thumbnail format combo change state
    
    value = self._frameTypeComboBox.currentText()
    if str(value) == self.kCustomFrame:
      self._customFrameLineEdit.setEnabled(True)
      self._preset.properties()["customFrameOffset"] = unicode(self._customFrameLineEdit.text())
    else:
      self._customFrameLineEdit.setEnabled(False)
    self._preset.properties()["frameType"] = unicode(value)    

  def thumbSizeComboBoxChanged(self):
    # Slot to handle change of thumbnail format combo change state
    
    value = self._thumbSizeComboBox.currentText()
    self._preset.properties()["thumbSize"] = unicode(value)

  def populateUI(self, widget, exportTemplate):
    layout = PySide.QtGui.QFormLayout()
    layout.setContentsMargins(9, 0, 9, 0)
    widget.setLayout(layout)

    # Thumb frame type layout
    thumbFrameLayout = PySide.QtGui.QHBoxLayout()
    self._frameTypeComboBox = PySide.QtGui.QComboBox()    
    self._frameTypeComboBox.setToolTip("Select a Frame to pick the thumbnail from")

    thumbFrameTypes = (self.kFirstFrame, self.kMiddleFrame, self.kLastFrame, self.kCustomFrame)
    for index, item in zip(range(0,len(thumbFrameTypes)), thumbFrameTypes):
      self._frameTypeComboBox.addItem(item)
      if item == str(self._preset.properties()["frameType"]):
        self._frameTypeComboBox.setCurrentIndex(index)

    self._frameTypeComboBox.setMaximumWidth(120);

    self._customFrameLineEdit = PySide.QtGui.QLineEdit()
    self._customFrameLineEdit.setEnabled(False)
    self._customFrameLineEdit.setToolTip("This is the frame offset from the first frame of the shot/sequence")
    self._customFrameLineEdit.setValidator(PySide.QtGui.QIntValidator())
    self._customFrameLineEdit.setMaximumWidth(80);
    self._customFrameLineEdit.setText(str(self._preset.properties()["customFrameOffset"]))

    thumbFrameLayout.addWidget(self._frameTypeComboBox, PySide.QtCore.Qt.AlignLeft)
    thumbFrameLayout.addWidget(self._customFrameLineEdit, PySide.QtCore.Qt.AlignLeft)
    #thumbFrameLayout.addStretch()

    # QImage save format type
    self._formatComboBox = PySide.QtGui.QComboBox()
    thumbFrameTypes = ("png", "jpg", "tiff", "bmp")
    for index, item in zip(range(0,len(thumbFrameTypes)), thumbFrameTypes):
      self._formatComboBox.addItem(item)
      if item == str(self._preset.properties()["format"]):
        self._formatComboBox.setCurrentIndex(index)

    self._formatComboBox.currentIndexChanged.connect(self.formatComboBoxChanged)
    

    # QImage save height
    self._thumbSizeComboBox = PySide.QtGui.QComboBox()
    self._thumbSizeComboBox.setToolTip("This is the maximum width of the thumbnail.\nLeave as Default or specify a max height in pixels.")
    thumbSizeTypes = ("Default","256","128", "64")
    for index, item in zip(range(0,len(thumbSizeTypes)), thumbSizeTypes):
      self._thumbSizeComboBox.addItem(item)
      if item == str(self._preset.properties()["thumbSize"]):
        self._thumbSizeComboBox.setCurrentIndex(index)

    self._thumbSizeComboBox.currentIndexChanged.connect(self.thumbSizeComboBoxChanged)
    self._frameTypeComboBox.currentIndexChanged.connect(self.frameTypeComboBoxChanged)
    self.frameTypeComboBoxChanged(0) # Trigger to make it set the enabled state correctly
    self._customFrameLineEdit.textChanged.connect(self.customOffsetTextChanged)
    
    layout.addRow("Thumbnail Frame:",thumbFrameLayout)
    layout.addRow("File Type:",self._formatComboBox)
    layout.addRow("Size:",self._thumbSizeComboBox)    

    
hiero.ui.taskUIRegistry.registerTaskUI(FnThumbnailExportTask.ThumbnailExportPreset, ThumbnailExportUI)