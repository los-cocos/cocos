from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "is_event_handler, on_key_press"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet

class PrintKey(cocos.layer.Layer):
    is_event_handler = True
    def on_key_press (self, key, modifiers):
        print("Key Pressed:", key, modifiers)

description = """
When pressing keys the key with modifiers should print on console
"""

def main():
    print(description)
    director.init()
    bg_layer = cocos.layer.ColorLayer(255,0,0,255)
    test_layer = PrintKey()
    main_scene = cocos.scene.Scene (bg_layer, test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
