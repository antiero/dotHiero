import os.path
import PySide.QtCore
import PySide.QtGui

import hiero.ui
import FnFTPCopyExporter


class FTPCopyExporterUI(hiero.ui.TaskUIBase):
  def __init__(self, preset):
    """Initialize"""
    hiero.ui.TaskUIBase.__init__(self, FnFTPCopyExporter.FTPCopyExporter, preset, "FTP Copy Exporter")

  def ftpSectionOnOff(self, state) :
  	stateBool = bool(state)
  	
  	self.ftpServerEdit.setEnabled(stateBool)
  	self.ftpPortEdit.setEnabled(stateBool)
  	self.ftpUserEdit.setEnabled(stateBool)
  	self.ftpPassEdit.setEnabled(stateBool)
  	self.emailConf.setEnabled(stateBool)
  	self.emailConfLabel.setEnabled(stateBool)
  	
  	if self.emailConf.isChecked() and stateBool == True : self.emailEdit.setEnabled(True)
  	else : self.emailEdit.setEnabled(False)
  	
  	
  def emailSectionOnOff(self, state) :
  	self.emailEdit.setEnabled(bool(state))


  def ftpServerEditChanged(self, state):
    # Slot to handle change of checkbox state
    self._preset.properties()["ftpServer"] = self.ftpServerEdit.text()  

  def ftpPortEditChanged(self, state):
    # Slot to handle change of checkbox state
    self._preset.properties()["ftpPort"] = self.ftpPortEdit.text()

  def ftpUserEditChanged(self, state):
    # Slot to handle change of checkbox state
    self._preset.properties()["ftpUser"] = self.ftpUserEdit.text()

  def ftpPassEditChanged(self, state):
    # Slot to handle change of checkbox state
    self._preset.properties()["ftpPassword"] = self.ftpPassEdit.text()

  def populateUI (self, widget, exportTemplate):
    layout = PySide.QtGui.QFormLayout()
    layout.setContentsMargins(9, 0, 9, 0)

    #add custom FTP/Email section
    self.ftpSectionCheckbox = PySide.QtGui.QCheckBox()
    self.ftpSectionCheckbox.setChecked(False)
    self.ftpSectionCheckbox.stateChanged.connect(self.ftpSectionOnOff)
    
    self.ftpServerEdit = PySide.QtGui.QLineEdit()
    self.ftpServerEdit.setPlaceholderText(self._preset.properties()["ftpServer"])
    self.ftpServerEdit.textChanged.connect(self.ftpServerEditChanged)
    self.ftpServerEdit.setEnabled(0)
    
    self.ftpPortLabel = PySide.QtGui.QLabel("Port")
    self.ftpPortEdit = PySide.QtGui.QLineEdit()
    self.ftpPortEdit.setText(self._preset.properties()["ftpPort"])
    self.ftpPortEdit.textChanged.connect(self.ftpPortEditChanged)
    self.ftpPortEdit.setEnabled(0)
    
    self.ftpServerPortLayout = PySide.QtGui.QHBoxLayout()
    self.ftpServerPortLayout.addWidget(self.ftpServerEdit)
    self.ftpServerPortLayout.addWidget(self.ftpPortLabel)
    self.ftpServerPortLayout.addWidget(self.ftpPortEdit)
    
    self.ftpUserEdit = PySide.QtGui.QLineEdit()
    self.ftpUserEdit.setPlaceholderText("username")
    self.ftpUserEdit.setText(self._preset.properties()["ftpUser"])
    self.ftpUserEdit.textChanged.connect(self.ftpUserEditChanged)
    self.ftpUserEdit.setEnabled(0)
    
    self.ftpPassLabel = PySide.QtGui.QLabel("Pass")
    self.ftpPassEdit = PySide.QtGui.QLineEdit()
    self.ftpPassEdit.setPlaceholderText("password")
    self.ftpPassEdit.setEnabled(0)
    self.ftpPassEdit.setEchoMode(PySide.QtGui.QLineEdit.EchoMode.Password)
    self.ftpPassEdit.setText(self._preset.properties()["ftpPassword"])
    self.ftpPassEdit.textChanged.connect(self.ftpPassEditChanged)
    
    self.ftpUserPassLayout = PySide.QtGui.QHBoxLayout()
    self.ftpUserPassLayout.addWidget(self.ftpUserEdit)
    self.ftpUserPassLayout.addWidget(self.ftpPassLabel)
    self.ftpUserPassLayout.addWidget(self.ftpPassEdit)
    
    self.emailConfLabel = PySide.QtGui.QLabel("Email Confirmation?")
    self.emailConfLabel.setEnabled(0)
    self.emailConf = PySide.QtGui.QCheckBox()
    self.emailConf.setChecked(False)
    self.emailConf.setEnabled(0)
    self.emailConf.stateChanged.connect(self.emailSectionOnOff)
    
    self.emailConfLayout = PySide.QtGui.QHBoxLayout()
    self.emailConfLayout.addWidget(self.emailConf)
    self.emailConfLayout.addWidget(self.emailConfLabel)
    
    self.emailEdit = PySide.QtGui.QLineEdit()
    self.emailEdit.setPlaceholderText("review@thefoundry.co.uk")
    self.emailEdit.setEnabled(0)
    
    
    #add custom section
    layout.addRow("Do Custom FTP Upload", self.ftpSectionCheckbox)
    layout.addRow("Server", self.ftpServerPortLayout)
    layout.addRow("Username", self.ftpUserPassLayout)
    layout.addRow("", self.emailConfLayout)
    layout.addRow("", self.emailEdit)    
    
    widget.setLayout(layout)




hiero.ui.taskUIRegistry.registerTaskUI(FnFTPCopyExporter.FTPCopyPreset, FTPCopyExporterUI)
