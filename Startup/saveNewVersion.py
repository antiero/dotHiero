from hiero.core import *
from hiero.ui import *
from PySide.QtGui import *
from PySide.QtCore import *
from hiero.core.util import *

# For projects with v# in the path name, saves out a new Project with v#+1
class SaveNewProjectVersion(QAction):

  def __init__(self):
    QAction.__init__(self, "Save New Version...", None)
    self.triggered.connect(self.saveNewVersion)
    hiero.core.events.registerInterest("kShowContextMenu/kBin", self.eventHandler)
    self.selection = None

  def saveNewVersion(self):
    if len(self.selectedProjects) is not None:
      for proj in self.selectedProjects:
        oldName = proj.name()
        path = proj.path()
        v = None
        prefix = None
        try:
          (prefix,v) = version_get(path,'v')
        except ValueError, msg:
          print msg

        if (prefix is not None) and (v is not None):
          v = int(v)
          newPath = version_set(path,prefix,v,v+1)
          try:
            proj.saveAs(newPath)
            print 'Saved new project version: %s to: %s ' % (oldName,newPath)
          except:
            print 'Unable to save Project: %s. Check file permissions.' % (oldName)
        else:
          print 'Project: ',proj, ' does not contain a version string (v#)'

  def eventHandler(self, event):
    self.selection = None
    if hasattr(event.sender, 'selection') and event.sender.selection() is not None and len( event.sender.selection() ) != 0:
      selection = event.sender.selection()
      self.selectedProjects = uniquify([item.project() for item in selection])
      event.menu.addAction( self )

act = SaveNewProjectVersion()