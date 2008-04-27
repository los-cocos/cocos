#
# Los Cocos: Multi-Menu Example
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
        item1= ToggleMenuItem('ToggleMenuItem: ', False, 
                        lambda x:printf('switch to:',x) )
                        
        resolutions = ['800x600', '1024x768', '320x200', '640x480']
        item2= MultipleMenuItem('MultipleMenuItem: ',
                        #value switch function:
                        lambda:setslice(resolutions,0,len(resolutions),
                                        resolutions[1:]+[resolutions[0]]),
                        #current value access function:
                        lambda:resolutions[0])

        item3 = MenuItem('MenuItem', self.on_quit )

        self.create_menu( [item1,item2,item3] )


    def on_quit( self ):
        pyglet.app.exit()



if __name__ == "__main__":

    pyglet.font.add_directory('.')

    director.init( resizable=True)
    director.run( Scene( MainMenu() ) )
