import hiero.core
import hiero.ui
from PySide.QtGui import *
from PySide.QtCore import *

class InspectorDialog(QWidget):
  
  def __init__(self):
    QWidget.__init__( self )

    self.currentSelection = None
    hiero.core.events.registerInterest('kSelectionChanged/kTimeline',self.updateSelection)
    hiero.core.events.registerInterest('kSelectionChanged/kSpreadsheet',self.updateSelection)
    self.initUI()

  def initUI(self):
    self.setWindowTitle( "Inspector" )
    self.setWindowIcon(QIcon("icons:TabMetadata.png"))

    self.formLayout = QFormLayout(self)
    self.shotNameLabel  = QLabel("")
    self.inTimeLabel  = QLabel("")
    self.outTimeLabel  = QLabel("")
    self.durationLabel  = QLabel("")
    self.handlesLabel  = QLabel("")
    self.formLayout.addRow("Name:",self.shotNameLabel)
    self.formLayout.addRow("In Time:",self.inTimeLabel)
    self.formLayout.addRow("Out Time:",self.outTimeLabel)
    self.formLayout.addRow("Duration:",self.durationLabel)
    self.formLayout.addRow("Handles:",self.handlesLabel)
  
    
  def updateSelection(self, event):
    self.currentSelection = event.sender.selection()

    self.updateInspectorUI()

  def clearInspectorUI(self):
    for widget in self.uiWidgets:
      widget.setValue(None)

  def updateInspectorUI(self):
    if len(self.currentSelection)==0:
      return
    if len(self.currentSelection)==1:
      self.shotNameLabel.setText(self.currentSelection[0].name())
      self.inTimeLabel.setText(str(self.currentSelection[0].timelineIn()))
      self.outTimeLabel.setText(str(self.currentSelection[0].timelineOut()))
      self.durationLabel.setText(str(self.currentSelection[0].duration()))
      handleIn = self.currentSelection[0].handleInLength()
      handleOut = self.currentSelection[0].handleOutLength()
      handles = abs(handleOut)+abs(handleIn)
      self.handlesLabel.setText('(%i)-%i-(%i)' % (handleIn,handles,handleOut))

# Create the widget and add to the Window menu
inspector = InspectorDialog()
wm = hiero.ui.windowManager()
wm.addWindow( inspector )