from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "Canvas, line_to"

import cocos
from cocos.director import director
from cocos import draw
import pyglet

import random
ri = random.randint

class TestFigure(draw.Canvas):
    def render(self):
        x,y = director.get_window_size()

        for i in range(100):
            start = ri(0,640), ri(0,480)
            end = ri(0,640), ri(0,480)
            color = ri(00,255),ri(00,255),ri(00,255),ri(00,255)
            width = ri(1,20)
            if (random.random() < 0.3) :
                self.set_color( color )
                self.set_stroke_width( width )
                self.move_to( start )
            self.line_to( end  )


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        self.add( TestFigure() )
        self.schedule( lambda x: 0 )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
