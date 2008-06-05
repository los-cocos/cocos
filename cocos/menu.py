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
#
# Ideas borrowed from:
#    pygext: http://opioid-interactive.com/~shang/projects/pygext/
#    pyglet astraea: http://www.pyglet.org
#    Grossini's Hell: http://www.pyweek.org/e/Pywiii/ 
#
"""A `Layer` that implements a simple menu

Menu
====

This module provides a Menu class. Menus can contain regular items 
(which trigger a function when selected), toggle items (which toggle a flag when selected),
or entry items (which lets you enter alphanumeric data).

To use a menu in your code, just subclass `Menu` and add the menu to an `Scene` or
another `Layer`.
"""

__docformat__ = 'restructuredtext'

import pyglet
from pyglet import font
from pyglet.window import key
from pyglet.gl import *

from layer import *
from director import *
from cocosnode import *
from actions import *

__all__ = [ 'Menu',                                 # menu class

    'MenuItem', 'ToggleMenuItem',                   # menu items classes
    'MultipleMenuItem', 'EntryMenuItem',

    'CENTER', 'LEFT', 'RIGHT', 'TOP', 'BOTTOM',     # menu aligment

    'shake', 'shake_back','zoom_in','zoom_out'      # Some useful actions for the menu items
    ]

#
# Class Menu
#

# Horizontal Align
CENTER = font.Text.CENTER
LEFT = font.Text.LEFT
RIGHT = font.Text.RIGHT

# Vertical Align
TOP = font.Text.TOP
BOTTOM = font.Text.BOTTOM

class Menu(Layer):
    """Abstract base class for menu layers.
    
    Normal usage is:

     - create a subclass
     - override __init__ to set all style attributes, 
       and then call `create_menu()`
     - Finally you shall add the menu to an `Scene` or another `Layer`
    """

    is_event_handler = True #: Receives pyglet events

    select_sound = None
    activate_sound = None
    def __init__( self, title = ''):
        super(Menu, self).__init__()

        #
        # Items and Title
        #
        self.title = title
        self.title_text = None

        self.menu_halign = CENTER
        self.menu_valign = CENTER

        #
        # Menu default options
        # Menus can be customized changing these variables
        #

        # Title
        self.font_title = {
            'text':'title',
            'font_name':'Arial',
            'font_size':56,
            'color':(192,192,192,255),
            'bold':False,
            'italic':False,
            'anchor_y':'center',
            'anchor_x':'center',
            'dpi':96,
            'x':0, 'y':0,
        }

        self.font_item= {
            'font_name':'Arial',
            'font_size':32,
            'bold':False,
            'italic':False,
            'anchor_y':'center',
            'anchor_x':'center',
            'color':(192,192,192,255),
            'dpi':96,
        }
        self.font_item_selected = {
            'font_name':'Arial',
            'font_size':42,
            'bold':False,
            'italic':False,
            'anchor_y':'center',
            'anchor_x':'center',
            'color':(255,255,255,255),
            'dpi':96,
        }

        self.title_height = 0

     
    def _generate_title( self ):
        width, height = director.get_window_size()

        self.font_title['x'] = width // 2
        self.font_title['text'] = self.title
        self.title_label = pyglet.text.Label( **self.font_title )
        self.title_label.y = height - self.title_label.content_height //2

        fo = font.load( self.font_title['font_name'], self.font_title['font_size'] )
        self.title_height = self.title_label.content_height

    def _generate_items( self ):
        width, height = director.get_window_size()

        fo = font.load( self.font_item['font_name'], self.font_item['font_size'] )
        fo_height = int( (fo.ascent - fo.descent) * 0.9 )

        if self.menu_halign == CENTER:
            pos_x = width // 2
        elif self.menu_halign == RIGHT:
            pos_x = width - 2
        elif self.menu_halign == LEFT:
            pos_x = 2
        else:
            raise Exception("Invalid anchor_x value for menu")

        for idx,i in enumerate( self.children):
            item = i[1]

            if self.menu_valign == CENTER:
                pos_y = height / 2 + (fo_height * len(self.children) )/2 - (idx * fo_height ) - self.title_height * 0.2
            elif self.menu_valign == TOP:
                pos_y = height - (idx * fo_height ) - self.title_height
            elif self.menu_valign == BOTTOM:
                pos_y = 0 + fo_height * len(self.children) - (idx * fo_height )

            item.transform_anchor = (pos_x, pos_y)

            self.font_item['x'] = pos_x
            self.font_item['y'] = pos_y
            self.font_item['text'] = item.label
            item.text = pyglet.text.Label( **self.font_item )

            self.font_item_selected['x'] = pos_x
            self.font_item_selected['y'] = pos_y
            self.font_item_selected['text'] = item.label
            item.text_selected = pyglet.text.Label( **self.font_item_selected )

    def _build_items( self ):
        self.font_item_selected['anchor_x'] = self.menu_halign
        self.font_item_selected['anchor_y'] = 'center'

        self.font_item['anchor_x'] = self.menu_halign
        self.font_item['anchor_y'] = 'center'

        self._generate_items()
        self.selected_index = 0
        self.children[ self.selected_index ][1].is_selected = True

    def _select_item(self, new_idx):
        if new_idx == self.selected_index:
            return

        if self.select_sound:
            self.select_sound.play()

        self.children[ self.selected_index][1].is_selected = False
        self.children[ self.selected_index][1].on_unselected()

        self.children[ new_idx ][1].is_selected = True 
        self.children[ new_idx ][1].on_selected()

        self.selected_index = new_idx

    def _activate_item( self ):
        if self.activate_sound:
            self.activate_sound.play()
        self.children[ self.selected_index][1].on_activated()
        self.children[ self.selected_index ][1].on_key_press( key.ENTER, 0 )

    def create_menu( self, items, selected_effect=None, unselected_effect=None, activated_effect=None ):
        """Creates the menu

        The order of the list important since the
        first one will be shown first.

        Example::
    
            l = []
            l.append( MenuItem('Options', self.on_new_game ) )
            l.append( MenuItem('Quit', self.on_quit ) )
            self.create_menu( l, zoom_in(), zoom_out() )

        :Parameters:
            `items` : list
                list of `MenuItem` that will be part of the `Menu`
            `selected_effect` : function
                This action will be executed when the `MenuItem` is selected
            `unselected_effect` : function
                This action will be executed when the `MenuItem` is unselected
            `activated_effect` : function
                this action will executed when the `MenuItem` is activated (pressing Enter or by clicking on it)
        """
        z=0
        for i in items:
            # calling super.add(). Z is important to mantain order
            self.add( i, z=z )

            i.activated_effect = activated_effect
            i.selected_effect = selected_effect
            i.unselected_effect = unselected_effect
            i.item_halign = self.menu_halign
            i.item_valign = self.menu_valign
            z += 1

        if items:
            self._build_items()

        self._generate_title()

    def draw( self ):
        self.title_label.draw()

    def on_text( self, text ):
        if text=='\r':
            return
        return self.children[self.selected_index][1].on_text(text)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.on_quit()
            return True
        elif symbol in (key.ENTER, key.NUM_ENTER):
            self._activate_item()
            return True
        elif symbol in (key.DOWN, key.UP):
            if symbol == key.DOWN:
                new_idx = self.selected_index + 1
            elif symbol == key.UP:
                new_idx = self.selected_index - 1

            if new_idx < 0:
                new_idx = len(self.children) -1
            elif new_idx > len(self.children) -1:
                new_idx = 0
            self._select_item( new_idx )
            return True
        else:
            # send the menu item the rest of the keys
            ret = self.children[self.selected_index][1].on_key_press(symbol, modifiers)

            # play sound if key was handled
            if ret and self.activate_sound:
                self.activate_sound.play()
            return ret

    def on_mouse_release( self, x, y, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)
        if self.children[ self.selected_index ][1].is_inside_box(x,y):
            self._activate_item()

    def on_mouse_motion( self, x, y, dx, dy ):
        (x,y) = director.get_virtual_coordinates(x,y)
        self._x = x
        self._y = y
        for idx,i in enumerate( self.children):
            item = i[1]
            if item.is_inside_box( x, y):
                self._select_item( idx )
                break

