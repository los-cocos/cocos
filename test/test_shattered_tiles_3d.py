from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 2, s, t 5.1, s, q"
tags = "ShatteredTiles3D"

import pyglet
import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *
from pyglet import gl

class BackgroundLayer(cocos.layer.Layer):
    def __init__(self):
        super(BackgroundLayer, self).__init__()
        self.img = pyglet.resource.image('background_image.png')

    def draw( self ):
        gl.glColor4ub(255, 255, 255, 255)
        gl.glPushMatrix()
        self.transform()
        self.img.blit(0,0)
        gl.glPopMatrix()

description = """
Shows the ShatteredTiles3D effect applied over the scene.
This effect produces a render change at start time, and no more
until the action duration is reached.

Since in this sample StopGrid() is not used after the grid action,
no change would be seen at end of action.
"""

def main():
    print(description)
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()

    main_scene.add( BackgroundLayer(), z=0 )

    # In real code after a sequence of grid actions the StopGrid() action
    # should be called. Omited here to stay in the last grid action render
    a = ShatteredTiles3D( randrange=6, duration=10, grid=(8,6) )
    main_scene.do( a )
    director.run (main_scene)

if __name__ == '__main__':
    main()
