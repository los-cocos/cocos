from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 2, s, t 4, s, q"
tags = "schedule, position"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
import random
from math import sin, cos

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        self.sprite = Sprite('grossini.png')
        self.add( self.sprite  )

        w,h = director.get_window_size()
        self.radius = h/3.0
        self._elapsed = 0.0
        self.schedule( self.change_sprite_pos )
        self.change_sprite_pos(0.0)

    def change_sprite_pos(self, dt):
        self._elapsed += dt
        w,h = director.get_window_size()
        self.sprite.position = ( w//2 + self.radius * cos(self._elapsed * 1.5),
                                 h//2 + self.radius * sin(self._elapsed * 1.5))

description = """
Grossini sprite will circle around the center of the screen
"""

def main():
    print(description)
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
