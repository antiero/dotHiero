# Helpers for creating Importing Clips and Sequences for Testing Purpose
import hiero.core
import random
import os

# Edit this list of root Folders at which to search for Clips
sequenceSearchDirs = ["/Users/ant/Movies"]

# List of valid image extensions
gImageExtensions = [".dpx", ".exr", ".tif", ".jpg", ".jpeg", ".mov", ".ari", ".r3d", ".tga", ".png", ".cin"]

def getListOfPossibleClipsFromMediaRoot(searchDirs = None):
  """Returns a list of possible Clip paths to import from a root path.
  @param: searchDirs - a directory path (or list of paths) to media in which to search for recursively or possible Clip candidates
  @return: A list of sequencified file paths which can be imported as a Clip
  """
  
  clipCanidates = []
  if not searchDirs:
    global sequenceSearchDirs
    searchDirs = sequenceSearchDirs

  for searchDir in searchDirs:
    # traverse root directory, and list directories as dirs and files as files
    for root, dirs, files in os.walk(searchDir):
        path = root.split('/')
        for dir in dirs:
          directory = os.path.join(root,dir)
          clipList = hiero.core.filenameList(directory, splitSequences=True, returnDirectories=False, returnHiddenFiles=False)
          clipCanidates += [os.path.join(directory, clip) for clip in clipList]

  hiero.core.log.debug("Found %i Clip candidates from search dirs: %s" % (len(clipCanidates), str(searchDirs)))
  return clipCanidates

def importRandomClip():

  global gImageExtensions
  proj = hiero.core.projects()[-1]
  root = proj.clipsBin()

  possibleClips = getListOfPossibleClipsFromMediaRoot()

  numClips = len(possibleClips)

  # Get a Random Clip
  randomClipPath = possibleClips[random.randint(0, numClips)]
  mediaSource = hiero.core.MediaSource(randomClipPath)
  mediaSourceIsValid = mediaSource.isMediaPresent()

  if not mediaSourceIsValid:
    numMediaImportRetries = 20 # We'll limit the retry to 20 times
    currentTry = 0
    while not mediaSourceIsValid and currentTry <= numMediaImportRetries:
      # Get a Random Clip
      randomClipPath = possibleClips[random.randint(0, numClips-1)]
      mediaSource = hiero.core.MediaSource(randomClipPath)
      mediaSourceIsValid = mediaSource.isMediaPresent()
      currentTry+=1

  # After 20 tries, if we haven't found a valid media source, the directory supplied is probably bad...
  if not mediaSource.isMediaPresent():
    raise "Unable to import a random Clip. Are you sure your search root directories contain media?"
  
  clip = hiero.core.Clip(mediaSource)
  clipBI = hiero.core.BinItem(clip)

  print "Importing Clip from this path: %s." % randomClipPath

  clip = hiero.core.Clip(hiero.core.MediaSource(randomClipPath))
  clipBI = hiero.core.BinItem(clip)

  # Import the Clip to the Bin
  root.addItem(clipBI)

  return clipBI