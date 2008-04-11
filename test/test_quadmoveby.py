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

    red = ColorLayer(1.0, 0.0, 0.0, 1.0)
    blue = ColorLayer(0.0, 0.0, 1.0, 1.0)
    green = ColorLayer(0.0, 1.0, 0.0, 1.0)
    white = ColorLayer(1.0, 1.0, 1.0, 1.0)

    main_scene.add( red, z=0 )
    main_scene.add( blue, z=1, scale=0.75 )
    main_scene.add( green, z=2, scale=0.5 )
    main_scene.add( white, z=3, scale=0.25 )

    move = QuadMoveBy( (320,240), (-630,0), (-320,-240),(630,0), duration=2 )

    main_scene.do( move )

    director.run (main_scene)
