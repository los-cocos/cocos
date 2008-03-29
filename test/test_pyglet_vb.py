import pyglet
from pyglet.gl import *
# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#
import math

class MeshSprite:
    def __init__(self, image, x_quads, y_quads):
        x_step = image.width / (x_quads)
        y_step = image.height / (y_quads)
        self.image = image
        self.texture = image.get_texture()

        w = float(image.width)/self.texture.tex_coords[3]
        h = float(image.height)/self.texture.tex_coords[7]
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
        
    def on_draw(self, dt):
        self.elapsed += dt
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for p in range(len(self.vertex_points)/2):
            x = self.vertex_points[2*p]
            y = self.vertex_points[2*p+1]
            scale = abs(math.cos ( float(x)/(y+0.5) + self.elapsed ) ) + 1
            x = (x-25) * scale + 25
            y = (y-50) * scale + 50
            self.vertex_list.vertices[2*p] = 200+int(x)
            self.vertex_list.vertices[2*p+1] = 200+int(y)

        self.vertex_list.draw(pyglet.gl.GL_QUADS)
        glPopAttrib()
        glDisable(self.texture.target)
        
        
window = pyglet.window.Window()

grossini = pyglet.resource.image("grossini.png")
grossini.anchor_x = grossini.width / 2
grossini.anchor_y = grossini.height / 2
ms = MeshSprite( grossini, 5,5 )
def update(dt):
    window.clear()
    ms.on_draw(dt)
    
pyglet.clock.schedule_interval(update, 1/60.)

@window.event
def on_draw():
    pass
    
pyglet.app.run()