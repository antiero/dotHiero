# Copyright (c) 2011 The Foundry Visionmongers Ltd.  All Rights Reserved.

import os.path
import os
import sys
import shutil
import ftplib
import traceback

import hiero.core
from hiero.exporters import FnFrameExporter


class FTPCopyExporter(FnFrameExporter.FrameExporter):
  def __init__( self, initDict ):
    """Initialize"""
    FnFrameExporter.FrameExporter.__init__( self, initDict )
    if self.nothingToDo():
      return
      
    self.ftp = ftplib.FTP()
    try:
      print self.ftp.retrlines('LIST')
      self.ftp.cwd('Hiero')
    except:
      print "Logging in..."
      self.ftp.connect(self._preset.properties()["ftpServer"], self._preset.properties()["ftpPort"])
      self.ftp.login(self._preset.properties()["ftpUser"], self._preset.properties()["ftpPassword"])
      #self.connectToFTP()


  """def progress(self):
    #return float(0)"""

  def connectToFTP(self):
    try:
      try:
          # move to the desired upload directory
          print "Currently in:", self.ftp.pwd()
          
          print "Files:"
          print self.ftp.retrlines('LIST')
          
          print "Making Directory...."
          try:
            self.ftp.mkd('Hiero')
          except:
            print 'Hiero Dir Exists'
          
          print "Setting Current Working Directory...."
          self.ftp.cwd('Hiero')
          print "Currently in:", self.ftp.pwd()
      finally:
          print "FINALLY!..."
          #self.ftp.quit()
    except:
      traceback.print_exc()
  
  
  
  def doFrame(self, src, dst):
    hiero.core.info( "FTPCopyExporter:" )
    hiero.core.info( "  - source: " + str(src) )
    hiero.core.info( "  - destination: " + str(dst) )

    # Find the base destination directory, if it doesn't exist create it
    dstdir = os.path.dirname(dst)
    print 'doFrame: dstdir:', str(dst)
    #if not os.path.exists(dstdir):
    #  hiero.core.info( "make dirs:" + dstdir )
    #  os.makedirs(dstdir)
 
    # Copy file including the permission bits, last access time, last modification time, and flags
    #shutil.copy2(src, dst)
    name = os.path.split(src)[-1]
    print 'Name is',name
    f = open(src, "rb")
    print "Uploading...",src
    self.ftp.storbinary('STOR ' + name, f)
    f.close()
    print "OK"        
    print "Files:"
    print self.ftp.retrlines('LIST')
    #self.ftp.quit()
   
  def taskStep(self):
    # If this is a single file (eg r3d or mov) then we don't need to do every frame.
    ret = FnFrameExporter.FrameExporter.taskStep(self)
    print 'ret is:', str(ret)
    return ret and not self._source.singleFile()


  def finishTask(self):
    """
      This will be called after jobs have been added.
      """
    self.ftp.quit()
    return


class FTPCopyPreset(hiero.core.TaskPresetBase):
  def __init__(self, name, properties):
    hiero.core.TaskPresetBase.__init__(self, FTPCopyExporter, name)
    # Set any preset defaults here
    self.properties()["ftpServer"] = "ftp://ftp.thefoundry.co.uk"
    self.properties()["ftpPort"] = "21"
    self.properties()["ftpUser"] = "mromeyisahiero"
    self.properties()["ftpPassword"] = "HieroSonyF3"
    
    
    # Update preset with loaded data
    self.properties().update(properties)

  def supportedItems(self):
    return hiero.core.TaskPreset.kTrackItem | hiero.core.TaskPreset.kClip


hiero.core.taskRegistry.registerTask(FTPCopyPreset, FTPCopyExporter)
