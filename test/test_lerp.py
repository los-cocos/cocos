from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 5, s, t 10.1, s, q"
tags = "Lerp"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import Lerp
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite('grossini.png')
        self.sprite.position = 0, y//2
        self.add( self.sprite  )

        self.sprite.do( Lerp("x", 0, x, 10) )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
