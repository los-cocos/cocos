from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.1, s, t 2.1, s, q"
tags = "on_mouse_motion, Label"
autotest = 0

import cocos
from cocos.actions import Delay, CallFunc 
from cocos.director import director


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
        if autotest:
            self.do( Delay(1) + CallFunc(self.move_label, 100, 100) +
                     Delay(1) + CallFunc(self.move_label, 500, 300))

    def on_mouse_motion( self, x, y, dx, dy ):
        if not autotest:
            vh, vy = director.get_virtual_coordinates(x, y)
            self.move_label(vh, vy)

    def move_label(self, x, y):
        self.label.element.text = '%d,%d' % (x,y)
        self.label.element.x = x
        self.label.element.y = y
        

description = """
A label its shown, initially 'Hi' at screen center, then telling the
mouse position at position near the mouse pointer
"""

def main():
    print(description)
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

if __name__ == '__main__':
    main()
