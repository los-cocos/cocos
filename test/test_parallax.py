from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.1, s, t 2.1, s, t 3.1, s, q"
tags = "parallax, set_focus, ScrollableLayer"
autotest = 0

import cocos
from cocos.director import director
from cocos.text import Label
from cocos.layer import ScrollingManager, ScrollableLayer
from pyglet.window import key
from cocos.actions import Delay, CallFunc


def update_focus(fx, fy):
    global m
    m.set_focus(fx, fy)

def main():
    global m
    director.init()

    m = ScrollingManager()

    fg = ScrollableLayer()
    l = Label('foreground')
    l.position = (100, 100)
    fg.add(l)
    m.add(fg)

    bg = ScrollableLayer(parallax=.5)
    l = Label('background, parallax=.5')
    l.position = (100, 100)
    bg.add(l)
    m.add(bg)

    if autotest:
        m.do( 
              Delay(1) + CallFunc(update_focus, 100, 200) +
              Delay(1) + CallFunc(update_focus, 200, 100) +
              Delay(1) + CallFunc(update_focus, 200, 200)
            )

    main_scene = cocos.scene.Scene(m)

    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)

    def update(dt):
        m.fx += (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 150 * dt
        m.fy += (keyboard[key.DOWN] - keyboard[key.UP]) * 150 * dt
        m.set_focus(m.fx, m.fy)
    main_scene.schedule(update)

    director.run (main_scene)

if __name__ == '__main__':
    main()
