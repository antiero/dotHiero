# nukeIcons - adds a hiero.core.nukeIconPath path to all you to use Nuke Icons in Menus etc.
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

hireo.core.nukeIconPath = os.path.join(PySide.QtGui.QApplication.applicationDirPath(),iconBit)

# Find the Action and set a Custom icon to the QACtion...
mc = hiero.ui.findMenuAction("hiero.project.export")
mc.setIcon(PySide.QtGui.QIcon(hireo.core.nukeIconPath+'/Write.png'))