#
# Los Cocos: Sprite Example
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyglet import image
from pyglet.gl import *
from pyglet.window import key

from cocos.actions2 import *
from cocos.director import director
from cocos.layer import Layer, AnimationLayer
from cocos.scene import Scene



class SpriteLayer ( AnimationLayer ):

    def __init__( self ):
        super( SpriteLayer, self ).__init__()

        sprite1 = ActionSprite('grossinis_sister1.png')
        sprite2 = ActionSprite('grossinis_sister2.png')
        sprite3 = ActionSprite('grossini.png')
        sprite4 = ActionSprite('grossini.png')
        sprite5 = ActionSprite('grossini.png')
        sprite6 = ActionSprite('grossinis_sister1.png')
        sprite7 = ActionSprite('grossinis_sister1.png')

        sprite1.place( (0,0,0) )
        sprite2.place( (640,0,0) )
        sprite3.place( (320,0,0) )
        sprite4.place( (320,240,0) )
        sprite5.place( (0,0,0) )
        sprite6.place( (20,200,0) )
        sprite7.place( (620,200,0) )

        self.add( sprite1, sprite2, sprite3, sprite4, sprite5, sprite6, sprite7 )

        go = Goto( (320,240,0), 5)
        mo = Move( (0,170,0), 5 )
        ro = Rotate( 720, 5 )
        sc = Scale( 8, 2 )

        ro1 = Rotate( 720, 5 )
        ro2 = Rotate( -720, 5 )

        go1 = Goto( (400,240,0), 1 )
        go2 = Goto( (400,300,0), 1 )
        go3 = Goto( (200,300,0), 2 )
        go4 = Goto( (200,240,0), 1 )
        mo1 = Move( (50,0,0), 0.5 )
        mo2 = Move( (0,50,0), 0.5 )

        ju = Jump( height=50, width=200, jumps=4, duration=4 )
        ju2 = Jump( height=50, width=-200, jumps=4, duration=4 )

        de = Delay( 0.5 )

#        sprite1.do( go | ro )
#        sprite2.do( go + mo )
#        sprite3.do( go )
#        sprite4.do( Spawn(ro,mo,sc) )
#        sprite4.do( Repeat( mo1 + mo2 ) )
#        sprite4.do( Repeat( go1 + go2 + go3 + go4 ) )
        sprite4.do( Repeat( mo1 + Repeat(ju,3) + mo2 + ju2 ) )
#        sprite5.do( Sequence( ju, Goto( (640,0,0), 1.25 ), de, Goto( (640,480,0), 1.25 ), de, Goto( (0,480,0), 1.25 ), de, Goto( (0,0,0), 1.25 ) ) )
#        sprite6.do( Repeat( ju ) )
#        sprite7.do( Repeat( ju2 ) )

    def on_key_release( self, keys, mod ):
        if keys == key.ENTER:
            director.scene.end("chau")
            return True

    def on_enter( self ):
        print '**** Sprites ****'


if __name__ == "__main__":
    director.init()
    director.run( Scene( SpriteLayer()) )
