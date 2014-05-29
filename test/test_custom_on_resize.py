from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 2.1, s, q"
tags = "director.on_cocos_resize"
autotest = 0

import pyglet
from pyglet.gl import *
import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import Delay, CallFunc

description = """
This script demonstrates:
    How to listen to director events, in particular the on_cocos_resize event.
    Instruct the director to not autoscale the scene when the window is
    resized.

What you should see:
    The window shows the usual background pic and three grossinis, resizing
    the window should show more o less from the scene, at the same scale, and
    the scene center will always match the window center.
"""


def resize():
    director.window.set_size(800, 600)

class AutocenteredBackgroundLayer(cocos.layer.Layer):
    """
    An unusual CocosNode that auto centers in the window when a resize happens.
    For doing that, it registers to the event on_cocos_resize and repositions
    itself whenever the event happens.
    """
    def __init__(self):
        super(AutocenteredBackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background_image.png')
        self.transform_anchor = 0, 0

    def on_enter(self):
        # handler's auto registration only happens for window's events;
        # we want to listen director events, so explicitly registering
        super(AutocenteredBackgroundLayer,self).on_enter()
        director.push_handlers(self.on_cocos_resize)
        if autotest:
            self.do(Delay(2.0) + CallFunc(resize) )

    def on_exit(self):
        # if a handler is explicitly attaching at on_enter, it should detach
        # at on_exit, else two bad things happens:
        #   The event dispatcher will continue calling the listener even if the
        # node is not in the active scene
        #   The event dispatcher retains a reference to the registered function,
        # thus preventing garbage collection
        director.remove_handlers(self.on_cocos_resize)
        super(AutocenteredBackgroundLayer,self).on_exit()

        # we want auto center to hold even when added to an active scene, or
        # when the scene containing the layer is director.pushed and then popped,
        # so we do here a direct call to on_cocos_resize
        self.on_cocos_resize(director._usable_width, director._usable_height)

    def draw( self ):
        glColor4ub(255, 255, 255, 255)
        glPushMatrix()
        self.transform()
        self.img.blit(0,0)
        glPopMatrix()

    def on_cocos_resize(self, usable_width, usable_height):
        # assumes  scene.scale==1.0
        x = (usable_width - self.img.width * self.scale) // 2
        y = (usable_height - self.img.height * self.scale) // 2
        self.position = (x, y)

def main():
    print(description)
    # telling director to not auto scale the scene when the window resizes and
    # to allow window resize, also that a 400x400 window is desired.
    director.init(width=400, height=400, autoscale=False, resizable=True)
    scene = cocos.scene.Scene()
    bg = AutocenteredBackgroundLayer()
    for i in range(3):
        sp = Sprite('grossini.png', position=(140 + i*180, 120))
        bg.add(sp)
    scene.add(bg)
    director.run( scene )

if __name__ == '__main__':
    main()
