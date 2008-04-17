#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
'''Mesh effects'''

import pyglet
from pyglet import image
from pyglet.gl import *
from euclid import Point2, Point3

from director import director
import framegrabber

__all__ = ['Mesh',
            'MeshGrid', 'MeshTiles', 'Mesh3DGrid',
            ]

class Mesh(object):
    """
    A Scene that takes two scenes and makes a transition between them
    """
    texture = None
    
    def __init__(self):
        super(Mesh, self).__init__()
        self._active = False

    def init( self, grid ):
        '''Initializes the grid creating both a vertex_list for an independent-tiled grid
        and creating also a vertex_list_indexed for a "united" (non independent tile) grid.

        :Parameters:
            `grid` : euclid.Point2
                size of a 2D grid
        '''
      
        self.grid = grid
        
        x,y = director.window.width, director.window.height

        if self.texture is None:
            self.texture = image.Texture.create_for_size(
                    GL_TEXTURE_2D, x, 
                    y, GL_RGB)
        
        self.grabber = framegrabber.TextureGrabber()
        self.grabber.grab(self.texture)

        self.x_step = x / self.grid.x
        self.y_step = y / self.grid.y

        self._init()

        
    def before_draw( self ):
        # capture before drawing
        self.grabber.before_render(self.texture)


    def after_draw( self ):
        # capture after drawing
        self.grabber.after_render(self.texture)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # blit
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        self._blit()       
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
        
        xsteps = (tx-txz) / self.grid.x
        ysteps = (ty-tyz) / self.grid.y

        self._on_resize( xsteps, ysteps, txz, tyz)


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
    def _init(self):
        raise NotImplementedError('abstract')
        
    def _blit(self):
        raise NotImplementedError('abstract')

    def _on_resize(self):
        raise NotImplementedError('abstract')
  

class MeshGrid(Mesh):
    '''A Mesh that implements an union grid. Each vertex is shared by the attached quads'''
    def _init( self ):
        # calculate vertex, textures depending on screen size
        idx_pts, ver_pts_idx, tex_pts_idx = self._calculate_vertex_points()

        # Generates a grid of joint quads
        self.vertex_list = pyglet.graphics.vertex_list_indexed( (self.grid.x+1) * (self.grid.y+1), 
                            idx_pts, "t2f", "v2i/stream","c4B")
        self.vertex_points = ver_pts_idx[:]
        self.vertex_list.vertices = ver_pts_idx
        self.vertex_list.tex_coords = tex_pts_idx
        self.vertex_list.colors = (255,255,255,255) * (self.grid.x+1) * (self.grid.y+1)
 
    def _blit(self ):
        self.vertex_list.draw(pyglet.gl.GL_TRIANGLES)

    def _on_resize(self, xsteps, ysteps, txz, tyz):
        tex_idx = [] 
        for x in range(self.grid.x+1):
            for y in range(self.grid.y+1):
                tex_idx += [ txz + x*xsteps, tyz+y*ysteps]
        self.vertex_list.tex_coords = tex_idx
    
    def _calculate_vertex_points(self):        
        w = float(self.texture.width)
        h = float(self.texture.height)

        index_points = []
        vertex_points_idx = []
        texture_points_idx = []

        for x in range(0,self.grid.x+1):
            for y in range(0,self.grid.y+1):
                vertex_points_idx += [-1,-1]
                texture_points_idx += [-1,-1]

        for x in range(0, self.grid.x):
            for y in range(0, self.grid.y):
                x1 = x * self.x_step 
                x2 = x1 + self.x_step
                y1 = y * self.y_step
                y2 = y1 + self.y_step
              
                #  d <-- c
                #        ^
                #        |
                #  a --> b 
                a = x * (self.grid.y+1) + y
                b = (x+1) * (self.grid.y+1) + y
                c = (x+1) * (self.grid.y+1) + (y+1)
                d = x * (self.grid.y+1) + (y+1)

                # 2 triangles: a-b-d, b-c-d
                index_points += [ a, b, d, b, c, d]    # triangles 

                l1 = ( a*2, b*2, c*2, d*2 )
                l2 = ( Point2(x1,y1), Point2(x2,y1), Point2(x2,y2), Point2(x1,y2) )

                # Mesh Grid vertex and texture points
                for i in range( len(l1) ):
                    vertex_points_idx[ l1[i] ] = l2[i].x
                    vertex_points_idx[ l1[i] + 1 ] = l2[i].y

                    texture_points_idx[ l1[i] ] = l2[i].x / w
                    texture_points_idx[ l1[i] + 1 ] = l2[i].y / h

        return ( index_points, vertex_points_idx, texture_points_idx )

