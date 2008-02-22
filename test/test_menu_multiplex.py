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
        self.switch_to( 2 )

    def on_options( self ):
        self.switch_to( 1 )

    def on_quit( self ):
        print "on_quit()"
        sys.exit()


class OptionMenu(Menu):
    def __init__( self ):
        super( OptionMenu, self ).__init__("GROSSINI'S SISTERS" )

        self.font_title = 'KonQa Black'
#        self.font_items = 'You Are Loved'
        self.menu_valign = BOTTOM
        self.menu_halign = RIGHT

        self.add_item( MenuItem('Fullscreen', self.on_fullscreen) )
        self.add_item( ToggleMenuItem('Show FPS', True, self.on_show_fps) )
        self.add_item( MenuItem('OK', self.on_quit) )
        self.build_items()

        self.fullscreen = False

    # Callbacks
    def on_fullscreen( self ):
        self.fullscreen = not self.fullscreen
        director.window.set_fullscreen( self.fullscreen )

    def on_quit( self ):
        self.switch_to( 0 )

    def on_show_fps( self, value ):
        director.show_FPS = value

class ScoreMenu(Menu):
    def __init__( self ):
        super( ScoreMenu, self ).__init__("GROSSINI'S SISTERS" )

        self.font_title = 'KonQa Black'
#        self.font_items = 'You Are Loved'
        self.menu_valign = BOTTOM
        self.menu_halign = LEFT

        self.add_item( MenuItem('Go Back', self.on_quit) )
        self.build_items()

    def on_quit( self ):
        self.switch_to( 0 )


if __name__ == "__main__":
    director.init( resizable=True)
    director.run( Scene( 
            MultiplexLayer( 
                ( MainMenu(), OptionMenu(), ScoreMenu() )
            ) ) )
