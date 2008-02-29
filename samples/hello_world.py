# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import cocos
from cocos.director import director

from pyglet import font

class HelloWorld(cocos.layer.Layer):
    def __init__(self):
        # see pyglet documentation for help on this lines
        ft = font.load('Arial', 36)
        self.text = font.Text(ft, 'Hello, World!', x=100, y=240)
        
    def step(self, dt):
        # this funcition is called on every frame
        # dt is the elapsed time betwen this frame and the last        
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