class MeshTiles(Mesh):
    '''A Mesh that is implemented with the union of several tiles.
    The vertex are not shared between the different tiles. Each tile has it's own
    4 vertex.
    '''
    def _init( self ):
        # calculate vertex, textures depending on screen size
        ver_pts, tex_pts = self._calculate_vertex_points()

       # Generates a grid of independent quads (think of tiles)
        self.vertex_list = pyglet.graphics.vertex_list(self.grid.x * self.grid.y * 4,
                            "t2f", "v2i/stream","c4B")
        self.vertex_points = ver_pts[:]
        self.vertex_list.vertices = ver_pts
        self.vertex_list.tex_coords = tex_pts
        self.vertex_list.colors = (255,255,255,255) * self.grid.x * self.grid.y * 4  

    def _blit(self):
        self.vertex_list.draw(pyglet.gl.GL_QUADS)

    def _on_resize(self, xsteps, ysteps, txz, tyz):
        tex = []
        for x in range(self.grid.x):
            for y in range(self.grid.y):
                ax = txz + x*xsteps
                ay = tyz + y*ysteps
                bx = txz + (x+1)*xsteps
                by = tyz + (y+1)*ysteps
                tex += [ ax, ay, bx, ay, bx, by, ax, by]    
        self.vertex_list.tex_coords = tex     
        
    def _calculate_vertex_points(self):
        w = float(self.texture.width)
        h = float(self.texture.height)

        vertex_points = []
        texture_points = []

        for x in range(0, self.grid.x):
            for y in range(0, self.grid.y):
                x1 = x * self.x_step 
                x2 = x1 + self.x_step
                y1 = y * self.y_step
                y2 = y1 + self.y_step
              
                # Mesh Tiles vertex and texture points
                vertex_points += [x1, y1, x2, y1, x2, y2, x1, y2]
                texture_points += [x1/w, y1/h, x2/w, y1/h, x2/w, y2/h, x1/w, y2/h]

        # Generates a quad for each tile, to perform tiles effect
        return (vertex_points, texture_points)

class Mesh3DGrid(Mesh):
    '''A Mesh that implements a 3D grid. Each vertex is shared by the attached quads and has 3 dimensions'''
    def _init( self ):
        # calculate vertex, textures depending on screen size
        idx_pts, ver_pts_idx, tex_pts_idx = self._calculate_vertex_points()

        # Generates a grid of joint quads
        self.vertex_list = pyglet.graphics.vertex_list_indexed( (self.grid.x+1) * (self.grid.y+1), 
                            idx_pts, "t3f", "v3i/stream","c4B")
        self.vertex_points = ver_pts_idx[:]
        self.vertex_list.vertices = ver_pts_idx
        self.vertex_list.tex_coords = tex_pts_idx
        self.vertex_list.colors = (255,255,255,255) * (self.grid.x+1) * (self.grid.y+1)
 
    def _blit(self ):
        self.vertex_list.draw(pyglet.gl.GL_TRIANGLES)

    def _on_resize(self, xsteps, ysteps, txz, tyz):
        tex_idx = [] 
        for x in range(self.grid.x+1):
            for y in range(self.grid.y+1):
                tex_idx += [ txz + x*xsteps, tyz+y*ysteps, 0]
        self.vertex_list.tex_coords = tex_idx
    
    def _calculate_vertex_points(self):        
        w = float(self.texture.width)
        h = float(self.texture.height)

        index_points = []
        vertex_points_idx = []
        texture_points_idx = []

        for x in range(0,self.grid.x+1):
            for y in range(0,self.grid.y+1):
                vertex_points_idx += [-1,-1,-1]
                texture_points_idx += [-1,-1,-1]

        for x in range(0, self.grid.x):
            for y in range(0, self.grid.y):
                x1 = x * self.x_step 
                x2 = x1 + self.x_step
                y1 = y * self.y_step
                y2 = y1 + self.y_step
              
                #  d <-- c
                #        ^
                #        |
                #  a --> b 
                a = x * (self.grid.y+1) + y
                b = (x+1) * (self.grid.y+1) + y
                c = (x+1) * (self.grid.y+1) + (y+1)
                d = x * (self.grid.y+1) + (y+1)

                # 2 triangles: a-b-d, b-c-d
                index_points += [ a, b, d, b, c, d]    # triangles 

                l1 = ( a*3, b*3, c*3, d*3 )
                l2 = ( Point3(x1,y1,0), Point3(x2,y1,0), Point3(x2,y2,0), Point3(x1,y2,0) )

                # Mesh Grid vertex and texture points
                for i in range( len(l1) ):
                    vertex_points_idx[ l1[i] ] = l2[i].x
                    vertex_points_idx[ l1[i] + 1 ] = l2[i].y
                    vertex_points_idx[ l1[i] + 2 ] = l2[i].z

                    texture_points_idx[ l1[i] ] = l2[i].x / w
                    texture_points_idx[ l1[i] + 1 ] = l2[i].y / h
                    texture_points_idx[ l1[i] + 2 ] = 0

        return ( index_points, vertex_points_idx, texture_points_idx )
    