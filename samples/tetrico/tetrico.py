# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


from game import *

from cocos.director import director
from cocos.layer import *
from cocos.scene import Scene
from cocos.scenes.transitions import *
from cocos.actions import *
from cocos.sprite import *
from cocos.menu import *
from cocos.text import *

import pyglet
from pyglet import gl, font
from pyglet.window import key

class MainMenu( Menu ):

    def __init__(self):
        super( MainMenu, self).__init__('TETRICO') 
        pyglet.font.add_directory('.')

        # you can override the font that will be used for the title and the items
#        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72
#        self.font_title['color'] = (240,16,32,255)
        self.font_title['color'] = (32,16,32,255)

#        self.font_item['font_name'] = 'You Are Loved'
#        self.font_item_selected['font_name'] = 'You Are Loved'

        # you can also override the font size and the colors. see menu.py for
        # more info

        # example: menus can be vertical aligned and horizontal aligned
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []

        items.append( MenuItem('New Game', self.on_new_game) )
        items.append( MenuItem('Options', self.on_options) )
        items.append( MenuItem('Scores', self.on_scores) )
        items.append( MenuItem('Quit', self.on_quit) )

        self.create_menu( items, zoom_in(), zoom_out() )

    def on_new_game(self):
        director.push( FadeTRTransition(
            get_newgame(), 1 ) )

    def on_options( self ):
        pass

    def on_scores( self ):
        pass

    def on_quit(self):
        pyglet.app.exit()

if __name__ == "__main__":

    pyglet.resource.path.append('data')
    pyglet.resource.reindex()
    font.add_directory('data')

    director.init( resizable=True )
    scene = Scene()
    scene.add( MainMenu(), z=1 ) 
    scene.add( ColorLayer(112,66,20,255), z=0 ) 
    director.run( scene )
