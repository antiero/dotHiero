# This example shows how to add Audio Tracks to a selection of TrackItems which are missing their audio
from hiero.core import *
from PySide.QtGui import *
from PySide.QtCore import *

def getAudioTrackWithName(sequence,trackName):
	for a in sequence.audioTracks():
		if a.name() == trackName:
			return a
	return None


class RebuildAudioAction(QAction):

	def __init__(self):
			QAction.__init__(self, "Rebuild Audio", None)
			self.triggered.connect(self.addAudioTracksToTrackItemSelection)
			hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
			self.setIcon(QIcon("icons:AudioOnly.png"))

	def addAudioTracksToTrackItemSelection(self):    
		# Get the sequence from the selection
		
		selection = self._selection
		if not selection:
			return
		
		sequence = selection[0].parent().parent()
		
		# Use only shots that are Video TrackItems from selection
		shots = [shot for shot in selection if (shot.MediaType() == hiero.core.TrackItem.MediaType.kVideo)]
	
		for shot in shots:
				clip = shot.source()
				clipMediaSource = clip.mediaSource()
				inTime = shot.timelineIn()
				outTime = shot.timelineOut()
				sourceIn = shot.sourceIn()
				sourceOut = shot.sourceOut()
		
				if clipMediaSource.hasAudio():
						numAudioTracks = clip.numAudioTracks()
						for t in range(1,numAudioTracks+1):
								trackName = shot.parent().name()+' A'+str(t)
								sequenceAudioTrackNames = [track.name() for track  in sequence.items()]
								if not trackName in sequenceAudioTrackNames:
										#print trackName, 'is not in ', sequence,' adding new Track'
										aTrack = hiero.core.AudioTrack(trackName)
										sequence.addTrack(aTrack)
								else:
									aTrack = getAudioTrackWithName(sequence,trackName)
								
								# Grab the same Clip as the Video Track
								newclip = clip
								newclip.setInTime(0)
								newclip.setOutTime(newclip.duration())     
								newclip.setInTime(sourceIn)
								newclip.setOutTime(sourceOut) 
								audioClip = aTrack.addTrackItem(newclip,t-1,shot.timelineIn())
								audioClip.link(shot)															
        
	def eventHandler(self, event):
		enabled = False
		self._selection = None
		if hasattr(event.sender, 'getSelection') and event.sender.getSelection() is not None and len( event.sender.getSelection() ) != 0:
			enabled = True
			
			selection = event.sender.getSelection()
			self._selection = [shot for shot in selection if (shot.MediaType() == hiero.core.TrackItem.MediaType.kVideo)]
			if len(selection)>0:
				event.menu.addAction( self )


action = RebuildAudioAction()

class RestoreClipNameAction(QAction):

	def __init__(self):
			QAction.__init__(self, "Restore Clip Names", None)
			self.triggered.connect(self.restoreClipNamesFromSelection)
			hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)

	def restoreClipNamesFromSelection(self):    
		# Get the sequence from the selection
		
		selection = self._selection
		if not selection:
			return
		
		sequence = selection[0].parent().parent()
		
		# Use only shots that are Video TrackItems from selection
		shots = [shot for shot in selection if (shot.MediaType() == hiero.core.TrackItem.MediaType.kVideo)]
	
		for shot in shots:
				clip = shot.source()
				shot.setName(clip.name())													
        
	def eventHandler(self, event):
		enabled = False
		self._selection = None
		if hasattr(event.sender, 'getSelection') and event.sender.getSelection() is not None and len( event.sender.getSelection() ) != 0:
			enabled = True
			
			selection = event.sender.getSelection()
			self._selection = [shot for shot in selection if (shot.MediaType() == hiero.core.TrackItem.MediaType.kVideo)]
			if len(selection)>0:
				event.menu.addAction( self )

restoreClipNameAction = RestoreClipNameAction()