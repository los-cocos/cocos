from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "transform_anchor, scale, zoom"

import cocos
from cocos.director import director
from cocos.sprite import *
from cocos.layer import *
import pyglet

def main():
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()

    white = ColorLayer(255,255,255,255)
    red = ColorLayer(255,0,0,255)
    blue = ColorLayer(0,0,255,255)
    green = ColorLayer(0,255,0,255)

    x, y = director.get_window_size()

    red.scale = 0.75
    blue.scale = 0.5
    blue.transform_anchor = 0, 0
    green.scale = 0.25
    green.transform_anchor = x,y

    red.add( Sprite( 'grossini.png', (0, y//2) ), z=1 )
    blue.add( Sprite( 'grossini.png', (0, y//2) ), z=1 )
    green.add( Sprite( 'grossini.png', (0, y//2) ), z=1 )
    red.add( Sprite( 'grossini.png', (x, y//2) ), z=1 )
    blue.add( Sprite( 'grossini.png', (x, y//2) ), z=1 )
    green.add( Sprite( 'grossini.png', (x, y//2) ), z=1 )

    main_scene.add( white, z=0 )
    main_scene.add( red, z=1 )
    main_scene.add( blue, z=2 )
    main_scene.add( green, z=3 )

    director.run (main_scene)

if __name__ == '__main__':
    main()