class MenuItem( CocosNode ):
    """A regular menu item. It triggers a function when it is activated"""
    
    selected_effect = None
    unselected_effect = None
    activated_effect = None

    def __init__(self, label, callback_func):
        """Creates a new menu item

        :Parameters:
            `label` : string
                The label the of the menu item
            `callback_func` : function
                The callback function
        """

        super( MenuItem, self).__init__()

        self.label = label
        self.callback_func = callback_func

        self.is_selected = False

        # Variables that will be set when init_font() is called
        self.text = None
        self.text_selected = None

        self.item_halign = None
        self.item_valign = None

    def get_box( self ):
        """Returns the box that contains the menu item.

        :rtype: (x1,x2,y1,y2)
        """

        width = self.text.content_width
        height = self.text.content_height

        if self.item_halign == CENTER:
            x_diff = - width / 2
        elif self.item_halign == RIGHT:
            x_diff = - width
        elif self.item_halign == LEFT:
            x_diff = 0
        else:
            raise Exception("Invalid halign: %s" % str(self.item_halign) )

        if self.item_valign == CENTER:
            y_diff = - height/ 2
        elif self.item_valign == TOP:
            y_diff = - height
        elif self.item_valign == BOTTOM:
            y_diff = 0
        else:
            raise Exception("Invalid valign: %s" % str(self.item_valign) )

        x1 = self.text.x + x_diff
        y1 = self.text.y + y_diff
        x2 = x1 + width
        y2 = y1 + height
        return (x1,y1,x2,y2)

    def draw( self ):
        glPushMatrix()
        self.transform()

        if self.is_selected:
            self.text_selected.draw()
        else:
            self.text.draw()

        glPopMatrix()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER and self.callback_func:
            self.callback_func()
            return True

    def on_text( self, text ):
        return True

    def is_inside_box( self, x, y ):
        """Returns whether the point (x,y) is inside the menu item.

        :rtype: bool 
        """
        (ax,ay,bx,by) = self.get_box()
        if( x >= ax and x <= bx and y >= ay and y <= by ):
            return True
        return False

    def on_selected( self ):
        if self.selected_effect:
            self.stop()
            self.do( self.selected_effect )

    def on_unselected( self ):
        if self.unselected_effect:
            self.stop()
            self.do( self.unselected_effect )

    def on_activated( self ):
        if self.activated_effect:
            self.stop()
            self.do( self.activated_effect )


