from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1, s, t 2.5, s, t 5, s, t 7.5, s, t 10.1, s, q"
tags = "CocosNode, Sprite, child, rotation, position, Rotate, ScaleBy"

import cocos
from cocos.director import director
from cocos.actions import  Rotate, MoveBy, ScaleBy
from cocos.sprite import Sprite

import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (x//2, y//2) )
        self.add( self.sprite )

        self.sprite2 = Sprite( 'grossinis_sister1.png',  (0, 101) )
        self.sprite.add( self.sprite2 )

        self.sprite3 = Sprite( 'grossinis_sister2.png', (0, 102) )
        self.sprite2.add( self.sprite3 )

        self.sprite.do( Rotate(360,10) )
        self.sprite2.do( ScaleBy(2,5)+ScaleBy(0.5,5) )
        self.sprite2.do( Rotate(360,10) )
        self.sprite3.do( Rotate(360,10) )
        self.sprite3.do( ScaleBy(2,5)+ScaleBy(0.5,5) )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
