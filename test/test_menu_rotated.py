from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "menu, layout_strategy, fixedPositionMenuLayout"

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyglet import font
from pyglet.app import exit

from cocos.director import director
from cocos.menu import Menu, MenuItem, fixedPositionMenuLayout
from cocos.menu import shake, shake_back
from cocos.scene import Scene

class MainMenu(Menu):
    def __init__( self ):
        super( MainMenu, self ).__init__("TITLE" )
        item1 = MenuItem('Item 1', self.on_quit )
        item2 = MenuItem('Item 2', self.on_quit )
        item3 = MenuItem('Item 3', self.on_quit )
        item4 = MenuItem('Item 4', self.on_quit )

        item1.rotation = 45
        item2.rotation = 90
        item3.scale = 2
        item4.scale= 1.5
        item4.rotation = 90

        items = [ item1, item2, item3, item4, ]
        self.create_menu( items,
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
