# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.text import Label
from cocos.layer import ScrollingManager, ScrollableLayer
from pyglet.window import key

def main():
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
