from director import director
from pyglet.gl import *
from pyglet.gl.glx import *
from pyglet import image
from gl_pbuffer import Pbuffer
from gl_framebuffer_object import FramebufferObject

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
            director.window.width, director.window.height, GL_RGB)
        
        self._grabber = TextureGrabber()
        self._grabber.grab (self.texture)
        
        self.texture = self.texture.get_region(0, 0, director.window.width, director.window.height)

    def prepare (self, target, dt):
        self._grabber.before_render(self.texture)
        target.step (dt)
        self._grabber.after_render(self.texture)
            
    def show (self):
        self.texture.blit (0, 0)

# Auxiliar classes for render-to-texture

def TextureGrabber():
    """Return an instance of the best texture grabbing class"""
    return FBOGrabber()

class GenericGrabber(object):
    def grab (self, texture):
        pass
    
    def before_render (self, texture):
        director.window.clear()
        
    def after_render (self, texture):
        buffer = image.get_buffer_manager().get_color_buffer()
        texture.blit_into(buffer, 0, 0, 0)

class PbufferGrabber(object):
    """Requires pbuffer extensions
    
    NOT WORKING
    """
    def grab (self, texture):
        self.pbuf = Pbuffer(director.window, [
            GLX_CONFIG_CAVEAT, GLX_NONE,
            GLX_RED_SIZE, 8,
            GLX_GREEN_SIZE, 8,
            GLX_BLUE_SIZE, 8,
            GLX_DEPTH_SIZE, 24,
            GLX_DOUBLEBUFFER, 1,
            ])
    
    def before_render (self, texture):
        self.pbuf.switch_to()
        gl.glViewport(0, 0, self.pbuf.width, self.pbuf.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.pbuf.width, 0, self.pbuf.height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        
    def after_render (self, texture):
        buffer = image.get_buffer_manager().get_color_buffer()
        texture.blit_into (buffer, 0, 0, 0)
        director.window.switch_to()


class FBOGrabber(object):
    """Base class for texture based effects. Prepare setups self.texture,
    with a window sized capture. Show just blits the texture, override to
    do more interesting things.
    Requires framebuffer_object extensions"""
    def grab (self, texture):
        self.fbuf = FramebufferObject()
        self.fbuf.bind()
        self.fbuf.texture2d (texture)
        self.fbuf.check_status()
        self.fbuf.unbind()
    
    def before_render (self, texture):
        self.fbuf.bind()
        glClear(GL_COLOR_BUFFER_BIT)
        
    def after_render (self, texture):
        self.fbuf.unbind()

