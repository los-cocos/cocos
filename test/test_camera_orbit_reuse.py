from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

# total time duration * action multiplier
testinfo = "s, t 2.0, s, t 4.0, s, t 6.1, s, q"
tags = "OrbitCamera, grid"

import pyglet
import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *

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

def main():
    director.init( resizable=True )
    director.set_depth_test()

    main_scene = cocos.scene.Scene()
    main_scene.add( BackgroundLayer(), z=0 )

    rot = OrbitCamera( delta_z=60, duration=2 )

    # In real code after a sequence of grid actions the StopGrid() action
    # should be called. Omited here to stay in the last grid action render
    main_scene.do( rot * 3 )

    director.run (main_scene)

if __name__ == '__main__':
    main()
