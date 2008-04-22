#
# Menu class for pyglet
#
# Ideas borrowed from:
#    pygext: http://opioid-interactive.com/~shang/projects/pygext/
#    pyglet astraea: http://www.pyglet.org
#    Grossini's Hell: http://www.pyweek.org/e/Pywiii/ 
# 
#
"""A menu layer for los-cocos.

Menu
====

This module provides a Menu class, which is a layer you can use in cocos
apps. Menus can contain regular items (which trigger a function when selected)
or toggle items (which toggle a flag when selected).

When you need a menu, you can define a class inheriting `Menu`, and setting
some attributes which control the menu appearance. Then you add `MenuItem` s to
it, prepare it, and use it as you would use any layer.

There is a menu demo in the samples folder.

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

__all__ = [ 'Menu', 'MenuItem', 'ToggleMenuItem', 
    'MultipleMenuItem', 'EntryMenuItem',
    'CENTER', 'LEFT', 'RIGHT', 'TOP', 'BOTTOM' ]

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
       then add items using `add_item()`,
       and then call `build_items()`
     - Finally you shall add the menu to a `Scene`
    """

    optionSound = None
    selectSound = None
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
            'valign':'center',
            'halign':'center',
            'dpi':96,
            'x':0, 'y':0,
        }

        self.font_item= {
            'font_name':'Arial',
            'font_size':32,
            'bold':False,
            'italic':False,
            'valign':'center',
            'halign':'center',
            'color':(192,192,192,255),
            'dpi':96,
        }
        self.font_item_selected = {
            'font_name':'Arial',
            'font_size':48,
            'bold':False,
            'italic':False,
            'valign':'center',
            'halign':'center',
            'color':(255,255,255,255),
            'dpi':96,
        }

        self.title_height = 0
        self._items_z = 0

     
    def _draw_title( self ):
        """ draws the title """
        width, height = director.get_window_size()

        fo = font.load( self.font_title['font_name'], self.font_title['font_size'] )
        title_height = fo.ascent - fo.descent  

        self.font_title['x'] = width // 2
        self.font_title['y'] = height - ( title_height //2 )
        self.font_title['text'] = self.title
        self.text = pyglet.text.Label( **self.font_title )

        fo = font.load( self.font_title['font_name'], self.font_title['font_size'] )
        self.title_height = fo.ascent * 0.9  # descent is not important

    def _draw_items( self ):

        width, height = director.get_window_size()

        fo = font.load( self.font_item['font_name'], self.font_item['font_size'] )
        fo_height = int( (fo.ascent - fo.descent) * 0.9 )

        if self.menu_halign == CENTER:
            pos_x = width / 2
        elif self.menu_halign == RIGHT:
            pos_x = width - 2
        elif self.menu_halign == LEFT:
            pos_x = 2
        else:
            raise Exception("Invalid halign value for menu")

        for idx,i in enumerate( self.children):

            item = i[1]

            if self.menu_valign == CENTER:
                pos_y = height / 2 + (fo_height * len(self.children) )/2 - (idx * fo_height ) - self.title_height
            elif self.menu_valign == TOP:
                pos_y = height - (idx * fo_height ) - self.title_height
            elif self.menu_valign == BOTTOM:
                pos_y = 0 + fo_height * len(self.children) - (idx * fo_height )

            self.font_item['x'] = pos_x
            self.font_item['y'] = pos_y
            self.font_item['text'] = item.label
            item._init_font_unsel( **self.font_item )

            self.font_item_selected['x'] = pos_x
            self.font_item_selected['y'] = pos_y
            self.font_item_selected['text'] = item.label
            item._init_font_sel( **self.font_item_selected )

    def add( self, item, z=-1, *args, **kw ):
        """Adds an item to the menu.

        The order of the list important since the
        first one will be shown first.

        :Parameters:
            `item` : a `MenuItem`
                The MenuItem that will part of the `Menu`
        """
        if z==-1:
            z=self._items_z
            self._items_z += 1
        item.halign = self.menu_halign
        item.valign = self.menu_valign
        super(Menu,self).add( item, z=z, *args, **kw )

    def on_draw( self ):
        self.text.draw()

    def build_items( self ):
        """Initializes all the menu items

        Call this method after you've added all the menu items."""

        self.font_item_selected['halign'] = self.menu_halign
        self.font_item_selected['valign'] = self.menu_valign

        self.font_item['halign'] = self.menu_halign
        self.font_item['valign'] = self.menu_valign

        self._draw_title()
        self._draw_items()
        self.selected_index = 0
        self.children[ self.selected_index ][1].is_selected = True


    def on_text( self, text ):
        return self.children[self.selected_index][1].on_text(text)
    #
    # Called everytime a key is pressed
    # return True to avoid passing the event to another handler
    #
    def on_key_press(self, symbol, modifiers):

        old_idx = self.selected_index

        if symbol == key.DOWN:
            self.selected_index += 1
        elif symbol == key.UP:
            self.selected_index -= 1
        elif symbol == key.ESCAPE:
            self.on_quit()
            return True
        else:
            if self.selectSound:
                self.selectSound.play()
            ret = self.children[self.selected_index][1].on_key_press(symbol, modifiers)

        if self.selected_index< 0:
            self.selected_index= len( self.children) -1
        elif self.selected_index > len( self.children) - 1:
            self.selected_index = 0

        if symbol in (key.DOWN, key.UP):
            if self.optionSound: self.optionSound.play()
            self.children[ old_idx ][1].is_selected = False
            self.children[ self.selected_index ][1].is_selected = True 
            self.children[ self.selected_index ][1].selected()
            return True

        return ret

    def on_mouse_release( self, x, y, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)
        if self.children[ self.selected_index ][1].is_inside_box(x,y):
            if self.selectSound:
                self.selectSound.play()
            return self.children[ self.selected_index ][1].on_key_press( key.ENTER, 0 )   # XXX: hack

    def on_mouse_motion( self, x, y, dx, dy ):
        (x,y) = director.get_virtual_coordinates(x,y)
        self._x = x
        self._y = y
        for idx,i in enumerate( self.children):
            item = i[1]
            if item.is_inside_box( x, y):
                if not item.is_selected: #Hack to play sound only once
                    if self.optionSound: self.optionSound.play()
                self.children[ self.selected_index ][1].is_selected = False
                item.is_selected = True
                self.selected_index = idx
                item.selected()

#
# MenuItem
#
class MenuItem( CocosNode ):
    """A menu item triggering a function."""

    def __init__(self, label, activate_func):
        """Creates a new menu item

        :Parameters:
            `label` : string
                The label the of the menu item
            `activate_func` : function
                The callback function
        """

        super( MenuItem, self).__init__()

        self.label = label
        self.activate_func = activate_func

        self.is_selected = False

        # Variables that will be set when init_font() is called
        self.text = None
        self.text_selected = None

        self.halign = None
        self.valign = None

        # default effect when item is selected
        angle = 5
        duration = 0.05

        rot = Accelerate(Rotate( angle, duration ), 2)
        rot2 = Accelerate(Rotate( -angle*2, duration), 2)
        self.effect = rot + (rot2 + Reverse(rot2)) * 2 + Reverse(rot)

    def get_box( self ):
        """Returns the box that contains the menu item.

        :rtype: (x1,x2,y1,y2)
        :returns: returns a tuple (a rectangle) that sets the boundaries of the menu item."""

        width = self.text.content_width
        height = self.text.content_height

        if self.halign == CENTER:
            x_diff = - width / 2
        elif self.halign == RIGHT:
            x_diff = - width
        elif self.halign == LEFT:
            x_diff = 0
        else:
            raise Exception("Invalid halign: %s" % str(self.halign) )

        if self.valign == CENTER:
            y_diff = - height/ 2
        elif self.valign == TOP:
            y_diff = - height
        elif self.valign == BOTTOM:
            y_diff = 0
        else:
            raise Exception("Invalid valign: %s" % str(self.valign) )

        x1 = self.text.x + x_diff
        y1 = self.text.y + y_diff
        x2 = x1 + width
        y2 = y1 + height
        return (x1,y1,x2,y2)

    def on_draw( self ):
        glPushMatrix()
        self.transform()

        if self.is_selected:
            self.text_selected.draw()
        else:
            self.text.draw()

        glPopMatrix()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER and self.activate_func:
            self.activate_func()
            return True

    def on_text( self, text ):
        return True

    def _init_font_unsel( self, **kwargs):
        # Unselected option
        self.text = pyglet.text.Label( **kwargs )

    def _init_font_sel( self, **kwargs ):
        # Selected option
        self.text_selected = pyglet.text.Label( **kwargs )

    def is_inside_box( self, x, y ):
        """Returns whether the point (x,y) is inside the menu item.

        :rtype: Boolean
        :Returns: Whether or not the point (x,y) is inside the menu item
        """
        (ax,ay,bx,by) = self.get_box()
        if( x >= ax and x <= bx and y >= ay and y <= by ):
            return True
        return False

    def selected( self ):
        if not self.actions_running():
            pass
#            self.do( self.effect )

#
# Item that can be toggled between N states
#
class MultipleMenuItem( MenuItem ):
    """A menu item for switching between multiple values.
    
    toggle_func will be called for switching when selected, and
    get_value_func should be a function returning the value as a
    string"""

    def __init__(self, label, toggle_func, get_value_func):
        """Creates a Toggle Menu Item

        :Parameters:
            `label` : string
                Item's label
            `toggle_func` : function
                Callback function
            `get_value_func` : function
                This function returns the item's
                actual value as a String
        """
        self.toggle_label = label
        self.toggle_func = toggle_func
        self.get_value_func = get_value_func
        self.value = get_value_func()
        super( MultipleMenuItem, self).__init__( self._get_label(), None )


    def _get_label(self):
        return self.toggle_label+self.get_value_func()

    def on_key_press(self, symbol, modifiers):
        if symbol in ( key.LEFT, key.RIGHT, key.ENTER):
            self.toggle_func( )
            self.text.text = self._get_label()
            self.text_selected.text = self._get_label()
            return True

class ToggleMenuItem( MultipleMenuItem ):
    """A menu item for a boolean toggle option.
    
    When selected, ``self.value`` is toggled, the callback function is
    called with ``self.value`` as argument."""

    def __init__(self, label, value, toggle_func):
        """Creates a Toggle Menu Item

        :Parameters:
            `label` : string
                Item's label
            `value` : Bool
                Default value: False is OFF, True is ON
            `toggle_func` : function
                Callback function
        """
        self.__value = value
        
        def switch_value():
            self.__value=not self.__value
            toggle_func(self.__value)
    
        super(ToggleMenuItem, self).__init__( label, switch_value, 
                lambda :['OFF','ON'][int(self.__value)] )          

class EntryMenuItem(MenuItem):
    """A menu item for entering a value.

    When selected, ``self.value`` is toggled, the callback function is
    called with ``self.value`` as argument."""

    value = property(lambda self: u''.join(self._value),
                     lambda self, v: setattr(self, '_value', list(v)))

    def __init__(self, label, value, set_func):
        """Creates an Entry Menu Item

        :Parameters:
            `label` : string
                Item's label
            `value` : String
                Default value: any string
            `set_func` : function
                Callback function taking one argument.
        """
        self.set_func = set_func
        self._value = list(value)
        self._label = label
        super(EntryMenuItem, self).__init__( "%s %s" %(label,value), None)

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
        self.set_func(self.value)
