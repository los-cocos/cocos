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
"""A thin wrapper for OpenGL framebuffer objets. For implementation use only"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import ctypes as ct

from pyglet import gl


class FramebufferObject (object):
    """
    Wrapper for framebuffer objects. See

    http://oss.sgi.com/projects/ogl-sample/registry/EXT/framebuffer_object.txt

    API is not very OO, should be improved.
    """
    def __init__(self):
        """Create a new framebuffer object"""
        id = gl.GLuint(0)
        gl.glGenFramebuffersEXT(1, ct.byref(id))
        self._id = id.value

    def bind(self):
        """Set FBO as current rendering target"""
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self._id)

    def unbind(self):
        """Set default framebuffer as current rendering target"""
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)

    def texture2d(self, texture):
        """Map currently bound framebuffer (not necessarily self) to texture"""
        gl.glFramebufferTexture2DEXT(
            gl.GL_FRAMEBUFFER_EXT,
            gl.GL_COLOR_ATTACHMENT0_EXT,
            texture.target,
            texture.id,
            texture.level)

    def check_status(self):
        """Check that currently set framebuffer is ready for rendering"""
        status = gl.glCheckFramebufferStatusEXT(gl.GL_FRAMEBUFFER_EXT)
        if status != gl.GL_FRAMEBUFFER_COMPLETE_EXT:
            raise Exception("Frambuffer not complete: %d" % status)

    def __del__(self):
        """Delete the framebuffer from the GPU memory"""
        id = gl.GLuint(self._id)
        gl.glDeleteFramebuffersEXT(1, ct.byref(id))
