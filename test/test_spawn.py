from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 5, s, t 10.1, s, t 10.2, s, q"
tags = "spawn, Reverse"

import cocos
from cocos.director import director
from cocos.actions import Rotate, Reverse, MoveBy, Delay
import pyglet
from cocos.sprite import Sprite

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (x//2, y//2) )
        self.add( self.sprite )

        self.sprite2 = Sprite( 'grossini.png', (x//2, y//4) )
        self.add( self.sprite2 )

        seq = Rotate( 360, 10 ) | MoveBy((x//2,0))
        self.sprite.do( seq )
        self.sprite2.do( Reverse( seq ) )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
