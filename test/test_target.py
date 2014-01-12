from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "dt 0.1, q"
tags = "debugging"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import *
import pyglet

class Dummy:
    """
    A CocosNode proxy that only offers the members a particular action needs
    and prints to stdout the changes made for the action in those members.

    Here is special cased to Rotate.

    Notice that changes produced by the action don't reachs the cocosnode
    """
    rotation = 0

    def __setattr__(self, attr, value):
        print("set", attr, "to", value)

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite('grossini.png')
        self.sprite.position = x//2, y//2
        self.add( self.sprite  )

        self.sprite.do( Rotate(90, 3), Dummy() )

description = """
Shows in the console the changes in a CocosNode instance produced by the a
Rotate action.

The node (grossini sprite) does not rotate on screen as a side effect of
the interception.

Variants of this could come handy for debugging, testing. 
"""

def main():
    print(description)
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
