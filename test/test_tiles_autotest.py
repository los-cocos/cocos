from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.1, s, t 2.1, s, t 3.1, s, t 4.1, s, t 5.1, s, t 6.1, s, q"
tags = "CallFunc, tiles"

import pyglet
pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, layer
from cocos.actions import CallFunc, ScaleTo, Delay
from cocos.director import director


class TestScene(cocos.scene.Scene):
    def __init__(self):
        super(TestScene, self).__init__()
        scroller = layer.ScrollingManager()
        scrollable = tiles.load('road-map.xml')['map0']
        scroller.add(scrollable)
        self.add(scroller)
        template_action = ( CallFunc(scroller.set_focus, 0, 0) + Delay(1) +
                            CallFunc(scroller.set_focus, 768, 0) + Delay(1) +
                            CallFunc(scroller.set_focus, 768, 768) +Delay(1) +
                            CallFunc(scroller.set_focus, 1500, 768) +Delay(1) +
                            ScaleTo(0.75, 1) +
                            CallFunc(scrollable.set_debug, True) + Delay(1) +
                            CallFunc(director.window.set_size, 800, 600)
                          )
        scroller.do(template_action)

def main():
    director.init(width=600, height=300, autoscale=False, resizable=True)
    main_scene = TestScene()
    director.run(main_scene)

if __name__ == '__main__':
    main()
