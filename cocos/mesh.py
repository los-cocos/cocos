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

__all__ = ['Mesh',
            'TILES_MODE', 'GRID_MODE', ]

TILES_MODE = "tiles"
GRID_MODE = "grid"

class Mesh(object):
    """
    A Scene that takes two scenes and makes a transition between them
    """
    texture = None
    
    def __init__(self):
        super(Mesh, self).__init__()
        self.active = False
        self.mesh_mode = "grid"

    def init( self, x_quads=4, y_quads=4 ):

        x = director.window.width
        y = director.window.height

        self.x_quads = x_quads
        self.y_quads = y_quads

        if self.texture is None:
            self.texture = image.Texture.create_for_size(
                    GL_TEXTURE_2D, x, 
                    y, GL_RGB)
        
        self.grabber = framegrabber.TextureGrabber()
        self.grabber.grab(self.texture)

        x_step = x / (x_quads)
        y_step = y / (y_quads)

#        w = float(x)/self.texture.tex_coords[3]
#        h = float(y)/self.texture.tex_coords[7]

        w = float(self.texture.width)
        h = float(self.texture.height)

        vertex_points = []
        vertex_points_idx = []
        texture_points_idx = []
        texture_points = []
        index_points = []

        for x in range(0,x_quads+1):
            for y in range(0,y_quads+1):
                vertex_points_idx += [-1,-1]
                texture_points_idx += [-1,-1]

        for x in range(0, x_quads):
            for y in range(0, y_quads):
                x1 = x*x_step 
                x2 = x1 + x_step
                y1 = y*y_step
                y2 = y1 + y_step
              

                #  d <-- c
                #        ^
                #        |
                #  a --> b 
                a = x * (x_quads+1) + y
                b = (x+1) * (x_quads+1) + y
                c = (x+1) * (x_quads+1) + (y+1)
                d = x * (x_quads+1) + (y+1)

#                index_points += [ a, b, c, a, c, d]    # triangles 
                index_points += [ a, b, c, d]           # or quads ?

                l1 = ( a*2, b*2, c*2, d*2 )
                l2 = ( (x1,y1), (x2,y1), (x2,y2), (x1,y2) )

                for i in range( len(l1) ):
                    vertex_points_idx[ l1[i] ] = l2[i][0]
                    vertex_points_idx[ l1[i] + 1 ] = l2[i][1]

                    texture_points_idx[ l1[i] ] = l2[i][0] / w
                    texture_points_idx[ l1[i] + 1 ] = l2[i][1] / h

                vertex_points += [x1, y1, x2, y1, x2, y2, x1, y2]
                texture_points += [x1/w, y1/h, x2/w, y1/h, x2/w, y2/h, x1/w, y2/h]

        # Generates a quad for each tile, to perform tiles effect
        self.vertex_list = pyglet.graphics.vertex_list(x_quads*y_quads*4, "t2f", "v2i/stream")
        self.vertex_points = vertex_points[:]
        self.vertex_list.vertices = vertex_points
        self.vertex_list.tex_coords = texture_points

        # Generates a grid... must faster, for effects that doesn't split the
        # grid in tiles
        self.vertex_list_idx = pyglet.graphics.vertex_list_indexed((x_quads+1)*(y_quads+1), index_points, "t2f", "v2i/stream")
        self.vertex_points_idx = vertex_points_idx[:]
        self.vertex_list_idx.vertices = vertex_points_idx
        self.vertex_list_idx.tex_coords = texture_points_idx

    def before_draw( self ):
        # capture before drawing
        self.grabber.before_render(self.texture)


    def after_draw( self ):
        # capture after drawingg
        self.grabber.after_render(self.texture)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.blit()

    def blit(self ):
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)

        if self.mesh_mode == TILES_MODE: 
            self.vertex_list.draw(pyglet.gl.GL_QUADS)
        elif self.mesh_mode == GRID_MODE:
            self.vertex_list_idx.draw(pyglet.gl.GL_QUADS)
#            self.vertex_list_idx.draw(pyglet.gl.GL_TRIANGLES)
        else:
            raise Exception("Invalid Mesh mode")

        glPopAttrib()
        glDisable(self.texture.target)
