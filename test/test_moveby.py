from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 3, s, t 6.1, s, q"
tags = "MoveBy"

import cocos
from cocos.director import director
from cocos.actions import  MoveBy
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (x//2, y//2) )
        self.add( self.sprite, name='sprite' )
        self.sprite.do( MoveBy( (x//2,y//2), 6 ) )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene()
    main_scene.add(test_layer, name='test_layer')
    director.run (main_scene)

if __name__ == '__main__':
    main()
