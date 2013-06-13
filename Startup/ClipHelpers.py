import hiero.core
import os, re

def splitClip(clip, makeNewClips = True, deleteOriginal = False):
  # Takes a Clip which may be a split sequence and Splits it into its component Clips
  mediaSource = clip.mediaSource()
  if mediaSource.singleFile():
    print 'clip input is not an image sequence and cannot be split'
    return None

  fileName = mediaSource.fileinfos()[0].filename()
  frameHead = mediaSource.filenameHead()
  frameDir = fileName.split(frameHead)[0]

  splitSeqs = [] 
  seqListCandidates = hiero.core.filenameList(frameDir, splitSequences = True, returnHiddenFiles = False)
  for seq in seqListCandidates:
    if frameHead in seq:
      splitSeqs+=[os.path.join(frameDir,seq)]

  if makeNewClips:
    clipBinRoot = c.binItem().parentBin()
    proj = clip.project()
    with proj.beginUndo('Split Bin Clip'):
      for source in splitSeqs:
        print 'Source file is:' + source

        # Detect the path frame padding form (%0#d) of the filename from the MediaSource
        M = hiero.core.MediaSource(source)
        filePathPadded = M.toString().split('Source:')[-1].split()[0]

        _first = None
        _last = None
        # Check for first-last extension...
        flCheck = re.findall('\d+\-\d+',source.split()[-1])
        if len(flCheck)==1:
          _first = int(flCheck[0].split('-')[0])
          _last = int(flCheck[0].split('-')[1])

        else:
          # It should be a single frame, with no 'first-last' in the media source path
          frame = re.findall(r'\b\d+\b', source)      
          if len(frame)!=1:
            print 'Frame Padding for %s was ambiguous and could not be detected.' % source
            return
          else:
            _first = int(frame[0])
            _last = _first

        clip = hiero.core.Clip(filePathPadded, _first, _last) 
        clipBinRoot.addItem(hiero.core.BinItem(clip))

  if deleteOriginal:
    clipBinRoot = c.binItem().parentBin()
    with proj.beginUndo('Delete Original Clip'):
      clipBinRoot.removeItem(clip.binItem())

  return splitSeqs


def _importFolder(self, dir, splitSequences = True):
  """
  Imports a Folder to the current Bin

  @param dir - the folder to import
  @param splitSequences (optional) - tells Hiero whether to import Clips as splitSequences (default = False)
  """
  if not splitSequences:
    try:
      self.importFolder(dir)
    except:
      raise "Unable to import directory: %s" % dir
  else:
    seqListCandidates = [os.path.join(dir,seq) for seq in hiero.core.filenameList(dir, splitSequences = True, returnHiddenFiles = False)]
    splitSeqs = [] 
    proj = self.project()
    with proj.beginUndo('Import Folder'):
      for seq in seqListCandidates:
        seq = os.path.join(dir,seq)
        print 'Importing: %s.' % seq
        M = hiero.core.MediaSource(seq)
        if not (M.hasAudio() or M.hasVideo()):
          hiero.core.log.debug('No Media with Audio/Video is present for: %s' % seq)
        elif M.singleFile():
          self.addItem(hiero.core.BinItem(hiero.core.Clip(seq)))
        else:
          fileName = M.fileinfos()[0].filename()
          frameHead = M.filenameHead()
          frameDir = fileName.split(frameHead)[0]

          # Why the FUCK isn't this given as part of the MediaSource object?!..
          F = M.fileinfos()[0]
          filePathPadded = "%s %d-%d" % (F.filename(), int(F.startFrame()),int(F.endFrame()))
          hiero.core.log.debug('FilePath Padded is: ' + str(filePathPadded))
          _first = None
          _last = None
          # Check for first-last extension...
          flCheck = re.findall('\d+\-\d+',seq.split()[-1])
          if len(flCheck)==1:
            _first = int(flCheck[0].split('-')[0])
            _last = int(flCheck[0].split('-')[1])

          else:
            # It should be a single frame, with no 'first-last' in the media source path
            frame = re.findall(r'\b\d+\b', seq)      
            if len(frame)==0:
              hiero.core.log.debug('Frame Padding for %s was ambiguous and could not be detected.' % seq)
            elif len(frame)==1:
              _first = int(frame[0])
              _last = _first
          if not _first or not _last:
            hiero.core.log.debug('Unable to detect the frame range from %s' % seq)
          else:
            hiero.core.log.debug('Attempting to import: %s with first=%d, last=%d' % (filePathPadded,_first,_last))
            try:
              hiero.core.log.debug('importing %s with first=%d, last=%d' % (filePathPadded,_first,_last))
              clip = hiero.core.Clip(filePathPadded, _first, _last) 
              self.addItem(hiero.core.BinItem(clip))
            except:
              hiero.core.log.debug('Unable to add Clip' + str(clip))

  return self  

hiero.core.Bin.importFolder = _importFolder