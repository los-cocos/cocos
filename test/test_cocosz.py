from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "Quad"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.gl import *

class Quad(cocos.cocosnode.CocosNode):
    def __init__(self, color, size):
        super(Quad, self).__init__()
        self.size = size
        self.qcolor = color

    def draw(self):
        points = (self.x, self.y,
                    self.x, self.y+self.size,
                    self.x+self.size, self.y+self.size,
                    self.x + self.size, self.y )
        color = self.qcolor * 4

        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
            ('v2i', points),
            ('c4B', color)
        )

class MultiQuadLayer(cocos.layer.Layer):
    def __init__(self):
        super(MultiQuadLayer, self).__init__()
        x, y = director.get_window_size()
        main = Quad((0,255,0,128), 200)
        for i in range(5):
            q = Quad((255,0,0,255), 30)
            q.position = (15*i, 15*i)
            main.add( q, z= i-2)
        main.position = ( x//2, y//2 )
        self.add( main )

def main():
    director.init()
    test_layer = MultiQuadLayer()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
