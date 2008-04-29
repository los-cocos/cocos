#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
'''Transitions between Scenes'''

import pyglet
from pyglet import image
from pyglet.gl import *

from math import *
import cocos.scene as scene
from cocos.director import director
import cocos.framegrabber as framegrabber

__all__ = ['TransitionScene',
            'Quad2DTransition',
            'FadeTransition',
            'GrowTransition', ]

class TransitionScene(scene.Scene):
    """
    A Scene that takes two scenes and makes a transition between them
    """
    in_texture = None
    out_texture = None
    
    def __init__(self, out_scene, in_scene, duration=2):
        self.in_scene = in_scene
        self.out_scene = out_scene
        if self.in_texture is None:
            TransitionScene.in_texture = image.Texture.create_for_size(
                    GL_TEXTURE_2D, director.window.width, 
                    director.window.height, GL_RGB)
        
        self.in_grabber = framegrabber.TextureGrabber()
        self.in_grabber.grab (self.in_texture)
        
        if self.out_texture is None:
            TransitionScene.out_texture = image.Texture.create_for_size(
                    GL_TEXTURE_2D, director.window.width, 
                    director.window.height, GL_RGB)
        
        self.out_grabber = framegrabber.TextureGrabber()
        self.out_grabber.grab (self.out_texture)
        
        self.dt = 0.0
        self.duration = duration

        super(TransitionScene, self).__init__()
        
class Quad2DTransition(TransitionScene):
    """
    Slides out one scene while sliding in onother.
    """    

    def __init__( self, *args, **kwargs ):
        super(Quad2DTransition, self ).__init__( *args, **kwargs)
        self.schedule( self.step )

    def step(self, dt):
        self.dt += dt
        if self.dt >= self.duration:
            self.unschedule(self.step)
            director.replace( self.in_scene )

    def on_draw( self ):
        # draw scene one
        self.out_grabber.before_render(self.out_texture)
        self.out_scene.visit()
        self.out_grabber.after_render(self.out_texture)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw scene two
        self.in_grabber.before_render(self.in_texture)
        self.in_scene.visit()
        self.in_grabber.after_render(self.in_texture)
    
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_scenes()
        
    def draw_scenes(self):
        #paste both scenes
        self.blit_texture( self.out_texture, self.out_proyect)
        self.blit_texture( self.in_texture, self.in_proyect)
        
    def blit_texture(self, texture, p):
        x, y = director.get_window_size()
        
        glEnable(GL_TEXTURE_2D)        
        glBindTexture(texture.target, texture.id)
        
        txz = director._offset_x/float(texture.width)
        tyz = director._offset_y/float(texture.height)
        
        rx = director.window.width - 2*director._offset_x
        ry = director.window.height - 2*director._offset_y
        
        tx = float(rx)/texture.width+txz
        ty = float(ry)/texture.height+tyz
        
        glBegin(GL_QUADS)
        glTexCoord2d(txz,tyz); glVertex2d(*p(0.0,0.0));
        glTexCoord2d(tx,tyz); glVertex2d(*p(x,0.0));
        glTexCoord2d(tx,ty); glVertex2d(*p(x,y));
        glTexCoord2d(txz,ty); glVertex2d(*p(0.0,y));
        glEnd()
        glDisable(GL_TEXTURE_2D)
        
    
class FadeTransition(Quad2DTransition):
    def draw_scenes(self):
        #paste both scenes
        p = self.dt/self.duration
        glColor4f(1,1,1,max(0,1-p*2))
        self.blit_texture( self.out_texture, self.out_proyect)
        if p > 0.5:
            glColor4f(1,1,1,p*2-1)
            self.blit_texture( self.in_texture, self.in_proyect)
        glColor4f(1,1,1,1)
        
    def out_proyect(self, x, y):
        return (x, y)
    
    def in_proyect(self, x, y):
        return (x, y)    


class GrowTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        dx = director.get_window_size()[0] * ((self.dt/self.duration))
        if x!=0:
            return (director.get_window_size()[0]-dx, y)
        return (x, y)
    
    def in_proyect(self, x, y):
        dx = director.get_window_size()[0] * ((self.dt/self.duration))
        if x==0:
            return (director.get_window_size()[0]-dx, y)
        return (x, y)       
