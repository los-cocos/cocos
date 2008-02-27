from ctypes import c_int, byref
from pyglet.gl import *
from pyglet.gl.glext_arb import *

class FramebufferObject (object):
    """
    Wrapper for framebuffer objects. See
    
    http://oss.sgi.com/projects/ogl-sample/registry/EXT/framebuffer_object.txt
    
    API is not very OO, should be improved.
    """
    def __init__ (self):
        """Create a new framebuffer object"""
        id = c_ulong(0)
        glGenFramebuffersEXT (1, byref(id))
        self._id = id.value

    def bind (self):
        """Set FBO as current rendering target"""
        glBindFramebufferEXT (GL_FRAMEBUFFER_EXT, self._id)

    def unbind (self):
        """Set default framebuffer as current rendering target"""
        glBindFramebufferEXT (GL_FRAMEBUFFER_EXT, 0)

    def texture2d (self, texture):
        """Map currently bound framebuffer (not necessarily self) to texture"""
        glFramebufferTexture2DEXT (
            GL_FRAMEBUFFER_EXT,
            GL_COLOR_ATTACHMENT0_EXT,
            texture.target,
            texture.id,
            texture.level)

    def check_status(self):
        """Check that currently set framebuffer is ready for rendering"""
        status = glCheckFramebufferStatusEXT (GL_FRAMEBUFFER_EXT)
        if status != GL_FRAMEBUFFER_COMPLETE_EXT:
            raise Exception ("Frambuffer not complete: %d" % status)

