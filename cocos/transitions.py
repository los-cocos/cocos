from pyglet.gl import *
from pyglet import image

from math import *
import scene
from director import director
import framegrabber

class TransitionScene(scene.Scene):
    """
    A Scene that takes two scenes and makes a transition
    """
    
class Quad2DTransition(TransitionScene):
    """
    Slides out one scene while sliding in onother.
    """
    def __init__(self, out_scene, in_scene, duration=10):
        self.in_scene = in_scene
        self.out_scene = out_scene
        self.in_texture = image.Texture.create_for_size(GL_TEXTURE_2D, 
            director.window.width, director.window.height, GL_RGB)
        
        self.in_grabber = framegrabber.TextureGrabber()
        self.in_grabber.grab (self.in_texture)

        self.out_texture = image.Texture.create_for_size(GL_TEXTURE_2D, 
            director.window.width, director.window.height, GL_RGB)
        
        self.out_grabber = framegrabber.TextureGrabber()
        self.out_grabber.grab (self.out_texture)
        
        self.dt = 0
        self.duration = duration
        
        super(Quad2DTransition, self).__init__()
        
    
    def step(self, dt):
        self.dt += dt
        if self.dt >= self.duration:
            director.replace( self.in_scene )
        x, y = director.get_window_size()
        # draw scene one
        self.out_grabber.before_render(self.out_texture)
        self.out_scene.step(dt)
        self.out_grabber.after_render(self.out_texture)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw scene two
        self.in_grabber.before_render(self.in_texture)
        self.in_scene.step(dt)
        self.in_grabber.after_render(self.in_texture)
        
    
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #paste both scenes
        self.blit_texture( self.out_texture, self.out_proyect)
        self.blit_texture( self.in_texture, self.in_proyect)
        
    def blit_texture(self, texture, p):
        glEnable(GL_TEXTURE_2D)        
        glBindTexture(texture.target, texture.id)
        x, y = director.get_window_size()
        
        #return        
        x = 2**ceil( log( x, 2) )
        y = 2**ceil( log( y, 2) )
        glBegin(GL_QUADS)
        glTexCoord2d(0.0,0.0); glVertex2d(*p(0.0,0.0));
        glTexCoord2d(1,0.0); glVertex2d(*p(x,0.0));
        glTexCoord2d(1.0,1.0); glVertex2d(*p(x,y));
        glTexCoord2d(0.0,1.0); glVertex2d(*p(0.0,y));
        glEnd()
        glDisable(GL_TEXTURE_2D)
        
        
class SlideLRTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        dx = director.get_window_size()[0] * (self.dt/self.duration)
        return (x-dx, y)
    
    def in_proyect(self, x, y):
        dx = director.get_window_size()[0] * (1-self.dt/self.duration)
        return (x+dx, y)    
        
class SlideLRTransition2(Quad2DTransition):       
    def out_proyect(self, x, y):
        dx = director.get_window_size()[0] * ((self.dt/self.duration)**2)
        return (x-dx, y)
    
    def in_proyect(self, x, y):
        dx = director.get_window_size()[0] * (1-(self.dt/self.duration)**2)
        print director.get_window_size()[0], x, y, dx
        return (x+dx, y)      
        