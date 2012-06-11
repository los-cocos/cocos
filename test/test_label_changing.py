# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#
testinfo = "s, t 5, s, t 10.1, s, q"
tags = "Label, color, text"

import time
import random

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import Rotate
from cocos.text import Label

import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()
        self.color = [127, 127, 127, 255]

        self.label = Label(time.ctime(), (x/2, y/2))
        self.label.do( Rotate( 360, 10 ) )
        self.add( self.label  )

        self.schedule_interval(self.update_time, .1)

    def update_time(self, dt):
        self.label.element.text = time.ctime()
        self.color[:3] = [self._change_color(self.color[i]) for i in range(3)]
        self.label.element.color = self.color

    def _change_color(self, old_color):
        new_color = old_color + random.randint(-10, 10)
        if new_color > 255:
            new_color = 255
        if new_color < 0:
            new_color = 0
        return new_color

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
