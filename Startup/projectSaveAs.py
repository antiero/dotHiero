from hiero.core import *
from hiero.ui import *
from PySide.QtGui import *
from PySide.QtCore import *

import re

# Method to Save a new Version of the activeHrox Project
class SaveProjectAs(QAction):

  def __init__(self):
    QAction.__init__(self, "Save Project As...", None)
    self.triggered.connect(self.projectSaveAs)
    print 'registering Interest in the Bin View'
    hiero.core.events.registerInterest("kShowContextMenu/kBin", self.eventHandler)
    self.menu = QMenu('Project')


  def projectSaveAs(self):
    s = hiero.ui.activeView().selection()[0]
    p = s.project()
    projectSavePath = p.path()
    savePath,filter = QFileDialog.getSaveFileName(None,caption="Save Project As...",dir = projectSavePath, filter = "*.hrox")
    print 'Saving To ' + str(savePath)
    msgBox = QMessageBox()
    try:
      p.saveAs(str(savePath))
      msgBox.setText('Saved to: "%s"' % str(savePath))
    except:
      msgBox.setText('Unable to save to: "%s"' % str(savePath))

    msgBox.exec_()


  def eventHandler(self, event):
    if not hasattr(event.sender, 'selection'):
      # Something has gone wrong, we shouldn't only be here if raised
      # by the timeline view which will give a selection.
      return

    s = event.sender.selection()
    if s is None:
      s = () # We disable on empty selection.
    title = "Save Project As..."
    self.setText(title)
    self.menu.addAction(self)
    event.menu.addMenu(self.menu)

action = SaveProjectAs()
