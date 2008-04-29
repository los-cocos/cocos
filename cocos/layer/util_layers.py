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
        self.batch = pyglet.graphics.Batch()
        self.acolor = color
        
    def on_enter(self):
        super(ColorLayer, self).on_exit()
        x, y = director.get_window_size()
        
        self.vertex_list = self.batch.add(4, pyglet.gl.GL_QUADS, None,
            ('v2i', (0, 0, 0, y, x, y, x, 0)),
            ('c4B', self.acolor*4)
        )
    
    def on_exit(self):
        super(ColorLayer, self).on_exit()
        self.vertex_list.delete()
   
       
    def on_draw(self):
        super(ColorLayer, self).on_draw()
        glPushMatrix()
        self.transform()
        glTranslatef( 
                -self.children_anchor_x, 
                -self.children_anchor_y,
                 0 )
        self.batch.draw()
        glPopMatrix()
