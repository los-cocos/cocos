from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1, s, t 2, s, t 3, s, t 4.1, s, t 4.2, s, q"
tags = "FlipY3D"

import pyglet
from pyglet.gl import glColor4ub, glPushMatrix, glPopMatrix 

import cocos
from cocos.director import director
from cocos.actions import *
from cocos.sprite import *

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
    main_scene = cocos.scene.Scene()
    main_scene.add( BackgroundLayer(), z=0 )

    # In real code after a sequence of grid actions the StopGrid() action
    # should be called. Omited here to stay in the last grid action render
    main_scene.do( FlipY3D(duration=4) )
    director.run (main_scene)

if __name__ == '__main__':
    main()
