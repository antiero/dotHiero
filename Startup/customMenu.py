# customMenu - adds a Custom Icon to a QAction and picks out the HieroNuke Icons
import hiero.core
import PySide.QtCore
import PySide.QtGui
import os,sys,glob

PLATFORM = sys.platform
# Find the HieroNuke icons root path..
if PLATFORM == 'win32':
  iconBit = 'HieroNuke/plugins/icons/'
elif PLATFORM == 'darwin':
  iconBit = 'HieroNuke.app/Contents/MacOS/plugins/icons/'
elif PLATFORM == 'linux2':
  iconBit = 'HieroNuke/plugins/icons/'

NukeIconPath = os.path.join(PySide.QtGui.QApplication.applicationDirPath(),iconBit)

# Find the Action and set a Custom icon to the QACtion...
#mc = hiero.ui.findMenuAction("hiero.project.export")
#mc.setIcon(PySide.QtGui.QIcon(NukeIconPath+'/Write.png'))