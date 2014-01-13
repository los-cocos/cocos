from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

# this test is not suitable for autotest because it uses a special clock
# that clashes with the clock used to autotest. So no testinfo here.
tags = "recorder"

import cocos
from cocos.director import director
from cocos.actions import JumpTo, JumpBy
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (x//5, y//3*2) )
        self.add( self.sprite )
        self.sprite.do( JumpTo( (x//5*4, 100), 100, 10, 6 ) )

        self.sprite2 = Sprite( 'grossini.png', (x//5, y//3) )
        self.add( self.sprite2 )
        self.sprite2.do( JumpBy( (x//5*4, 100), 100, 10, 6 ) )

description = """
records 6 seconds, snapshots in the tmp subdir
"""

def main():
    print(description)
    director.set_recorder(25, "tmp/frame-%d.png", 6)
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
