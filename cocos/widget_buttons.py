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

#
# widgets based on QT's hierachy
#

__all__ = [ 'CCAbstractButton', 'CCRadioButton','CCPushButton', 'CCCheckBox', 'CCActionButton' ]

def rect_contains_point( rect, point ):
    return (point[0] >= rect[0] and
            point[0] < rect[0] + rect[2] and
            point[1] >= rect[1] and
            point[1] < rect[1] + rect[3] )

class CCWidget(CocosNode):
    pass

class CCAbstractButton(CCWidget):
    """XXX TODO
    """

    UNSELECTED, SELECTED, DISABLED = range(3)

    def __init__(self, clicked_callback=None, pressed_callback=None, released_callback=None, toggled_callback=None, normal_icon=None, selected_icon=None, disabled_icon=None, parent=None, group=None):
        super(CCAbstractButton, self).__init__()

        # signals
        self.signal_clicked = clicked_callback
        self.signal_pressed = pressed_callback
        self.signal_released = released_callback
        self.signal_toggled = toggled_callback

        self.checked = False

        self.icon_size = (0,0)
        self._icons = [None, None, None]
        for idx, icon in enumerate( (normal_icon, selected_icon, disabled_icon) ):
            self._load_icon( icon, idx )

        self._group = group
        self._parent = parent

        self._state = CCAbstractButton.UNSELECTED

    def hitButton( self, rect ):
        '''Returns true if pos is inside the clickable button rectangle; otherwise returns false.
        By default, the clickable area is the entire widget. Subclasses may reimplement this function to provide support for clickable areas of different shapes and sizes.'''
        return False

    def _get_group( self ):
        return self._group
    def _set_group( self, group ):
        self._group = group
    group = property(_get_group, _set_group, doc='''
    Returns the group that this button belongs to / sets a new group for the button.
    If the button is not a member of any group, this function returns None.
    ''')
    
    def _get_icon( self ):
        return self._icon[0]

    def _set_icon( self, icon ):
        self._icon[0] = icon 
        # update icon size
        self._update_icon_size()
    icon = property(_get_icon, _set_icon, doc='set/get an icon')

    # width, height and rect:w
    def _get_width( self ):
        return self._icons[ self._state ].width
    width = property(_get_width, None, doc='')

    def _get_height( self ):
        return self._icons[ self._state ].height
    height = property(_get_height, None, doc='')

    def get_rect(self):
        return [self.x, self.y, self.width, self.height]

    #
    # events
    #
    def on_mouse_click( self ):
        if self.signal_clicked:
            self.signal_clicked( self )

    def on_mouse_press( self, x, y ):
        pass

    def on_mouse_release( self, x, y ):
        pass

    def on_mouse_drag( self, x, y, dx, dy ):
        pass

    def on_toggle( self ):
        if self.signal_toggle:
            self.signal_toggle( self )

    def on_select( self ):
        self._state = self.SELECTED

    def on_unselect( self ):
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

class CCRadioButton(CCAbstractButton):
    pass

class CCPushButton( CCAbstractButton ):
    pass

class CCCheckBox( CCAbstractButton ):
    pass

class CCActionButton( CCAbstractButton ):
    def __init__( self, *args, **kw ):
        super(CCActionButton, self).__init__(*args, **kw)

    def draw( self ):
        glPushMatrix()
        self.transform()
        self._icons[self._state].blit(0,0,0)
        glPopMatrix()
