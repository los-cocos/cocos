# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from operator import setslice

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

from HUD import BackgroundLayer
import soundex

class OptionsMenu( Menu ):
    def __init__(self):
        super( OptionsMenu, self).__init__('TETRICO') 
        self.select_sound = soundex.load('move.mp3')

        # you can override the font that will be used for the title and the items
        self.font_title['font_name'] = 'Edit Undo Line BRK'
        self.font_title['font_size'] = 72
        self.font_title['color'] = (204,164,164,255)

        self.font_item['font_name'] = 'Edit Undo Line BRK',
        self.font_item['color'] = (32,16,32,255)
        self.font_item['font_size'] = 32
        self.font_item_selected['font_name'] = 'Edit Undo Line BRK'
        self.font_item_selected['color'] = (32,16,32,255)
        self.font_item_selected['font_size'] = 46

        # you can also override the font size and the colors. see menu.py for
        # more info

        # example: menus can be vertical aligned and horizontal aligned
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []

        self.volumes = ['Mute','10','20','30','40','50','60','70','80','90','100']

        items.append( MultipleMenuItem(
                        'SFX volume: ', 
                        self.on_sfx_volume,
                        self.volumes,
                        int(soundex.sound_vol * 10) )
                    )
        items.append( MultipleMenuItem(
                        'Music volume: ', 
                        self.on_music_volume,
                        self.volumes,
                        int(soundex.music_player.volume * 10) )
                    )
        items.append( ToggleMenuItem('Show FPS:', self.on_show_fps, director.show_FPS) )
        items.append( MenuItem('Fullscreen', self.on_fullscreen) )
        items.append( MenuItem('Back', self.on_quit) )
        self.create_menu( items, shake(), shake_back() )

    def on_fullscreen( self ):
        director.window.set_fullscreen( not director.window.fullscreen )

    def on_quit( self ):
        self.parent.switch_to( 0 )

    def on_show_fps( self, value ):
        director.show_FPS = value

    def on_sfx_volume( self, idx ):
        vol = idx / 10.0
        soundex.sound_volume( vol )

    def on_music_volume( self, idx ):
        vol = idx / 10.0
        soundex.music_volume( vol )

class MainMenu( Menu ):

    def __init__(self):
        super( MainMenu, self).__init__('TETRICO') 

        self.select_sound = soundex.load('move.mp3')

        # you can override the font that will be used for the title and the items
        # you can also override the font size and the colors. see menu.py for
        # more info
        self.font_title['font_name'] = 'Edit Undo Line BRK'
        self.font_title['font_size'] = 72
        self.font_title['color'] = (204,164,164,255)

        self.font_item['font_name'] = 'Edit Undo Line BRK',
        self.font_item['color'] = (32,16,32,255)
        self.font_item['font_size'] = 32
        self.font_item_selected['font_name'] = 'Edit Undo Line BRK'
        self.font_item_selected['color'] = (32,16,32,255)
        self.font_item_selected['font_size'] = 46


        # example: menus can be vertical aligned and horizontal aligned
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []

        items.append( MenuItem('New Game', self.on_new_game) )
        items.append( MenuItem('Options', self.on_options) )
        items.append( MenuItem('Scores', self.on_scores) )
        items.append( MenuItem('Quit', self.on_quit) )

        self.create_menu( items, shake(), shake_back() )

    def on_new_game(self):
        import gameview
        director.push( FlipAngular3DTransition(
            gameview.get_newgame(), 1.5 ) )

    def on_options( self ):
        self.parent.switch_to(1)


    def on_scores( self ):
        pass

    def on_quit(self):
        pyglet.app.exit()

if __name__ == "__main__":

    pyglet.resource.path.append('data')
    pyglet.resource.reindex()
    font.add_directory('data')

    director.init( resizable=True, width=600, height=720 )
    scene = Scene()
    scene.add( MultiplexLayer(
                    MainMenu(), 
                    OptionsMenu() ),
                z=1 ) 
    scene.add( BackgroundLayer(), z=0 )
    director.run( scene )
