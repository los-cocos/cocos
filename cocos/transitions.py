from pyglet.gl import *
from pyglet import image

from math import *
import scene
from director import director

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
        
        self.dt = 0
        self.duration = duration
        
        super(Quad2DTransition, self).__init__()
        
    
    def step(self, dt):
        self.dt += dt
        if self.dt >= self.duration:
            director.replace( self.in_scene )
        x, y = director.window.width, director.window.height
        # draw scene one
        self.out_scene.on_enter()
        self.out_scene.step(dt)
        self.out_scene.on_exit()
        
        # capture and clear
        buffer = image.get_buffer_manager().get_color_buffer()
        out_texture = buffer.texture
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw scene two
        self.in_scene.on_enter()
        self.in_scene.step(dt)
        self.in_scene.on_exit()
        
    
        # capture and clear
        in_buffer = image.get_buffer_manager().get_color_buffer()
        in_texture = buffer.texture
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #paste both scenes
        self.blit_texture( out_texture, self.out_proyect)
        self.blit_texture( in_texture, self.in_proyect)
        
    def blit_texture(self, texture, p):
        glEnable(GL_TEXTURE_2D)        
        glBindTexture(texture.target, texture.id)
        
        #return        
        x = 2**ceil( log( texture.width, 2) )
        y = 2**ceil( log( texture.height, 2) )
        glBegin(GL_QUADS)
        glTexCoord2d(0.0,0.0); glVertex2d(*p(0.0,0.0));
        glTexCoord2d(1,0.0); glVertex2d(*p(x,0.0));
        glTexCoord2d(1.0,1.0); glVertex2d(*p(x,y));
        glTexCoord2d(0.0,1.0); glVertex2d(*p(0.0,y));
        glEnd()
        glDisable(GL_TEXTURE_2D)
        
        
class SlideLRTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        dx = director.window.width * (self.dt/self.duration)
        return (x-dx, y)
    
    def in_proyect(self, x, y):
        dx = director.window.width * (1-self.dt/self.duration)
        return (x+dx, y)    
        
class SlideLRTransition2(Quad2DTransition):       
    def out_proyect(self, x, y):
        dx = director.window.width * ((self.dt/self.duration)**2)
        return (x-dx, y)
    
    def in_proyect(self, x, y):
        dx = director.window.width * (1-(self.dt/self.duration)**2)
        return (x+dx, y)      
        