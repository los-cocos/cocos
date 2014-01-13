from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.1, s, t 2.1, s, t 3.1, s, q"
tags = "schedule_interval, position"

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
        self.coords_from_corner = [(0, 0), (0, h), (w, h), (w, 0)]
        self.corner = 0
        self.schedule_interval( self.change_sprite_pos, 1 )
        self.change_sprite_pos(0.0)
        self.schedule(lambda x:0)

    def change_sprite_pos(self, dt):
        self.sprite.position = self.coords_from_corner[self.corner]
        self.corner = (self.corner + 1) % len(self.coords_from_corner)

description = """
Grossini sprite will change position each second, showing at the screen corners
"""

def main():
    print(description)
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
