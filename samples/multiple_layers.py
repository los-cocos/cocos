#
# cocos2d
# http://python.cocos2d.org
#
# This code is so you can run the samples without installing the package

from __future__ import division, print_function, unicode_literals

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


import cocos
from cocos.director import director

from pyglet import gl


# Defining a new layer type...

class Square(cocos.layer.Layer):

    """Square (color, c, y, size=50) : A layer drawing a square at (x,y) of
    given color and size"""

    def __init__(self, color, x, y, size=50):
        super(Square, self).__init__()

        self.x = x
        self.y = y
        self.size = size
        self.layer_color = color

    def draw(self):
        super(Square, self).draw()

        gl.glColor4f(*self.layer_color)
        x, y = self.x, self.y
        w = x + self.size
        h = y + self.size
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(x, y)
        gl.glVertex2f(x, h)
        gl.glVertex2f(w, h)
        gl.glVertex2f(w, y)
        gl.glEnd()
        gl.glColor4f(1, 1, 1, 1)

if __name__ == "__main__":
    director.init()
    # Create a large number of layers
    layers = [Square((0.03 * i, 0.03 * i, 0.03 * i, 1), i * 20, i * 20) for i in range(5, 20)]
    # Create a scene with all those layers
    sc = cocos.scene.Scene(*layers)
    # You can also add layers to a scene later:
    sc.add(Square((1, 0, 0, 0.5), 150, 150, 210), name="big_one")
    director.run(sc)
