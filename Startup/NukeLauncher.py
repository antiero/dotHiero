import hiero.core
import os, subprocess
def launchNukeCustom(nuke=None, switches=None, script=None, argv=None, ranges=None):
  """
  Launches Nuke via subprocess.Popen

  launchNukeCustom constructs a command using the Nuke's general command line syntax.
  
  This is the general syntax for using these options when launching Nuke at the command prompt:

  nuke <switches> <script> <argv> <ranges>

  This method takes the following keyword arguments:

  @param nuke - (optional) the path to Nuke for launching (defaults to Nuke set in Hiero Preferences)
  @param switches - (optional) a list of extra command line arguments to pass to as Nuke switches (e.g. --nukex -q)
  @param script - (optional) path to Nuke Script (.nk) to open with Nuke
  @param argv - (optional) keyword argument, a list of argvs to pass to the command line, [argv n], placed between the <script> and <ranges> 
  @param ranges - (optional) keyword argument, a list of frame ranges used for rendering.
  @return - the subprocess.Popen object for the Nuke instance launched

  Example Usage: launchNukeCustom(nuke='/usr/local/somenuke', script='/tmp/myComp.nk', switches=['-x','--nukex'], ranges=['1-5'])
  """

  allArgs=[]
  # nuke <switches> <script> <argv> <ranges>
  if not nuke:
    nuke = hiero.core.getInteractiveNukeExecutablePath()
  if os.path.exists(nuke):
    allArgs.append(nuke)
  else:
    raise IOError("Nuke Executable Path Not Found!")

  # This method allows for strings, tuples or lists to be used...
  def buildArgs(argsList1,argsList2):
    if isinstance(argsList2,str):
      argsList1.append(argsList2)
    elif isinstance(argsList2,(list,tuple)):
      argsList1.extend(argsList2)
    else:
      raise IOError("Inputs must by strings, lists, or tuples of argumenets")
    return argsList1

  if switches:
    buildArgs(allArgs,switches)
  if script:
    buildArgs(allArgs,script)
  if argv:
    buildArgs(allArgs,argv)
  if ranges:
    buildArgs(allArgs,ranges)

  hiero.core.log.debug('Launching Nuke subprocess with args: %s' % str(allArgs))
  # Set close_fds here, because otherwise the Nuke process inherits any open sockets and this causes bad things to happen with the Hiero-Nuke bridge
  return subprocess.Popen(allArgs, shell=False, close_fds=True)

# Duck punch this custom method into hiero.core.nuke module...
hiero.core.nuke.launchNukeCustom = launchNukeCustom

