from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"

import cocos
from cocos.director import director
from cocos import draw
import pyglet, math


class TestFigure(draw.Canvas):
    def render(self):
        x,y = director.get_window_size()
        ye = 15
        xs = 15
        line_width = 35
        self.set_color( (255,255,0,125) )
        self.set_stroke_width( line_width )
        parts = 20
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

        self.add( TestFigure() )
        self.schedule( lambda x: 0 )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
