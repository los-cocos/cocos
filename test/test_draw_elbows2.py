from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "Draw, join"

import cocos
from cocos.director import director
from cocos import draw
import pyglet


class TestFigure(draw.Canvas):
    def render(self):
        x,y = director.get_window_size()
        ys = y//4
        ye = ys*3
        xs = x//4
        line_width = 50
        self.set_color( (255,255,0,100) )
        self.set_stroke_width( line_width )

        self.set_join( draw.ROUND_JOIN )
        self.move_to( (xs, ys) )
        self.line_to( (xs*2,ys) )
        self.line_to( (xs*3,ys*2) )
        self.line_to( (xs*3+100,ys*2) )





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
