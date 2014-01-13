from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "dt 0.016, s, f 20 0.016, s, f 20 0.016, s, f 20 0.016, s, q"
tags = "vertex_list"

import pyglet
from pyglet.gl import *
import math

def sign(x): return 1 if x >= 0 else -1

class MeshSprite:
    def __init__(self, image, x_quads, y_quads):
        x_step = image.width // (x_quads)
        y_step = image.height // (y_quads)
        self.image = image
        self.texture = image.get_texture()

        w = image.width / self.texture.tex_coords[3]
        h = image.height / self.texture.tex_coords[7]
        vertex_points = []
        texture_points = []
        for x in range(0, x_quads):
            for y in range(0, y_quads):
                x1 = x*x_step
                x2 = x1 + x_step
                y1 = y*y_step
                y2 = y1 + y_step

                vertex_points += [x1, y1, x2, y1, x2, y2, x1, y2]
                texture_points += [x1/w, y1/h, x2/w, y1/h, x2/w, y2/h, x1/w, y2/h]


        self.vertex_list = pyglet.graphics.vertex_list(x_quads*y_quads*4, "t2f", "v2i/stream")
        self.vertex_points = vertex_points[:]
        self.vertex_list.vertices = vertex_points
        self.vertex_list.tex_coords = texture_points
        self.elapsed = 0

    def draw(self, dt):
        self.elapsed += dt
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for p in range(len(self.vertex_points)//2):
            x = self.vertex_points[2*p]
            y = self.vertex_points[2*p+1]
            if 0:
                scale = abs(math.cos ( x/(y+0.5) + self.elapsed ) ) + 1
                x = (x-25) * scale + 25
                y = (y-50) * scale + 50
            else:
                center = (2+self.elapsed)**4
                disttoc = math.sqrt( (x-25)**2 + (y-50)**2 ) - center
                scale = min(1/abs(disttoc), 1)*10

                x = x + sign(x-25) * scale
                y = y + sign(y-50) * scale
            self.vertex_list.vertices[2*p] = 200+int(x)
            self.vertex_list.vertices[2*p+1] = 200+int(y)

        self.vertex_list.draw(pyglet.gl.GL_QUADS)
        glPopAttrib()
        glDisable(self.texture.target)

description = """
A prof of concept: using pyglet vertex lists to deform a sprite.
The entity is not a CocosNode, and some details should be adjusted: by
example at rest the top of grossini sprite is not visible.
"""

def main():
    print(description)
    window = pyglet.window.Window()

    grossini = pyglet.resource.image("grossini.png")
    grossini.anchor_x = grossini.width // 2
    grossini.anchor_y = grossini.height // 2
    ms = MeshSprite( grossini, 15,31 )
    def update(dt):
        window.clear()
        ms.draw(dt)

    pyglet.clock.schedule(update)

    @window.event
    def on_key_press(key, mods):
        ms.elapsed = 0

    pyglet.app.run()

if __name__ == '__main__':
    main()
