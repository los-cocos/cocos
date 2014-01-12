from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 5, s, t 10.1, s, q"
tags = "Label, text, ScaleTo"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import *
from cocos.text import *

import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.text = Label("hello", (x//2, y//2))
        self.text.do( Rotate( 360, 10 ) )
        self.text.do( ScaleTo( 10, 10 ) )
        self.add( self.text  )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
