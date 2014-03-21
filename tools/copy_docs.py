"""
helper for the final release build of cocos

It is meant to be run from a working copy or export of trunk, speifically
from one of the subdirs tools/ or docgen/

It will copy generated documentation to the harcoded destination ..\cocos_build
where the setuptools build is supossed to be generated.

See workflow in tools\building_release_notes.txt
"""
from __future__ import division, print_function, unicode_literals

import os
import shutil

build_dir = "../../cocos_build"
if not os.path.isdir(build_dir):
    print("Error, directory %s must exist")
    sys.exit(1)
dst = os.path.join(build_dir, "doc/html")

cwd = os.getcwd()
if os.path.basename(cwd) == 'tools':
    src = "../docgen/_build/html"
elif os.path.basename(cwd) == 'docgen':
    src = "_build/html"
else:
    print("This command must be run from the tools/ or docgen/ directory")
    sys.exit(1)

if os.path.exists(dst):
    shutil.rmtree(dst)

shutil.copytree(src, dst)

print("*** Done ***")
