from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "EntryMenuItem"

import pyglet

from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *


class MainMenu(Menu):
    def __init__( self ):
        super( MainMenu, self ).__init__("EntryMenuItem")

        l = []
        l.append( EntryMenuItem('Name:', self.on_name, 'default') )
        l.append( MenuItem('Quit', self.on_quit ) )

        self.create_menu( l )

    def on_name( self, value ):
        print(value)

    def on_quit( self ):
        pyglet.app.exit()

def main():

    director.init( resizable=True)
    director.run( Scene( MainMenu() ) )

if __name__ == '__main__':
    main()
