from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.1, s, t 2.1, s, q"
tags = "Canvas"
autotest = 0


import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos import draw
from cocos.actions import Delay, CallFunc
import pyglet

import random
ri = random.randint

class TestFigure(draw.Canvas):
    def render(self):
        x,y = director.get_window_size()
        ys = y//4
        ye = ys*3
        xs = x//4
        line_width = 50
        self.set_color( (255,255,0,180) )
        self.set_stroke_width( line_width )

        # draw lines
        self.set_endcap( draw.ROUND_CAP )
        self.move_to( (x//2, y//2-line_width//2) ); self.line_to( (x//2-300,y//2-300) )


class TestLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super( TestLayer, self ).__init__()

        self.add( TestFigure() )
        self.schedule( lambda x: 0 )
        if autotest:
            self.do(Delay(1.0) + CallFunc(self.upscale) +
                    Delay(1.0) + CallFunc(self.upscale))

    def on_key_press(self, k, mod):
        self.upscale()

    def upscale(self):
        self.scale += 1

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
