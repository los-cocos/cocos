from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.1, s, q"
tags = "CallFunc, visible"

import cocos
from cocos.director import director
from cocos.actions import CallFunc, Delay
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (x//2, y//2) )
        self.sprite.visible = False
        self.add( self.sprite )

        def make_visible( sp ):
            sp.visible = True
        self.sprite.do( Delay(1) + CallFunc( make_visible, self.sprite ) )

description = """Sprite grossini starts invisible, after 1 second will turn
visible thanks to action CallFunc
"""

def main():
    print(description)
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
