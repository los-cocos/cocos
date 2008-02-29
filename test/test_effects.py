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
from cocos.effect import TextureFilterEffect, ColorizeEffect
import pyglet
from pyglet import font
from pyglet.window import key
from pyglet.gl import *

class PictureLayer(Layer):

    def __init__ (self, y):
        self.x = 100
        self.y = y
        self.speed = 35
        self.img = pyglet.image.load ('ball.png')
    
    def step (self, dt):
        self.x += self.speed * dt
        if self.x > 200 and self.speed > 0: self.speed = -self.speed
        if self.x < 100 and self.speed < 0: self.speed = -self.speed
        self.img.blit (self.x, self.y)

class MyEffect (TextureFilterEffect):
    def __init__ (self, scale=1.0):
        super (MyEffect, self).__init__ ()
        self.scale=scale

    def show (self):
        self.texture.blit (0, 0, width=director.get_window_size()[0]*self.scale)

class DynamicColorizeEffect (ColorizeEffect):
    def __init__ (self):
        super (ColorizeEffect, self).__init__ ()
        self.color = (1,1,1,1)
        self.timer = 0

    def prepare (self, target, dt):
        super (ColorizeEffect, self).prepare (target, dt)
        self.timer += dt
        # red glow: 
        red = self.timer % 2
        if red > 1: red = 2-red
        # set color
        self.color = (red,1,1,1)
        
class ControlLayer(Layer):
    def step(self, dt):
        ft_title = font.load( None, 32 )
        ft_subtitle = font.load( None, 18 )
        ft_help = font.load( None, 16 )

        self.text_title = font.Text(ft_title, "Effect Demos",
            x=5,
            y=480,
            halign=font.Text.LEFT,
            valign=font.Text.TOP)
        self.text_title.draw()

        self.text_subtitle = font.Text(ft_subtitle, effects[current_effect][0],
            x=5,
            y=400,
            halign=font.Text.LEFT,
            valign=font.Text.TOP)
        self.text_subtitle.draw()
        
        self.text_help = font.Text(ft_help,"Press LEFT / RIGHT for prev/next example",
            x=320,
            y=20,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER)
        self.text_help.draw()
        
    def on_key_press( self, k , m ):
        global current_effect
        if k == key.LEFT:
            current_effect = (current_effect-1)%len(effects)
            ball.set_effect(effects[current_effect][1])
        if k == key.RIGHT:
            current_effect = (current_effect+1)%len(effects)
            ball.set_effect(effects[current_effect][1])


current_effect = 0

if __name__ == "__main__":
    director.init()

    effects = [
        ("ball = Layer(...)\n"
         " No effect", None),
        ("ball.set_effect (ColorizeEffect(color=(0.5,1,0.5,0.65)))\n"
         " Greenish hue, 65% opacity", ColorizeEffect(color=(0.5,1,0.5,0.65))),
        ("ball.set_effect (MyEffect(0.5))\n"
         " You can define a custom effect. This one scales horizontally", MyEffect(0.5)),
        ("ball.set_effect (DynamicColorizeEffect())\n"
         " Dynamic colorize effect made inheriting ColorizeEffect\n"
         " and redefining prepare() to change self.color each frame", DynamicColorizeEffect()),
              ]
    ball = PictureLayer(240)
    director.run( Scene (ColorLayer(0.1,0.1,0.2,1), ball, ControlLayer()) )


