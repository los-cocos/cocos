# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import pyglet
import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *

class BackgroundLayer( cocos.layer.Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background_image.png')

    def draw( self ):
        self.img.blit(0,0)

if __name__ == "__main__":
    director.init( resizable=True )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    main_scene.add( BackgroundLayer(), z=0 )

    move = QuadMoveBy( delta0=(320,240), delta1=(-630,0), delta2=(-320,-240), delta3=(630,0), duration=2 )
#    move = QuadMoveBy( delta0=(640,480), delta1=(-640,480), delta2=(-640,-480), delta3=(640,-480), duration=2 )

    main_scene.do( move + Reverse(move) )
#    main_scene.do( move )

    director.run (main_scene)
