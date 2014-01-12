from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "Sprite"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet

## the following is in case we want to get the images
## from other directories:
# pyglet.resource.path.append("/data/other/directory")
# pyglet.resource.reindex()


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite('grossini.png')
        self.sprite.position = x//2, y//2
        self.add( self.sprite  )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
