from hiero.core import *
from hiero.ui import *
from PySide.QtGui import *
from PySide.QtCore import *

class FrameToolAction:
  def __init__(self):
      self._frameToolShowAction = self.createMenuAction("Shot Tool", self.doit)
      hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)


  # This is just a convenience method for returning QActions with a title and a triggered method
  def createMenuAction(self, title, method):
    action = QAction(title,None)
    action.triggered.connect( method )
    return action

  class FrameToolDialog(QDialog):

    def __init__(self, parent=None):
      super(FrameToolAction.FrameToolDialog, self).__init__(parent)
      self.setWindowTitle("Shot Tool")
      layout = QGridLayout()
      self.setLayout(layout)
      self.appSettings  = hiero.core.ApplicationSettings()

      label = QLabel("What would you like to do?\n")
      layout.addWidget(label, 0,0)

      self._trimExtendButton = QRadioButton("Trim")
      self._trimExtendButton.setToolTip('Trim/Extend frames off the Head/Tail of a Shot. Positive value trims frames, negative extends.')
      self._trimExtendheadTailDropdown = QComboBox()
      self._trimExtendheadTailDropdown.addItem('Head+Tail')
      self._trimExtendheadTailDropdown.addItem('Head')
      self._trimExtendheadTailDropdown.addItem('Tail')

      self._frameInc = QSpinBox()
      self._frameInc.setMinimum(-1e9)
      self._frameInc.setMaximum(1e9)
      self._frameInc.setValue(int(self.getFrameIncDefault()))

      layout.addWidget( self._trimExtendButton, 1,0 )
      layout.addWidget( self._trimExtendheadTailDropdown, 1,1 )

      self._moveButton = QRadioButton("Move")
      self._moveButton.setToolTip('Move Shots forwards (+) or backwards (-) by X number of frames.')
      layout.addWidget( self._moveButton, 2,0 )

      self._slipButton = QRadioButton("Slip")
      self._slipButton.setToolTip('Slip Shots forwards (+) or backwards (-) by X number of frames.')
      layout.addWidget( self._slipButton, 3,0 )

      label = QLabel("By this many frames:")
      layout.addWidget(label, 4,0)
      layout.addWidget( self._frameInc, 4,1 )

      self._trimExtendButton.setChecked(True)
      self._trimExtendheadTailDropdown.setEnabled(True)

      self._trimExtendButton.clicked.connect(self.radioButtonClicked)
      self._moveButton.clicked.connect(self.radioButtonClicked)
      self._slipButton.clicked.connect(self.radioButtonClicked)

      buttonBox = QDialogButtonBox( QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel )
      buttonBox.accepted.connect( self.accept )
      buttonBox.rejected.connect( self.reject )
      layout.addWidget( buttonBox )

    def radioButtonClicked(self):
      if self._trimExtendButton.isChecked():
        self._trimExtendheadTailDropdown.setEnabled(True)
      elif self._moveButton.isChecked():
        self._trimExtendheadTailDropdown.setEnabled(False)

      elif self._slipButton.isChecked():
        self._trimExtendheadTailDropdown.setEnabled(False)

    def selectedAction(self):
      if self._trimButton.isChecked():
        return FrameToolDialog.kTrim,
      elif self._moveButton.isChecked():
        return FrameToolDialog.kMove
      elif self._slipButton.isChecked():
        return FrameToolDialog.kSlip
      else:
        return FrameToolDialog.kExtend

    def getFrameIncDefault(self):
      frameInc = self.appSettings.value('Sequence/frame_increment')
      if frameInc == "":
        frameInc = 12
      return frameInc

    def setFrameIncPreference(self):
      self.appSettings.setValue('Sequence/frame_increment',str(self._frameInc.value()))

  def doitGetSelection(self):

    self.selectedTrackItems = []
    view = hiero.ui.activeView()
    if not view:
      return
    if not hasattr(view,'selection'):
      return

    s = view.selection()
    if s is None:
      return

    # Ignore transitions from the selection
    self.selectedTrackItems = [item for item in s if isinstance(item, hiero.core.TrackItem)]
    if not self.selectedTrackItems:
      return

    self.doit()

  def doit(self):
    d = self.FrameToolDialog()
    if d.exec_():
      frames = d._frameInc.value()
      # Update this preference...
      d.setFrameIncPreference()
      if d._trimExtendButton.isChecked():
        headTailOpt = d._trimExtendheadTailDropdown.currentText()
        self.trimExtendSelection(frames, headTail = headTailOpt)

      elif d._moveButton.isChecked():
        self.moveSelection(frames)
      elif d._slipButton.isChecked():
          self.slipSelection(frames)

  def trimExtendSelection(self, frames, headTail = 'Head+Tail'):
    p = self.selectedTrackItems[0].project()
    p.beginUndo('Trim Selection')
    print 'frames value is: ', str(frames)
    if headTail == 'Head+Tail':
      for t in self.selectedTrackItems:
        t.trimIn(frames)
        t.trimOut(frames)
        #t.move(-frames)

    elif headTail == 'Head':
      for t in self.selectedTrackItems:
        t.trimIn(frames)
        #t.move(-frames)
    elif headTail == 'Tail':
      for t in self.selectedTrackItems:
        t.trimOut(frames)
        #t.move(-frames)
    p.endUndo()

  def moveSelection(self, frames):
    p = self.selectedTrackItems[0].project()
    p.beginUndo('Move Selection')
    for t in self.selectedTrackItems:
      t.move(frames)
    p.endUndo()

  def slipSelection(self, frames):
    p = self.selectedTrackItems[0].project()
    p.beginUndo('Slip Selection')
    for t in self.selectedTrackItems:
      t.setSourceIn(int(t.sourceIn())+(int(frames)))
      t.setSourceOut(int(t.sourceOut())+(int(frames)))
    p.endUndo()

  # This handes events from the Timeline
  def eventHandler(self, event):
    self.selectedTrackItems = []
    s = event.sender.selection()
    if len(s)>1:
      enabled = False
    enabled = True
    if s is None:
      s = () # We disable on empty selection.
      enabled = False
    else:
      # Ignore transitions from the selection
      self.selectedTrackItems = [item for item in s if isinstance(item, hiero.core.TrackItem)]

    self._frameToolShowAction.setEnabled(enabled)
    event.menu.addAction(self._frameToolShowAction)

# Add the Action
a = FrameToolAction()

# Grab Hiero's MenuBar
M = hiero.ui.menuBar()

# Add a Menu to the MenuBar
ToolsMenu = M.addMenu('Tools')
# Create a new QAction
showFrameToolDialogAction = a.createMenuAction('Shot Tool',a.doitGetSelection)
showFrameToolDialogAction.setShortcut(QKeySequence('Ctrl+Shift+X'))

# Add the Action to your Nuke Menu
ToolsMenu.addAction(showFrameToolDialogAction)
