import PySide.QtCore
import PySide.QtGui
import hiero.ui
import math
from hiero.ui.TagsMenu import TagsMenu

class Pie(PySide.QtGui.QWidget):
  def __init__(self):
    PySide.QtGui.QWidget.__init__(self)
    self.setAttribute( PySide.QtCore.Qt.WA_TranslucentBackground, True )
    self.setWindowFlags( PySide.QtCore.Qt.Popup | PySide.QtCore.Qt.FramelessWindowHint )
    self.setMouseTracking(True)
    self._actions = []
    self._highlightAction = None
    self._layout = None
    self._lineWidth = 2

    font = PySide.QtGui.QFont()
    font.setPixelSize(16)
    self.setFont(font)
    self.tagsMenu = TagsMenu()
  
  def addAction(self, a):
    PySide.QtGui.QWidget.addAction(self, a)
    self._actions.append(a)
    self._layout = None

  def showAt(self, pos):
    self.__layoutActions()
    self.move(pos.x()-self.width()/2, pos.y()-self.height()/2)
    self.show()

  def paintEvent(self, e):
    self.__layoutActions()
    painter = PySide.QtGui.QPainter(self)
    painter.setRenderHint(PySide.QtGui.QPainter.Antialiasing, True)
#Debug:    painter.fillRect(self.rect(), PySide.QtGui.QColor(255, 127, 127, 64))
    painter.setPen( PySide.QtCore.Qt.white )
    painter.setBrush( self.palette().window() )
    painter.drawEllipse( self.width()/2-10, self.height()/2-10, 20, 20 )
    painter.setFont(self.font())
    actions = self.actions()
    count = len(actions)
    angle = 360.0/float(count)
    angleRadians = angle*math.pi/180.0

    for a in self._layout.keys():
      r = self._layout[a]
      if a == self._highlightAction:
        painter.setBrush( self.palette().highlight() )
        painter.setPen(self.palette().color(PySide.QtGui.QPalette.HighlightedText))
      else:
        painter.setBrush( self.palette().window() )
        painter.setPen(self.palette().color(PySide.QtGui.QPalette.Text))
      painter.drawRoundedRect(r, 8, 8)
      painter.drawText(r, PySide.QtCore.Qt.AlignCenter, a.text())

  def __layoutActions(self):
    if self._layout == None:
      self._layout = dict()
      actions = self.actions()
      count = len(actions)
      angleStep = 2.0*math.pi/float(count)
      angle = 0
      fontMetrics = PySide.QtGui.QFontMetrics(self.font())
      radius = 75
      bounds = PySide.QtCore.QRect()
      for a in actions:
        r = fontMetrics.boundingRect(a.text()).adjusted(-8, -8, 8, 8)
        r = r.translated(radius*math.cos(angle), radius*math.sin(angle))
        r = r.translated(-r.width()/2, -r.height()/2)
        r = r.translated(self.width()/2, self.height()/2)
        self._layout[a] = r
        bounds |= r
        angle += angleStep

      bounds = bounds.adjusted(-self._lineWidth, -self._lineWidth, self._lineWidth, self._lineWidth)
      for a in self._layout.keys():
        r = self._layout[a]
        r.translate(-bounds.x(), -bounds.y())

      self.resize(bounds.width(), bounds.height())

  def __actionAtPoint(self, pos):
    for a in self._layout.keys():
      r = self._layout[a]
      if r.contains(pos):
        return a;
    return None

  def mousePressEvent(self, e):
    self.__setHighlightAction(self.__actionAtPoint(e.pos()))
    if self._highlightAction == None:
      self.close()

  def mouseMoveEvent(self, e):
    self.__setHighlightAction(self.__actionAtPoint(e.pos()))

  def mouseReleaseEvent(self, e):
    if self._highlightAction != None:
      self._highlightAction.trigger()
      self.close()

  def enterEvent(self, e):
    self.__layoutActions()

  def leaveEvent(self, e):
    self.__setHighlightAction(None)

  def __setHighlightAction(self, a):
    if a != self._highlightAction:
      self._highlightAction = a
      self.update()

_pie = None

def showPieMenu():
  global _pie
  _pie = Pie()
  v = hiero.ui.activeView()

  if type(v) == hiero.ui.Viewer:
    _pie.tagsMenu.currentViewer = hiero.ui.currentViewer()
    _pie.tagsMenu.currentClipSequence = _pie.tagsMenu.currentViewer.player().sequence()
    menu = _pie.tagsMenu.createTagMenuForView('kViewer')
    acts = menu.actions()
  elif type(v) == hiero.ui.TimelineEditor or type(v) == hiero.ui.SpreadsheetView:
    _pie.tagsMenu._selection = v.selection()
    menu = _pie.tagsMenu.createTagMenuForView('kTimeline/kSpreadsheet')
    acts = menu.actions()
    if len(_pie.tagsMenu._selection) == 0:
      _pie.tagsMenu._selection = v.sequence().items()
      for act in acts:
        if "Tag Shot Selection" in act.text():
          acts.remove(act)
    
  elif type(v) == hiero.ui.BinView:
    _pie.tagsMenu._selection = v.selection()
    menu = _pie.tagsMenu.createTagMenuForView('kBin')
    acts = menu.actions()
  else:
    _pie.addAction( PySide.QtGui.QAction("Apple Pie", None) )

  for act in acts:
    _pie.addAction(act)

  _pie.showAt(PySide.QtGui.QCursor.pos())

action = PySide.QtGui.QAction("Mmmmmmm...Pie...", None)
action.setShortcut(PySide.QtGui.QKeySequence("/"))
action.triggered.connect(showPieMenu)
hiero.ui.addMenuAction("Edit", action)
