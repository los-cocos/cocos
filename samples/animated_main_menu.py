#
# Cocos: Multi-Menu Example
# http://code.google.com/p/los-cocos/
#
# Particle Engine done by Phil Hassey
# http://www.imitationpickles.org
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
from pyglet.gl import *

from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *
from cocos.actions import *
from cocos.sprite import ActionSprite

import random; rr = random.randrange


class Fire: 
    def __init__(self,x,y,vy,frame,size):
        self.x,self.y,self.vy,self.frame,self.size = x,y,vy,frame,size

class FireManager( Layer ):
    def __init__(self, view_width, num):
        super( FireManager, self ).__init__()

        self.view_width = view_width
        self.goodies = []
        self.batch = pyglet.graphics.Batch()
        self.fimg = pyglet.resource.image('fire.jpg')
        self.group = pyglet.sprite.SpriteGroup(self.fimg.texture,
            blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE)
        self.vertex_list = self.batch.add(4*num, GL_QUADS, self.group,
            'v2i', 'c4B', ('t3f', self.fimg.texture.tex_coords*num))
        for n in xrange(0, num):
            f = Fire(0,0,0,0,0)
            self.goodies.append(f)
            self.vertex_list.vertices[n*8:(n+1)*8] = [0, 0, 0, 0, 0, 0, 0, 0]
            self.vertex_list.colors[n*16:(n+1)*16] = [0,0,0,0,] * 4

        self.schedule( self.step )

    def step(self,dt):
        w,h = self.fimg.width,self.fimg.height
        fires = self.goodies
        verts, clrs = self.vertex_list.vertices, self.vertex_list.colors
        for n,f in enumerate(fires):
            if not f.frame:
                f.x = rr(0,self.view_width)
                f.y = rr(-120,-80)
                f.vy = rr(40,70)/100.0
                f.frame = rr(50,250)
                f.size = 8+pow(rr(0.0,100)/100.0,2.0)*32;
                f.scale= f.size/32.0
            
            x = f.x = f.x+ rr(-50,50)/100.0
            y = f.y = f.y+f.vy*4
            c = 3*f.frame/255.0;
            r,g,b = (min(255,int(c*0xc2)),min(255,int(c*0x41)),min(255,int(c*0x21)))
            f.frame -= 1
            ww,hh = w*f.scale,h*f.scale
            x-=ww/2
            verts[n*8:(n+1)*8] = map(int,[x,y,x+ww,y,x+ww,y+hh,x,y+hh])
            clrs[n*16:(n+1)*16] = [r,g,b,255] * 4

    def on_draw( self ):
        self.batch.draw()


class SpriteLayer ( Layer ):

    def __init__( self ):
        super( SpriteLayer, self ).__init__()

        sprite1 = ActionSprite('grossini.png' )
        sprite2 = ActionSprite('grossinis_sister1.png')
        sprite3 = ActionSprite('grossinis_sister2.png')

        sprite1.position = (320,240)
        sprite2.position = (620,100)
        sprite3.position = (20,100)

        self.add( sprite1 )
        self.add( sprite2 )
        self.add( sprite3 )

        ju_right = Jump( y=100, x=600, jumps=4, duration=5 )
        ju_left = Jump( y=100, x=-600, jumps=4, duration=5 )
        rot1 = Rotate( 180 * 4, duration=5)

        sprite1.opacity = 128

        sc = ScaleBy( 9, 5 )
        rot = Rotate( 180, 5 )
        

        sprite1.do( Repeat( sc + Reverse(sc) ) )
        sprite1.do( Repeat( rot + Reverse(rot) ) )
        sprite2.do( Repeat( ju_left + Reverse(ju_left) ) )
        sprite2.do( Repeat( Reverse(rot1) + rot1 ) )
        sprite3.do( Repeat( ju_right + Reverse(ju_right) ) )
        sprite3.do( Repeat( rot1 + Reverse(rot1) ) )

