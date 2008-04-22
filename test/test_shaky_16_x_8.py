# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *

if __name__ == "__main__":
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()

    red = ColorLayer(255, 0, 0, 255)
    blue = ColorLayer(0, 0, 255, 255)
    green = ColorLayer(0, 255, 0, 255)
    white = ColorLayer(255, 255, 255, 255)

    blue.scale = 0.75
    green.scale = 0.5
    white.scale = 0.25

    main_scene.add( red, z=0 )
    main_scene.add( blue, z=1)
    main_scene.add( green, z=2)
    main_scene.add( white, z=3)

    main_scene.do( Shaky( randrange=6, grid=(16,8), duration=5) )

    director.run (main_scene)
