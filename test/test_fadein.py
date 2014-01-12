from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 2.5, s, t 5.1, s, t 5.2, s, q"
tags = "FadeIn, opacity"

import cocos
from cocos.director import director
from cocos.actions import FadeIn
from cocos.sprite import Sprite

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (x//2, y//2) )
        self.sprite.opacity = 0
        self.add( self.sprite )
        self.sprite.do( FadeIn( 5 ) )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
