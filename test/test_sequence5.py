from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 4.9, s, t 5.1, s, t 10.1, s, t 10.2, s, q"
tags = "MoveBy, spawn"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import Place, MoveBy, Hide

import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (0,y//2)  )
        self.add( self.sprite )
        self.sprite.do( MoveBy( (x//2, 0) ) * 2 )

description = """
Starting from left border, sprites moves
two times screen_width/2 to the right."""

def main():
    print(description)
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
