#
# Cocos
# http://code.google.com/p/los-cocos/
#

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


from cocos.director import director
from cocos.actions import Flip, Waves3D
from cocos.sprite import Sprite
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene

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

if __name__ == "__main__":
    print 'you shall see an scaled red background and fliping sprites. the background always must be seen (scaled)'
    director.init( resizable=True )
    main_scene = Scene()

    red = ColorLayer(255,0,0,128)

    sprite = SpriteLayer()

    red.scale = 0.75

    main_scene.add( red, z=0 )
    main_scene.add( sprite, z=1 )

    sprite.do( Waves3D(duration=4) + Flip(duration=4) )
    director.run (main_scene)
