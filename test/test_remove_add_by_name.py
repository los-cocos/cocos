from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

# This test is not suitable for autotest because the significative info
# produced is a traceback, and autotest collects but not analize tracebacks
# So no testinfo here
tags = "name"

import cocos
from cocos.director import director
from cocos.layer import *

def main():
    print("expected to fail")
    print("with traceback ... :Exception: Name already exists: color")

    director.init( resizable=True )

    main_scene = cocos.scene.Scene()
    color = ColorLayer(255,0,0,255)
    main_scene.add( color, name='color' )

    # this one doesn't remove it's name
    main_scene.remove(color)

    # this one works
    #main_scene.remove('color')
    main_scene.add( color, name='color' )

if __name__ == '__main__':
    main()
