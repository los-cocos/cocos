# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *
from cocos.scenes import *
from cocos.sprite import *
import pyglet
from pyglet.gl import *

class BackgroundLayer( cocos.layer.Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background_image.png')

        self.anchor = (320,240)
#        self.do( RotateBy( 360,2) )

    def draw( self ):
        glPushMatrix()
        self.transform()
        self.img.blit(0,0)
        glPopMatrix()


if __name__ == "__main__":
    director.init( resizable=True )
    scene = cocos.scene.Scene()

    l = cocos.layer.Layer()
    s = Sprite('grossini.png', (0,0) )
    l.add( s )

    scene.add( BackgroundLayer(), z=0 )
    scene.add( l, z=1)

    director.run( scene )
