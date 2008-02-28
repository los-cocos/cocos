from director import director
from pyglet.gl import *

from pyglet import image
from framegrabber import TextureGrabber

class Effect(object):
    """Base class for effects. Effects are applied to layers (or
    anything that is shown with a step (dt) method). Useful effects can
    inherit this one, which is just the identity effect"""
    
    def prepare (self, target, dt):
        """Advance target in dt, preparing effect display."""
        self.target = target
        self.dt = dt
    
    def show (self):
        """Show on screen"""
        self.target.step (self.dt)

class TextureFilterEffect (Effect):
    """Base class for texture based effects. Prepare setups self.texture,
    with a window sized capture. Show just blits the texture, override to
    do more interesting things"""
    def __init__ (self):
        self.texture = image.Texture.create_for_size(GL_TEXTURE_2D, 
            director.window.width, director.window.height, GL_RGBA)
        
        self._grabber = TextureGrabber()
        self._grabber.grab (self.texture)
        
        self.texture = self.texture.get_region(0, 0, director.window.width, director.window.height)

    def prepare (self, target, dt):
        self._grabber.before_render(self.texture)
        target.step (dt)
        self._grabber.after_render(self.texture)
            
    def show (self):
        self.texture.blit (0, 0)

class ColorizeEffect (TextureFilterEffect):
    """Applies recoloring (multiplication) and alpha blending."""
    def __init__ (self, color=(1,1,1,1)):
        super (ColorizeEffect, self).__init__ ()
        self.color = color

    def show (self):
        glEnable (GL_BLEND)
        glColor4f (*self.color)
        self.texture.blit (0, 0)
        glColor4f (1,1,1,1)
        # Not disabling this, other people assumes it is on :( (including image.blit)
        #glDisable (GL_BLEND) 

