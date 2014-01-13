from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.1, s, t 2.1, s, t 3.1, s, q"
tags = "Label, color, text"


import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import Rotate, Repeat, Delay, CallFunc
from cocos.text import Label


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()
        self.color1 = [255, 0, 0, 255]
        self.color2 = [0, 0, 255, 255]

        self.label = Label('', (x//2, y//2))
        self.label.do( Rotate( 360, 10 ) )
        self.label.do( Repeat( Delay(1) + CallFunc(self.set_color, 0) +
                               Delay(1) + CallFunc(self.set_color, 1) +
                               Delay(1) + CallFunc(self.set_color, 2)
                              )) 
        self.add(self.label)
        self.set_color(2)

    def set_color(self, color_selector):
        colors = [ (255, 32, 64, 255), (0, 240, 100, 255), (90, 90, 250, 255) ]
        color = colors[color_selector]
        text = "(%s, %s, %s, %s)"%color
        self.label.element.text = text
        self.label.element.color = color

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
