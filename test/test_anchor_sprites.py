# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.0, s, t 2.1, s, q"
tags = "transform_anchor, Rotate"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import *
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        sprite1 = Sprite('grossini.png')
        sprite1.position = x/4, y/2
        self.add( sprite1  )

        sprite2 = Sprite('grossini.png')
        sprite2.position = x/4, y/2
        self.add( sprite2, z=2  )
        sprite2.scale = 0.3

        sprite2.do( RotateBy(duration=2, angle=360) )
        sprite1.do( RotateBy(duration=2, angle=-360) )

        sprite1.transform_anchor = 0, 0

        sprite3 = Sprite('grossini.png')
        sprite3.position = 3*x/4, y/2
        self.add( sprite3  )

        sprite4 = Sprite('grossini.png')
        sprite4.position = 3*x/4, y/2
        self.add( sprite4, z=2  )
        sprite4.scale = 0.3

        sprite3.do( RotateBy(duration=2, angle=360) )
        sprite4.do( RotateBy(duration=2, angle=-360) )

        sprite3.transform_anchor = sprite3.image.width/2, sprite3.image.height/2

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
