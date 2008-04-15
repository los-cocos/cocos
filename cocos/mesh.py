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
        self._active = False
        self.mesh_mode = GRID_MODE

    def init( self, x_quads=4, y_quads=4 ):
        
        self.x_quads = x_quads
        self.y_quads = y_quads
        
        
        x,y = director.window.width, director.window.height

        if self.texture is None:
            self.texture = image.Texture.create_for_size(
                    GL_TEXTURE_2D, x, 
                    y, GL_RGB)
        
        self.grabber = framegrabber.TextureGrabber()
        self.grabber.grab(self.texture)

        # calculate vertex, textures depending on screen size
        idx_pts, ver_pts_idx, tex_pts_idx, ver_pts, tex_pts = self._calculate_vertex_points(x,y)

        # Generates a grid of joint quads
        self.vertex_list_idx = pyglet.graphics.vertex_list_indexed((x_quads+1)*(y_quads+1), 
                            idx_pts, "t2f", "v2i/stream")
        self.vertex_points_idx = ver_pts_idx[:]
        self.vertex_list_idx.vertices = ver_pts_idx
        self.vertex_list_idx.tex_coords = tex_pts_idx
 
       # Generates a grid of independent quads (think of tiles)
        self.vertex_list = pyglet.graphics.vertex_list(x_quads*y_quads*4,
                            "t2f", "v2i/stream")
        self.vertex_points = ver_pts[:]
        self.vertex_list.vertices = ver_pts
        self.vertex_list.tex_coords = tex_pts


    def _calculate_vertex_points(self, x, y):        
        self.x_step = x / self.x_quads
        self.y_step = y / self.y_quads

        w = float(self.texture.width)
        h = float(self.texture.height)

        index_points = []
        vertex_points_idx = []
        texture_points_idx = []
        vertex_points = []
        texture_points = []

        for x in range(0,self.x_quads+1):
            for y in range(0,self.y_quads+1):
                vertex_points_idx += [-1,-1]
                texture_points_idx += [-1,-1]

        for x in range(0, self.x_quads):
            for y in range(0, self.y_quads):
                x1 = x*self.x_step 
                x2 = x1 + self.x_step
                y1 = y* self.y_step
                y2 = y1 + self.y_step
              

                #  d <-- c
                #        ^
                #        |
                #  a --> b 
                a = x * (self.x_quads+1) + y
                b = (x+1) * (self.x_quads+1) + y
                c = (x+1) * (self.x_quads+1) + (y+1)
                d = x * (self.x_quads+1) + (y+1)

#                index_points += [ a, b, c, a, c, d]    # triangles 
                index_points += [ a, b, c, d]           # or quads ?

                l1 = ( a*2, b*2, c*2, d*2 )
                l2 = ( (x1,y1), (x2,y1), (x2,y2), (x1,y2) )

                # Mesh Grid vertex and texture points
                for i in range( len(l1) ):
                    vertex_points_idx[ l1[i] ] = l2[i][0]
                    vertex_points_idx[ l1[i] + 1 ] = l2[i][1]

                    texture_points_idx[ l1[i] ] = l2[i][0] / w
                    texture_points_idx[ l1[i] + 1 ] = l2[i][1] / h

                # Mesh Tiles vertex and texture points
                vertex_points += [x1, y1, x2, y1, x2, y2, x1, y2]
                texture_points += [x1/w, y1/h, x2/w, y1/h, x2/w, y2/h, x1/w, y2/h]

        # Generates a quad for each tile, to perform tiles effect
        return ( index_points, vertex_points_idx, texture_points_idx, vertex_points, texture_points)

        # Generates a grid... must faster, for effects that doesn't split the
        # grid in tiles
        
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

    def on_resize(self, w, h):
        '''on_resize handler. Don't return 'True' since this event
        shall be propagated to all the meshes
        '''
        if not self.active:
            return
        
        if director.window.width > self.texture.width or director.window.height > self.texture.height:
            self.texture = image.Texture.create_for_size(
                    GL_TEXTURE_2D, director.window.width, 
                    director.window.height, GL_RGB)
            self.grabber = framegrabber.TextureGrabber()
            self.grabber.grab(self.texture)
        
        txz = director._offset_x/float(self.texture.width)
        tyz = director._offset_y/float(self.texture.height)
        
        rx = director.window.width - 2*director._offset_x
        ry = director.window.height - 2*director._offset_y
        
        tx = float(rx)/self.texture.width+txz
        ty = float(ry)/self.texture.height+tyz
        
        xsteps = (tx-txz) / self.x_quads
        ysteps = (ty-tyz) / self.y_quads

        if self.mesh_mode == GRID_MODE:
            tex_idx = [] 
            for x in range(self.x_quads+1):
                for y in range(self.y_quads+1):
                    tex_idx += [ txz + x*xsteps, tyz+y*ysteps]
            self.vertex_list_idx.tex_coords = tex_idx

        elif self.mesh_mode == TILES_MODE:
            tex = []
            for x in range(self.x_quads):
                for y in range(self.y_quads):
                    ax = txz + x*xsteps
                    ay = tyz + y*ysteps
                    bx = txz + (x+1)*xsteps
                    by = tyz + (y+1)*ysteps
                    tex += [ ax, ay, bx, ay, bx, by, ax, by]    
            self.vertex_list.tex_coords = tex       
        
        else:
            raise Exception("Invalid grid mode")

    def _set_active(self, bool):
        if self._active == bool:
            return
        self._active = bool
        if self._active == True:
            self._handlers = director.push_handlers(self.on_resize)
        elif self._active == False:
            director.pop_handlers()
        else:
            raise Exception("Invalid value for Mesh.active")
                                        
    def _get_active(self):
        return self._active

    active = property(_get_active, _set_active,
                      doc='''Determines if the mesh is active or not                 
                     :type: bool
                     ''')       