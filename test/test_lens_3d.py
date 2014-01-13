from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1, s, t 5.1, s, q"
tags = "Lens3D, StopGrid"

import pyglet
from pyglet.gl import glColor4ub, glPushMatrix, glPopMatrix 
import cocos
from cocos.director import director
from cocos.actions import *

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

description = """
Shows a background image, after 1 sec the Lens3D effect is applied to,
the scene, and 5 secs after thet the effect turns off.

It is a static efect, to get a moving lens effect more code updating
the lens position should be added.
"""

def main():
    print(description)
    director.init( resizable=True )
    director.set_depth_test()

    main_scene = cocos.scene.Scene()

    main_scene.add( BackgroundLayer(), z=0 )

    # important:  maintain the aspect ratio in the grid
    e = Lens3D( center=(320,200), lens_effect=0.9, radius=240, grid=(64,48),
                duration=5 )

    # StopGrid returns to the normal view
    main_scene.do( Delay(1) + e + StopGrid() )

    director.run (main_scene)

if __name__ == '__main__':
    main()
