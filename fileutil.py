import shutil
from pathlib import Path

class Path_Util:
    _path = None

    def __init__ (self, dir=None):
        self._path = dir

    def exists(self):
        return (Path(self._path).exists())

    def mkdir(self, subfolder):
        newpath = self._path + '/' + subfolder
        Path(newpath).mkdir()
        return (newpath)

    def move(self, sourcefn, destdir):
        sourcefile = self._path+'/'+sourcefn
        destfile = destdir + '/' + sourcefn
        shutil.move(sourcefile, destfile)