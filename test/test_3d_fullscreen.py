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

def toggle_fullscreen():
    director.window.set_fullscreen( not director.window.fullscreen )

if __name__ == "__main__":
    director.init( resizable=True )
    director.set_depth_test()

    main_scene = cocos.scene.Scene()

    main_scene.add( BackgroundLayer(), z=0 )

    # set a 3d grid with a grid3d action
    e = WavesTiles3D( amplitude=60, waves=2, grid=(32,24), duration=3)
    f = ShuffleTiles( duration=3, grid=(32,24) )

    main_scene.do( e +  \
        CallFunc( toggle_fullscreen ) + \
        Reverse(e) + \
        CallFunc(toggle_fullscreen) + \
        f + \
        CallFunc(toggle_fullscreen) + \
        Reverse(f) + \
        StopGrid() \
        )

    director.run (main_scene)
