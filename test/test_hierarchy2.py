from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "CocosNode, Sprite, child, rotation, position"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        # rotation and childs, with default transform_anchor s
        self.sprite_a1 = Sprite( 'grossini.png', (x//4, int(y*0.66))  )
        self.sprite_a2 = Sprite( 'grossini.png', (0,0), rotation=30 )
        self.sprite_a3 = Sprite( 'grossini.png', (0,0), rotation=30 )

        self.sprite_a1.add( self.sprite_a2 )
        self.sprite_a2.add( self.sprite_a3 )
        self.add( self.sprite_a1 )

        # position and childs, with default transform_anchor s
        self.sprite_b1 = Sprite( 'grossinis_sister1.png', (x//2, int(y*0.66))  )
        self.sprite_b2 = Sprite( 'grossinis_sister1.png', (100,0) )
        self.sprite_b3 = Sprite( 'grossinis_sister1.png', (100,0) )

        self.sprite_b1.add( self.sprite_b2 )
        self.sprite_b2.add( self.sprite_b3 )
        self.add( self.sprite_b1 )

        # combo, with default transform_anchor s
        self.sprite_c1 = Sprite( 'grossinis_sister2.png', (int(x*0.33), int(y*0.33))  )
        self.sprite_c2 = Sprite( 'grossinis_sister2.png', (100,0), rotation=30 )
        self.sprite_c3 = Sprite( 'grossinis_sister2.png', (100,0), rotation=30 )

        self.sprite_c1.add( self.sprite_c2 )
        self.sprite_c2.add( self.sprite_c3 )
        self.add( self.sprite_c1 )

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
