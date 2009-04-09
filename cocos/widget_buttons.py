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


"""Widgets

Widgets
=======

All Widgets objects starts with a capital W.

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

#
# widgets based on QT's hierachy
#

__all__ = [ 'WObject', 'WButtonGroup', 'WAbstractButton', 'WRadioButton','WPushButton', 'WCheckBox', 'WToolButton',
            'WHBoxLayout', 'WVBoxLayout',
]

def rect_contains_point( rect, point ):
    return (point[0] >= rect[0] and
            point[0] < rect[0] + rect[2] and
            point[1] >= rect[1] and
            point[1] < rect[1] + rect[3] )


class WObject( CocosNode ):
    def __init__(self, *args, **kw):
        super(WObject,self).__init__(*args, **kw)
        self._selected_widget = None
        self._width = 0
        self._height = 0

        self._layout = None

    def on_mouse_press( self, x, y, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)

        for z,widget in self.children:
            (posx, posy) = widget.absolute_position()
            rect = [posx, posy, widget.width, widget.height] 
            if rect_contains_point( rect, (x,y) ):
                self._select_widget( widget )
                widget.on_mouse_press(x,y, buttons, modifiers)
                return True

        self._unselect_widget()
        return False

    def on_mouse_click_proxy( self, widget, x, y, buttons, modifiers ):
        widget.on_mouse_click( x, y, buttons, modifiers )

    def on_mouse_release( self, x, y, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)

        node = self._selected_widget
        if node:
            (posx, posy) = node.absolute_position()
            rect = [posx, posy, node.width, node.height] 
            if rect_contains_point( rect, (x,y) ):
                node.on_mouse_release(x,y, buttons, modifiers)
                self.on_mouse_click_proxy(node, x, y, buttons, modifiers)
                self._unselect_widget()
                return True

        self._unselect_widget()

        for z,widget in self.children:
            (posx, posy) = widget.absolute_position()
            rect = [posx, posy, widget.width, widget.height] 
            if rect_contains_point( rect, (x,y) ):
                widget.on_mouse_release(x,y, buttons, modifiers)
                return True

        return False

    def on_mouse_drag( self, x, y, dx, dy, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)

        # drag within the selected widget

        node = self._selected_widget
        if node:
            # XXX: dispatch only on enter
            # XXX: it is not necessary to dispatch this event all the time
            node.on_select()

            (posx, posy) = node.absolute_position()
            rect = [posx, posy, node.width, node.height] 
            if rect_contains_point( rect, (x,y) ):
                node.on_mouse_drag( x, y , dx, dy, buttons, modifiers)
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

    def on_select( self ):
        pass

    def on_unselect( self ):
        if self._selected_widget:
            self._selected_widget.on_unselect()


    def add(self, child, *args, **kw ):
        super( WObject, self).add( child, *args, **kw )
        if self.layout:
            self.layout.align_widget( child )

    # layout
    def _get_layout( self ):
        return self._layout
    def _set_layout( self, l ):
        self._layout = l
    layout = property(lambda self:self._get_layout(), lambda self,y:self._set_layout(y), doc='')

    # width, height and rect:w
    def _get_width( self ):
        return self._width
    width = property(lambda self:self._get_width(), None, doc='')

    def _get_height( self ):
        return self._height
    height = property(lambda self:self._get_height(), None, doc='')

    def get_rect(self):
        return [self.x, self.y, self.width, self.height]

class WButtonGroup( WObject ):
    def __init__(self, *args, **kw):
        super(WButtonGroup, self).__init__(*args, **kw)
        self._exclusive = True

    def on_mouse_click_proxy( self, widget, x, y, buttons, modifiers):

        if not self.exclusive or not widget.checked:
            widget.on_mouse_click(x,y, buttons, modifiers)

        if self.exclusive:
            for z,w in self.children:
                if w is widget:
                    continue
                if w.checked:
                    w.checked = False
                    w.on_toggle()

    def on_mouse_click( self, x, y, buttons, modifiers ):
        # ignore
        pass

    def _get_width( self ):
        w = 0
        for z,widget in self.children:
            x,y = widget.position
            w = max(w,x + widget.width)
        return w
    def _get_height( self ):
        h = 0
        for z,widget in self.children:
            x,y = widget.position
            h = max(h,y + widget.height )
        return h

    def _get_exclusive( self ):
        return self._exclusive
    def _set_exclusive( self, ex ):
        self._exclusive = ex
    exclusive = property( lambda self:self._get_exclusive(), lambda self,y:self._set_exclusive(y), doc='''
    This property holds whether the button group is exclusive.
If this property is true then only one button in the group can be checked at any given time. The user can click on any button to check it, and that button will replace the existing one as the checked button in the group.
In an exclusive group, the user cannot uncheck the currently checked button by clicking on it; instead, another button in the group must be clicked to set the new checked button for that group.
By default, this property is true.
    ''')


class WAbstractButton(WObject):
    """XXX TODO
    """

    UNSELECTED, SELECTED, DISABLED = range(3)

    def __init__(self, clicked_callback=None, pressed_callback=None, released_callback=None, toggled_callback=None, normal_icon=None, selected_icon=None, disabled_icon=None, group=None):
        super(WAbstractButton, self).__init__()

        # signals
        self.signal_clicked = clicked_callback
        self.signal_pressed = pressed_callback
        self.signal_released = released_callback
        self.signal_toggled = toggled_callback

        self._checked = False
        self._checkable = False

        self.icon_size = (0,0)
        self._icons = [None, None, None]
        for idx, icon in enumerate( (normal_icon, selected_icon, disabled_icon) ):
            self._load_icon( icon, idx )

        self._group = group

        self._state = WAbstractButton.UNSELECTED

    def _get_width( self ):
        return self._icons[0].width

    def _get_height( self ):
        return self._icons[0].height

    def hitButton( self, rect ):
        '''Returns true if pos is inside the clickable button rectangle; otherwise returns false.
        By default, the clickable area is the entire widget. Subclasses may reimplement this function to provide support for clickable areas of different shapes and sizes.'''
        return False

    def _get_group( self ):
        return self._group
    def _set_group( self, group ):
        self._group = group
    group = property(lambda self:self._get_group(), lambda self,y:self._set_group(y), doc='''
    Returns the group that this button belongs to / sets a new group for the button.
    If the button is not a member of any group, this function returns None.
    ''')

    def _get_checkable( self ):
        return self._checkable
    def _set_checkable( self, c):
        self._checkable = c
    checkable = property(lambda self:self._get_checkable(), lambda self,y:self._set_checkable(y), doc='This property holds whether the button is checkable.  By default, the button is not checkable.')

    def _get_checked( self ):
        return self._checked
    def _set_checked( self, checked):
        if self.checkable:
            self._checked = checked
            if checked:
                self._state = self.SELECTED
            else:
                self._state = self.UNSELECTED
    checked = property(lambda self:self._get_checked(), lambda self,y:self._set_checked(y), doc='''
    This property holds whether the button is checked.
    Only checkable buttons can be checked. By default, the button is unchecked.
    ''')
    
    def _get_icon( self ):
        return self._icon[0]
    def _set_icon( self, icon ):
        self._icon[0] = icon 
        # update icon size
        self._update_icon_size()
    icon = property(lambda self:self._get_icon(), lambda self,y:self._set_icon(y), doc='set/get an icon')

    #
    # events
    #
    def on_mouse_click( self, x, y, buttons, modifiers ):
        if self.checkable:
            self.checked = not self.checked
        if self.signal_clicked:
            self.signal_clicked(self)

    def on_toggle( self ):
        if self.signal_toggled:
            self.signal_toggled( self )

    def on_select( self ):
        self._state = self.SELECTED

    def on_unselect( self ):
        if not self.checked:
            self._state = self.UNSELECTED

    #
    # private methods
    #
    def _load_icon( self, icon, idx):
        if icon:
            if isinstance(icon, str):
                image = pyglet.resource.image(icon)
            self._icons[idx] =  image
        else:
            self._icons[idx] = self._icons[0]

    def _update_icon_size( self ):
        # all icons sizes must be equal
        pass

class WRadioButton(WAbstractButton):
    pass

class WPushButton( WAbstractButton ):
    pass

class WCheckBox( WAbstractButton ):
    pass

class WToolButton( WAbstractButton ):
    def draw( self ):
        glPushMatrix()
        self.transform()
        self._icons[self._state].blit(0,0,0)
        glPopMatrix()


#
# Layouts
#
class WLayout( object ):
    def align_widget( self, widget ):
        pass

LeftToRight = TopToBottom = 0
RightToLeft = BottomToTop = 1

class WBoxLayout( WLayout ):
    def __init__( self, spacing=4, direction = LeftToRight):
        self._spacing = spacing
        self._direction = direction 

    def _get_spacing( self ):
        return self._spacing
    def _set_spacing( self, spacing ):
        self._spacing = spacing
    spacing = property( lambda self:self._get_spacing(), lambda self,y:self._set_spacing(y), doc='XXX: spacing property' )

    def _get_direction( self ):
        return self._direction
    def _set_direction( self, direction):
        self._direction = direction 
    direction = property( lambda self:self._get_direction(), lambda self,y:self._set_direction(y), doc='XXX: direction property' )


class WHBoxLayout( WBoxLayout ):
    def __init__(self, *args, **kw ):
        super(WHBoxLayout, self).__init__( *args, **kw)
        self.direction = LeftToRight

        self._last_pos = 0

    def align_widget( self, widget ):

        x,y = widget.position
        if self.direction == LeftToRight:
            x += self._last_pos
            widget.position = (x,y)

            self._last_pos += self.spacing + widget.width
        else:
            raise Exception("xxx: implement me")


class WVBoxLayout( WBoxLayout ):
    def __init__(self, *args, **kw ):
        super(WHBoxLayout, self).__init__( *args, **kw)
        self.direction = TopToBottom

        self._last_pos = 0

    def align_widget( self, widget ):

        x,y = widget.position
        if self.direction == TopToBottom:
            y += self._last_pos
            widget.position = (x,y)

            self._last_pos += self.spacing + widget.width
        else:
            raise Exception("xxx: implement me")
