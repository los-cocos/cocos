# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import *
import pyglet
        

if __name__ == "__main__":
    director.init()
    bg_layer = cocos.layer.ColorLayer(255,0,0,255)
    translate_layer = cocos.layer.Layer()
    x, y = director.get_window_size()
    sub = cocos.scene.Scene( bg_layer )
    sub.do( MoveBy( (x/2, y/2), 5) )
    sub.do( ScaleBy( 1/2.1, 5) )
    main_scene = cocos.scene.Scene (sub)
    director.run (main_scene)
