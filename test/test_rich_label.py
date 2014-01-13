from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 5, s, t 10.1, s, q"
tags = "RichLabel"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import *
from cocos.text import *

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.text = RichLabel(
        "Hello {color (255, 0, 0, 255)}World!",
        (x//2, y//2))
        self.text.element.document.set_style(0, 5, dict(bold = True))
        self.text.element.document.set_style(6, 11, dict(italic = True))

        self.text.do( Rotate( 360, 10 ) )
        self.text.do( ScaleTo( 10, 10 ) )
        self.add( self.text  )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
