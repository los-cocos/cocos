"""
demo for load and intantiation of levels created with protoeditor

It doens't care to draw a background for simplicity.
Scale is different from the one seen in editor to demostrate how
you define how much of world can be seen on screen; to match the editor
view set the same width, height in both consts['window'] and consts['view']
"""

import sys
import os
import pprint

import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import *

import cocos
from cocos.director import director
import loader as lo

from gamedef import game
import controllers as co

consts = {
    "window": {
        # make sure width/height here is the same as width/height in view
        "width": 640,
        "height": 480,
        "vsync": True,
        "resizable": False
        },
    "view": {
        # how much of world can be seen at every time, in world units
        "width": 640.0, # 400,
        "height": 480.0, # 300
        },
    "controller": {
        "bindings": {
            key.LEFT: 'left',
            key.RIGHT: 'right',
            key.UP: 'up',
            key.DOWN: 'down',
            },
        },
    "world": {
        # tweak later those two
        "collman_dynamic_cell_width": 1.25 * 32,
        "collman_static_cell_width": 65.0,
        # ~ 1.1 * max k for all questions dist(player, other) > k
        "max_proximity_distance": 1.1 * 110.0,
        "player": {
            "max_fastness": 150.0,
            "accel": 400.0,
            },
        "wanderer": {
            "max_wandering_fastness": 100.0,
            "min_wandering_fastness": 80.0,
            "chasing_fastness": 120,
            "start_chase_distance": 60.0,
            "end_chase_distance": 64.0,
            },
        "chained": {
            "max_wandering_fastness": 70.0,
            "min_wandering_fastness": 50.0,
            "chasing_fastness": 150,
            "start_chase_distance": 120.0,
            "end_chase_distance": 128.0,
            },
        },
    }

print __doc__

# ensure we have a context
director.init(**consts["window"])
director.show_FPS = True
# get access to game resources
# tip: don't change the location of starting script relative to gamedir along
# the development
pyglet.resource.reindex()
# uncomment to see which resources can see pyglet
##print '\nresources:'
##pprint.pprint(pyglet.resource._default_loader._index)

# build the scene
scene = cocos.scene.Scene()
scroller = cocos.layer.ScrollingManager()
scene.add(scroller)

wconsts = consts["world"]
bindings = consts["controller"]["bindings"]
controller = co.ButtonsKBDController(bindings)
args = [controller, wconsts]
worldview = lo.load_level('data/levels/level_00.lvl', args)
zoom = 1.0
scroller.scale = zoom * consts['window']['width'] / float(consts['view']['width'])

scroller.add(worldview)

# run the scene
director.run(scene)
