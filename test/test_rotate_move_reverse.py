# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import pyglet
import cocos
from cocos.actions import *
from cocos.director import director

key = pyglet.window.key

class DebugLabel(cocos.text.Label):
    def draw(self):
        sprite = self.parent.sprite
        self.element.text = "* (%.0f, %.0f) %.0f" % (sprite.position
                                                     + (sprite.rotation,))
        super(DebugLabel, self).draw()

class Logo(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self):
        super(Logo, self).__init__()
        self.wx, self.wy = director.get_window_size()
        self.sprite = cocos.sprite.Sprite('grossini.png')
        self.sprite.position = self.wx/2, self.wy/2
        self.label = DebugLabel()
        self.add(self.label)
        self.add(self.sprite)
        
    def on_key_press(self, k, m):
        if k == key.SPACE:
            action = RotateBy(360, .5) | Delay(0.5)
            self.sprite.do(action + Reverse(action))

if __name__=="__main__":
    director.init(fullscreen=0, width=800, height=600)
    scene = cocos.scene.Scene()
    scene.add(Logo())
    director.run(scene)

