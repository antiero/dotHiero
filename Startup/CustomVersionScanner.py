import hiero.core

def myNextVersion(self):
    print 'next next next'
def myMinVersion(self):
    print 'min min min'

hiero.core.VersionScanner.BinItem.minVersion = myMinVersion
hiero.core.VersionScanner.BinItem.nextVersion = myNextVersion