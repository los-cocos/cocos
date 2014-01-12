from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 3, s, t 5.1, s, t 5.2, s, q"
tags = "FadeTo"

import cocos
from cocos.director import director
from cocos.actions import FadeTo
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (x//2, y//2) )
        self.add( self.sprite )
        self.sprite.do( FadeTo(0, 5 ) )

        self.sprite2 = Sprite('grossini.png',  (x//4*3,y//2), opacity=0)
        self.add( self.sprite2 )
        self.sprite2.do( FadeTo(255, 5 ) )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
