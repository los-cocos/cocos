#
# Cocos
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyglet import image
from pyglet.gl import *
from pyglet import font

from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *

from operator import setslice

def printf(*args):
    sys.stdout.write(''.join([str(x) for x in args])+'\n')

class MainMenu(Menu):
    def __init__( self ):
        super( MainMenu, self ).__init__("Test Menu Items")

        # then add the items
        item1= ToggleMenuItem('ToggleMenuItem: ', self.on_toggle_callback, True )
                        
        resolutions = ['320x200','640x480','800x600', '1024x768', '320x200']
        item2= MultipleMenuItem('MultipleMenuItem: ',
                        self.on_multiple_callback,
                        resolutions,
                        0 )

        item3 = MenuItem('MenuItem', self.on_callback )

        self.create_menu( [item1,item2,item3] )


    def on_quit( self ):
        pyglet.app.exit()

    def on_multiple_callback(self, idx ):
        print 'multiple item callback', idx

    def on_toggle_callback(self, b ):
        print 'toggle item callback', b

    def on_callback(self ):
        print 'item callback'


if __name__ == "__main__":

    pyglet.font.add_directory('.')

    director.init( resizable=True)
    director.run( Scene( MainMenu() ) )
