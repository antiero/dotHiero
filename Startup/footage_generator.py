# Hiero footage generator

exportPreset = {'name': 'DPX-10bit', 'ext': 'dpx', 'file_type': 'dpx',
 'dpx': {'datatype': '10 bit'},
 'reformat': {'width': '2048','height':1080}} ,
 'channels': 'rgb'}


def ExportWithRawParameters(testName, sourcePath, data):
  '''Pass in raw parameters to create Processors on the fly and use for Export Tasks.
  '''
  if data['presetType'] == "TranscodePreset":
    transcodePreset = TranscodePreset("PresetName", data['transcode'] )
    templateFilename = ((data['templatename'], transcodePreset ),)

    exportFlags = { "exportTemplate" : templateFilename,
                    "exportRoot" : exportRootDir }
    exportFlags.update(data['exportflags'])

  elif data['presetType'] == "ShotProcessorPreset":
    transcodePreset = ShotProcessorPreset("PresetName", data['transcode'] )
    templateFilename = ((data['templatename'], transcodePreset ),)

    exportFlags = { "exportTemplate" : templateFilename,
                    "exportRoot" : exportRootDir }
    exportFlags.update(data['exportflags'])

  if data['processorType'] == "binprocessor":
    binclip = addBinClip(sourcePath, data)
    tlWrapper = [hiero.core.ItemWrapper(binclip.activeItem())]
    processorPreset = FnBinProcessor.BinProcessorPreset("Clips", exportFlags)

  return processorPreset, tlWrapper

def runExportTask():
  global exitCode

  # Disable the R3D Rocket card as this appears to be giving Image compare failures
  disableR3DRocketCard()
  
  # For speed, do not limit the Nuke Transcode number
  setFastTranscodes()
  
  if presetName:
    processorPreset, tlWrapper = ExportWithXMLPreset(testName, sourcePath, data, presetName, presetPath)
  else:
    processorPreset, tlWrapper = ExportWithRawParameters(testName, sourcePath, data)

  FnHieroLog.log("Executing task preset %s" % processorPreset.name())
#   hiero.core.log.setLogLevel(hiero.core.log.kDebug)
  registry.createAndExecuteProcessor(processorPreset, tlWrapper, data['submissionType'])