# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008 Daniel Moisset, Ricardo Quesada, Rayentray Tappa, Lucio Torre
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
"""A `WidgetContainer` that implements a container

WidgetContainer
===============

XXX TODO
"""

__docformat__ = 'restructuredtext'

import pyglet
from pyglet import font
from pyglet.window import key
from pyglet.gl import *
import pyglet.graphics

from layer import *
from director import *
from cocosnode import *
from actions import *
from sprite import Sprite

__all__ = [ 'WidgetContainer', 'RadioWidgetContainer'
            ]

def rect_contains_point( rect, point ):
    return (point[0] >= rect[0] and
            point[0] < rect[0] + rect[2] and
            point[1] >= rect[1] and
            point[1] < rect[1] + rect[3] )

class WidgetContainer(Layer):
    """XXX TODO
    """

    is_event_handler = True #: Receives pyglet events

    def __init__(self, height=32, width=800, align='left', spacing=5 ):
        super(WidgetContainer, self).__init__()
        self._width = width
        self._height = height
        self._align = align
        self._spacing = spacing

        self._children_z = 0
        self._children_width = 0

        self._selected_item = -1


    def add( self, node, **kw ):
        super(WidgetContainer, self).add( node, z=self._children_z, **kw )
        self._children_z += 1
        self._children_width += node.width

    def align_horizontal( self, type ='left' ):
        if type=='left':
            offset = 0
            for z,c in self.children:
                c.position = (offset, c.position[1])
                offset += self._spacing + c.width

        elif type=='right':
            offset = self._width
            for z,c in reversed(self.children):
                offset -= c.width
                c.position = (offset, c.position[1])
                offset -= self._spacing

        elif type=='center':
            offset = (self._width - self._children_width - self._spacing * (len(self.children) -1 )) / 2.0
            for z,c in self.children:
                c.position = (offset, c.position[1])
                offset += c.width + self._spacing

        return self

    def on_key_press(self, symbol, modifiers):
        return False

    def on_mouse_press( self, x, y, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)

        for idx,i in enumerate( self.children):
            node = self.children[ idx ][1]
            (posx, posy) = node.absolute_position()
            rect = [posx, posy, node.width, node.height] 
            if rect_contains_point( rect, (x,y) ):
                self._select_item( idx )
                return True
        self._unselect_item()
        return False

    def on_mouse_release( self, x, y, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)

        node = self.children[ self._selected_item ][1]
        (posx, posy) = node.absolute_position()
        rect = [posx, posy, node.width, node.height] 
        if rect_contains_point( rect, (x,y) ):
            self._activate_item()
            self._unselect_item()
            return True
        self._unselect_item()
        return False

    def on_mouse_drag( self, x, y, dx, dy, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)

        # unselect button 
        if self._selected_item != -1:
            node = self.children[ self._selected_item ][1]
            (posx, posy) = node.absolute_position()
            rect = [posx, posy, node.width, node.height] 
            if not rect_contains_point( rect, (x,y) ):
                self._unselect_item()
                return True

        # unselect button 
        for idx,i in enumerate( self.children):
            node = self.children[ idx ][1]
            (posx, posy) = node.absolute_position()
            rect = [posx, posy, node.width, node.height] 
            if rect_contains_point( rect, (x,y) ):
                self._select_item( idx )
                return True

        return False

    def _unselect_item( self ):
        if self._selected_item != -1:
            self.children[ self._selected_item][1].on_unselect()
            self._selected_item = -1

    def _select_item( self, new_idx ):
        if self._selected_item == new_idx:
            return

        if self._selected_item != -1:
            self.children[ self._selected_item][1].on_unselect()

        self._selected_item = new_idx
        self.children[ self._selected_item][1].on_select()

    def _activate_item( self ):
        self.children[ self._selected_item ][1].on_activate()


class RadioWidgetContainer(Layer):
    """XXX TODO
    """
    def __init__(self, selected=1, *args, **kw ):
        super(RadioWidgetContainer, self).__init__( *args, **kw)
