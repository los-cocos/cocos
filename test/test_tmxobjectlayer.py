from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "TMX, tiles, TmxObjectLayer"

import pyglet
from pyglet.window import key
from pyglet.gl import glClearColor
pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layer

description = """
Loads a tmx map containing a tile layer and an object layer.
The tiles layer is rendered as black region with four green dots.

The debug view of the TmxObjectLayer is draw over that, with four objects
of type 'rect', 'ellipse', 'polygon', 'polyline'

The debug view only draws the Axis Aligned Bounding Box of each object.

You should see four green points covered by translucid white-ish rectangles,
roughly centered at each point. 
"""

def main():
    from cocos.director import director
    director.init(width=800, height=600, autoscale=False, resizable=True)
    glClearColor(255, 255, 255, 255)

    scroller = layer.ScrollingManager()
    maploaded = tiles.load('obj.tmx')
    test_layer = maploaded["tiles_layer_1"]
    scroller.add(test_layer)
    object_layer = maploaded['test_object_layer']
    scroller.add(object_layer)
    main_scene = cocos.scene.Scene(scroller)
    print(test_layer.px_width , test_layer.px_height)
    scroller.set_focus(test_layer.px_width // 2, test_layer.px_height //2)

    director.run(main_scene)

if __name__ == '__main__':
    print(description)
    main()
