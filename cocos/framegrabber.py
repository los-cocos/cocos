# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2015  Richard Jones, Claudio Canepa
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
"""Utility classes for rendering to a texture.

It is mostly used for internal implementation of cocos, you normally shouldn't
need it. If you are curious, check implementation of effects to see an example.
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

from pyglet import gl
from pyglet import image
import pyglet

from cocos.gl_framebuffer_object import FramebufferObject
from cocos.director import director

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
        # TEST XXX
        # _best_grabber = GenericGrabber
        _best_grabber = FBOGrabber
        return _best_grabber()
    except:
        import traceback
        traceback.print_exc()
    # Fallback: GL generic grabber
    raise Exception("ERROR: GPU doesn't support Frame Buffers Objects. Can't continue")
#    _best_grabber = GenericGrabber
#    return _best_grabber()


class _TextureGrabber(object):
    def __init__(self):
        """Create a texture grabber."""

    def grab(self, texture):
        """Capture the current screen."""

    def before_render(self, texture):
        """Setup call before rendering begins."""

    def after_render(self, texture):
        """Rendering done, make sure texture holds what has been rendered."""


class GenericGrabber(_TextureGrabber):
    """A simple render-to-texture mechanism. Destroys the current GL display;
    and considers the whole layer as opaque. But it works in any GL
    implementation."""
    def __init__(self):
        self.before = None
        x1 = y1 = 0
        x2, y2 = director.get_window_size()
        self.vertex_list = pyglet.graphics.vertex_list(4,
                                                       ('v2f', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                                       ('c4B', [255, 255, 255, 255] * 4))

    def before_render(self, texture):
        # self.before = image.get_buffer_manager().get_color_buffer()
        director.window.clear()

    def after_render(self, texture):
        buffer = image.get_buffer_manager().get_color_buffer()
        texture.blit_into(buffer, 0, 0, 0)
        director.window.clear()
        return

        self.before.blit(0, 0)
        glEnable(self.before.texture.target)
        glBindTexture(self.before.texture.target, self.before.texture.id)

        glPushAttrib(GL_COLOR_BUFFER_BIT)

        self.vertex_list.draw(gl.GL_QUADS)

        glPopAttrib()
        glDisable(self.before.texture.target)


class PbufferGrabber(_TextureGrabber):
    """A render-to texture mechanism using pbuffers.
    Requires pbuffer extensions. Currently only implemented in GLX.

    Not working yet, very untested

    TODO: finish pbuffer grabber
    """
    def grab(self, texture):
        self.pbuf = gl.Pbuffer(director.window, [
            gl.GLX_CONFIG_CAVEAT, gl.GLX_NONE,
            gl.GLX_RED_SIZE, 8,
            gl.GLX_GREEN_SIZE, 8,
            gl.GLX_BLUE_SIZE, 8,
            gl.GLX_DEPTH_SIZE, 24,
            gl.GLX_DOUBLEBUFFER, 1,
            ])

    def before_render(self, texture):
        self.pbuf.switch_to()
        gl.glViewport(0, 0, self.pbuf.width, self.pbuf.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.pbuf.width, 0, self.pbuf.height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glEnable(gl.GL_TEXTURE_2D)

    def after_render(self, texture):
        buffer = image.get_buffer_manager().get_color_buffer()
        texture.blit_into(buffer, 0, 0, 0)
        director.window.switch_to()


class FBOGrabber(_TextureGrabber):
    """Render-to texture system based on framebuffer objects (the GL
    extension). It is quite fast and portable, but requires a recent GL
    implementation/driver.

    Requires framebuffer_object extensions"""
    def __init__(self):
        # This code is on init to make creation fail if FBOs are not available
        self.fbuf = FramebufferObject()
        self.fbuf.check_status()

    def grab(self, texture):
        self.fbuf.bind()
        self.fbuf.texture2d(texture)
        self.fbuf.check_status()
        self.fbuf.unbind()

    def before_render(self, texture):
        self.fbuf.bind()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def after_render(self, texture):
        self.fbuf.unbind()
