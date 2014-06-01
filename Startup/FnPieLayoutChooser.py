import PySide.QtCore
import PySide.QtGui
import hiero.ui
import math

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
      radius = 100
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

def getWorkspaceNames():
  """Returns a list of available Workspace names"""
  layoutMenu  = hiero.ui.findMenuAction("foundry.workspace.Conforming").parent()

  layoutActions = layoutMenu.children()
  workspaceNames = []
  for action in layoutActions:
    if action.objectName().startswith("foundry.workspace."):
      workspaceNames += [action.text()]

  return workspaceNames

# This is just a convenience method for returning QActions with a title, triggered method and icon.
def makeWorkspaceAction(title, method):
  action = PySide.QtGui.QAction(title,None)

  # We do this magic, so that the title string from the action is used to trigger the version change
  def methodWrapper():
    method(title)

  action.triggered.connect( methodWrapper )
  return action  

_pie = None
_workspaces = getWorkspaceNames()

def showPieMenu():
  global _pie
  global _workspaces
  _pie = Pie()
  v = hiero.ui.activeView()

  for workspaceName in _workspaces:
    action = makeWorkspaceAction(workspaceName, hiero.ui.setWorkspace)
    _pie.addAction( action )

  _pie.showAt(PySide.QtGui.QCursor.pos())

# Add the workspace Chooser to the Window menu for now...
action = PySide.QtGui.QAction("Workspace Chooser", None)
action.setShortcut(PySide.QtGui.QKeySequence("Ctrl+`"))
action.triggered.connect(showPieMenu)
hiero.ui.addMenuAction("Window", action)