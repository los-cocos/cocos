from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.1, s, q"
tags = "MultiplexLayer"
autotest = 0


import pyglet
from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *
from cocos.actions import Delay, CallFunc

class MainMenu(Menu):
    def __init__( self ):

        # call superclass with the title
        super( MainMenu, self ).__init__("MultiplexLayer")

        l = []
        l.append( MenuItem('Options', self.on_new_game ) )
        l.append( MenuItem('Quit', self.on_quit ) )

        self.create_menu( l )
        if autotest:
            self.do( Delay(1) + CallFunc(self.on_new_game))

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

description = """
Demostrates MultiplexLayer, a layer which can hold many layers, showing
one of them at a time and handling navigation between layers.
Activate 'Options' to switch to the 'options' layer.
"""

def main():
    print(description)
    director.init( resizable=True)
    scene =Scene(
            MultiplexLayer( MainMenu(), OptionMenu() )
            )

    director.run( scene )

if __name__ == '__main__':
    main()
