from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "Sprite, scale_x, scale_y"

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

        sprite = Sprite('grossini.png')
        sprite.position = x//5, y//2
        self.add(sprite)

        sprite = Sprite('grossini.png')
        sprite.position = x*2//5, y//2
        sprite.scale_x = 0.5
        self.add(sprite)

        sprite = Sprite('grossini.png')
        sprite.position = x*3//5, y//2
        sprite.scale_y = 0.5
        self.add(sprite)

        sprite = Sprite('grossini.png')
        sprite.position = x*4//5, y//2
        sprite.scale_y = 0.5
        sprite.scale = 2.0
        self.add(sprite)

description = """
Shows four images of Grossini, from left to right:
    No scaled at all
    scale_x = 0.5 , should look stretched to half width
    scale_y = 0.5 , should look stretched to half height
    scale_y = 0.5 and scale = 2.0 , should look normal height and double width
"""

def main():
    print(description)
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
