#
# Cocos: 
# http://code.google.com/p/los-cocos/
#
# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import pyglet
from pyglet.gl import *

import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *

class BackgroundLayer( cocos.layer.Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background_image.png')
        self.img2 = pyglet.resource.image('grossini.png')
        self.opacity = 255

    def on_draw( self ):
        glPushAttrib(GL_CURRENT_BIT)
        glColor4ub( 255,255,255,int(self.opacity) )

        self.img.blit(0,0)

        glPopAttrib()

        self.img2.blit(320,240)


if __name__ == "__main__":
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()

    layer = BackgroundLayer()
    main_scene.add( layer, z=0 )

    layer.do( FadeOut( duration=2) )

    director.run (main_scene)
