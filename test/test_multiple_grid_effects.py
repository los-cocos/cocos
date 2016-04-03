from __future__ import division, print_function, unicode_literals

#
# Cocos
# http://code.google.com/p/los-cocos/
#

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1, s, t 3, s, t 4, s, t 5, s, t 8.1, s"
tags = "ShuffleTiles, Flip, ShuffleTiles"

import pyglet
from pyglet.gl import glColor4ub, glPushMatrix, glPopMatrix 

import cocos
from cocos.director import director
from cocos.actions import Flip, Waves3D, ShuffleTiles
from cocos.sprite import Sprite
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from pyglet import gl

class SpriteLayer ( Layer ):

    def __init__( self ):
        super( SpriteLayer, self ).__init__()

        sprite1 = Sprite( 'grossini.png' )
        sprite2 = Sprite( 'grossinis_sister1.png')
        sprite3 = Sprite( 'grossinis_sister2.png')

        sprite1.position = (400,240)
        sprite2.position = (300,240)
        sprite3.position = (500,240)

        self.add( sprite1 )
        self.add( sprite2 )
        self.add( sprite3 )

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
Aplying different effects to different scene parts. 
The background does a ShuffleTiles, the layer with sprites does
a Wave3D followed by a Flip.
"""

def main():
    print(description)
    director.init( resizable=True )
    main_scene = Scene()

    back = BackgroundLayer()
    sprite = SpriteLayer()


    main_scene.add( back, z=0 )
    main_scene.add( sprite, z=1 )

    # In real code after a sequence of grid actions the StopGrid() action
    # should be called. Omited here to stay in the last grid action render
    sprite.do( Waves3D(duration=4) + Flip(duration=4) )
    back.do( ShuffleTiles(duration=3, grid=(16,12)) )
    director.run (main_scene)

if __name__ == '__main__':
    main()
