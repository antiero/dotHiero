import hiero.core

def whereAmI(self, searchType='TrackItem'):
  """returns a list of objects which contain this Clip. 
  By default this will return a list of TrackItems where the Clip is used in its project.
  You can also return a list of Sequences by specifying the searchType to be 'Sequence'

  Example usage:

  shotsForClip = clip.whereAmI('TrackItem')
  sequencesForClip = clip.whereAmI('Sequence')
  """
  proj = self.project()

  if ('TrackItem' not in searchType) and ('Sequence' not in searchType):
    print "searchType argument must be 'TrackItem' or 'Sequence'"
    return None

  # If user specifies a TrackItem, then it will return 
  searches = hiero.core.findItemsInProject(proj, searchType)

  if len(searches)==0:
    print 'Unable to find %s in any items of type: %s' % (str(self),str(searchType)) 
    return None
  
  # Case 1: Looking for Shots (trackItems)
  clipUsedIn = []
  if isinstance(searches[0],hiero.core.TrackItem):
    for shot in searches:
      if shot.source().binItem() == self.binItem():
        clipUsedIn.append(shot)

  # Case 1: Looking for Shots (trackItems)
  elif isinstance(searches[0],hiero.core.Sequence):
      for seq in searches:
        # Iterate tracks > shots...
        tracks = seq.items()
        for track in tracks:
          shots = track.items()
          for shot in shots:
            if shot.source().binItem() == self.binItem():
              clipUsedIn.append(seq)

  return clipUsedIn

# Add new method to Clip object
hiero.core.Clip.whereAmI = whereAmI