from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "get_virtual_coordinates, mouse hit"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import FadeOut, FadeIn
import pyglet

## the following is in case we want to get the images
## from other directories:
# pyglet.resource.path.append("/data/other/directory")
# pyglet.resource.reindex()
sw = 800;sh = 600
#sw = 768;sh = 480

class TestLayer(cocos.layer.ColorLayer):
    def __init__(self):
        super( TestLayer, self ).__init__(0,0,50,255)

        # get the sizes
        sprite = Sprite('fire.png')
        w, h =  sprite.width//2, sprite.height//2

        # thes are the center of the sprites, where to click
        self.positions = [
            (w, h),
            (sw-w, h),
            (w, sh-h),
            (sw-w, sh-h),
            (sw//2, sh//2),
        ]

        # let's draw the sprites
        self.sprites = []
        for pos in self.positions:
            sprite = Sprite('fire.png')
            sprite.position = pos
            self.add(sprite)
            self.sprites.append(sprite)

        self.dd = sprite

    def click(self, x, y):
        # validate positions
        for i, (pos_x, pos_y) in enumerate(self.positions):
            ok_x = pos_x - 5 <= x <= pos_x + 5
            ok_y = pos_y - 5 <= y <= pos_y + 5
            if ok_x and ok_y:
                sprite = self.sprites[i]
                sprite.do(FadeOut(.5) + FadeIn(.5))
                break

class MouseManager(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, test):
        super(MouseManager, self).__init__()
        self.test = test

    def on_mouse_press(self, x, y, buttons, modifiers):
        x, y = director.get_virtual_coordinates (x, y)
        self.test.click(x, y)

description = """
Interactive test checking good behavior of virtual coordinates after resizes.
Clicking the ball center should blink the ball, for any ball, whatever the
resize done (including fullscreen, done with ctrl + F)
"""

def main():
    print(description)
    director.init(width=sw, height=sh, resizable=True)
    test_layer = TestLayer()
    main_scene = cocos.scene.Scene(test_layer)
    main_scene.add(MouseManager(test_layer))
    director.run(main_scene)

if __name__ == '__main__':
    main()
