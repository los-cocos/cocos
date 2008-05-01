#
# Cocos
# http://code.google.com/p/los-cocos/
#
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

__docformat__ = 'restructuredtext'

import pyglet
from pyglet.gl import *

from cocos.director import *
from base_layers import Layer
import cocos.cocosnode

__all__ = ['ColorLayer']    


class ColorLayer(Layer):
    """Creates a layer of a certain color.
    The color shall be specified in the format (r,g,b,a).
    
    For example, to create green layer::
    
        l = ColorLayer(0, 255, 0, 0 )
    """
    def __init__(self, *color):
        super(ColorLayer, self).__init__()
        self._batch = pyglet.graphics.Batch()
        self._rgb = color[:3]
        self._opacity = color[3]
        
    def on_enter(self):
        super(ColorLayer, self).on_enter()
        x, y = director.get_window_size()
        
        self._vertex_list = self._batch.add(4, pyglet.gl.GL_QUADS, None,
            ('v2i', (0, 0, 0, y, x, y, x, 0)),
            'c4B')

        self._update_color()

    def on_exit(self):
        super(ColorLayer, self).on_exit()
        self._vertex_list.delete()
        self._vertex_list = None

    def on_draw(self):
        super(ColorLayer, self).on_draw()
        glPushMatrix()
        self.transform()
        glTranslatef( 
                -self.children_anchor_x, 
                -self.children_anchor_y,
                 0 )
        self._batch.draw()
        glPopMatrix()

    def _update_color(self):
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
