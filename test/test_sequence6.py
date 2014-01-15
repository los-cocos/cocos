from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1, s, t 1.05, s, t 1.15, s, t 1.20, s, q"
tags = "MoveBy, spawn"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import Place, MoveBy, MoveTo, Repeat, Reverse

import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (x//4,y//2)  )
        self.add( self.sprite )
        shake_part = MoveBy((-4.0, 0.0), 0.05)
        shake = shake_part + Reverse(shake_part)*2 + shake_part
        self.sprite.do( MoveTo( (x//2, y//2), 1 ) + Repeat( shake ) )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
