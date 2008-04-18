# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import *
from cocos.sprite import *
from cocos.layer import *
import pyglet

class SpriteLayer ( Layer ):

    def __init__( self ):
        super( SpriteLayer, self ).__init__()

        self.image = pyglet.resource.image('grossini.png')
        self.image.anchor_x = self.image.width / 2
        self.image.anchor_y = self.image.height / 2

        self.image_sister1 = pyglet.resource.image('grossinis_sister1.png')
        self.image_sister1.anchor_x = self.image_sister1.width / 2
        self.image_sister1.anchor_y = self.image_sister1.height / 2

        self.image_sister2 = pyglet.resource.image('grossinis_sister2.png')
        self.image_sister2.anchor_x = self.image_sister2.width / 2
        self.image_sister2.anchor_y = self.image_sister2.height / 2

        sprite1 = ActionSprite( self.image )
        sprite2 = ActionSprite( self.image_sister1 )
        sprite3 = ActionSprite( self.image_sister2 )

        ju_right = Jump( y=100, x=600, jumps=4, duration=5 )
        ju_left = Jump( y=100, x=-600, jumps=4, duration=5 )
        rot1 = Rotate( 180 * 4, duration=5)

        self.add( sprite1, (320,240) )
        self.add( sprite2, (620,100) )
        self.add( sprite3, (20,100) )

        sc = ScaleBy( 9, 5 )
        rot = Rotate( 180, 5 )
        

        sprite1.do( Repeat( sc + Reverse(sc) ) )
        sprite1.do( Repeat( rot + Reverse(rot) ) )
        sprite2.do( Repeat( ju_left + Reverse(ju_left) ) )
        sprite2.do( Repeat( Reverse(rot1) + rot1 ) )
        sprite3.do( Repeat( ju_right + Reverse(ju_right) ) )
        sprite3.do( Repeat( rot1 + Reverse(rot1) ) )

if __name__ == "__main__":
    director.init( resizable=True )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    red = ColorLayer(1.0, 0.0, 0.0, 1.0)
    blue = ColorLayer(0.0, 0.0, 1.0, 1.0)
    green = ColorLayer(0.0, 1.0, 0.0, 1.0)
    white = ColorLayer(1.0, 1.0, 1.0, 1.0)

    main_scene.add( red, z=0 )
    main_scene.add( blue, z=1, scale=0.75 )
    main_scene.add( green, z=2, scale=0.5 )
    main_scene.add( white, z=3, scale=0.25 )

    main_scene.add( SpriteLayer(), z=4 )

    main_scene.do( Delay(2) + Waves3D( waves=16, grid=(16,16), duration=10) )
    director.run (main_scene)
