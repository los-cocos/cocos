# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from cocos.layer import *
from cocos.text import *

import pyglet
from pyglet.gl import *

from status import status

class BackgroundLayer( Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background.png')

    def draw( self ):
        glPushMatrix()
        self.transform()
        self.img.blit(0,0)
        glPopMatrix()

class ScoreLayer( Layer ): 
    def __init__(self):
        super( ScoreLayer, self).__init__()
        self.label =  Label('Score:', font_size=48)
        self.label.position=(20,600)
        self.add( self.label )

    def draw(self):
        super( ScoreLayer, self).draw()
        self.label.element.text = 'Score: %4d' % status.score 
        
        if status.next_piece:
            status.next_piece.draw()

class HUD( Layer ):
    def __init__( self ):
        super( HUD, self).__init__()
        self.add( BackgroundLayer(), z=-1)
        self.add( ScoreLayer() )
