#
# Los Cocos: Effect Example
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.director import director
from cocos.layer import Layer, ColorLayer 
from cocos.scene import Scene
from cocos.effect import TextureFilterEffect, ColorizeEffect, RepositionEffect
from cocos.actions import *

import pyglet
from pyglet import font
from pyglet.window import key
from pyglet.gl import *

class PictureLayer(Layer):

    def __init__ (self, y):
        super( PictureLayer, self ).__init__()
        img0 = pyglet.image.load ('ball.png')
        img1 = pyglet.image.load ('grossini.png')
        img2 = pyglet.image.load ('grossinis_sister1.png')
        img3 = pyglet.image.load ('grossinis_sister2.png')

        sprite1 = ActionSprite( img0 )
        sprite1.do( Repeat( MoveBy( (500,0), 5 ) + MoveBy( (-500,0), 5 ) ))

        sprite2 = ActionSprite( img1 )
        sprite2.do( Repeat( MoveBy( (500,0), 4 ) + MoveBy( (-500,0), 4 ) ) )

        sprite3 = ActionSprite( img2 )
        sprite3.do( Repeat( MoveBy( (500,0), 3 ) + MoveBy( (-500,0), 3 ) ) )

        sprite4 = ActionSprite( img3 )
        sprite4.do( Repeat( MoveBy( (500,0), 2 ) + MoveBy( (-500,0), 2 ) ) )

        self.add( sprite1, position=(20,40) )
        self.add( sprite2, position=(20,120) )
        self.add( sprite3, position=(20,210) )
        self.add( sprite4, position=(20,300) )

    def on_exit( self ):
        for o in self.objects:
            if hasattr(o, "stop"):
                o.stop()
    
class DynamicColorizeEffect (ColorizeEffect):
    def __init__ (self):
        super (DynamicColorizeEffect, self).__init__ ()
        self.color = (1,1,1,1)
        self.timer = 0

        pyglet.clock.schedule( self.step )

    def step( self, dt ):
        self.timer += dt
    
    def show(self):
        # red glow: 
        red = self.timer % 2
        if red > 1: red = 2-red
        # set color
        self.color = (red,1,1,1)
        super (DynamicColorizeEffect, self).show()
        
class ControlLayer(Layer):

    def on_enter( self ):

        self.text_title = pyglet.text.Label("Effect Demos",
            font_size=32,
            x=5,
            y=director.get_window_size()[1],
            halign=font.Text.LEFT,
            valign=font.Text.TOP,
            batch=self.batch)

        self.text_subtitle = pyglet.text.Label(effects[current_effect][0],
            font_size=16,
            multiline=True,
            x=5,
            y=director.get_window_size()[1] - 80,
            halign=font.Text.LEFT,
            valign=font.Text.TOP,
            batch=self.batch )

        self.text_help = pyglet.text.Label("Press LEFT / RIGHT for prev/next test",
            font_size=16,
            x=director.get_window_size()[0] /2,
            y=20,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER,
            batch=self.batch )

    def on_key_press( self, k , m ):
        global current_effect
        if k == key.LEFT:
            current_effect = (current_effect-1)%len(effects)
            ball.set_effect(effects[current_effect][1])
        elif k == key.RIGHT:
            current_effect = (current_effect+1)%len(effects)
            ball.set_effect(effects[current_effect][1])

        if k in( key.LEFT, key.RIGHT ):
            self.text_subtitle.text = effects[current_effect][0]

current_effect = 0

if __name__ == "__main__":
    director.init( resizable=True )
#    director.window.set_fullscreen(True)

    effects = [
        ("ball = Layer(...)\n"
         " No effect", None),
        ("ball.set_effect (ColorizeEffect(color=(0.5,1,0.5,0.65)))\n"
         " Greenish hue, 65% opacity", ColorizeEffect(color=(0.5,1,0.5,0.65))),
        ("ball.set_effect (RepositionEffect(width=director.get_window_size()[0]/2))\n"
         " Horizontally scaled 50%", RepositionEffect(width=director.get_window_size()[0]/2)),
        ("ball.set_effect (DynamicColorizeEffect())\n"
         " Dynamic colorize effect made inheriting ColorizeEffect\n"
         " and redefining show() to change self.color each frame", DynamicColorizeEffect()),
              ]
    ball = PictureLayer(240)
    director.run( Scene (ColorLayer(0.0,0.0,1.0,1.0), ball, ControlLayer()) )
