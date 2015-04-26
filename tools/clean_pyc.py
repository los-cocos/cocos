"""recursive delete of *.pyc files and __pycache__"""
from __future__ import division, print_function, unicode_literals

import sys, os, shutil

if len(sys.argv)<2:
    print("Recursively erases al *.pyc files under the topdir")
    print("\nUsage:\n\t%s topdir"%os.path.basename(sys.argv[0]))
    sys.exit(1)
    
target_dir=sys.argv[1]
if not os.path.isdir(target_dir):
    print("Not a directory:", target_dir)
    sys.exit(1)

toClean = [target_dir]
while toClean:
    d = toClean.pop()
    dl = [ (os.path.join(d,f)) for f in os.listdir(d)]
    files = [ (f) for f in dl if f.endswith('.pyc') and not os.path.isdir(f)]
    for f in files:
        os.remove(f)
    dirs = [ (f) for f in dl if os.path.isdir(f) ]
    dirs_pycache = [ d for d in dirs if os.path.basename(d)=="__pycache__" ]
    for d in dirs_pycache:
        shutil.rmtree(d)
    dirs = list(set(dirs) - set(dirs_pycache))
    toClean.extend(dirs)
print ('*** Done.')
