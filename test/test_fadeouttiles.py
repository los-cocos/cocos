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

    rr = random.randrange
    for i in range(32):
        l = ColorLayer(rr(0,255),rr(0,255), rr(0,255),255)
        l.scale = (32-i)/32.0
        main_scene.add( l, z=i )

    e = FadeOutTiles( grid=(16,16), duration=2 )
    main_scene.do( e )

    director.run (main_scene)
