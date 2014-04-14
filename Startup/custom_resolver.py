from hiero.exporters.FnShotProcessor import ShotProcessorPreset

def shot_addUserResolveEntries(self, resolver):

  def grade_state(task):
    """returns 'graded' or 'ungraded' depending on whether a Grade Tag exists on a shot with graded/ungraded in the note"""
    trackItem = task._item
    try:
      gradeTag = [tag for tag in trackItem.tags() if tag.name() == "Grade"][0]
    except:
      gradedState = ""
      return gradedState
    if gradeTag.note().lower() == "graded":
      return "graded"
    elif gradeTag.note().lower() == "ungraded":
      return "ungraded"
    else:
      return ""

  resolver.addResolver("{graded}", "Graded state based on the Graded Tag (graded or ungraded)", lambda keyword, task: grade_state(task) )

# This token only applies to the Shot Processor as it references the shotname
ShotProcessorPreset.addUserResolveEntries = shot_addUserResolveEntries