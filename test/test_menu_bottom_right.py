#
# Los Cocos: Multi-Menu Example
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyglet import image
from pyglet.gl import *
from pyglet import font

from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *

class MainMenu(Menu):
    def __init__( self ):
        super( MainMenu, self ).__init__("TITLE" )

        self.menu_valign = BOTTOM
        self.menu_halign = RIGHT

        # then add the items
        self.add_item( MenuItem('Item 1', self.on_quit ) )
        self.add_item( MenuItem('Item 2', self.on_quit ) )
        self.add_item( MenuItem('Item 3', self.on_quit ) )
        self.add_item( MenuItem('Item 4', self.on_quit ) )

        # after adding all the items just call build_items()
        self.build_items()

    def on_quit( self ):
        pyglet.app.exit()



if __name__ == "__main__":

    pyglet.font.add_directory('.')

    director.init( resizable=True)
    director.run( Scene( MainMenu() ) )
