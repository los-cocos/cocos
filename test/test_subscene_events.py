from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "dt 0.1, q"
tags = "window event, enable_handlers, Scene, subscene"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet

class PrintKey(cocos.layer.Layer):
    is_event_handler = True
    def on_key_press (self, key, modifiers):
        print("Key Pressed:", key, modifiers)

class SwitchLayer(cocos.layer.Layer):
    def __init__(self, subscene):
        super(SwitchLayer, self).__init__()
        self.subscene = subscene
        self.dispatch = False

    is_event_handler = True
    def on_key_press (self, key, modifiers):
        if key == pyglet.window.key.SPACE:
            self.dispatch = not self.dispatch
            print("\nDISPATCH EVENTS:", self.dispatch)
            self.subscene.enable_handlers(self.dispatch)

description = """
A Scene node can block propagation of window events to her subtree.
Scene.enable_handlers() is used to enable / disable passing events.
The active scene is set by director to propagate window events.

'space' will will togle the state propgate / non propagate and report
on console ther actual propagation status.

When any other key is pressed:
    with dispatch events == True a line will be printed reporting the keypress
    with dispatch events == False nothing will be printed    
"""

def main():
    print(description)
    director.init()
    bg_layer = cocos.layer.ColorLayer(255,0,0,255)
    sub = cocos.scene.Scene(bg_layer, PrintKey())
    test_layer = SwitchLayer(sub)
    main_scene = cocos.scene.Scene (sub, test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
