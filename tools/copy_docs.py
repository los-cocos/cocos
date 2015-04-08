"""
helper for the final release build of cocos

It is meant to be run from a clean clone of cocos repo, specifically
from one of the subdirs tools/ or docgen/

It will copy the sphinx generated documentation from the sphinx dest to
($clone_topdir)\docs\html

After the copy do a docgen/make clean (docgen/Makefile clean) to clean-up
before packaging with setuptools

See workflow in tools\building_release_notes.txt
"""
from __future__ import division, print_function, unicode_literals

import os
import shutil

cwd = os.getcwd()
if os.path.basename(cwd) == 'tools':
    src = "../docgen/_build/html"
elif os.path.basename(cwd) == 'docgen':
    src = "_build/html"
else:
    print("This command must be run from the tools/ or docgen/ directory.")
    sys.exit(1)

if not os.path.isdir(src):
    print("Error, directory %s must exist, probably need to build docs.")
    sys.exit(1)

top_dir = "../"
dst = os.path.join(top_dir, "docs/html")

if os.path.exists(dst):
    shutil.rmtree(dst)

shutil.copytree(src, dst)

print("*** Done ***")
