# Give Me Python Selection
# This example adds a right-click Menu to the Timeline, Spreadsheet and Bin View for getting the current Selection
# After running this action, 'hiero.selectedItems' will store the selected items for use in the Script Editor.
# An Action is also added to the Edit Menu, with a keyboard shortcut of Ctrl/Cmd+Alt+C.
# By default in the Bin View, the selection will return the activeItem, i.e. the Clip or Sequence, rather than the BinItem.
# This behaviour can be overridden by changing kAlwaysReturnActiveItem = True to False
# This can be set dynamically in the Script editor via: hiero.plugins.getPythonSelection.SelectedShotAction.kAlwaysReturnActiveItem = False
# v1.3 - Antony Nasce, Oct 19th, 2013
# Install in ~/.hiero/Python/Startup

import hiero.core
import hiero.ui
from PySide.QtGui import QAction

class SelectedShotAction(QAction):
  kAlwaysReturnActiveItem = True # Change me to False if you want BinItems rather than Clips/Sequences in the BinView
  def __init__(self):
    QAction.__init__(self, "Get Python Selection", None)
    self.triggered.connect(self.getPythonSelection)
    hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
    hiero.core.events.registerInterest("kShowContextMenu/kBin", self.eventHandler)
    hiero.core.events.registerInterest("kShowContextMenu/kSpreadsheet", self.eventHandler)
    self.setShortcut("Ctrl+Alt+C")
    self._selection = ()

  def getPythonSelection(self):
    """Get the Python selection and stuff it in: hiero.selectedItems"""
    self.updateActiveViewSelection()
    
    print "Python selection stored in: hiero.selectedItems:\n", self._selection
    hiero.selectedItems = self._selection
  
  def updateActiveViewSelection(self):
    view = hiero.ui.activeView()

    if hasattr(view, 'selection'):
      selection = view.selection()

      # If we're in the BinView, we pretty much always want the activeItem, so whack that in...
      if isinstance(view,hiero.ui.BinView):
        if self.kAlwaysReturnActiveItem:
          self._selection = [(item.activeItem() if hasattr(item,'activeItem') else item) for item in selection]
          
          # We  special case when a Project is selected, as the default selection method returns a Bin('Sequences') item, not a Project.
          indices_to_replace = [i for i, item in enumerate(self._selection) if (hasattr(item,'parentBin') and isinstance(item.parentBin(), hiero.core.Project))]
          for ix in indices_to_replace:
            self._selection[ix] = self._selection[ix].parentBin()

        else:
          self._selection = selection

      elif isinstance(view,(hiero.ui.TimelineEditor, hiero.ui.SpreadsheetView)):
          self._selection = selection

      # Finally, if there is only one item selected, don't bother returning a tuple, just that item
      if len(self._selection)==1:
        self._selection = self._selection[0]

  def eventHandler(self, event):
    self._selection = () # Clear the curent selection

    # Add the Menu to the right-click menu
    event.menu.addAction( self )

# The act of initialising the action adds it to the right-click menu...
SelectedShotAction = SelectedShotAction()

# And to enable the Ctrl/Cmd+Alt+C, add it to the Menu bar Edit menu...
editMenu = hiero.ui.findMenuAction("Edit")
editMenu.menu().addAction(SelectedShotAction)