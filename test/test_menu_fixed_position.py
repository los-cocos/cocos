from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "menu, layout_strategy, fixedPositionMenuLayout"

from pyglet import font
from pyglet.app import exit

from cocos.director import director
from cocos.menu import Menu, MenuItem, fixedPositionMenuLayout
from cocos.menu import shake, shake_back
from cocos.scene import Scene

class MainMenu(Menu):
    def __init__( self ):
        super( MainMenu, self ).__init__("TITLE" )
        items = [
            ( MenuItem('Item 1', self.on_quit ) ),
            ( MenuItem('Item 2', self.on_quit ) ),
            ( MenuItem('Item 3', self.on_quit ) ),
            ( MenuItem('Item 4', self.on_quit ) ),
        ]
        self.create_menu( items, selected_effect=shake(),
                          unselected_effect=shake_back(),
                          layout_strategy=fixedPositionMenuLayout(
                            [(450, 300), (130, 200), (200, 100), (400, 50)]))
    def on_quit( self ):
        exit()

def main():
    font.add_directory('.')

    director.init( resizable=True)
    director.run( Scene( MainMenu() ) )

if __name__ == '__main__':
    main()
