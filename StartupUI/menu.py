import hiero.core
import hiero.ui

def makeMenuBarMenus(event):
  mb = hiero.ui.menuBar()
  menus = ['File','Edit','View','Clip','Project','Timeline','Cache']
  acts = event.menu.actions()
  for act in acts:
    event.menu.removeAction(act)

  for menu in menus:
    m = hiero.ui.findMenuAction(menu)

    event.menu.addMenu(m.menu())

hiero.core.events.registerInterest('kShowContextMenu',makeMenuBarMenus)