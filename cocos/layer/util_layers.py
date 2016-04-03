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
"""Layer class and subclasses

A `Layer` has as size the whole drawable area (window or screen),
and knows how to draw itself. It can be semi transparent (having holes
and/or partial transparency in some/all places), allowing to see other layers
behind it. Layers are the ones defining appearance and behavior, so most
of your programming time will be spent coding Layer subclasses that do what
you need. The layer is where you define event handlers.
Events are propagated to layers (from front to back) until some layer catches
the event and accepts it.
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import pyglet
from pyglet import gl

from cocos.director import *
from .base_layers import Layer

__all__ = ['ColorLayer']


class ColorLayer(Layer):
    """Creates a layer of a certain color.
    The color shall be specified in the format (r,g,b,a).

    For example, to create green layer::

        l = ColorLayer(0, 255, 0, 0 )

    The size and position can be changed, for example::

        l = ColorLayer( 0, 255,0,0, width=200, height=400)
        l.position = (50,50)

    """
    def __init__(self, r, g, b, a, width=None, height=None):
        super(ColorLayer, self).__init__()
        self._batch = pyglet.graphics.Batch()
        self._vertex_list = None
        self._rgb = r, g, b
        self._opacity = a

        self.width = width
        self.height = height

        w, h = director.get_window_size()
        if not self.width:
            self.width = w
        if not self.height:
            self.height = h

    def on_enter(self):
        super(ColorLayer, self).on_enter()
        x, y = self.width, self.height
        ox, oy = 0, 0

        self._vertex_list = self._batch.add(4, pyglet.gl.GL_QUADS, None,
                                            ('v2i', (ox, oy,
                                                     ox, oy + y,
                                                     ox + x, oy + y,
                                                     ox + x, oy)), 'c4B')

        self._update_color()

    def on_exit(self):
        super(ColorLayer, self).on_exit()
        self._vertex_list.delete()
        self._vertex_list = None

    def draw(self):
        super(ColorLayer, self).draw()
        gl.glPushMatrix()
        self.transform()
        gl.glPushAttrib(gl.GL_CURRENT_BIT)
        self._batch.draw()
        gl.glPopAttrib()
        gl.glPopMatrix()

    def _update_color(self):
        if self._vertex_list:
            r, g, b = self._rgb
            self._vertex_list.colors[:] = [r, g, b, int(self._opacity)] * 4

    def _set_opacity(self, opacity):
        self._opacity = opacity
        self._update_color()

    opacity = property(lambda self: self._opacity, _set_opacity,
                       doc='''Blend opacity.

    This property sets the alpha component of the colour of the layer's
    vertices.  This allows the layer to be drawn with fractional opacity,
    blending with the background.

    An opacity of 255 (the default) has no effect.  An opacity of 128 will
    make the sprite appear translucent.

    :type: int
    ''')

    def _set_color(self, rgb):
        self._rgb = map(int, rgb)
        self._update_color()

    color = property(lambda self: self._rgb, _set_color,
                     doc='''Blend color.

    This property sets the color of the layer's vertices. This allows the
    layer to be drawn with a color tint.

    The color is specified as an RGB tuple of integers ``(red, green, blue)``.
    Each color component must be in the range 0 (dark) to 255 (saturated).

    :type: (int, int, int)
    ''')
