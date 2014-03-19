from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

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
import hiscore

class ScoresLayer( ColorLayer):

    FONT_SIZE=30

    is_event_handler = True #: enable pyglet's events

    def __init__(self):

        w,h = director.get_window_size()
        super( ScoresLayer,self).__init__( 32,32,32,16, width=w, height=h-86)

        self.font_title = {}

        # you can override the font that will be used for the title and the items
        self.font_title['font_name'] = 'Edit Undo Line BRK'
        self.font_title['font_size'] = 72
        self.font_title['color'] = (204,164,164,255)
        self.font_title['anchor_y'] ='top'
        self.font_title['anchor_x'] ='center'

        title = Label('TETRICO', **self.font_title )

        title.position=(w/2.0,h)

        self.add(title,z=1)

        self.table = None

    def on_enter( self ):
        super(ScoresLayer,self).on_enter()

        scores = hiscore.hiscore.get()

        if self.table:
            self.remove_old()

        self.table =[]
        for idx,s in enumerate(scores):

            pos= Label( '%d:' % (idx+1), font_name='Edit Undo Line BRK',
                        font_size=self.FONT_SIZE,
                        anchor_y='top',
                        anchor_x='left',
                        color=(255,255,255,255) )

            name = Label( s[1], font_name='Edit Undo Line BRK',
                        font_size=self.FONT_SIZE,
                        anchor_y='top',
                        anchor_x='left',
                        color=(255,255,255,255) )

            score = Label( str(s[0]), font_name='Edit Undo Line BRK',
                        font_size=self.FONT_SIZE,
                        anchor_y='top',
                        anchor_x='right',
                        color=(255,255,255,255) )

            lvl = Label( str(s[2]), font_name='Edit Undo Line BRK',
                        font_size=self.FONT_SIZE,
                        anchor_y='top',
                        anchor_x='right',
                        color=(255,255,255,255) )

            self.table.append( (pos,name,score,lvl) )

        self.process_table()

    def remove_old( self ):
        for item in self.table:
            pos,name,score,lvl = item
            self.remove(pos)
            self.remove(name)
            self.remove(score)
            self.remove(lvl)
        self.table = None

    def process_table( self ):
        w,h = director.get_window_size()

        for idx,item in enumerate(self.table):
            pos,name,score,lvl = item

            posy = h - 100 - ( (self.FONT_SIZE+15) * idx )

            pos.position=( 5, posy)
            name.position=( 48, posy)
            score.position=( w-150, posy )
            lvl.position=( w-10, posy)

            self.add( pos, z=2 )
            self.add( name, z=2 )
            self.add( score, z=2 )
            self.add( lvl, z=2 )

    def on_key_press( self, k, m ):
        if k in (key.ENTER, key.ESCAPE, key.SPACE):
            self.parent.switch_to( 0 )
            return True

    def on_mouse_release( self, x, y, b, m ):
        self.parent.switch_to( 0 )
        return True


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
        self.menu_anchor_y = CENTER
        self.menu_anchor_x = CENTER

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
        self.menu_anchor_y = CENTER
        self.menu_anchor_x = CENTER

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
        self.parent.switch_to(2)

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
                    OptionsMenu(),
                    ScoresLayer(),
                    ),
                z=1 ) 
    scene.add( BackgroundLayer(), z=0 )
    director.run( scene )
