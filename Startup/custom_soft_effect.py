# custom_soft_effect.py - Example of registering a custom Soft Effect 
from hiero.ui import registerAction
from PySide.QtGui import QAction, QIcon

# This creates an action with an icon and effect named 'Awesome OCIO'
action = QAction(QIcon("icons:TCStop.png"), "Slug", None)

# Soft effect actions can be found by prefixing the QAction's objectName with: 'foundry.timeline.effect'
action.setObjectName("foundry.timeline.effect.addSlug")

# You can optionally set a tooltip for this action
action.setToolTip("Will apply a Slug Gizmo")

# Setting of Data here will point to the Nuke node class name.
# Here, we assume there is a plugin with a Class name 'AwesomeOCIO'
# Note: for soft effects to work, the Nuke node must use a gpuEngine implementation.
action.setData("Slug")

# This registers your custom action with the Effects Menu
registerAction(action)

# This creates an action with an icon and effect named 'SuperGrade'
action = QAction(QIcon("icons:LUT.png"), "SuperGrade", None)

# Soft effect actions can be found by prefixing the QAction's objectName with: 'foundry.timeline.effect.'
action.setObjectName("foundry.timeline.effect.addCustomGrade")

# You can optionally set a tooltip for this action
action.setToolTip("Will apply a Custom Grade soft effect")

action.setData("SuperGrade")

# This registers your custom action with the Effects Menu
registerAction(action)