class MultipleMenuItem( MenuItem ):
    """A menu item for switching between multiple values.

    Example::

        self.volumes = ['Mute','10','20','30','40','50','60','70','80','90','100']

        items.append( MultipleMenuItem(
                        'SFX volume: ', 
                        self.on_sfx_volume,
                        self.volumes,
                        8 )
    """

    def __init__(self, label, callback_func, items, default_item=0):
        """Creates a Toggle Menu Item

        :Parameters:
            `label` : string
                Item's label
            `callback_func` : function
                Callback function
            `items` : list
                List of strings containing the values 
            `default_item` : integer
                Default item of the list. It is an index of the list. Default: 0
        """
        self.my_label = label
        self.items = items
        self.idx = default_item
        if self.idx < 0 or self.idx >= len(self.items):
            raise Exception("Index out of bounds")
        super( MultipleMenuItem, self).__init__( self._get_label(), callback_func )

    def _get_label(self):
        return self.my_label+self.items[self.idx]

    def on_key_press(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.idx = max(0, self.idx-1)
        elif symbol in (key.RIGHT, key.ENTER):
            self.idx = min(len(self.items)-1, self.idx+1)

        if symbol in (key.LEFT, key.RIGHT, key.ENTER):
            self.text.text = self._get_label()
            self.text_selected.text = self._get_label()
            self.callback_func( self.idx )
            return True

class ToggleMenuItem( MultipleMenuItem ):
    '''A menu item for a boolean toggle option.  

    Example::

        items.append( ToggleMenuItem('Show FPS:', self.on_show_fps, director.show_FPS) )
    '''

    def __init__(self, label, callback_func, value=False ):
        """Creates a Toggle Menu Item

        :Parameters:
            `label` : string
                Item's label
            `callback_func` : function
                Callback function
            `value` : bool
                Default value of the item: False is 'OFF', True is 'ON'. Default:False
        """

        super(ToggleMenuItem, self).__init__( label, callback_func, ['OFF','ON'],  int(value) )

    def on_key_press( self, symbol, mod ):
        if symbol in (key.LEFT, key.RIGHT, key.ENTER):
            self.idx += 1
            if self.idx > 1:
                self.idx = 0
            self.text.text = self._get_label()
            self.text_selected.text = self._get_label()
            self.callback_func( int(self.idx) )
            return True

class EntryMenuItem(MenuItem):
    """A menu item for entering a value.

    When selected, ``self.value`` is toggled, the callback function is
    called with ``self.value`` as argument."""

    value = property(lambda self: u''.join(self._value),
                     lambda self, v: setattr(self, '_value', list(v)))

    def __init__(self, label, callback_func, value ):
        """Creates an Entry Menu Item

        :Parameters:
            `label` : string
                Item's label
            `callback_func` : function
                Callback function taking one argument.
            `value` : String
                Default value: any string
        """
        self._value = list(value)
        self._label = label
        super(EntryMenuItem, self).__init__( "%s %s" %(label,value), callback_func )

    def on_text( self, text ):
        self._value.append(text)
        self._calculate_value()
        return True

    def on_key_press(self, symbol, modifiers):
        if symbol == key.BACKSPACE:
            try:
                self._value.pop()
            except IndexError:
                pass
            self._calculate_value()
            return True

    def _calculate_value( self ):
        new_text = u"%s %s" % (self._label, self.value)
        self.text.text = new_text
        self.text_selected.text = new_text
        self.callback_func(self.value)


def shake():
    '''Predefined action that performs a slight rotation and then goes back to the original rotation
    position.
    '''
    angle = 05
    duration = 0.05

    rot = Accelerate(RotateBy( angle, duration ), 2)
    rot2 = Accelerate(RotateBy( -angle*2, duration), 2)
    return rot + (rot2 + Reverse(rot2)) * 2 + Reverse(rot)

def shake_back():
    '''Predefined action that rotates to 0 degrees in 0.1 seconds'''
    return RotateTo(0,0.1)

def zoom_in():
    '''Predefined action that scales to 1.5 factor in 0.2 seconds'''
    return ScaleTo( 1.5, duration=0.2 )

def zoom_out():
    '''Predefined action that scales to 1.0 factor in 0.2 seconds'''
    return ScaleTo( 1.0, duration=0.2 )
