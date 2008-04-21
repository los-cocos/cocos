# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import cocos
from cocos.director import director

import pyglet

class HelloWorld(cocos.layer.Layer):
    def __init__(self):

        super( HelloWorld, self ).__init__()

        # see pyglet documentation for help on this lines
        self.text = pyglet.text.Label('Hello, World!', font_name='', font_size=32, x=100, y=240 )

    def on_draw( self ):
        self.text.draw()

if __name__ == "__main__":
    # director init takes the same arguments as pyglet.window
    director.init()
    # We create a new layer, an instance of HelloWorld
    hello_layer = HelloWorld ()
    # A scene that contains the layer hello_layer
    main_scene = cocos.scene.Scene (hello_layer)
    # And now, start the application, starting with main_scene
    director.run (main_scene)
    # or you could have written, without so many comments:
    #      director.run( cocos.scene.Scene( HelloWorld() ) )
