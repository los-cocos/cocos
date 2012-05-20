# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 4, s, t 8, s, t 12, s, t 16.1, s, q"
tags = "OrbitCamera"

import pyglet
import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *

from pyglet.gl import *


class BackgroundLayer( cocos.layer.Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background_image.png')

    def draw( self ):
        glPushMatrix()
        self.transform()
        self.img.blit(0,0)
        glPopMatrix()

def main():
    director.init( resizable=True )
    #director.set_depth_test()

    main_scene = cocos.scene.Scene()

    background = BackgroundLayer()
    color = ColorLayer(255,32,32,128)

    main_scene.add( background, z=0 )
    main_scene.add( color, z=1 )

    # use the remaining grid and move it's camera
    rot = OrbitCamera( angle_x=45,  angle_z=0, delta_z=360, duration=8 )
    rot2 = OrbitCamera( radius=2, delta_radius=-1, angle_x=0, angle_z=0, delta_z=360, duration=8 )

    background.do( rot + Reverse(rot) )
    color.do( rot2 + Reverse(rot2) )

    director.run (main_scene)

if __name__ == '__main__':
    main()
