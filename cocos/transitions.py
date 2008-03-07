from pyglet import image
from pyglet.gl import *

from math import *
import scene
from director import director
import framegrabber

__all__ = ['TransitionScene',
            'Quad2DTransition',
            'SlideLRTransition','SlideRLTransition',
            'SlideBTTransition','SlideTBTransition',
            'MoveInLTransition','MoveInRTransition',
            'MoveInBTransition','MoveInTTransition',
            'FadeTransition',
            'ShrinkAndGrow',
            'CornerMoveTransition',
            'GrowTransition', ]

class TransitionScene(scene.Scene):
    """
    A Scene that takes two scenes and makes a transition
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

        self.scheduled = False
        
        super(TransitionScene, self).__init__()

    # helper functions
    def disable_step( self ):
        """Disables the step callback"""
        self.scheduled = False
        pyglet.clock.unschedule( self.step )

    def enable_step( self ):
        """Enables the step callback. It calls the `step` method every frame"""
        if not self.scheduled:
            self.scheduled = True 
            pyglet.clock.schedule( self.step )
        
    def step( self, dt ):
        pass

class Quad2DTransition(TransitionScene):
    """
    Slides out one scene while sliding in onother.
    """    

    def __init__( self, *args, **kwargs ):
        super(Quad2DTransition, self ).__init__( *args, **kwargs)
        self.enable_step()

    def step(self, dt):
        self.dt += dt
        if self.dt >= self.duration:
            self.disable_step()
            director.replace( self.in_scene )

    def on_draw( self ):
        x, y = director.get_window_size()
        # draw scene one
        self.out_grabber.before_render(self.out_texture)
        self.out_scene.on_draw()
        self.out_grabber.after_render(self.out_texture)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw scene two
        self.in_grabber.before_render(self.in_texture)
        self.in_scene.on_draw()
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

class SlideLRTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        dx = director.get_window_size()[0] * (self.dt/self.duration)
        return (x-dx, y)
    
    def in_proyect(self, x, y):
        dx = director.get_window_size()[0] * (1-self.dt/self.duration)
        return (x+dx, y)    

class SlideRLTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        dx = director.get_window_size()[0] * (self.dt/self.duration)
        return (x+dx, y)
    
    def in_proyect(self, x, y):
        dx = director.get_window_size()[0] * (1-self.dt/self.duration)
        return (x-dx, y)    
        
class SlideBTTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        dy = director.get_window_size()[1] * (self.dt/self.duration)
        return (x, y+dy)
    
    def in_proyect(self, x, y):
        dy = director.get_window_size()[1] * (1-self.dt/self.duration)
        return (x, y-dy)    
        
class SlideTBTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        dy = director.get_window_size()[1] * (self.dt/self.duration)
        return (x, y-dy)
    
    def in_proyect(self, x, y):
        dy = director.get_window_size()[1] * (1-self.dt/self.duration)
        return (x, y+dy)    
        
class MoveInTTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        return (x, y)
    
    def in_proyect(self, x, y):
        dy = director.get_window_size()[1] * (1-self.dt/self.duration)
        return (x, y+dy)    

class MoveInBTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        return (x, y)
    
    def in_proyect(self, x, y):
        dy = director.get_window_size()[1] * (1-self.dt/self.duration)
        return (x, y-dy)  
                
class MoveInLTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        return (x, y)
    
    def in_proyect(self, x, y):
        dx = director.get_window_size()[0] * (1-self.dt/self.duration)
        return (x-dx, y)  

class MoveInRTransition(Quad2DTransition):       
    def out_proyect(self, x, y):
        return (x, y)
    
    def in_proyect(self, x, y):
        dx = director.get_window_size()[0] * (1-self.dt/self.duration)
        return (x+dx, y)  

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

class CornerMoveTransition(Quad2DTransition):  
      
    def out_proyect(self, x, y):
        if not (x!=0 and y==0): return x,y
        xz, yz = director.get_window_size()
        dt = (self.dt/self.duration)
        x = xz * (1-dt)
        y = yz * dt
        return (x, y)
    
    def in_proyect(self, x, y):
        if not (x==0 and y!=0): return x,y
        xz, yz = director.get_window_size()
        dt = (self.dt/self.duration)
        x = xz * (1-dt)
        y = yz * dt
        return (x, y)
    

class ShrinkAndGrow(Quad2DTransition):       
    def draw_scenes(self):
        #paste both scenes
        
        if self.dt/self.duration < 0.5:
            self.blit_texture( self.in_texture, self.in_proyect)
            self.blit_texture( self.out_texture, self.out_proyect)
        else:
            self.blit_texture( self.out_texture, self.out_proyect)
            self.blit_texture( self.in_texture, self.in_proyect)
        
        
    def out_proyect(self, x, y):
        dt = (self.dt/self.duration)
        cx = director.get_window_size()[0]/4
        cy = director.get_window_size()[1]/2
        return ((x-cx)*(1-dt)+cx, (y-cy)*(1-dt)+cy)
    
    def in_proyect(self, x, y):
        dt = (self.dt/self.duration)
        cx = director.get_window_size()[0]/4*3
        cy = director.get_window_size()[1]/2
        return ((x-cx)*(dt)+cx, (y-cy)*(dt)+cy)
       

