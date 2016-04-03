from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 3.0, s, t 5.0, s, t 10.0, s, q"
tags = "grid_actions, AccelDeccelAmplitude, Waves3D"

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
Shows how to use AccelDeccelAmplitude to modify a GridAction.
AccelDeccelAction will reparametrize time for the target action.
It should be seen the stock background shaken with waves of increasing
magnitude, then of decreasing magnitue, begginning and ending  with a
flat image.
"""

def main():
    print(description)
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()
    main_scene.add( BackgroundLayer(), z=0 )

    # In real code after a sequence of grid actions the StopGrid() action
    # should be called. Omited here to stay in the last grid action render
    action1 = Waves3D( waves=16, amplitude=80, grid=(16,16), duration=10)
    action2 = AccelDeccelAmplitude(action1, rate=4.0)

    main_scene.do(action2) 
    director.run (main_scene)

if __name__ == '__main__':
    main()
