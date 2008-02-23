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

        sprite1.place(0,0,0)
        sprite2.place(640,0,0)

        self.add( sprite1 )
        self.add( sprite2 )

        go = goto( (320,240,0), 5 )
        pl = place( 320,400,0 )

        sprite1.do( go + pl )
        sprite2.do( go )

    def on_key_release( self, keys, mod ):
        if keys == key.ENTER:
            director.scene.end("chau")
            return True

    def on_enter( self ):
        print '**** Sprites ****'


if __name__ == "__main__":
    director.init()
    director.run( Scene( SpriteLayer()) )
