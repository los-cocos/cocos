from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1, s, t 2, s, t 3, s, t 4.1, s, t 4.2, s, q"
tags = "FadeIn, FadeOut, ColorLayer"

import pyglet
from pyglet.gl import *

import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *

def main():
    print(description)
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()

    l = ColorLayer( 255,128,64,64 )
    main_scene.add( l, z=0 )

    l.do( FadeOut( duration=2) + FadeIn( duration=2) )

    director.run (main_scene)

description = """
A ColorLayer is faded-out and fadded-in.
Notice this will not work for arbitrary Layer objects.
"""

if __name__ == '__main__':
    main()
