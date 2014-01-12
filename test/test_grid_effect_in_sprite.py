from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.7, s, t 3.7, s, t 6.7, s, t 9.7, s, t 12, s, q"
tags = "Sprites, Waves, Twirl, WavesTiles3D, TurnOffTiles, StopGrid"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import *

import pyglet
from pyglet.gl import *


class BackgroundLayer(cocos.layer.Layer):
    def __init__(self):
        super(BackgroundLayer, self).__init__()
        self.img = pyglet.resource.image('background_image.png')

    def draw( self ):
        glColor4ub(255, 255, 255, 255)
        glPushMatrix()
        self.transform()
        self.img.blit(0,0)
        glPopMatrix()

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (x//2,y//2), scale = 1 )
        self.add( self.sprite )
        self.sprite.do( Repeat( ScaleBy( 5, 2 ) + ScaleBy( 0.2, 2 )  ) )
        self.sprite.do( Repeat( RotateBy( 360, 10 ) ) )

        self.sprite.do(
            Waves( duration=3 ) +
            Twirl( amplitude=1, twirls=3, grid=(32,24), duration=3 ) + 
            WavesTiles3D( waves=4, grid=(32,24), duration=3 ) + 
            TurnOffTiles( grid=(32,24), duration=1.5) + 
            Reverse( TurnOffTiles( grid=(32,24), duration=1.5) ) + 
            StopGrid() )

def main():
    director.init()
    background = BackgroundLayer()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene ()

    main_scene.add( background, z=0 )
    main_scene.add( test_layer, z=1 )

    director.run (main_scene)

if __name__ == '__main__':
    main()
