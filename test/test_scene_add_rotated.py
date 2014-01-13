from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "Scene, rotation"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.layer import *
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()
        sprite1 = Sprite( 'grossini.png' , (x//4, y//2) )
        sprite2 = Sprite( 'grossinis_sister1.png', (x//2, y//2) )
        sprite3 = Sprite( 'grossinis_sister2.png', (x/(4/3.0), y//2) )

        self.add( sprite2 )
        self.add( sprite1 )
        self.add( sprite3 )

def main():
    director.init()
    main_scene = cocos.scene.Scene()
    main_scene.add( ColorLayer( 255, 0, 0, 255 ) )
    l = TestLayer()
    l.rotation = 45
    main_scene.add( l )
    director.run (main_scene)

if __name__ == '__main__':
    main()
