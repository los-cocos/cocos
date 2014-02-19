from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "menu items, ToggleMenuItem, MultipleMenuItem, MenuItem, EntryMenuItem, ImageMenuItem, ColorMenuItem"

from pyglet import image
from pyglet.gl import *
from pyglet import font

from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *

def printf(*args):
    sys.stdout.write(''.join([str(x) for x in args])+'\n')

class MainMenu(Menu):
    def __init__( self ):
        super( MainMenu, self ).__init__("Test Menu Items")

        # then add the items
        item1= ToggleMenuItem('ToggleMenuItem: ', self.on_toggle_callback, True )

        resolutions = ['320x200','640x480','800x600', '1024x768', '1200x1024']
        item2= MultipleMenuItem('MultipleMenuItem: ',
                        self.on_multiple_callback,
                        resolutions)
        item3 = MenuItem('MenuItem', self.on_callback )
        item4 = EntryMenuItem('EntryMenuItem:', self.on_entry_callback, 'value',
                              max_length=8)
        item5 = ImageMenuItem('imagemenuitem.png', self.on_image_callback)

        colors = [(255, 255, 255), (129, 255, 100), (50, 50, 100), (255, 200, 150)]
        item6 = ColorMenuItem('ColorMenuItem:', self.on_color_callback, colors)
        self.create_menu( [item1,item2,item3,item4,item5,item6] )


    def on_quit( self ):
        pyglet.app.exit()

    def on_multiple_callback(self, idx ):
        print('multiple item callback', idx)

    def on_toggle_callback(self, b ):
        print('toggle item callback', b)

    def on_callback(self ):
        print('item callback')

    def on_entry_callback (self, value):
        print('entry item callback', value)

    def on_image_callback (self):
        print('image item callback')

    def on_color_callback(self, value):
        print('color item callback:', value)

def main():

    pyglet.font.add_directory('.')

    director.init( resizable=True)
    director.run( Scene( MainMenu() ) )

if __name__ == '__main__':
    main()
