#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  peertalk.py
#
# Copyright (C) 2012    David House <davidahouse@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 or version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# This script depends on the usbmux python script that you can find here:
# http://code.google.com/p/iphone-dataprotection/source/browse/usbmuxd-python-client/?r=3e6e6f047d7314e41dcc143ad52c67d3ee8c0859
# Also only works with the PeerTalk iOS application that you can find here:
# https://github.com/rsms/peertalk
#
import hiero.core
import hiero.ui
import sys
import usbmux
import SocketServer
import select
from optparse import OptionParser
import sys
import threading
import struct
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtWebKit import *

class PeerTalkThread(threading.Thread):
  def __init__(self,*args):
    self._psock = args[0]
    self._running = True
    threading.Thread.__init__(self)

  def run(self):
    framestructure = struct.Struct("! I I I I")
    while self._running:
      try:
        data = self._psock.recv(1024)
        #if len(msg) > 0:
        #  frame = framestructure.unpack(msg)
        #  size = frame[3]
          #msgdata = self._psock.recv(size)
        
        if len(data)>0:
          print 'Len of recv data is: %i' % len(data)

          msgStr = str(repr(data))
          print 'msgStr was ' + msgStr

      except:
        #print 'Received something, but could not print it'
        pass

  def stop(self):
    self._running = False

class PeerTalkPanel(QWidget):
  def __init__(self):
    QWidget.__init__( self )

    self.setWindowTitle( "PeerTalk" )
    self.setLayout( QVBoxLayout() )
    self.logText = "Welcome to PeerTalk"

    self.editor = QLineEdit()

    self.console = QTextEdit()
    self.console.setEnabled(False)
    self.console.setFixedHeight(160)

    self.stopStartButton = QPushButton("Start")
    self.stopStartButton.clicked.connect(self.start)

    self.sendButton = QPushButton("Send")
    self.sendButton.clicked.connect(self.sendPressed)
    

    #QObject.connect( self.locationEdit, SIGNAL('returnPressed()'),  self.changeLocation )
    self.layout().addWidget(self.console)
    self.layout().addWidget(self.stopStartButton)
    self.layout().addWidget(self.editor)
    self.layout().addWidget(self.sendButton)

    self.done = False

  def start(self):
    print "peertalk starting"
    self.mux = usbmux.USBMux()

    print "Waiting for devices..."
    if not self.mux.devices:
        self.mux.process(1.0)
    if not self.mux.devices:
        print "No device found"

    self.dev = self.mux.devices[0]
    print "connecting to device %s" % str(self.dev)
    self.psock = self.mux.connect(self.dev, 2345)
    self.psock.setblocking(0)
    self.psock.settimeout(2)

    self.ptthread = PeerTalkThread(self.psock)
    
    # This stops the App from hanging on exit    
    self.ptthread.start()
    QCoreApplication.instance().aboutToQuit.connect(self.ptthread.stop)      

  def sendPressed(self):
    currentText = self.editor.text()
    self.logText += '\n'+currentText
    self.console.setText(self.logText)
    if currentText.lower() == "quit":
      print 'Attempting to stop the connection'
      self.ptthread.stop()
    else:
      try:
        r8 = currentText.encode('utf-8')
        headervalues = (1,101,0,len(r8)+4)
        framestructure = struct.Struct("! I I I I")
        packed_data = framestructure.pack(*headervalues)
        self.psock.send(packed_data)
        messagevalues = (len(r8),r8)
        fmtstring = "! I {0}s".format(len(r8))
        sm = struct.Struct(fmtstring)
        packed_message = sm.pack(*messagevalues)
        self.psock.send(packed_message)
      except:
        print 'Unable to send message to device'


ptp = PeerTalkPanel()
wm = hiero.ui.windowManager()
wm.addWindow( ptp )