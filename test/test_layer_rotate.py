# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import RotateBy
from cocos.sprite import Sprite
from cocos.layer import *
import pyglet

if __name__ == "__main__":
    director.init()
    main_scene = cocos.scene.Scene()
    test_layer = ColorLayer(64,64,64,255)
    test_layer.scale = 0.75
    main_scene.add( test_layer )

    test_layer.do( RotateBy( 360, 2 ) )
    director.run (main_scene)
