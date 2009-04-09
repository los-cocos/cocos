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
"""
WidgetEventDispatcher
=====================

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
from widget_buttons import *

__all__ = [ 'WidgetEventDispatcher' ]

def rect_contains_point( rect, point ):
    return (point[0] >= rect[0] and
            point[0] < rect[0] + rect[2] and
            point[1] >= rect[1] and
            point[1] < rect[1] + rect[3] )

class WidgetEventDispatcher(Layer):
    """XXX TODO
    """

    is_event_handler = True #: Receives pyglet events

    def __init__(self):
        super(WidgetEventDispatcher, self).__init__()
        self._widgets = []
        self._selected_widget = None

    def add_widget( self, widget):

        # XXX: Don't test subclass. Test if it implements a protocol/interface.
        if isinstance( widget, WAbstractButton ):
            self._widgets.append( widget )

        for n in widget.children:
            w = n[1]
            self.add_widget( w )

    def remove_widget( self, widget ):
        self._widgets.remove( widget )

    def on_mouse_press( self, x, y, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)

        for widget in self._widgets:
            (posx, posy) = widget.absolute_position()
            rect = [posx, posy, widget.width, widget.height] 
            if rect_contains_point( rect, (x,y) ):
                self._select_widget( widget )
                widget.on_mouse_press(x,y)
                return True

        self._unselect_widget()
        return False

    def on_mouse_release( self, x, y, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)

        node = self._selected_widget
        if node:
            (posx, posy) = node.absolute_position()
            rect = [posx, posy, node.width, node.height] 
            if rect_contains_point( rect, (x,y) ):
                node.on_mouse_release(x,y)
                node.on_mouse_click()
                self._unselect_widget()
                return True

        self._unselect_widget()

        for widget in self._widgets:
            (posx, posy) = widget.absolute_position()
            rect = [posx, posy, widget.width, widget.height] 
            if rect_contains_point( rect, (x,y) ):
                widget.on_mouse_release(x,y)
                return True

        return False

    def on_mouse_drag( self, x, y, dx, dy, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)

        # drag within the selected widget

        node = self._selected_widget
        if node:
            # XXX: only on enter, it is not necessary to dispatch this event all the time
            node.on_select()

            (posx, posy) = node.absolute_position()
            rect = [posx, posy, node.width, node.height] 
            if rect_contains_point( rect, (x,y) ):
                node.on_mouse_drag( x, y , dx, dy)
                return True

            # dont set selected_widget to -1
            node.on_unselect()

        return False

    def _select_widget( self, new_widget):
        if self._selected_widget == new_widget:
            return

        self._selected_widget = new_widget
        new_widget.on_select()

    def _unselect_widget( self ):
        if self._selected_widget:
            self._selected_widget.on_unselect()
            self._selected_widget = None
