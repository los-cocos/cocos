#
# Cocos
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


import pyglet
from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *

class MainMenu(Menu):
    def __init__( self ):

        # call superclass with the title
        super( MainMenu, self ).__init__("MultiplexLayer")

        l = []
        l.append( MenuItem('Options', self.on_new_game ) )
        l.append( MenuItem('Quit', self.on_quit ) )

        self.create_menu( l )

    # Callbacks
    def on_new_game( self ):
        self.parent.switch_to( 1 )

    def on_quit( self ):
        pyglet.app.exit()


class OptionMenu(Menu):
    def __init__( self ):
        super( OptionMenu, self ).__init__("MultiplexLayer")

        l = []
        l.append( MenuItem('Fullscreen', self.on_fullscreen) )
        l.append( MenuItem('OK', self.on_quit) )

        self.create_menu( l )

    # Callbacks
    def on_fullscreen( self ):
        pass

    def on_quit( self ):
        self.parent.switch_to( 0 )

if __name__ == "__main__":
    director.init( resizable=True)
    scene =Scene( 
            MultiplexLayer( MainMenu(), OptionMenu() )
            )

    director.run( scene )
