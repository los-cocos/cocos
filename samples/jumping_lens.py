#
# Cocos:
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
from pyglet.gl import *

from cocos.director import *
from cocos.scene import *
from cocos.layer import *
from cocos.actions import *

import random; rr = random.randrange


class BackLayer( Layer ):

    def __init__( self ):
        super( BackLayer, self).__init__()
        self.image = pyglet.resource.image('flag.png')

    def on_draw( self ):
        self.image.blit(0,0)

if __name__ == "__main__":
    director.init( resizable=True)
    scene = Scene( BackLayer() )

    lens = Lens3D( radius=150, lens_effect=0.7, center=(150,150), grid=(20,16), duration=10)
    jump = Jump(150,360,5,5 )

    action = scene.do( lens )
    scene.do( jump + Reverse(jump), target=action)
    director.run( scene )
