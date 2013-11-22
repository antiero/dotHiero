import hiero.core

defaultsRef = {
  "histogram/guides" : True,
  "histogram/targets" : True,
  "histogram/channel" : '1',

  "waveformscope/guides" : True,
  "waveformscope/targets" : True,
  "waveformscope/channel" : '1',  

  "vectorscope/guides" : True,
  "vectorscope/targets" : True,
  "vectorscope/channel" : '1',  

  "sdiOut/viewerGammaGain" : False,
  "sdiOut/verticalFlip" : False,
  "sdiOut/videoMode" : False,
  "sdiOut/numBits" : '8',
  "sdiOut/displayLUT" : 'None',
  "sdiOut/viewerAB" : '0',
  "sdiOut/device" : 'None'        
}

def compareKeyValueWithRef(defaultsRef):
  keys = defaultsRef.keys()
  appSettings = hiero.core.ApplicationSettings()
  for key in keys:
    refValue = defaultsRef[key]
    if isinstance( refValue , bool ):
      testValue = appSettings.boolValue(key)
    else:
      testValue = appSettings.value(key)
    if testValue == refValue:
      print '[PASS]: %s preference default was %s, as expected' % (key, testValue)
    else:
      print '[FAIL]: %s preference default did not match (got %s, expected %s' % (key, testValue, refValue)

compareKeyValueWithRef(defaultsRef)

# TODO
"""
[General]
HieroNukeBridge.warnUserAboutMissingNukeTools=true
startupWorkspace=Editing
showSplashScreen=true
loadProjectWorkspaces=true
autoSavePreprocessedEffect=false
reconstructDirectoriesOnIngest=true
showStartupDialog=true
cacheFolder=/var/tmp/hiero
autoCacheFolder=
autoLocaliseFolder=
dragAndDropFullImageSequence=true
enableAutoVersionScanning=true
platformPathRemaps=@Invalid()
ocioConfigFile=
viewerFullscreenMonitor=0
imageSequenceTimecode=0
redTimecode=0
maxValidTimebase=10000
useVideoEDLTimecodes=false
setBlackPointKey=0
setWhitePointKey=1
yCbCrEncoding=1
useCustomNuke=false
useInteractiveNukeLicense=false
launchNukeX=true
nukePathOSX=/Applications/Nuke7.0v6/Nuke7.0v6.app
userConfigureNuke=0
nukeNumberOfThreads=0
nukeCacheMemoryInGbs=1
quickTimeSubProcessCount=8
foundry.hiero.preferencesdialog=@Rect(333 154 773 586)
framerate=24/1
samplerate=48000/1
defaultMediaFormat="1,[ 0, 0, 1920, 1080],[ 0, 0, 1920, 1080],HD 1080"
timedisplayformat=0
starttimecode=86400
viewerLut=sRGB
thumbnailLut=sRGB
eightBitLut=sRGB
sixteenBitLut=sRGB
logLut=Cineon
floatLut=linear
nukeUseOCIO=false

[histogram]
guides=true
targets=true

[waveformscope]
guides=true
targets=true

[vectorscope]
guides=true
targets=true

[sdiOut]
viewerAB=0
viewerGammaGain=false
verticalFlip=false
videoMode=false
numBits=8
displayLUT=None

[autosave]
period=5

[localisation]
maxSizeFiles=10000

[viewer]
playbackModeChoice=1
defaultGuides=@Invalid()
seeThroughMissingMedia=true
cropToFormat=false
backgroundPattern=0
backgroundBrightness=75
backgroundCheckBrightness=127
frameIncrement=12
viewerFilteringMode=Auto
viewerThreadsPerReader=2
viewerThreadsPerExtension=@Invalid()
viewerARRIHelperThreads=0
viewerOpenEXRHelperThreads=0
playbackExpand3To4ComponentsOSX=true
playbackcacheSize=33
playbackCacheLock=true
playbackCacheUnlockInBackground=true
viewerFlushCacheOnAppBackground=false
viewerPauseDecodersOnAppBackground=true
downsizeSampling8=1
downsizeSampling16I=1
downsizeSampling16F=1
downsizeSampling32=1

[audio]
disable=false
device=Built-in Output
defaultLatencyAdjustmentMs=0
defaultVolume=50

[red]
useRocket=true

[scripteditor]
font=@Variant(\0\0\0@\0\0\0\x16\0\x43\0o\0u\0r\0i\0\x65\0r\0 \0N\0\x65\0w@(\0\0\0\0\0\0\xff\xff\xff\xff\x2\x1\0\x32\x10)
indent=4
SaveAndLoadHistory=true

[PlatformPathRemapWidget]
headerColumns=@ByteArray(\0\0\0\xff\0\0\0\0\0\0\0\x1\0\0\0\x1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x1\xa4\0\0\0\x3\0\x1\x1\0\0\0\0\0\x3\0\0\0\0\0\0\0\x64\xff\xff\xff\xff\0\0\0\x84\0\0\0\0\0\0\0\x1\0\0\x1\xa4\0\0\0\x3\0\0\0\x1)
"""