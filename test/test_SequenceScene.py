# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

from cocos.director import director
from cocos.scene import Scene
from cocos.sprite import *
from cocos.utils import SequenceScene
from cocos.text import *
from cocos.layer import *

from pyglet import font
from pyglet.window import key

class introLayer(Layer):

    is_event_handler = True     #: enable pyglet's events

    def __init__( self ):

        super(introLayer, self).__init__()

        #Title
        self.text_title = pyglet.text.Label("INTRO",
            font_size=32,
            x=director.get_window_size()[0] /2,
            y=director.get_window_size()[1],
            anchor_x=font.Text.CENTER,
            anchor_y=font.Text.TOP )

        #A grossini is added
        self.sprite = Sprite( 'grossini.png', (320,240) )
        self.add( self.sprite )

        #The Press key text.
        self.text_pressKey = pyglet.text.Label("Press ENTER to continue",
            font_size=16,
            x=director.get_window_size()[0] /2,
            y=20,
            anchor_x=font.Text.CENTER,
            anchor_y=font.Text.CENTER)

    def draw( self ):
        self.text_title.draw()
        self.text_pressKey.draw()

    def on_key_press( self, k , m ):
        if k == key.ENTER:
            director.pop()


class mainMenu(Layer):

    is_event_handler = True     #: enable pyglet's events

    def __init__( self ):

        super(mainMenu, self).__init__()

        #Title
        self.text_title = pyglet.text.Label("Menu",
            font_size=32,
            x=director.get_window_size()[0] /2,
            y=director.get_window_size()[1],
            anchor_x=font.Text.CENTER,
            anchor_y=font.Text.TOP )

        #A grossini is added
        self.sprite = Sprite( 'grossinis_sister1.png', (320,240) )
        self.add( self.sprite )

        #The Press key text.
        self.text_pressKey = pyglet.text.Label("Press ENTER to continue",
            font_size=16,
            x=director.get_window_size()[0] /2,
            y=20,
            anchor_x=font.Text.CENTER,
            anchor_y=font.Text.CENTER)

    def draw( self ):
        self.text_title.draw()
        self.text_pressKey.draw()

    def on_key_press( self, k , m ):
        if k == key.ENTER:
            director.pop()


if __name__ == "__main__":
    director.init( resizable=True, width=640, height=480 )
    scene1 = Scene()
    scene2 = Scene()

    scene1.add( introLayer(), z=1 )
    scene2.add( mainMenu(), z=1 )

    director.run( SequenceScene(scene1, scene2) )
    print 'end'