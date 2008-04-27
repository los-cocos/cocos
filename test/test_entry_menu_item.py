#
# Los Cocos: Multi-Menu Example
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
        super( MainMenu, self ).__init__("EntryMenuItem")

        l = []
        l.append( EntryMenuItem('Name:', 'default', self.on_name) )
        l.append( MenuItem('Quit', self.on_quit ) )

        # after adding all the items just call build_items()
        self.create_menu( l )

    def on_name( self, value ):
        print value

    def on_quit( self ):
        pyglet.app.exit()

if __name__ == "__main__":

    director.init( resizable=True)
    director.run( Scene( MainMenu() ) )
