# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 7, s, t 8, s, t 10.1, s, q"
tags = "grid_actions, AccelAmplitude, Waves3D"

import pyglet
import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *

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
    action1 = Waves3D( waves=16, amplitude=80, grid=(16,16), duration=10)
    action2 = AccelAmplitude(action1, rate=4.0)

    main_scene.do( action2 )
    director.run( main_scene )

if __name__ == '__main__':
    main()
