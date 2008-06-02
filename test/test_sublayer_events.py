# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
        
class PrintKey(cocos.layer.Layer):
    is_event_handler = True
    def on_key_press (self, key, modifiers):
        print "Key Pressed:", key, modifiers

class SwitchLayer(cocos.layer.Layer):
    def __init__(self):
        super(SwitchLayer, self).__init__()
        self.other = PrintKey()
        self.added = False
    
    is_event_handler = True
    def on_key_press (self, key, modifiers):
        if key == pyglet.window.key.SPACE:
            self.added = not self.added
            print "sublayer present:", self.added
            if self.added:
                self.add(self.other)
            else:
                self.remove(self.other)
            
    
if __name__ == "__main__":
    director.init()
    bg_layer = cocos.layer.ColorLayer(255,0,0,255)
    test_layer = SwitchLayer()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
