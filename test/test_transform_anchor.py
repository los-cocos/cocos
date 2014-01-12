from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.25, s, t 3, s, t 5, s, q"
tags = "CocosNode, transform_anchor"

import cocos
from cocos.director import director
import cocos.actions as ac
from cocos.layer import *

description = """
Demostrates:
    CocosNode transform_anchor role (defines point to rotate around / zoom in
    or out)

You should see:
    Two squares performing the same action; they only differ in the
    transform_anchor value

    bluish square alternates between still, rotating around his own center,
    zooming in and out with focus on his own center

    redish square alternates between still, rotating around his bottom left
    corner, zooming in and out with focus on his bottom left corner.
"""

def get_test_scene():
    template_action = ac.Repeat( # repeat forever (
                         ac.Delay(1.0) # wait 1 second
                         + # and then
                         ac.Rotate(360, 2.0) # rotate 360 degrees in 2 seconds
                         + # and then
                         ac.Delay(1.0) # wait 1 second
                         + # and then
                         ac.ScaleTo(2.0, 1.0) #  zoom to 2x in 1 second
                         + # and then
                         ac.ScaleTo(1.0, 1.0)  # zoom to 1x in 1 second
                         )

    w, h = director.get_window_size()
    world = cocos.layer.Layer()

    # bluish square
    bluish_square = cocos.layer.ColorLayer(0, 160, 176, 255, width=100, height=100)
    # transform_anchor set to the center position of itself
    bluish_square.transform_anchor = (bluish_square.width/2.0, bluish_square.height/2.0)
    bluish_square.position = (w//3, h//2)
    bluish_square.do(template_action)
    world.add(bluish_square, z=2)

    mark_anchor = cocos.layer.ColorLayer(161, 191, 54, 255, width=8, height=8)
    mark_anchor.position = (bluish_square.x + bluish_square.transform_anchor_x,
                            bluish_square.y + bluish_square.transform_anchor_y)
    world.add(mark_anchor, z=3)

    # redish square
    redish_square = cocos.layer.ColorLayer(201, 43, 0, 255, width=100, height=100)
    # transform_anchor set to the bottomleft corner of itself
    redish_square.transform_anchor = (0, 0)
    redish_square.position = (w*2//3, h//2)
    redish_square.do(template_action)
    world.add(redish_square, z=2)

    mark_anchor = cocos.layer.ColorLayer(161, 191, 54, 255, width=8, height=8)
    mark_anchor.position = (redish_square.x + redish_square.transform_anchor_x,
                            redish_square.y + redish_square.transform_anchor_y)
    world.add(mark_anchor, z=3)

    scene = cocos.scene.Scene()
    scene.add(world)
    return scene

def main():
    print(description)
    director.init( resizable=True )
    scene = get_test_scene()
    director.run(scene)

if __name__ == '__main__':
    main()
