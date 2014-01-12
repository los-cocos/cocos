# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.5, s, t 3, s, t 4.1, s, q"
tags = "compose_actions, sequence, spawn"

import pyglet
import cocos
from cocos.actions import ScaleTo, MoveTo, Accelerate
from cocos.sprite import Sprite
from cocos.director import director
from cocos.scene import Scene

class Bg(cocos.layer.Layer):
    def __init__(self):
        super(Bg, self).__init__()
        self.image = pyglet.resource.image('grossini.png')

    def on_enter(self):
        super(Bg, self).on_enter()
        sprite = Sprite(self.image)
        self.add(sprite)
        sprite.position = 320, 240
        sprite.do(ScaleTo(4,0))

        action = MoveTo((640, 480), 4) | ( ScaleTo(2,2) + ScaleTo(4,2) )

        sprite.do(action)

def main():
    director.init()
    director.run(Scene(Bg()))

if __name__ == '__main__':
    main()
