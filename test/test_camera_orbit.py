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

    def on_draw( self ):
        self.img.blit(0,0)

if __name__ == "__main__":
    director.init( resizable=True )
    director.set_depth_test()

    main_scene = cocos.scene.Scene()

    main_scene.add( BackgroundLayer(), z=0 )

    # set a 3d grid with a grid3d action
    e = WavesTiles3D( amplitude=60, waves=8, grid=(32,24), duration=8)

    # use the remaining grid and move it's camera
    rot = OrbitCamera( angle_x=45,  angle_z=0, delta_z=360, duration=8 )

    main_scene.do( e )
    main_scene.do( rot + Reverse(rot) )

    director.run (main_scene)
