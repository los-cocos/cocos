from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1, s, t 2, s, t 3, s, t 4, s, t 5.1, s, t 5.5, s, q"
tags = "loop"

import cocos
from cocos.director import director
from cocos.actions import loop, MoveBy
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite1 = Sprite('grossini.png', (0, y // 3))
        self.add( self.sprite1 )
        self.sprite1.do( MoveBy((x/10,0),1) * 5 )

        self.sprite2 = Sprite('grossini.png', (0, y*2 // 3))
        self.add( self.sprite2 )
        self.sprite2.do( loop(MoveBy((x/10,0),1), 5) )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
