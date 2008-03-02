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

from pyglet import font
from pyglet import media
from pyglet import window
from pyglet.window import key
from pyglet.gl import *

from layer import *
from director import *

__all__ = [ 'Menu', 'MenuItem', 'ToggleMenuItem', 'CENTER', 'LEFT', 'RIGHT', 'TOP', 'BOTTOM' ]

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

     - create a descendent from this class
     - override __init__ to set all style attributes, add items,
       and call build_items
     - add to a scene
    """

    def __init__( self, title = ''):
        super(Menu, self).__init__()

        #
        # Items and Title
        #
        self.items = []
        self.title = title
        self.title_text = None

        #
        # Menu default options
        # Menus can be customized changing these variables
        #

        # Title
        self.font_title = ''
	"""Title's font name"""
        self.font_title_size = 72
	"""Title's font size. Default size is 72"""
        self.font_title_color = ( 0.6, 0.6, 0.6, 1.0 )
	"""Title's font color. Default color is (0.6, 0.6, 0.6, 1.0)"""

        # Items
        self.font_items = ''            # Full font name
	"""Items' font name"""
        self.font_items_size = 48
	"""Items' font size when unselected. Default size is 48"""
        self.font_items_color = (0.6, 0.6, 0.6, 1.0 ) 
	"""Items' font color when unselected. Default color is (0.6, 0.6, 0.6, 1.0)"""
        self.font_items_selected_size = 64 
	"""Items' font size when selected. Default size is 64"""
        self.font_items_selected_color = (1.0, 1.0, 1.0, 1.0 )
	"""Items' font color when selected. Default color is (1.0, 1.0, 1.0, 1.0)"""

        # Sound
        self.sound_filename = 'menuchange.wav'

        # Alignment
        self.menu_halign = CENTER
	"""Horizontal alignment. Possible options: CENTER, RIGHT or LEFT. Default is CENTER"""
        self.menu_valign = CENTER
	"""Vertical alignment. Possible options: CENTER, TOP or BOTTOM. Default is CENTER"""

     
    def _draw_title( self ):
        """ draws the title """
        width, height = director.get_window_size()

        ft = font.load( self.font_title, self.font_title_size )
        ft_height = ft.ascent - ft.descent
        text = font.Text(ft, self.title)

        text = font.Text(ft, self.title,
            x=width / 2,
            y=height - 40,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER)
        text.color = self.font_title_color

        self.title_text = text

    def _draw_items( self ):

        width, height = director.get_window_size()

        fo = font.load( self.font_items, self.font_items_size )
        fo_selected = font.load( self.font_items, self.font_items_selected_size )
        fo_height = int( (fo.ascent - fo.descent) * 0.9 )

        if self.menu_halign == CENTER:
            pos_x = width / 2
        elif self.menu_halign == RIGHT:
            pos_x = width - 2
        elif self.menu_halign == LEFT:
            pos_x = 2
        else:
            raise Exception("Invalid halign value for menu")

        for idx,item in enumerate( self.items ):

            if self.menu_valign == CENTER:
                pos_y = height / 2 + (fo_height * len(self.items) )/2 - (idx * fo_height )
            elif self.menu_valign == TOP:
                pos_y = height - (idx * fo_height )
            elif self.menu_valign == BOTTOM:
                pos_y = 0 + fo_height * len(self.items) - (idx * fo_height )

            item._init_font( fo, fo_selected, pos_x, pos_y )


    def add_item( self, item ):
        """Adds an item to the menu.

        The order of the list important since the
        one will be shonw first.

        :Parameters:
            `item` : a MenuItem
                The MenuItem
        """
        item.halign = self.menu_halign
        item.valign = self.menu_valign
        item.color = self.font_items_color
        item.selected_color = self.font_items_selected_color
        self.items.append( item )

    # overriden method from Layer
    def step( self, dt ):
        self.title_text.draw()
        for i in self.items:
            i.step(dt)

    def build_items( self ):
        """Initializes all the menu items

        Call this method after you've added all the menu items."""
        self._draw_title()
        self._draw_items()
        self.selected_index = 0
        self.items[ self.selected_index ].selected = True


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
            ret = self.items[self.selected_index].on_key_press(symbol, modifiers)

        if self.selected_index< 0:
            self.selected_index= len( self.items ) -1
        elif self.selected_index > len( self.items ) - 1:
            self.selected_index = 0

        if symbol in (key.DOWN, key.UP):
            self.items[ old_idx ].selected = False
            self.items[ self.selected_index ].selected = True 
