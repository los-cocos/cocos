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
from cocos.actions import Waves3D
from cocos.sprite import ActionSprite
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene

class SpriteLayer ( Layer ):

    def __init__( self ):
        super( SpriteLayer, self ).__init__()

        sprite1 = ActionSprite( 'grossini.png' )
        sprite2 = ActionSprite( 'grossinis_sister1.png')
        sprite3 = ActionSprite( 'grossinis_sister2.png')

        sprite1.position = (400,240)
        sprite2.position = (300,240)
        sprite3.position = (500,240)

        self.add( sprite1 )
        self.add( sprite2 )
        self.add( sprite3 )

if __name__ == "__main__":
    print 'you shall see waving sprites and a red background'
    director.init( resizable=True )
    main_scene = Scene()

    red = ColorLayer(255,0,0,128)

    sprite = SpriteLayer()

    main_scene.add( red, z=0 )
    main_scene.add( sprite, z=1 )

    sprite.do( Waves3D( waves=16, amplitude=40, grid=(16,16), duration=10) )
    director.run (main_scene)
