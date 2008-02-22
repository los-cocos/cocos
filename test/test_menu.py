#
# Los Cocos: Menu Example
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

class MainMenu(Menu):
    def __init__( self ):

        # call superclass with the title
        super( MainMenu, self ).__init__("GROSSINI'S SISTERS" )

        # you can override the font that will be used for the title and the items
        self.font_title = 'KonQa Black'
        self.font_items = 'You Are Loved'

        font.add_directory('.')

        self.font_title = 'KonQa Black'
        self.font_items = 'You Are Loved'

        # you can also override the font size and the colors. see menu.py for
        # more info

        # example: menus can be vertical aligned and horizontal aligned
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        self.add_item( MenuItem('New Game', self.on_new_game ) )
        self.add_item( MenuItem('Options', self.on_options ) )
        self.add_item( MenuItem('Scores', self.on_scores ) )
        self.add_item( MenuItem('Quit', self.on_quit ) )

        # after adding all the items just call build_items()
        self.build_items()


    # Callbacks
    def on_new_game( self ):
#        director.set_scene( StartGame() )
        print "on_new_game()"
           

    def on_scores( self ):
#        self.switch_to( 2 )
        print "on_scores()"

    def on_options( self ):
#        self.switch_to( 1 )
        print "on_options()"

    def on_quit( self ):
        print "on_quit()"
        sys.exit()


if __name__ == "__main__":
    director.init( resizable=True)
    director.run( Scene( MainMenu()) )
