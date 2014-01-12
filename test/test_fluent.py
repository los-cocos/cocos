from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "CocosNode, child"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet

def main():
    director.init()
    x,y = director.get_window_size()

    main_scene = (
        cocos.scene.Scene()
            .add( cocos.layer.ColorLayer( 255,255,0,255) )
            .add( cocos.layer.Layer()
                .add( Sprite('grossini.png', (x//2, y//2))
            )
        )
    )
    director.run (main_scene)

if __name__ == '__main__':
    main()
