# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


import cocos
from cocos.director import director

import pyglet
from pyglet import font, image
from pyglet.gl import *
from cocos.actions import ActionSprite

class HelloWorld(cocos.layer.Layer):
    def __init__(self):

        super( HelloWorld, self ).__init__()

        # see pyglet documentation for help on this lines
        self.text = pyglet.text.Label('Hello, World!', font_name='', font_size=32, x=100, y=240, batch=self.batch)

        
class BackgroundLayer(cocos.layer.Layer):
    """
    """
    def __init__( self, path_name ):
        self.image = image.load(path_name)
        
        
    def step(self, dt):
        texture = self.image.texture
        
        rx = director.window.width - 2*director._offset_x
        ry = director.window.height - 2*director._offset_y
        
        tx = float(rx)/texture.width
        ty = float(ry)/texture.height


        glEnable(GL_TEXTURE_2D)        
        glBindTexture(texture.target, texture.id)

        x, y = director.get_window_size()
        glBegin(gl.GL_QUADS)
        glTexCoord2d(0,0);
        glVertex2f( 0, 0 )
        glTexCoord2d(0,ty);
        glVertex2f( 0, y )
        glTexCoord2d(tx,ty);
        glVertex2f( x, y )
        glTexCoord2d(tx,0);
        glVertex2f( x, 0 )
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
        
        
class TitleLayer(cocos.layer.Layer):
    def __init__(self, text):
        # see pyglet documentation for help on this lines
        ft = font.load('Gill Sans', 64)
        self.text = font.Text(ft, text, x=100, y=240)
        
    def step(self, dt):
        # this function is called on every frame
        # dt is the elapsed time between this frame and the last        
        self.text.draw()

    
if __name__ == "__main__":
    director.init()
    
    background = BackgroundLayer("background.png")
    #background = BackgroundLayer("coconut.jpg")
    main_scene = cocos.scene.Scene (background, TitleLayer("holamundo!"))
    director.run (main_scene)

