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

from shutil import copytree, copy2, rmtree, move, copymode, copystat
from argparse import ArgumentParser
from os import path, remove, makedirs, walk, mkdir, umask
from l_filecmp import dircmp, filecmp
from time import time

version = '0.3.0'

def printifverbose(string, vlevel):
  if args.verb >= vlevel:
    print(string)

def makedirs_mode(source, target):
  mysource = path.abspath(source).split('/')
  mytarget = path.abspath(target).split('/')
  commons = 0
  while (mysource[-1*(commons+1)] == mytarget[-1*(commons+1)]) and (commons < min(len(mysource), len(mytarget))):
    commons += 1
  if commons:
    targetline =  '/'.join(mytarget[:(-1*commons)])
    sourceline =  '/'.join(mysource[:(-1*commons)])
  else:
    targetline =  '/'.join(mytarget)
    sourceline =  '/'.join(mysource)
  if (not path.exists(targetline)):
    makedirs(targetline)
  for i in range(commons):
    targetline += ('/' + mytarget[i-commons])
    sourceline += ('/' + mysource[i-commons])
    if (not path.exists(targetline)):
      oldmask = umask(000)
      mkdir(targetline, 0o0777)
      copymode(sourceline, targetline)
      umask(oldmask)

def process_one(source, target, diffdir=None):
  if path.isfile(source):
    printifverbose('Checking File: ' + source, 4)
    if path.exists(target):
      if not filecmp(source, target):
        printifverbose('Updating File: ' + target, 2)
        if diffdir:
          makedirs_mode(path.dirname(target), diffdir + path.abspath(path.dirname(source)))
          copy2(target, diffdir + path.abspath(source))
          copymode(target, diffdir + path.abspath(source))
        if args.verb >= 7:
          ts = time()
        copy2(source, target)
        if args.verb >= 7:
          print('*** Timing copy2', time() - ts)
          ts = time()
        copymode(source, target)
        if args.verb >= 7:
          print('*** Timing copymode', time() - ts)
    else:
      printifverbose('Creating File: ' + target, 2)
      if args.verb >= 7:
        ts = time()
      makedirs_mode(path.dirname(source), path.dirname(target))
      if args.verb >= 7:
        print('*** Timing makedirs_mode', time() - ts)
        ts = time()
      copy2(source, target)
      if args.verb >= 7:
        print('*** Timing copy2', time() - ts)
        ts = time()
      copymode(source, target)
      if args.verb >= 7:
        print('*** Timing copymode', time() - ts)
  elif path.isdir(source):
    printifverbose('Checking Dir: ' + source, 4)
    if not path.exists(target):
      makedirs_mode(source, target)
    if args.verb >= 7:
      ts = time()
    dcmp = dircmp(source, target)
    if args.verb >= 7:
      print('*** Timing dircmp', time() - ts)
    printifverbose('Directories:', 5)
    printifverbose('Source only: ' + str(dcmp.results['dirleft']), 5)
    printifverbose('Both: ' + str(dcmp.results['dirboth']), 5)
    printifverbose('Target only: ' + str(dcmp.results['dirright']), 5)
    printifverbose('Files:', 5)
    printifverbose('Source only: ' + str(dcmp.results['fileleft']), 5)
    printifverbose('Equal: ' + str(dcmp.results['fileequal']), 5)
    printifverbose('Different: ' + str(dcmp.results['filedifferent']), 5)
    printifverbose('Target only: ' + str(dcmp.results['fileright']), 5)
    for item in (dcmp.results['dirleft']):
      skipit = False
      if exclude is not None:
        for exitem in exclude:
          if path.abspath(source + '/' + item) == path.abspath(exitem):
            skipit = True
      if keywordex is not None:
        for exitem in keywordex:
          if item == exitem:
            skipit = True
      if skipit:
        printifverbose('Skipped Dir:' + source + '/' + item, 3)
      else:
        printifverbose('Creating Dir: ' + target + '/' + item, 2)
        if args.verb >= 7:
          ts = time()
        mkdir(target + '/' + item)
        if args.verb >= 7:
          print('*** Timing mkdir', time() - ts)
          ts = time()
        copymode(source + '/' + item, target + '/' + item)
        if args.verb >= 7:
          print('*** Timing copymode', time() - ts)
        if diffdir:
          process_one(source + '/' + item, target + '/' + item, diffdir + '/' + item)
        else:
          process_one(source + '/' + item, target + '/' + item)
    for item in (dcmp.results['dirboth']):
      if diffdir:
        process_one(source + '/' + item, target + '/' + item, diffdir + '/' + item)
      else:
        process_one(source + '/' + item, target + '/' + item)
    for item in (dcmp.results['dirright']):
      if diffdir:
        if not path.exists(diffdir + path.abspath(source)):
          makedirs_mode(target, diffdir + path.abspath(source))
        elif path.exists(diffdir + path.abspath(source) + '/' + item):
          rmtree(diffdir + path.abspath(source) + '/' + item)
        copytree(target + '/' + item, diffdir + path.abspath(source) + '/' + item)
        copymode(target + '/' + item, diffdir + path.abspath(source) + '/' + item)
      printifverbose('Deleting Dir: ' + target + '/' + item, 2)
      if args.verb >= 7:
        ts = time()
      rmtree(target + '/' + item)
      if args.verb >= 7:
        print('*** Timing rmtree', time() - ts)
    for item in (dcmp.results['fileleft']):
      skipit = False
      if exclude is not None:
        for exitem in exclude:
          if path.abspath(source + '/' + item) == path.abspath(exitem):
            skipit = True
      if keywordex is not None:
        for exitem in keywordex:
          if item == exitem:
            skipit = True
      if skipit:
        printifverbose('Skipped File:' + source + '/' + item, 3)
      else:
        printifverbose('Creating File: ' + target + '/' + item, 2)
        if args.verb >= 7:
          ts = time()
        copy2(source + '/' + item, target + '/' + item)
        if args.verb >= 7:
          print('*** Timing copy2', time() - ts)
          ts = time()
        copymode(source + '/' + item, target + '/' + item)
        if args.verb >= 7:
          print('*** Timing copymode', time() - ts)
    for item in (dcmp.results['filedifferent']):
      skipit = False
      if exclude is not None:
        for exitem in exclude:
          if path.abspath(source + '/' + item) == path.abspath(exitem):
            skipit = True
      if keywordex is not None:
        for exitem in keywordex:
          if item == exitem:
            skipit = True
      if skipit:
        printifverbose('Skipped File:' + source + '/' + item, 3)
      else:
        if diffdir:
          if not path.exists(diffdir + path.abspath(source)):
            makedirs_mode(target, diffdir + path.abspath(source))
          copy2(target + '/' + item, diffdir + path.abspath(source) + '/' + item)
          copymode(target + '/' + item, diffdir + path.abspath(source) + '/' + item)
        printifverbose('Updating File: ' + target + '/' + item, 2)
        if args.verb >= 7:
          ts = time()
        copy2(source + '/' + item, target + '/' + item)
        if args.verb >= 7:
          print('*** Timing copy2', time() - ts)
          ts = time()
        copymode(source + '/' + item, target + '/' + item)
        if args.verb >= 7:
          print('*** Timing copymode', time() - ts)
    for item in (dcmp.results['fileright']):
      if diffdir:
        if not path.exists(diffdir + path.abspath(source)):
          makedirs_mode(target, diffdir + path.abspath(source))
        copy2(target + '/' + item, diffdir + path.abspath(source) + '/' + item)
        copymode(target + '/' + item, diffdir + path.abspath(source) + '/' + item)
      printifverbose('Deleting File: ' + target + '/' + item, 2)
      if args.verb >= 7:
        ts = time()
      remove(target + '/' + item)
      if args.verb >= 7:
        print('*** Timing remove', time() - ts)

parser = ArgumentParser()
parser.add_argument("-s", "--source", dest="sourcedir", default = "")
parser.add_argument("-t", "--target", dest="targetdir", default = "target")
parser.add_argument("-d", "--diff", dest="diffdir")
parser.add_argument("-n", "--numdiff", dest="numdiff", default = "9", type=int)
parser.add_argument("-v", "--verb", dest="verb", default = "2", type=int)
parser.add_argument("-e", "--exclude", dest="exclude")
parser.add_argument("-k", "--keywordex", dest="keywordex")
args = parser.parse_args()

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
  if args.diffdir:
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
      makedirs_mode(root, rootto)
      for file in files:
        copy2(root+'/'+file, rootto+'/'+file)
        copymode(root+'/'+file, rootto+'/'+file)


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
    process_one(sourcedir, targetdir)


  printifverbose('Done...', 1)
else:
  printifverbose('Source dir does not exist: '+sourcedir, 1)
  printifverbose('Specify source dir with -s example/mysourcedir', 1)
