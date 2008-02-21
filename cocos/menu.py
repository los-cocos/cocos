#
#
# Menu class for pyglet
#
# Ideas borrowed from:
#    pygext: http://opioid-interactive.com/~shang/projects/pygext/
#    pyglet astraea: http://www.pyglet.org
#    Grossini's Hell: http://www.pyweek.org/e/Pywiii/ 
# 
#

from pyglet import font
from pyglet import media
from pyglet import window
from pyglet.window import key
from pyglet.gl import *

from new_api import *

__all__ = [ 'Menu', 'MenuItem', 'ToggleMenuItem' ]

#
# Class Menu
#

# Horizontal Align
CENTER = font.Text.CENTER
LEFT = font.Text.LEFT
RIGHT = font.Text.RIGHT

# Vertial Align
TOP = font.Text.TOP
BOTTOM = font.Text.BOTTOM



class Menu(Layer):

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
        self.font_title = ''            # Full font name
        self.font_title_size = 72
        self.font_title_color = ( 0.6, 0.6, 0.6, 1.0 )

        # Items
        self.font_items = ''            # Full font name
        self.font_items_size = 48
        self.font_items_color = (0.6, 0.6, 0.6, 1.0 ) 
        self.font_items_selected_size = 64 
        self.font_items_selected_color = (1.0, 1.0, 1.0, 1.0 )

        # Sound
        self.sound_filename = 'menuchange.wav'

        # Alignment
        self.menu_halign = CENTER
        self.menu_valign = CENTER

     
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

            item.init_font( fo, fo_selected, pos_x, pos_y )


    def add_item( self, item ):
        """add_item( menu_item ) -> None

        Adds an item to the menu. The order of the list important since the
        one will be shonw first."""
        item.halign = self.menu_halign
        item.valign = self.menu_valign
        item.color = self.font_items_color
        item.selected_color = self.font_items_selected_color
        self.items.append( item )

    # overriden method from Scene
    def draw( self ):
        self.title_text.draw()
        for i in self.items:
            i.draw()


    def tick( self, dt ):
        for i in self.items:
            i.tick( dt )

    def build_items( self ):
        """build_items() -> None

        Initialize the menu with the added menu items.
        Don't call this method before adding all the menu items"""
        self._draw_title()
        self._draw_items()
        self.selected_index = 0
        self.items[ self.selected_index ].selected = True


    #
    # Called when the menu will appear
    #
    def enter( self ):
        director.get_window().push_handlers( self.on_key_press, self.on_mouse_motion, self.on_mouse_release )

    #
    # Called when the menu will disappear
    #
    def exit( self ):
        director.get_window().pop_handlers()

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
            self.sound.play()
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
    # Called everytime you press escape
    #
    def on_quit( self ):
        pass        # override in subclases


#
# MenuItem
#
class MenuItem( object ):

    def __init__(self, label, activate_func):
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

    def _get_box( self ):
        """_get_box() -> (x1,y1,x2,y2)

        returns a tuple that contains the margins of the item."""
       
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


    def draw( self ):
        if self.selected:
            self.text_selected.draw()
        else:
            self.text.draw()

    def tick( self, dt ):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER and self.activate_func:
            self.activate_func()
            return True

    def init_font( self, aFont, aFont_selected, x, y ):
        """init_font( normal_font, selected_font, x, y) -> None

        Creates pyglet Font objects ready to be drawn when necesary."""

        # Unselected option
        self.text = font.Text( aFont, self.label, x=x , y=y, halign=self.halign, valign=self.valign )
        self.text.color = self.color

        # Selected option
        self.text_selected = font.Text( aFont_selected, self.label, x=x, y=y, halign=self.halign, valign=self.valign )
        self.text_selected.color = self.selected_color

    def is_inside_box( self, x, y ):
        """is_inside_box( x, y ) -> Boolean

        Returns whether x,y are inside the item."""
        (ax,ay,bx,by) = self._get_box()
        if( x >= ax and x <= bx and y >= ay and y <= by ):
            return True
        return False
        

        
#
# Item that can be toggled
#
class ToggleMenuItem( MenuItem ):

    def __init__(self, label, value, toggle_func):
        self.toggle_label = label
        self.value = value
        self.toggle_func = toggle_func
        super(ToggleMenuItem, self).__init__( self._get_label(), None )

    def _get_label(self):
        return self.toggle_label + (self.value and ': ON' or ': OFF')

    def tick( self, dt ):
        # useful to animate the items
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol in ( key.LEFT, key.RIGHT, key.ENTER):
            self.value = not self.value
            self.text.text = self._get_label()
            self.text_selected.text = self._get_label()
            self.toggle_func( self.value )
            return True
