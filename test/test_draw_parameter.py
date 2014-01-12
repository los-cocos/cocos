from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.5, s, t 3.1, s, q"
tags = "Draw, parameter"

import cocos
from cocos.director import director
from cocos.actions import Lerp, Reverse, Repeat
from cocos import draw
import pyglet, math


class TestFigure(draw.Canvas):
    line_width = draw.parameter(5)

    def render(self):
        x,y = director.get_window_size()
        ye = 15
        xs = 15
        line_width = self.line_width
        self.set_color( (255,255,0,125) )
        self.set_stroke_width( line_width )
        parts = 5
        # draw lines
        self.set_endcap( draw.ROUND_CAP )
        self.translate(( x//2, y//2 ))
        for j in range(parts):
            self.move_to( (0,0) )
            self.rotate( 2*math.pi/ parts )
            self.push()
            for i in range(parts):
                self.line_to( (xs,ye) )
                self.translate( (xs,ye) )
                self.rotate( math.pi/ parts )
            self.pop()


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        f = TestFigure()
        self.add( f )
        a = Lerp("line_width", 5, 55, 3)
        f.do( Repeat( a + Reverse( a ) ) )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
