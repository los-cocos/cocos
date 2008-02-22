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

from cocos.actions import *
from cocos.director import director
from cocos.layer import Layer, AnimationLayer
from cocos.scene import Scene



class SpriteLayer ( AnimationLayer ):

    def __init__( self ):
        super( SpriteLayer, self ).__init__()
        sprite1 = ActionSprite('grossini.png')
        sprite2 = ActionSprite('grossinis_sister2.png')
        sprite3 = ActionSprite('grossinis_sister2.png')
        sprite4 = ActionSprite('grossinis_sister1.png')
        sprite5 = ActionSprite('grossinis_sister1.png')

        sprite1.translate = Point3( 320,240,0)

        sprite2.translate = Point3( 20,180,0)
        sprite3.translate = Point3( 20,180,0)

        sprite4.translate = Point3( 20,180,0)
        sprite5.translate = Point3( 20,180,0)

        self.add( sprite1 )
        self.add( sprite2 )
        self.add( sprite3 )
        self.add( sprite4 )
        self.add( sprite5 )

        go = goto( Point3(320,240,0), 5 )
        go2 = goto( Point3(40,80,0), 5 )

        mo = move( Point3(600,0,0), 10 )

        ro = rotate( 300, 5 )
        ro2 = rotate( -300, 5 )

        sc_up = scale( 15, 5 )
        sc_down = scale( 0.1, 5 )

        import foo
        bz = bezier( foo.curva, 5 )
        bz2 = bezier( foo.new228555, 5 )

        sprite1.do( repeat( sc_up + sc_down ) )
        sprite1.do( repeat( ro + ro2 ) )
#        sprite3.do( timewarp( linear(0.8), bz2) )
        sprite4.do( jump( mo ) )
        sprite5.do( reverse( jump( mo ) ) )
        sprite2.do( bz )
        sprite3.do( reverse( bz ) )


    def on_key_release( self, keys, mod ):
        if keys == key.ENTER:
            director.scene.end("chau")
            return True

    def on_enter( self ):
        print '**** Sprites ****'


if __name__ == "__main__":
    director.init()
    director.run( Scene( SpriteLayer()) )
