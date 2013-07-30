import sys

if sys.platform == 'darwin':
  sys.path.append('/Library/Python/2.7/site-packages')
else:
  # Linux, Windows Paths...
  sys.path.append('/Library/Python/2.7/site-packages')

__author__ = 'Ant'
from images2gif import writeGif
from PIL import Image
import os, cStringIO

flagRootPath = '/Users/ant/workspace/Apps/Hiero/Hiero/src/Application/UI/Resources/Images/flags'
file_names = sorted((os.path.join(flagRootPath,fn) for fn in os.listdir(flagRootPath) if fn.endswith('.png')))

images = [Image.open(fn) for fn in file_names]

#print writeGif.__doc__
# writeGif(filename, images, duration=0.1, loops=0, dither=1)
#    Write an animated gif from the specified images.
#    images should be a list of numpy arrays of PIL images.
#    Numpy images of type float should have pixels between 0 and 1.
#    Numpy images of other types are expected to have values between 0 and 255.


#images.extend(reversed(images)) #infinit loop will go backwards and forwards.

#filename = "/tmp/my_gif.GIF"
#writeGif(filename, images, duration=0.2)

import hiero.core
import hiero.ui
import PySide.QtGui
import PySide.QtCore

import sys
from PySide import QtGui, QtCore

class RenderPreviewDialog(QtGui.QWidget):
    
    def __init__(self):
        super(RenderPreviewDialog, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        self.pixmap = QtGui.QPixmap("icons:TagHiero.png")

        self.lbl = PySide.QtGui.QLabel(self)
        self.lbl.setPixmap(self.pixmap)
        self.lbl.setScaledContents(True) 
        self.lbl.move(100, 5)       

        self.pbar = PySide.QtGui.QProgressBar(self)
        self.pbar.setGeometry(30, 80, 220, 20)

        self.btn = QtGui.QPushButton('Cancel', self)
        self.btn.move(100, 110)
        self.btn.clicked.connect(self.cancel)

        self.setGeometry(300, 300, 280, 140)
        self.setWindowTitle('Hiero Animated GIF Renderer')

        self.renderingEnabled = True
        

    def cancel(self):
      self.renderingEnabled = False

class MakeGifAction(PySide.QtGui.QAction):
  def __init__(self):
      PySide.QtGui.QAction.__init__(self, "Make Animated Gif", None)
      self._currentSequence = None
      self._inFrame = None
      self._outFrame = None
      self.renderPreview = RenderPreviewDialog()

      self.triggered.connect(self.doit)
      hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
      hiero.core.events.registerInterest("kShowContextMenu/kViewer", self.eventHandler)

  def doit(self):
    # remove any non-trackitem entries (ie transitions)
    if not self._currentSequence:
      return

    try:
      self._inFrame = self._currentSequence.inTime()
      self._outFrame = self._currentSequence.outTime()
      self._duration = self._outFrame - self._inFrame
      print 'Duration of In/Out is ' + str(self._duration)
    except:
      msgBox = PySide.QtGui.QMessageBox()
      msgBox.setText("Please set an In and Out point. (Frame Range is limited to 500 frames)")
      msgBox.exec_()
      return

    # Images for GIF...
    if hasattr(self._currentSequence,'thumbnail'):
      images = []
      self.renderPreview.show()

      count = 1
      for t in range(self._inFrame,self._outFrame):
        thumb = self._currentSequence.thumbnail(t)

        buffer = PySide.QtCore.QBuffer()
        buffer.open(PySide.QtCore.QIODevice.ReadWrite)
        thumb.save(buffer, "PNG")

        strio = cStringIO.StringIO()
        strio.write(buffer.data())
        buffer.close()
        strio.seek(0)
        images += [Image.open(strio)]

        progress = int(100.0*(float(count)/float(self._duration)))
        hiero.core.log.debug('Progress is: '+ str(progress))
        self.renderPreview.lbl.setPixmap(PySide.QtGui.QPixmap(thumb)) 

        self.renderPreview.pbar.setValue(progress)
        QtCore.QCoreApplication.processEvents()

        count+=1

        if not self.renderPreview.renderingEnabled:
          print 'Rendering Cancelled'
          self.renderPreview.hide()
          self.renderPreview.renderingEnabled = True
          return

    filename = "/tmp/my_gif.GIF"
    writeGif(filename, images, duration=0.2)
    self.renderPreview.hide()
    hiero.ui.revealInOSShell(filename)


  def eventHandler(self, event):
    # Check if this actions are not to be enabled
    activeView = hiero.ui.activeView()
    enabled = True
    if isinstance(activeView,hiero.ui.Viewer):
      print 'View is a Timeline'
    elif isinstance(activeView,hiero.ui.TimelineEditor):
      print 'View is a Timeline'

    cv = hiero.ui.currentViewer()
    p = cv.player()

    self._currentSequence = p.sequence()

    if not self._currentSequence:
      enabled = False

    title = "Make Animated Gif"
    self.setText(title)
    self.setEnabled(enabled)
    hiero.ui.insertMenuAction( self, event.menu )

# Instantiate the action to get it to register itself.
action = MakeGifAction()