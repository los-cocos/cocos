# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from cocos.layer import *

import pyglet
from pyglet.gl import *

class BackgroundLayer( Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background.png')

    def draw( self ):
        glPushMatrix()
        self.transform()
        self.img.blit(0,0)
        glPopMatrix()

class HUD( Layer ):
    def __init__( self ):
        super( HUD, self).__init__()
        self.add( BackgroundLayer(), z=-1)