#            self.sound.play()
            return True

        return ret

    def on_mouse_release( self, x, y, buttons, modifiers ):
        (x,y) = director.get_virtual_coordinates(x,y)
        if self.items[ self.selected_index ].is_inside_box(x,y):
            return self.items[ self.selected_index ].on_key_press( key.ENTER, 0 )   # XXX: hack

    def on_mouse_motion( self, x, y, dx, dy ):
        (x,y) = director.get_virtual_coordinates(x,y)
        self._x = x
        self._y = y
        for idx,i in enumerate( self.items ):
            if i.is_inside_box( x, y):
                self.items[ self.selected_index ].selected = False
                i.selected = True
                self.selected_index = idx

#
# MenuItem
#
class MenuItem( object ):
    """A menu item triggering a function."""

    def __init__(self, label, activate_func):
        """Creates a new menu item

        :Parameters:
            `label` : string
                The label the of the menu item
            `activate_func` : function
                The callback function
        """
        self.label = label
        self.activate_func = activate_func

        self.selected = False

        # Variables that will be set when init_font() is called
        self.text = None
        self.text_selected = None

        self.color = None
        self.selected_color = None
        self.halign = None
        self.valign = None

    def get_box( self ):
        """Returns the box that contains the menu item.

        :rtype: (x1,x2,y1,y2)
        :returns: returns a tuple (a rectangle) that sets the boundaries of the menu item."""
       
        if self.halign == CENTER:
            x_diff = - self.text.width / 2
        elif self.halign == RIGHT:
            x_diff = - self.text.width
        elif self.halign == LEFT:
            x_diff = 0

        if self.valign == CENTER:
            y_diff = - self.text.height/ 2
        elif self.valign == TOP:
            y_diff = - self.text.height
        elif self.valign == BOTTOM:
            y_diff = 0

        x1 = self.text.x + x_diff
        y1 = self.text.y + y_diff
        x2 = x1 + self.text.width
        y2 = y1 + self.text.height
        return (x1,y1,x2,y2)


    def step( self, dt ):
        if self.selected:
            self.text_selected.draw()
        else:
            self.text.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER and self.activate_func:
            self.activate_func()
            return True

    def _init_font( self, aFont, aFont_selected, x, y ):
        # Unselected option
        self.text = font.Text( aFont, self.label, x=x , y=y, halign=self.halign, valign=self.valign )
        self.text.color = self.color

        # Selected option
        self.text_selected = font.Text( aFont_selected, self.label, x=x, y=y, halign=self.halign, valign=self.valign )
        self.text_selected.color = self.selected_color

    def is_inside_box( self, x, y ):
        """Returns whether the point (x,y) is inside the menu item.

        :rtype: Boolean
        :Returns: Whether or not the point (x,y) is inside the menu item
        """
        (ax,ay,bx,by) = self.get_box()
        if( x >= ax and x <= bx and y >= ay and y <= by ):
            return True
        return False
        

        
#
# Item that can be toggled
#
class ToggleMenuItem( MenuItem ):
    """A menu item for a boolean toggle option.
    
    When selected, ``self.value`` is toggled, the callback function is
    called with ``self.value`` as argument."""

    def __init__(self, label, value, toggle_func):
        """Creates a Toggle Menu Item

        :Parameters:
            `label` : string
                Item's label
            `value` : Boolean
                Item's default value: True or False
            `toggle_func` : function
                Callback function
        """
        self.toggle_label = label
        self.value = value
        self.toggle_func = toggle_func
        super(ToggleMenuItem, self).__init__( self._get_label(), None )

    def _get_label(self):
        return self.toggle_label + (self.value and ': ON' or ': OFF')

    def on_key_press(self, symbol, modifiers):
        if symbol in ( key.LEFT, key.RIGHT, key.ENTER):
            self.value = not self.value
            self.text.text = self._get_label()
            self.text_selected.text = self._get_label()
            self.toggle_func( self.value )
            return True
