#
# cocos2d:
# http://cocos2d.org
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
from pyglet.gl import *
import cocos
from cocos.director import director


class BackgroundLayer( cocos.layer.Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background_image.png')

    def on_enter(self):
        super(BackgroundLayer,self).on_enter()
        director.push_handlers(self.on_resize)

    def draw( self ):
        self.img.blit(0,0)

    def on_resize( self, width, height ):
        # change to custom projection projection
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, 1.0*width/height, 0.1, 3000.0)
        glMatrixMode(GL_MODELVIEW)

if __name__ == '__main__':
    director.init()
    s = cocos.scene.Scene()
    s.add( BackgroundLayer() )
    director.run( s )
