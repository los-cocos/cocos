from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 3.0, s, t 5.0, s, t 10.0, s, q"
tags = "batch, BatchNode, Sprite"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from cocos.actions import MoveBy

# Same as test_batch, but now create 4 groups

class TestBatch(cocos.layer.Layer):
    def __init__(self):
        super( TestBatch, self ).__init__()
        x,y = director.get_window_size()
        self.batchnode = cocos.batch.BatchNode()
        self.batchnode.position = 50,100
        self.add(self.batchnode)
        for i in range(216):
            sprite = Sprite('grossini.png')
            sprite.position = (i//12)*30, (i%12)*25
            self.batchnode.add(sprite, z=i%4)
        self.batchnode.do(MoveBy((100, 100), 10))

def main():
    director.init()
    test_layer = TestBatch ()
    main_scene = cocos.scene.Scene (test_layer)
    director.show_FPS = True
    director.run (main_scene)

if __name__ == '__main__':
    main()
