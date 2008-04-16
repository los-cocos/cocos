# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import *
from cocos.actions import *
from cocos.layer import *
import pyglet
import random

from cocos.mesh import *

if __name__ == "__main__":
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()

    for i in range(8):
        l = ColorLayer(random.random(), random.random(), random.random(), 1.0)
        scale = (8-i)/8.0
        main_scene.add( l, z=i, scale=scale )

    e = SkewVertical( duration=1 )
    main_scene.do( e )

    director.run( main_scene )
