from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 0.5, s, t 1, s, t 1.5, s, t 2.1, s, q"
tags = "QuadMoveBy"

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

def main():
    director.init( resizable=True )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    main_scene.add( BackgroundLayer(), z=0 )

    move = QuadMoveBy( delta0=(320,240), delta1=(-630,0), delta2=(-320,-240),
                       delta3=(630,0), duration=1 )
    #move = QuadMoveBy( delta0=(640,480), delta1=(-640,480), delta2=(-640,-480), delta3=(640,-480), duration=2 )

    main_scene.do( move + Reverse(move) )
    #main_scene.do( move )

    director.run (main_scene)

if __name__ == '__main__':
    main()
