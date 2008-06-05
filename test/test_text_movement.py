#
# Cocos
# http://code.google.com/p/los-cocos/
#
# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import cocos

class HelloWorld(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self):
        super( HelloWorld, self ).__init__()

        # a cocos.text.Label is a wrapper of pyglet.text.Label
        # with the benefit of being a cocosnode
        self.label = cocos.text.Label('Hi',
            font_name='Times New Roman',
            font_size=32,
            x=320, y=240,
            anchor_x='center', anchor_y='center')

        self.add( self.label )

    def on_mouse_motion( self, x, y, dx, dy ):
        self.label.element.text = '%d,%d' % (x,y)
        self.label.element.x = x
        self.label.element.y = y


if __name__ == "__main__":
    # director init takes the same arguments as pyglet.window
    cocos.director.director.init()

    # We create a new layer, an instance of HelloWorld
    hello_layer = HelloWorld ()

    # A scene that contains the layer hello_layer
    main_scene = cocos.scene.Scene (hello_layer)

    # And now, start the application, starting with main_scene
    cocos.director.director.run (main_scene)

    # or you could have written, without so many comments:
    #      director.run( cocos.scene.Scene( HelloWorld() ) )
