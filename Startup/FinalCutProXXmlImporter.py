'''
.fcpxml Importer
v1.0 - Initial release.
'''

import os
import urllib
from xml.dom.minidom import parse
import hiero.core

def getGapFromFCPGapTag(gap_xml_tag):
  # This is probably not needed ...
  #<gap offset="0s" name="Gap" duration="10010/24000s" start="86400314/24000s"/>
  offset_str = gap_xml_tag.attributes['offset'].value
  duration_str = gap_xml_tag.attributes['duration'].value
  start_str = gap_xml_tag.attributes['start'].value

def getSequenceNodesFromFCPSequenceTag(sequence_xml_tag):

  spine = sequence_xml_tag.getElementsByTagName("spine")[0]
  
  # We can have gaps, (why?!)
  #<gap offset="0s" name="Gap" duration="10010/24000s" start="86400314/24000s"/>
  
  # Or Clips:
  #  <clip offset="10010/24000s" name="Shot0310_720p" duration="38038/24000s" start="817817/24000s" tcFormat="NDF">
  #      <video offset="817817/24000s" ref="r3" duration="38038/24000s" start="817817/24000s">
  #          <audio lane="-1" offset="1635634/48000s" ref="r3" duration="76076/48000s" start="1635634/48000s" role="dialogue"/>
  #      </video>
  #  </clip>

  # Get the ELEMENT_NODE children, ignore TEXT_NODE (e.g. '=\n')
  spineNodes = []
  for node in spine.childNodes:
    if node.nodeType == node.ELEMENT_NODE:
      spineNodes.append(node)
  
  return spineNodes


def getFCPXMLContents(xml_file='/Users/ant/Movies/FCPXExport/TestMedia.fcpxml'):

  # Start by parsing in the XML file from the path specified
  dom = parse( xml_file )

  # Get the project info
  """A <project> element also includes a <resources> element
  that lists additional data the project depends upon, including external assets,
  video formats, and effects. ."""
  project = dom.getElementsByTagName("project")
  projectName = project[0].getAttribute('name')
  print 'Found Project Name: ' + projectName

  # The resources are where the Clip source info (assets) are contained
  resources = project[0].getElementsByTagName("resources")

  ### <format id="r1" name="FFVideoFormat720p30" frameDuration="100/3000s" width="1280" height="720"/>
  resources_format = resources[0].getElementsByTagName("format")
  gFrameDuration = resources_format[0].getAttribute('frameDuration')
  gFormatWidth = resources_format[0].getAttribute('width')
  gFormatHeight = resources_format[0].getAttribute('height')

  ###<projectRef id="r2" name="Tour of Tripoli" uid="A9D4D5D3-C197-4CBC-B83C-6B564C9F0FED"/>
  resources_projectRef = resources[0].getElementsByTagName("projectRef")

  assets = resources[0].getElementsByTagName("asset")
  
  sequences = project[0].getElementsByTagName("sequence")

  # This is a list of assets which can be looked up by ID
  assetID_Dict = {}
  # Create an assets directory
  for a in assets:
    id = str(a.getAttribute('id'))
    name = str(a.getAttribute('name'))
    uid = str(a.getAttribute('uid'))
    projectRef = str(a.getAttribute('projectRef'))
    src = str(a.getAttribute('src'))
    start = str(a.getAttribute('start'))
    duration = str(a.getAttribute('duration')) # "2718000/90000s"
    hasVideo = str(a.getAttribute('hasVideo'))
    hasAudio = str(a.getAttribute('hasAudio'))
    audioSources = str(a.getAttribute('audioSources'))
    audioChannels = str(a.getAttribute('audioChannels'))
    audioRate= str(a.getAttribute('audioRate'))
    assetID_Dict[id] = {'name':name,'uid':uid,'projectRef':projectRef,
                     'src':src, 'start':start, 'duration':duration,
                     'hasVideo':hasVideo,'hasAudio':hasAudio,
                     'audioSources':audioSources,'audioChannels':audioChannels,
                     'audioRate':audioRate}

  # Now go for the Sequence..
  """<sequence duration="44s" format="r1" tcStart="0s" tcFormat="NDF" audioLayout="surround" audioRate="48k">
      <spine>
          <clip name="Tour of Tripoli 20 April 2012 004" duration="90600/3000s" tcFormat="NDF">
              <video ref="r3" duration="906000/30000s">
                  <audio lane="-1" ref="r3" duration="1331820/44100s" role="dialogue" outCh="L, R"/>
              </video>
              <clip lane="1" offset="132/5s" name="Tour of Tripoli 20 April 2012 014" duration="6100/3000s" tcFormat="NDF">
                  <video ref="r4" duration="61000/30000s">
                      <audio lane="-1" ref="r4" duration="89670/44100s" role="dialogue" outCh="L, R"/>
                  </video>
              </clip>"""

  sequence = dom.getElementsByTagName("sequence")


  # TODO: Work out the clip-lane nesting logic.

  # For now, return a list of assets (i.e. Clips), which we can drop in to Hiero
  return (assetID_Dict, projectName, assets, sequences)