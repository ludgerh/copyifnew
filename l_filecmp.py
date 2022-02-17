from os import path, scandir, stat
from time import time

class CannotCompareFileException(Exception):
  def __init__(self, source, target):
    self.source = source
    self.target = target

class NoFileJustDirsException(Exception):
  def __init__(self, source):
    self.source = source

class NoDirJustFilesException(Exception):
  def __init__(self, source):
    self.source = source

class NoSymlinksHereException(Exception):
  def __init__(self, source):
    self.source = source

class PathDoesNotExistException(Exception):
  def __init__(self, source):
    self.source = source

def filecmp(left, right):
  if not path.isfile(left):
    raise NoDirJustFilesException(left)
  if not path.isfile(right):
    raise NoDirJustFilesException(right)
  leftstats = stat(left)
  rightstats = stat(right)
  return((leftstats.st_mtime_ns//1000 == rightstats.st_mtime_ns//1000) and (leftstats.st_size == rightstats.st_size))
    


class dircmp():
  def __init__(self, leftpath, rightpath, symlinks=False):
    if not path.isdir(leftpath):
      raise NoFileJustDirsException(leftpath)
    if not path.exists(rightpath):
      raise PathDoesNotExistException(rightpath)
    if not path.isdir(rightpath):
      raise NoFileJustDirsException(rightpath)
    if path.islink(leftpath) and (not symlinks):
      raise NoSymlinksHereException(leftpath)
    if path.islink(rightpath) and (not symlinks):
      raise NoSymlinksHereException(rightpath)
    self.results = {}
    self.results['dirleft'] = []
    self.results['dirboth'] = []
    self.results['dirright'] = []
    self.results['fileleft'] = []
    self.results['fileequal'] = []
    self.results['filedifferent'] = []
    self.results['fileright'] = []
    allleft = []
    stat_dict = {}
    with scandir(rightpath) as rightlist:
      for item in rightlist:
        if (not item.is_symlink()) or symlinks: #not tested
          if item.is_file():
            stat_dict[item.name] = item.stat()
    with scandir(leftpath) as leftlist:
      for item in leftlist:
        if (not item.is_symlink()) or symlinks: #not tested
          allleft.append(item.name)
          if item.is_dir():
            if path.exists(rightpath+'/'+item.name):
              self.results['dirboth'].append(item.name)
            else:
              self.results['dirleft'].append(item.name)
          elif item.is_file():
            leftstats = item.stat()
            if item.name in stat_dict:
              rightstats = stat_dict[item.name]
              #print(leftstats.st_mtime_ns//1000, rightstats.st_mtime_ns//1000, leftstats.st_size, rightstats.st_size)
              if (leftstats.st_mtime_ns//1000 == rightstats.st_mtime_ns//1000) and (leftstats.st_size == rightstats.st_size):
                self.results['fileequal'].append(item.name)
              else:
                self.results['filedifferent'].append(item.name)
            else:
              self.results['fileleft'].append(item.name)
    with scandir(rightpath) as rightlist:
      for item in rightlist:
        if (not item.is_symlink()) or symlinks: #not tested
          if item.is_dir():
            if not item.name in allleft:
              self.results['dirright'].append(item.name)
          elif item.is_file():
            if not item.name in allleft:
              self.results['fileright'].append(item.name)
    
    
      

