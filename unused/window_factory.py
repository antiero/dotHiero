# This stuff to go into hiero.ui....
import hiero.core
import hiero.ui
import PySide.QtGui

# Example code for users....
def webBrowserFactory(id, *args, **kwds):
  import PySide.QtWebKit
  w = PySide.QtWebKit.QWebView()
  w.setObjectName(id);
  w.load( PySide.QtCore.QUrl(args[0]) )
  return w

hiero.ui.registerWindow('blah.web-browser-foundry', webBrowserFactory, 'The Foundry on the Web', None, 'http://www.thefoundry.co.uk')
hiero.ui.registerWindow('blah.web-browser-nukepedia', webBrowserFactory, 'Nukepedia', None, 'http://www.nukepedia.com')