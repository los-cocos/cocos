"""Utility classes for rendering to a texture.

It is mostly used for internal implementation of cocos, you normally shouldn't
need it. If you are curious, check implementation of effects to see an example.
"""

from gl_pbuffer import Pbuffer
from gl_framebuffer_object import FramebufferObject
from pyglet.gl import *
from director import director
from pyglet import image

# Auxiliar classes for render-to-texture

_best_grabber = None

__all__ = ['TextureGrabber']

def TextureGrabber():
    """Returns an instance of the best texture grabbing class"""
    # Why this isn't done on module import? Because we need an initialized
    # GL Context to query availability of extensions
    global _best_grabber
    if _best_grabber is not None:
        return _best_grabber()
    # Preferred method: framebuffer object
    try:
        _best_grabber = FBOGrabber
        return _best_grabber()
    except:
        pass
    # Fallback: GL generic grabber
    print "Warning: using fallback texture grabber. Effects will treat" \
          "layer transparency as black"
    _best_grabber = GenericGrabber
    return _best_grabber()

class GenericGrabber(object):
    """A simple render-to-texture mechanism. Destroys the current GL display;
    and considers the whole layer as opaque. But it works in any GL
    implementation."""
    def grab (self, texture):
        pass
    
    def before_render (self, texture):
        director.window.clear()
        
    def after_render (self, texture):
        buffer = image.get_buffer_manager().get_color_buffer()
        texture.blit_into(buffer, 0, 0, 0)

class PbufferGrabber(object):
    """A render-to texture mechanism using pbuffers.
    Requires pbuffer extensions. Currently only implemented in GLX.
    
    Not working yet, very untested
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
        gl.glEnable (gl.GL_TEXTURE_2D)
        
    def after_render (self, texture):
        buffer = image.get_buffer_manager().get_color_buffer()
        texture.blit_into (buffer, 0, 0, 0)
        director.window.switch_to()


class FBOGrabber(object):
    """Render-to texture system based on framebuffer objects (the GL
    extension). It is quite fast and portable, but requires a recent GL
    implementation/driver.

    Requires framebuffer_object extensions"""
    def __init__ (self):
        # This code is on init to make creation fail if FBOs are not available
        self.fbuf = FramebufferObject()

    def grab (self, texture):
        self.fbuf.bind()
        self.fbuf.texture2d (texture)
        self.fbuf.check_status()
        self.fbuf.unbind()
    
    def before_render (self, texture):
        self.fbuf.bind()
        glClear(GL_COLOR_BUFFER_BIT)
        
    def after_render (self, texture):
        self.fbuf.unbind()

