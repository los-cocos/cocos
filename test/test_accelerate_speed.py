from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 2, s, t 5, s, t 8, s, t 10.1, s, q"
tags = "Speed, Accelerate"

import cocos
from cocos.director import director
from cocos.actions import Accelerate, Speed, Rotate
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite1 = Sprite( 'grossini.png', (x//4, y//2) )
        self.add( self.sprite1  )
        self.sprite2 = Sprite( 'grossini.png', ((x//4)*3, y//2)  )
        self.add( self.sprite2 )

        self.sprite1.do( Accelerate( Speed( Rotate( 360, 1 ), 0.1 ), 4)  )
        self.sprite2.do( Speed( Accelerate( Rotate( 360, 1 ), 4 ), 0.1)  )

description = """
Shows how to use Speed to modify an action duration.
Speed will multiply by a factor the duration of the target action.
It should be seen two grossinis, rotating 360 degrees, first slowly
then faster. 
"""

def main():
    print(description)
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene ()
    main_scene.add(test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
