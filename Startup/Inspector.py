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
    self.thumbnailImage = QLabel("")
    self.scn = QGraphicsScene()
    self.thumbView = QGraphicsView(self.scn)
    #self.thumbView.setFixedWidth( 128 );
    self.thumbView.setFixedHeight( 128 );
    self.thumbView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.thumbView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    self.thumbView.ensureVisible ( self.scn.sceneRect() );
    self.thumbView.fitInView( self.scn.sceneRect(), Qt.KeepAspectRatio)    

    self.pixmap = QPixmap("/Users/ant/Downloads/icon128.png")
    self.gfxPixItem = self.scn.addPixmap(self.pixmap)

    self.thumbView.fitInView(self.gfxPixItem)
    
    self.formLayout = QFormLayout(self)

    self.shotNameLabel  = QLabel("")
    self.inTimeLabel  = QLabel("")
    self.outTimeLabel  = QLabel("")
    self.durationLabel  = QLabel("")
    self.handlesLabel  = QLabel("")
    
    self.formLayout.addRow("",self.thumbView)     
    #self.formLayout.addRow("",self.thumbnailImage)
    self.formLayout.addRow("Name:",self.shotNameLabel)
    self.formLayout.addRow("In Time:",self.inTimeLabel)
    self.formLayout.addRow("Out Time:",self.outTimeLabel)
    self.formLayout.addRow("Duration:",self.durationLabel)
    self.formLayout.addRow("Handles:",self.handlesLabel)
  
  def getThumbnail(self):  
    imageView = None
    item = self.currentSelection[0]

    if item.mediaType() == hiero.core.TrackItem.MediaType.kAudio:
      imageView = QImage("icons:AudioOnly.png")
      painter.fillRect(r, QColor(45, 59,45))
    
    if not imageView:
      try:
        imageView = item.source().thumbnail()
      except:
        imageView  = QImage("icons:Offline.png")
    
    return imageView
    
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
      toClear = self.scn.items()
      for item in toClear:
        self.scn.removeItem(item)
      self.scn.addPixmap(QPixmap.fromImage(self.getThumbnail()))
      self.thumbView.fitInView( self.scn.sceneRect(), Qt.KeepAspectRatio)
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