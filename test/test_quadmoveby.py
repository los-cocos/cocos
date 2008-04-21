# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *
import pyglet

from cocos.mesh import *

if __name__ == "__main__":
    director.init( resizable=True )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    red = ColorLayer(255, 0, 0, 255)
    blue = ColorLayer(0, 0,255, 255)
    blue.scale = 0.75
    green = ColorLayer(0, 255, 0, 255)
    green.scale = 0.5
    white = ColorLayer(255, 255, 255, 255)
    white.scale = 0.25
    
    main_scene.add( red, z=0 )
    main_scene.add( blue, z=1)
    main_scene.add( green, z=2)
    main_scene.add( white, z=3)

    move = QuadMoveBy( delta0=(320,240), delta1=(-630,0), delta2=(-320,-240), delta3=(630,0), duration=2 )
#    move = QuadMoveBy( delta0=(640,480), delta1=(-640,480), delta2=(-640,-480), delta3=(640,-480), duration=2 )

#    main_scene.do( move + Reverse(move) )
    main_scene.do( move )

    director.run (main_scene)
