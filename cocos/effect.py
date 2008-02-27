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
        self.texture = self.texture.get_region(0, 0, director.window.width, director.window.height)

    def prepare (self, target, dt):
        director.window.clear()
        target.step (dt)
        buffer = image.get_buffer_manager().get_color_buffer()
        self.texture.blit_into(buffer, 0, 0, 0)
            
    def show (self):
        self.texture.blit (0, 0)

class TextureFilterEffectPbuffer (Effect):

    """Base class for texture based effects. Prepare setups self.texture,
    with a window sized capture. Show just blits the texture, override to
    do more interesting things.
    Requires pbuffer extensions
    
    NOT WORKING"""
    def __init__ (self):
        self.pbuf = Pbuffer(director.window, [
            GLX_CONFIG_CAVEAT, GLX_NONE,
            GLX_RED_SIZE, 8,
            GLX_GREEN_SIZE, 8,
            GLX_BLUE_SIZE, 8,
            GLX_DEPTH_SIZE, 24,
            GLX_DOUBLEBUFFER, 1,
            ])
        self.texture = image.Texture.create_for_size(GL_TEXTURE_2D, 
            director.window.width, director.window.height, GL_RGB)
        self.texture = self.texture.get_region(0, 0, director.window.width, director.window.height)

    def prepare (self, target, dt):
        self.pbuf.switch_to()
        gl.glViewport(0, 0, self.pbuf.width, self.pbuf.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.pbuf.width, 0, self.pbuf.height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        target.step (dt)
        buffer = image.get_buffer_manager().get_color_buffer()
        self.texture.blit_into (buffer, 0, 0, 0)
        director.window.switch_to()
            
    def show (self):
        self.texture.blit (0, 0)

class TextureFilterEffectFramebuffer (Effect):
    """Base class for texture based effects. Prepare setups self.texture,
    with a window sized capture. Show just blits the texture, override to
    do more interesting things.
    Requires framebuffer_object extensions"""
    def __init__ (self):
        self.fbuf = FramebufferObject()
        self.texture = image.Texture.create_for_size(GL_TEXTURE_2D, 
            director.window.width, director.window.height, GL_RGB)
        self.fbuf.bind()
        self.fbuf.texture2d (self.texture)
        self.fbuf.check_status()
        self.fbuf.unbind()
        self.texture = self.texture.get_region(0, 0, director.window.width, director.window.height)

    def prepare (self, target, dt):
        self.fbuf.bind()
        glClear(GL_COLOR_BUFFER_BIT)
        target.step (dt)
        buffer = image.get_buffer_manager().get_color_buffer()
        self.fbuf.unbind()
            
    def show (self):
        self.texture.blit (0, 0)

