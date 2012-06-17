# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#
testinfo = "s, t 5, s, t 10.1, s, q"
tags = "Label, color, text"


import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import Rotate
from cocos.text import Label


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()
        self.color1 = [255, 0, 0, 255]
        self.color2 = [0, 0, 255, 255]

        self.label = Label('', (x//2, y//2))
        self.label.do( Rotate( 360, 10 ) )
        self.add( self.label  )
        self._elapsed = 0.0

        self.schedule_interval(self.update_time, .1)

    def update_time(self, dt):
        self._elapsed += dt 
        self.label.element.text = "%03d ms"%int(self._elapsed*1000)
        r = (self._elapsed*0.2) % 1.0
        r = 4.0 * r * (1.0 - r)
        color = [int(r*self.color1[i] + (1.0 - r) * self.color2[i])
                                                          for i in range(4)]
        self.label.element.color = color

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
