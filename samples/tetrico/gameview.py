# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# stdlib
import weakref

from pyglet.gl import *

# cocos2d related
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.director import director
from cocos.actions import *

# tetrico related
from gamectrl import *
import levels
from constants import *
import soundex
from HUD import *


__all__ = ['get_newgame']

class GameView( Layer ):

    def __init__(self):
        super(GameView,self).__init__()

        width, height = director.get_window_size()

        aspect = width / float(height)
        self.grid_size = ( int(20 *aspect),20)
        self.duration = 5

        self.position = ( width/2 - COLUMNS * SQUARE_SIZE / 2, 0 )
        self.transform_anchor = ( COLUMNS*SQUARE_SIZE /2, ROWS * SQUARE_SIZE/2)

        # background layer to delimit the pieces visually
        cl = ColorLayer( 112,66,20,30, width = COLUMNS * SQUARE_SIZE, height=ROWS * SQUARE_SIZE )
        self.add( cl, z=-1)

    def on_enter(self):
        super(GameView,self).on_enter()

        self.ctrl = weakref.ref( self.parent.get('controller') )
        self.hud = self.parent.get('hud')

        self.ctrl().push_handlers( self.on_line_complete, \
                                    self.on_special_effect, \
                                    self.on_game_over, \
                                    self.on_level_complete, \
                                    self.on_move_block, \
                                    self.on_drop_block, \
                                    )

        soundex.set_music('tetris.mp3')
        soundex.play_music()

    def on_exit(self):
        super(GameView,self).on_exit()
        soundex.stop_music()

    def on_line_complete( self, lines ):
        soundex.play('line.mp3')
        return True

    def on_move_block(self ):
        soundex.play('move.mp3')
        return True

    def on_drop_block(self ):
        soundex.play('drop.mp3')
        return True

    def on_level_complete( self ):
        soundex.play('level_complete.mp3')
        self.hud.show_message('Level complete', self.ctrl().set_next_level)
        return True

    def on_game_over( self ):
        print 'on_game_over'
        return True

    def on_special_effect( self, effects ):
        print 'on_special_effect:' , effects

        for e in effects.iterkeys():
            a = self.get_action(e)
            self.do( a * effects[e] )

    def get_action( self, e ):
        '''returns the actions for a specific effects'''

        # basic actions
        if e == Colors.ROTATE:
            a = RotateBy( 360, duration=self.duration)
        elif e == Colors.SCALE:
            a = ScaleTo( 0.5, duration=self.duration/2.0) + ScaleTo(1, duration=self.duration/2.0)

        # Grid actions
        elif e == Colors.LIQUID:
            a = Liquid( grid=self.grid_size, duration=self.duration)
        elif e == Colors.WAVES:
            a = Waves( grid=self.grid_size, duration=self.duration)
        elif e == Colors.TWIRL:
            a = Twirl( grid=self.grid_size, duration=self.duration)
        elif e == Colors.LENS:
            w,h = director.get_window_size()
            a = Lens3D( radius=h/2, grid=self.grid_size, duration=self.duration)
        elif e == Colors.SPEED_UP:
            a = Delay( 0 )
        elif e == Colors.SPEED_DOWN:
            a = Delay( 0 )
        else:
            raise Exception("Effect not implemented: %s" % str(e) )
            
        return a

    def draw( self ):
        '''draw the map and the block'''

        glPushMatrix()
        self.transform()

        for i in xrange( COLUMNS ):
            for j in xrange( ROWS ):
                color = self.ctrl().map.get( (i,j) )
                if color:
                    Colors.images[color].blit( i * SQUARE_SIZE, j* SQUARE_SIZE)
        self.ctrl().block.draw()

        glPopMatrix()


def get_newgame():
    '''returns the game scene'''
    scene = Scene()

    # init model and controller
    scene.add( GameCtrl( levels.Level1() ), z=1, name="controller" )

    # init view
    scene.add( HUD(), z=3, name="hud" )
    scene.add( BackgroundLayer(), z=0, name="background" )
    scene.add( GameView(), z=2, name="view" )

    return scene
