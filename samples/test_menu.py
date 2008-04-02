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

        # call superclass with the title
        super( MainMenu, self ).__init__("GROSSINI'S SISTERS" )

        # you can override the font that will be used for the title and the items
        font_title = {
            'font_name':'KonQa',
            'font_size':72,
            'bold':True,
            }
        self.font_title.update( font_title )

        font_item = {
            'font_name':'You Are Loved',
            'font_size': 32,
            }
        self.font_item.update( font_item )

        font_item = {
            'font_name':'You Are Loved',
            'font_size': 48,
            }
        self.font_item_selected.update( font_item )

        # example: menus can be vertical aligned and horizontal aligned
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        # then add the items
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
        self.switch_to( 2 )

    def on_options( self ):
        self.switch_to( 1 )

    def on_quit( self ):
        print "on_quit()"
        sys.exit()


class OptionMenu(Menu):
    def __init__( self ):
        super( OptionMenu, self ).__init__("GROSSINI'S SISTERS" )

        font_title = {
            'font_name':'KonQa',
            'font_size':72,
            'bold':True,
            }
        self.font_title.update( font_title )

        font_item = {
            'font_name':'You Are Loved',
            'font_size': 32,
            }
        self.font_item.update( font_item )

        font_item = {
            'font_name':'You Are Loved',
            'font_size': 48,
            }
        self.font_item_selected.update( font_item )

        self.menu_valign = BOTTOM
        self.menu_halign = RIGHT

        self.add_item( MenuItem('Fullscreen', self.on_fullscreen) )
        self.add_item( ToggleMenuItem('Show FPS', True, self.on_show_fps) )
        self.add_item( MenuItem('OK', self.on_quit) )
        self.build_items()


    # Callbacks
    def on_fullscreen( self ):
        director.window.set_fullscreen( not director.window.fullscreen )

    def on_quit( self ):
        self.switch_to( 0 )

    def on_show_fps( self, value ):
        director.show_FPS = value

class ScoreMenu(Menu):
    def __init__( self ):
        super( ScoreMenu, self ).__init__("GROSSINI'S SISTERS" )

        font_title = {
            'font_name':'KonQa',
            'font_size':72,
            'bold':True,
            }
        self.font_title.update( font_title )

        font_item = {
            'font_name':'You Are Loved',
            'font_size': 32,
            }
        self.font_item.update( font_item )

        font_item = {
            'font_name':'You Are Loved',
            'font_size': 48,
            }
        self.font_item_selected.update( font_item )

        self.menu_valign = BOTTOM
        self.menu_halign = LEFT

        self.add_item( MenuItem('Go Back', self.on_quit) )
        self.build_items()

    def on_quit( self ):
        self.switch_to( 0 )


if __name__ == "__main__":

    pyglet.resource.path.append('.')
    pyglet.resource.reindex()
    pyglet.font.add_directory('.')

    director.init( resizable=True)
    director.run( Scene(
            MultiplexLayer( MainMenu(), OptionMenu(), ScoreMenu() )
            ) )
