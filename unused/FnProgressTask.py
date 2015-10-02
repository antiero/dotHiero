from PySide import QtGui
from hiero.ui import mainWindow # Need this to work around OS X 'Start Dictation' Bug

class FnProgressTask(QtGui.QProgressDialog):
  """
  A modal progress bar dialog, which wraps QProgressDialog from PySide.QtGui.

  FnProgressTask( title = 'Progress', message = 'Progress...', parent = mainWindow(), showNow = True)

  @param title - the title of the progress dialog
  @param message - the task label of the progress dialog
  @param parent - the parent of the dialog (defaults to hiero.ui.mainWindow())
  @param showNow - a boolean, if True (default) shows dialog immediately after creation. If False, call show() later to show the dialog.

  setProgress(...)
     self.setProgress(x) -> None.
     x is integer, representing the current task progress

  setMessage(...)
     self.setMessage(s) -> None.
     
     sets the message for the progress task

  progress(...)
     self.setMessage(s) -> returns current progress value (default range 0-100).

  isCancelled(...)
     self.isCancelled() -> True if the user has requested the task to be cancelled.

  For more info, see: http://srinikom.github.io/pyside-docs/PySide/QtGui/QProgressDialog.html

  Note: On OS X 10.7 and above, 'parent' should be hiero.ui.mainWindow(), to avoid 'Start Dictation... messages!'"""

  def __init__(self, title = 'Progress', message = 'Progress...', parent = mainWindow(), showNow = True ):
    QtGui.QProgressDialog.__init__(self, parent)
    self.setWindowTitle(title) # The title of the modal progress window
    self.setMessage(message) # The task label displayed (PySide method is setLabelText)
    self.setAutoClose(False) # If you set this to True, the dialog will automatically close when the max value is reached
    self.setAutoReset(False) # If you set this to True, the progress will automatically reset when the max value is reached
    if showNow:
      self.show() # To match Nuke, shows the dialog when initialised. Alternatively, use showNow = False, as keyword argument, and call show() later.

  # Nuke-style method for setting the progress message label
  def setMessage(self,message):
    self.setLabelText(message)

  # Nuke-style method for setting the progress value
  def setProgress(self,value):
    self.setValue(value)

  # Returns the current progress value
  def progress(self):
    return self.value()

  # This is the Nuke way! Not sure how useful it is here, because Cancel closes the dialog
  def isCancelled(self):
    return self.wasCanceled()