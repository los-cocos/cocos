#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
'''Mesh effects'''

import pyglet
from pyglet import image
from pyglet.gl import *

from director import director
import framegrabber

__all__ = ['Mesh', ]

class Mesh(object):
    """
    A Scene that takes two scenes and makes a transition between them
    """
    texture = None
    
    def __init__(self, x_quads=4, y_quads=4):

        super(Mesh, self).__init__()

        x = director.window.width
        y = director.window.height

        if self.texture is None:
            Mesh.texture = image.Texture.create_for_size(
                    GL_TEXTURE_2D, x, 
                    y, GL_RGB)
        
        self.grabber = framegrabber.TextureGrabber()
        self.grabber.grab(self.texture)
        self.active = False

        x_step = x / (x_quads)
        y_step = y / (y_quads)

        w = float(x)/self.texture.tex_coords[3]
        h = float(y)/self.texture.tex_coords[7]

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

    def before_draw( self ):
        # capture before drawing
        self.grabber.before_render(self.texture)


    def after_draw( self ):
        # capture after drawing
        self.grabber.after_render(self.texture)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.blit()

    def blit(self ):

        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.vertex_list.draw(pyglet.gl.GL_QUADS)

        glPopAttrib()
        glDisable(self.texture.target)
