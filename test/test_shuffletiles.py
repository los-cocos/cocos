# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *
from cocos.sprite import ActionSprite
import pyglet
import random

from cocos.mesh import *


if __name__ == "__main__":
    director.init( resizable=True, fullscreen=False )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    for i in range(16):
        l = ColorLayer(random.random(), random.random(), random.random(), 1.0)
        scale = (16-i)/16.0
        main_scene.add( l, z=i, scale=scale )

    e = ShuffleTiles( grid=(16,8), duration=5 )
    main_scene.do( e )

    director.run (main_scene)
