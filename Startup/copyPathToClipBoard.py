# copyPathToClipBoard.py
# This example adds a right-click Menu to the Timeline, Spreadsheet and Bin View for Copying the Clip media paths of the current selected items
# After running this action, 'hiero.selectedClipPaths' will store the selected items for use in the Script Editor.
# Paths will be copied to the system Clip board so you can paste with Ctrl/Cmd+V
# Action is added to the Edit Menu, with a keyboard shortcut of Ctrl/Cmd+Shift+Alt+C. (THE CLAW!)
# v1.0 - Antony Nasce, June 10th 2014
# Install in ~/.hiero/Python/StartupUI

import hiero.core
import hiero.ui
from PySide.QtGui import QAction, QApplication

def filePathFromClip(clip):
  """Convenience method to drill down from Clip > Mediasource to return file path as string"""
  try:
    file_path = clip.mediaSource().fileinfos()[0].filename()
  except:
    file_path = ""
  return file_path

class CopyPathToClipBoardAction(QAction):
  
  def __init__(self):
    QAction.__init__(self, "Copy Media Path(s) to Clipboard", None)
    self.triggered.connect(self.getPythonSelection)
    hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
    hiero.core.events.registerInterest("kShowContextMenu/kBin", self.eventHandler)
    hiero.core.events.registerInterest("kShowContextMenu/kSpreadsheet", self.eventHandler)
    self.setShortcut("Ctrl+Shift+Alt+C")
    self.setObjectName("foundry.menu.copypathstoclipboard")

  def getPythonSelection(self):
    """Get the Clip media path in the active View and stuff it in: hiero.selectedClipPaths"""
    selection = self.getClipPathsForActiveView()

    if selection:    
      hiero.selectedClipPaths = selection
      clipboard = QApplication.clipboard()
      clipboard.setText(str(hiero.selectedClipPaths))
      print "Clip media path selection copied to Clipboard and stored in: hiero.selectedClipPaths:\n", selection      
  
  def getClipPathsForActiveView(self):
    view = hiero.ui.activeView()
    selection = None
    if hasattr(view, 'selection'):
      selection = view.selection()

      # If we're in the BinView, the selection is always a BinItem. The Clips are accessed via 'activeItem'
      if isinstance(view,hiero.ui.BinView):

        selection = [ filePathFromClip( item.activeItem() ) for item in selection if hasattr(item, 'activeItem') and isinstance( item.activeItem(), hiero.core.Clip) ]

      # If we're in the Timeline/Spreadsheet, the selection we're after is a TrackItem. The Clips are accessed via 'source'
      elif isinstance(view,(hiero.ui.TimelineEditor, hiero.ui.SpreadsheetView)):
          selection = [ filePathFromClip( item.source() ) for item in selection if hasattr( item, 'source' ) and isinstance( item, hiero.core.TrackItem) ]

      # If there is only one item selected, don't bother returning a list, just that item
      if len(selection)==1:
        selection = selection[0]
    
    return selection

  def eventHandler(self, event):
    if not hasattr(event.sender, 'selection'):
      return

    # Add the Menu to the right-click menu
    event.menu.addAction( self )

# The act of initialising the action adds it to the right-click menu...
CopyPathToClipBoardAction = CopyPathToClipBoardAction()

# And to enable the Ctrl/Cmd+Alt+C, add it to the Menu bar Edit menu...
editMenu = hiero.ui.findMenuAction("Edit")
editMenu.menu().addAction(CopyPathToClipBoardAction)