from ctypes import c_int, byref
from pyglet.gl import *
from pyglet.gl.glext_arb import *

class FramebufferObject (object):
    def __init__ (self):
        id = c_ulong(0)
        glGenFramebuffersEXT (1, byref(id))
        self._id = id.value

    def bind (self):
        glBindFramebufferEXT (GL_FRAMEBUFFER_EXT, self._id)

    def unbind (self):
        glBindFramebufferEXT (GL_FRAMEBUFFER_EXT, 0)

    def texture2d (self, texture):
        glFramebufferTexture2DEXT (
            GL_FRAMEBUFFER_EXT,
            GL_COLOR_ATTACHMENT0_EXT,
            texture.target,
            texture.id,
            texture.level)

    def check_status(self):
        status = glCheckFramebufferStatusEXT (GL_FRAMEBUFFER_EXT)
        if status != GL_FRAMEBUFFER_COMPLETE_EXT:
            raise Exception ("Frambuffer not complete: %d" % status)

