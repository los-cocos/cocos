from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "dt 0.1, q"
tags = "window event, on_key_press"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet

class PrintKey(cocos.layer.Layer):
    is_event_handler = True
    def on_key_press (self, key, modifiers):
        print("Sublayer sees on_key_pressed:", key, modifiers)

class SwitchLayer(cocos.layer.Layer):
    def __init__(self):
        super(SwitchLayer, self).__init__()
        self.other = PrintKey()
        self.added = False

    is_event_handler = True
    def on_key_press (self, key, modifiers):
        print('Layer sees on_key_pressed:', key, modifiers)
        if key == pyglet.window.key.SPACE:
            self.added = not self.added
            print("\nSublayer present:", self.added)
            if self.added:
                self.add(self.other)
            else:
                self.remove(self.other)

description = """
Demostrates
    How window events cascade from children to parent.
    After removing a child from the active scene, it doesn't receive
    windows events.

    Pressing 'space' will add / remove a sublayer

    When the sublayer is present, pressing any key except 'space' should
    print two lines, one from the layer and another from the sublayer;

    When the sublayer is not present, pressing any key except 'space' should
    print one line from the layer.
"""

def main():
    print(description)
    director.init()
    bg_layer = cocos.layer.ColorLayer(255,0,0,255)
    test_layer = SwitchLayer()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
