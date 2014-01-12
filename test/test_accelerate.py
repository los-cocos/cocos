from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 4, s, t 8, s, t 10.1, s, q"
tags = "Accelerate"

import cocos
from cocos.director import director
from cocos.actions import Accelerate, Rotate
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png',  (x//2, y//2)  )
        self.add( self.sprite )
        self.sprite.do( Accelerate( Rotate( 360, 10 ), 4 ) )

description = """
Shows how to use Accelerate to modify an action by changing the time flow.
Accelerate will reparametrize time for the target action.
It should be seen grossini in the screen's center, rotating 360 degrees,
first slowly then faster. 
"""

def main():
    print(description)
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
