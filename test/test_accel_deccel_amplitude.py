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

        sprite1 = ActionSprite( 'grossini.png' )
        sprite2 = ActionSprite( 'grossinis_sister1.png')
        sprite3 = ActionSprite( 'grossinis_sister2.png')

        sprite1.position = (320,240)
        sprite2.position = (620,100)
        sprite3.position = (20,100)

        self.add( sprite1 )
        self.add( sprite2 )
        self.add( sprite3 )

        ju_right = Jump( y=100, x=600, jumps=4, duration=5 )
        ju_left = Jump( y=100, x=-600, jumps=4, duration=5 )
        rot1 = Rotate( 180 * 4, duration=5)

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
    main_scene = cocos.scene.Scene()

    white = ColorLayer(255,255,255,255)
    red = ColorLayer(255,0,0,255)
    blue = ColorLayer(0,0,255,255)
    green = ColorLayer(0,255,0,255)

    red.scale = 0.75
    blue.scale = 0.5
    green.scale = 0.25

    main_scene.add( white, z=0 )
    main_scene.add( red, z=1 )
    main_scene.add( blue, z=2 )
    main_scene.add( green, z=3 )
    main_scene.add( SpriteLayer(), z=4 )

    main_scene.do( AccelDeccelAmplitude(Waves3D( waves=16, amplitude=80, grid=(16,16), duration=10), rate=4.0 ) )
    director.run (main_scene)
