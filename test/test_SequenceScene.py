from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 2.1, s, t 4.1, s, t 6.1, s, q"
tags = "SequenceScene, CallFunc"

from cocos.director import director
from cocos.scene import Scene
from cocos.sprite import *
from cocos.utils import SequenceScene
from cocos.text import *
from cocos.layer import *
import cocos.actions as ac

from pyglet import font
from pyglet.window import key

def pop_scene():
    director.pop()

def push_sequence_scene():
    scene_blue = Scene()
    layer_blue = ColorLayer(32,32,255,255)
    scene_blue.add( layer_blue, z=0 )
    scene_blue.do(ac.Delay(2) + ac.CallFunc(pop_scene))

    scene_red = Scene()
    layer_red = ColorLayer(255,32,0,255)
    scene_red.add( layer_red, z=0 )
    scene_red.do(ac.Delay(2) + ac.CallFunc(pop_scene))

    director.push( SequenceScene(scene_blue, scene_red) )

description = """
Uses SequenceSecene to push some scenes in the director stack.
You should see 2 sec Green, 2 sec Blue, 2 sec Red, forever Green
"""

def main():
    print(description)
    director.init( resizable=True, width=640, height=480 )
    scene_green = Scene()
    layer_green = ColorLayer(32,255,0,255)
    scene_green.add(layer_green)
    scene_green.do(ac.Delay(2.0) + ac.CallFunc(push_sequence_scene))
    # pyglet 1.1.4 needs this to timely pump actions 
    pyglet.clock.schedule(lambda dt: None)
    director.run(scene_green)

if __name__ == '__main__':
    main()