class MainMenu(Menu):
    def __init__( self ):

        # call superclass with the title
        super( MainMenu, self ).__init__("GROSSINI'S SISTERS" )

        pyglet.font.add_directory('.')

        # you can override the font that will be used for the title and the items
        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        # you can also override the font size and the colors. see menu.py for
        # more info

        # example: menus can be vertical aligned and horizontal aligned
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        self.add( MenuItem('New Game', self.on_new_game ) )
        self.add( MenuItem('Options', self.on_options ) )
        self.add( MenuItem('Scores', self.on_scores ) )
        self.add( MenuItem('Quit', self.on_quit ) )

        # after adding all the items just call build_items()
        self.build_items()


    # Callbacks
    def on_new_game( self ):
#        director.set_scene( StartGame() )
        print "on_new_game()"
           

    def on_scores( self ):
        self.parent.switch_to( 2 )

    def on_options( self ):
        self.parent.switch_to( 1 )

    def on_quit( self ):
        pyglet.app.exit()


class OptionMenu(Menu):
    def __init__( self ):
        super( OptionMenu, self ).__init__("GROSSINI'S SISTERS" )

        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        self.menu_valign = BOTTOM
        self.menu_halign = RIGHT

        self.add( MenuItem('Fullscreen', self.on_fullscreen) )
        self.add( ToggleMenuItem('Show FPS', True, self.on_show_fps) )
        self.add( MenuItem('OK', self.on_quit) )
        self.build_items()

    # Callbacks
    def on_fullscreen( self ):
        director.window.set_fullscreen( not director.window.fullscreen )

    def on_quit( self ):
        self.parent.switch_to( 0 )

    def on_show_fps( self, value ):
        director.show_FPS = value

class ScoreMenu(Menu):
    def __init__( self ):
        super( ScoreMenu, self ).__init__("GROSSINI'S SISTERS" )

        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72
        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        self.menu_valign = BOTTOM
        self.menu_halign = LEFT

        self.add( MenuItem('Go Back', self.on_quit) )
        self.build_items()

    def on_quit( self ):
        self.parent.switch_to( 0 )


if __name__ == "__main__":
    director.init( resizable=True)
    scene =Scene( 
            FireManager(director.get_window_size()[0], 250),
            SpriteLayer(),
            MultiplexLayer( MainMenu(), OptionMenu(), ScoreMenu() )
            )

    lens = Lens3D( radius=240, center=(320,240), grid=(32,24), duration=5)
    waves3d = AccelDeccelAmplitude( Waves3D( waves=18, amplitude=80, grid=(20,20), duration=15), rate=4.0 )
    flipx =  FlipX3D(duration=1)
    flipy = FlipY3D(duration=1)
    flip = Flip(duration=1)
    liquid = Liquid( grid=(16,12), duration=8)
    shuffle = ShuffleTiles( grid=(16,12), duration=5)
    shakyt = ShakyTiles( grid=(16,12), duration=5)
    shaky = Shaky( grid=(16,12), duration=5)
    corners = CornerSwap( duration=1)
    waves = Waves( grid=(32,24), duration=5)
    shattered = ShatteredTiles( grid=(32,24), duration=1 )
    quadmove = QuadMoveBy( delta0=(320,240), delta1=(-630,0), delta2=(-320,-240), delta3=(630,0), duration=2 )


#    scene.do( ShuffleTiles( grid(16,16), duration=5) + Liquid( grid=(16,16), duration=500) )
    scene.do(
              Delay(3) +
              DoAndPause( quadmove, duration=1) +
              Reverse(quadmove) +
              shuffle +
              DoAndPause(liquid, duration=4) +
              DoAndPause(flipx, duration=4) + 
              DoAndPause(shakyt, duration=4) +
              DoAndPause(flip, duration=4) +
              Reverse(flip) +
              lens +
              DoAndPause(flipy, duration=4) + 
              waves3d +
              DoAndPause(shaky, duration=4) +
              DoAndPause(corners, duration=4) +
              Reverse(corners) +
              DoAndPause(waves, duration=4) +
              DoAndPause(shattered, duration=4)
              )

    director.run( scene )
