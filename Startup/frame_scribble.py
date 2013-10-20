

from PySide.QtGui import *
from PySide.QtCore import *
import hiero.core
import hiero.ui
import threading

class ScribbleArea(QWidget):


    def getFullScreenSnapshot(self):
        cv = hiero.ui.currentViewer()
        cv.toggleFullScreen1_1()
        QCoreApplication.instance().processEvents()
        image = hiero.ui.currentViewer().image()
        QCoreApplication.instance().processEvents()
        cv.toggleFullScreen1_1()
        QCoreApplication.instance().processEvents()

        return image
       
    def __init__(self, parent=None):
        super(ScribbleArea, self).__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)
        self.modified = False
        self.scribbling = False
        self.myPenWidth = 5
        self.myPenColor = Qt.red
        self.image = hiero.core.executeInMainThreadWithResult(self.getFullScreenSnapshot) #hiero.ui.currentViewer().image() #
        self.originalImage = self.image
        self.lastPoint = QPoint()

    def saveImage(self, fileName, fileFormat):
        visibleImage = self.image
        #self.resizeImage(visibleImage)

        if visibleImage.save(fileName):
            self.modified = False
            return True
        else:
            return False

    def setPenColor(self, newColor):
        self.myPenColor = newColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

    def clearImage(self):
        print 'Restoring to original Image'
        self.image = self.originalImage
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.scribbling = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.scribbling:
            self.drawLineTo(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.scribbling:
            self.drawLineTo(event.pos())
            self.scribbling = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QPoint(0, 0), self.image)

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            newWidth = max(self.width() + 128, self.image.width())
            newHeight = max(self.height() + 128, self.image.height())
            self.resizeImage(self.image, QSize(newWidth, newHeight))
            self.update()

        super(ScribbleArea, self).resizeEvent(event)

    def drawLineTo(self, endPoint):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.myPenColor, self.myPenWidth,
                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(self.lastPoint, endPoint)
        self.modified = True

        rad = self.myPenWidth / 2 + 2
        self.update(QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QPoint(endPoint)

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return

        newImage = QImage(newSize, QImage.Format_RGB32)
        newImage.fill(qRgb(0, 0, 0))
        painter = QPainter(newImage)
        painter.drawImage(QPoint(0, 0), image)
        self.image = newImage

    def print_(self):
        printer = QPrinter(QPrinter.HighResolution)

        printDialog = QPrintDialog(printer, self)
        if printDialog.exec_() == QDialog.Accepted:
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.image.rect())
            painter.drawImage(0, 0, self.image)

    def isModified(self):
        return self.modified

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth

class FrameScribbleAction(QAction):


  class FrameScribbleDialog(QMainWindow):
			def __init__(self):
					super(FrameScribbleAction.FrameScribbleDialog, self).__init__()
	
					self.saveAsActs = []
	
					self.scribbleArea = ScribbleArea()
					self.setCentralWidget(self.scribbleArea)
	
					self.createActions()
					self.createMenus()
	
					self.setWindowTitle("Export Still Frame")
					self.resize(self.scribbleArea.image.width(),self.scribbleArea.image.height())
	
			def closeEvent(self, event):
					if self.maybeSave():
							event.accept()
					else:
							event.ignore()
	
			"""def open(self):
					if self.maybeSave():
							fileName,_ = QFileDialog.getOpenFileName(self, "Open File",
											QDir.currentPath())
							if fileName:
									self.scribbleArea.openImage(fileName)"""
	
			def save(self):
					action = self.sender()
					fileFormat = action.data()
					self.saveFile(fileFormat)
	
			def penColor(self):
					newColor = QColorDialog.getColor(self.scribbleArea.penColor())
					if newColor.isValid():
							self.scribbleArea.setPenColor(newColor)
	
			def penWidth(self):
					newWidth, ok = QInputDialog.getInteger(self, "Scribble",
									"Select pen width:", self.scribbleArea.penWidth(), 1, 50, 1)
					if ok:
							self.scribbleArea.setPenWidth(newWidth)
	
			def about(self):
					QMessageBox.about(self, "About",
									"Draw on the Frame and save an image")
	
			def createActions(self):
					"""self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
									triggered=self.open)"""
	
					for format in ['PNG','JPG','TIFF']:
							text = format + "..." #str(format.toUpper() + "...")
	
							action = QAction(text, self, triggered=self.save)
							action.setData(format)
							self.saveAsActs.append(action)
	
					self.printAct = QAction("&Print...", self,
									triggered=self.scribbleArea.print_)
	
					self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
									triggered=self.close)
	
					self.penColorAct = QAction("&Pen Color...", self,
									triggered=self.penColor)
	
					self.penWidthAct = QAction("Pen &Width...", self,
									triggered=self.penWidth)
	
					self.clearScreenAct = QAction("&Clear Screen", self,
									shortcut="Ctrl+L", triggered=self.scribbleArea.clearImage)
	
					self.aboutAct = QAction("&About", self, triggered=self.about)
	
					self.aboutQtAct = QAction("About &Qt", self,
									triggered=qApp.aboutQt)
	
			def createMenus(self):
					self.saveAsMenu = QMenu("&Save As", self)
					for action in self.saveAsActs:
							self.saveAsMenu.addAction(action)
	
					fileMenu = QMenu("&File", self)
					#fileMenu.addAction(self.openAct)
					fileMenu.addMenu(self.saveAsMenu)
					#fileMenu.addAction(self.printAct)
					fileMenu.addSeparator()
					fileMenu.addAction(self.exitAct)
	
					optionMenu = QMenu("&Options", self)
					optionMenu.addAction(self.penColorAct)
					optionMenu.addAction(self.penWidthAct)
					optionMenu.addSeparator()
					optionMenu.addAction(self.clearScreenAct)
	
					helpMenu = QMenu("&Help", self)
					helpMenu.addAction(self.aboutAct)
					helpMenu.addAction(self.aboutQtAct)
	
					self.menuBar().addMenu(fileMenu)
					self.menuBar().addMenu(optionMenu)
					self.menuBar().addMenu(helpMenu)
	
			def maybeSave(self):
					if self.scribbleArea.isModified():
							ret = QMessageBox.warning(self, "Scribble",
													"The image has been modified.\n"
													"Do you want to save your changes?",
													QMessageBox.Save | QMessageBox.Discard |
													QMessageBox.Cancel)
							if ret == QMessageBox.Save:
									return self.saveFile('png')
							elif ret == QMessageBox.Cancel:
									return False
	
					return True
	
			def saveFile(self, fileFormat):
					initialPath = QDir.currentPath() + '/untitled.' + fileFormat
	
					fileName,_ = QFileDialog.getSaveFileName(None, "Save As")
					if fileName:
							return self.scribbleArea.saveImage(fileName, fileFormat)
	
					return False

  def __init__(self):
      QAction.__init__(self, "Scribble Frame", None)
      self.triggered.connect(self.doit)
      hiero.core.events.registerInterest("kShowContextMenu/kViewer", self.eventHandler)

  def doit(self):    
    global dialog
    dialog = self.FrameScribbleDialog()
    dialog.show()

  def eventHandler(self, event):
    enabled = True
    # enable/disable the action each time
    self.setEnabled(enabled)
    event.menu.addAction( self );

dialog = None
# Instantiate the action to get it to register itself.
FrameScribbleAction = FrameScribbleAction()


