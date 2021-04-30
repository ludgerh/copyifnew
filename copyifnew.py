# Copyright (C) 2021 Ludger Hellerhoff, ludger@booker-hellerhoff.de
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from shutil import copytree, copy2, rmtree, move
from argparse import ArgumentParser
from os import path, remove, makedirs, walk
from filecmp import dircmp, cmp

version = '0.1.5'

def printifverbose(string, vlevel):
  if args.verb >= vlevel:
    print(string)


def process_one(source, target, diff, dcompobj=None):
  if path.isfile(source):
    printifverbose('Checking File: ' + source, 4)
    if path.exists(target):
      if not cmp(source, target):
        printifverbose('Updating File: ' + target, 2)
        try:
          copy2(source, target)
        except PermissionError:
          printifverbose('*** Permission Error', 1)
    else:
      printifverbose('Creating File: ' + target, 2)
      try:
        makedirs(path.dirname(target), exist_ok=True)
        copy2(source, target)
      except PermissionError:
        printifverbose('*** Permission Error', 1)
  else:
    printifverbose('Checking Dir: ' + source, 4)
    if not path.exists(target):
      makedirs(target)
    if dcompobj is None:
      dcmp = dircmp(source, target)
    else:
      dcmp = dcompobj 
    printifverbose(('Source only: ' + str(len(dcmp.left_only)) + '   '
      + 'Target only: ' + str(len(dcmp.right_only)) + '   '
      + 'Same files: ' + str(len(dcmp.same_files)) + '   '
      + 'Different files: ' + str(len(dcmp.diff_files)))
      , 5)
    if (len(dcmp.common_dirs) > 0) and (args.verb >= 5):
      print('***',dcmp.common_dirs)
    try:
      my_right_only = dcmp.right_only
    except PermissionError:
      printifverbose('*** Permission Error while scanning Dir', 1)
      my_right_only = []
    for i in my_right_only:
      newtarget = target+'/'+i
      if dodiff:
        newdiff = diff+'/'+i
      if path.isfile(newtarget):
        if dodiff:
          makedirs(path.dirname(newdiff), exist_ok=True)
          copy2(newtarget, newdiff)
        printifverbose('Deleting File: ' + newtarget, 2)
        remove(newtarget)
      elif path.isdir(newtarget):
        if dodiff:
          makedirs(newdiff, exist_ok=True)
          rmtree(newdiff)
          copytree(newtarget,newdiff)
        printifverbose('Deleting Dir: ' + newtarget, 2)
        rmtree(newtarget)

    try:
      my_left_only = dcmp.left_only
    except PermissionError:
      printifverbose('*** Permission Error while scanning Dir', 1)
      my_left_only = []
    for i in my_left_only:
      newsource = source+'/'+i
      newtarget = target+'/'+i
      if dodiff:
        newdiff = diff+'/'+i
      else:
        newdiff = None
      if path.islink(newsource):
        printifverbose('Did not follow link:' + newsource, 1)
      else:
        newtarget = target+'/'+i
        if path.isfile(newsource):
          printifverbose('Creating File: ' + newtarget, 2)
          try:
            copy2(newsource, target)
          except PermissionError:
            printifverbose('*** Permission Error', 1)
        elif path.isdir(newsource):
          skipit = False
          if exclude is not None:
            for item in exclude:
              if path.abspath(newsource) == item:
                skipit = True
          if keywordex is not None:
            for item in keywordex:
              if newsource[(-1*len(item)-1):] == ('/'+item):
                skipit = True
          if skipit:
            printifverbose('Skipped Dir:' + newsource, 3)
          else:
            printifverbose('Creating Dir: ' + newtarget, 2)
            process_one(newsource, newtarget, newdiff)

    try:
      my_diff_files = dcmp.diff_files
    except PermissionError:
      printifverbose('*** Permission Error while scanning Dir', 1)
      my_diff_files = []
    for i in my_diff_files:
      newsource = source+'/'+i
      newtarget = target+'/'+i
      if dodiff:
        newdiff = diff+'/'+i
        makedirs(path.dirname(newdiff), exist_ok=True)
        copy2(newtarget, newdiff)
      printifverbose('Updating File: ' + newtarget, 2)
      try:
        copy2(newsource, target)
      except PermissionError:
        printifverbose('*** Permission Error', 1)

    for i in dcmp.common_dirs:
      newsource = source+'/'+i
      newtarget = target+'/'+i
      if dodiff:
        newdiff = diff+'/'+i
        process_one(newsource, newtarget, newdiff, dcmp.subdirs[i])
      else:
        process_one(newsource, newtarget, None, dcmp.subdirs[i])


parser = ArgumentParser()
parser.add_argument("-s", "--source", dest="sourcedir", default = "")
parser.add_argument("-t", "--target", dest="targetdir", default = "target")
parser.add_argument("-d", "--diff", dest="diffdir")
parser.add_argument("-n", "--numdiff", dest="numdiff", default = "9", type=int)
parser.add_argument("-v", "--verb", dest="verb", default = "2", type=int)
parser.add_argument("-e", "--exclude", dest="exclude")
parser.add_argument("-k", "--keywordex", dest="keywordex")
args = parser.parse_args()

dodiff = (args.diffdir is not None)
sourcedir = args.sourcedir

if args.exclude is None:
  exclude = None
else:
  exclude = [path.abspath(x) for x in args.exclude.split(",")]

if args.keywordex is None:
  keywordex = None
else:
  keywordex = args.keywordex.split(",")

if path.exists(sourcedir):	
  targetdir = args.targetdir
  if dodiff:
    diffdir = args.diffdir
    numdiff = args.numdiff
    printifverbose('copyifnew:  source = '+sourcedir+'  target = '+targetdir
      +'  diff = '+diffdir+'  ndiff = '+str(numdiff), 1)
    printifverbose('version: '+version, 1)
    makedirs(diffdir+'/'+str(numdiff), exist_ok=True)

    copysource = diffdir+'/'+str(numdiff-1)	
    copytarget = diffdir+'/'+str(numdiff)	
    for root, _, files in walk(copysource):
      rootto = root.replace(copysource, copytarget, 1)
      makedirs(rootto, exist_ok=True)
      for file in files:
        copy2(root+'/'+file, rootto+'/'+file)


    if path.exists(diffdir+'/'+str(numdiff-1)):	
      rmtree(diffdir+'/'+str(numdiff-1))
    for i in range(numdiff-2,0,-1):
      if path.exists(diffdir+'/'+str(i)):	
        move(diffdir+'/'+str(i), diffdir+'/'+str(i+1))
    makedirs(diffdir+'/1', exist_ok=True)
    process_one(sourcedir, targetdir, diffdir+'/1')
  else:
    printifverbose('copyifnew:  source = '+sourcedir+'  target = '+targetdir, 1)
    printifverbose('version: '+version, 1)
    process_one(sourcedir, targetdir, None)


  printifverbose('Done...', 1)
else:
  printifverbose('Source dir does not exist: '+sourcedir, 1)
  printifverbose('Specify source dir with -s example/mysourcedir', 1)
