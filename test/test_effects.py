#
# Los Cocos: Transition Example
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
        self.texture.blit (0, 0, width=director.window.width*self.scale)

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
        
if __name__ == "__main__":
    director.init()
    # One little ball is scaled
    l1 = PictureLayer(50)
    l1.set_effect (MyEffect(0.5))
    # The one above it is translucent
    l2 = PictureLayer(100)
    l2.set_effect (ColorizeEffect(color=(0.5,1,0.5,0.75))) # 75 % opacity, greenish hue
    # The one above it is translucent
    l3 = PictureLayer(150)
    l3.set_effect (DynamicColorizeEffect())
    # The one above has no effect
    l4 = PictureLayer(200)
    director.run( Scene (ColorLayer(0.8,0.8,0.8,1), l1, l2, l3, l4) )


