from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "dt 0.1, q"
tags = "actions"

import cocos
from cocos.director import director
from cocos.actions import  *
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):

    def _step( self, dt ):
        super(TestLayer,self)._step(dt)
        print('shall not happen')
        print(self.rotation)

description = """
If a node is not in the active scene, will not perfom any action.
No output should be seen on console.
"""

def main():
    print(description)
    director.init()
    test_layer = TestLayer ()
    # note test_layer is NOT in the scene
    main_scene = cocos.scene.Scene()
    test_layer.do( RotateBy(360, duration=2) )
    director.run (main_scene)

if __name__ == '__main__':
    main()
