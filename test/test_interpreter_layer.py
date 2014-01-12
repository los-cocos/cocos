from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "PythonInterpreterLayer"

import cocos
from cocos.director import director
import pyglet

def main():
    director.init( resizable=True )
    interpreter_layer = cocos.layer.PythonInterpreterLayer()
    main_scene = cocos.scene.Scene(interpreter_layer)
    director.run(main_scene)

if __name__ == '__main__':
    main()
