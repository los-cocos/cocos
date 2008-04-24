#
# Cocos
# http://code.google.com/p/los-cocos/
#
'''Grid effects'''

import pyglet
from pyglet import image
from pyglet.gl import *
from euclid import Point2, Point3

from director import director
import framegrabber

__all__ = ['GridBase',
            'Grid', 'TiledGrid', 'Grid3D',
            ]

class GridBase(object):
    """
    A Scene that takes two scenes and makes a transition between them
    """
    texture = None
    
    def __init__(self):
        super(GridBase, self).__init__()
        self._active = False
        self.reuse_grid = 0     #! Number of times that this grid will be reused

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

        # blit
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA8, self.texture.width, self.texture.height , 0, GL_RGBA, GL_UNSIGNED_BYTE, 0 )

        glPushAttrib(GL_COLOR_BUFFER_BIT)

        self._blit()
               
        glPopAttrib()
        glDisable(self.texture.target)

    def on_resize(self, w, h):
        '''on_resize handler. Don't return 'True' since this event
        shall be propagated to all the grids
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
            self.vertex_list.delete()
            director.pop_handlers()
        else:
            raise Exception("Invalid value for GridBase.active")
                                        
    def _get_active(self):
        return self._active

    active = property(_get_active, _set_active,
                      doc='''Determines whether the grid is active or not                 
                     :type: bool
                     ''')       
    def _init(self):
        raise NotImplementedError('abstract')
        
    def _blit(self):
        raise NotImplementedError('abstract')

    def _on_resize(self):
        raise NotImplementedError('abstract')
  

class Grid(GridBase):
    '''`Grid` is a 2D grid implementation.
    
    The vertex array will be built with::

        self.vertex_list.vertices: x,y (ints)   
        self.vertex_list.tex_coords: x,y (floats)
        self.vertex_list.colors: RGBA, with values from 0 - 255
    '''
    def _init( self ):
        # calculate vertex, textures depending on screen size
        idx_pts, ver_pts_idx, tex_pts_idx = self._calculate_vertex_points()

        # Generates a grid of joint quads
        self.vertex_list = pyglet.graphics.vertex_list_indexed( (self.grid.x+1) * (self.grid.y+1), 
                            idx_pts, "t2f", "v2i/stream")
        self.vertex_points = ver_pts_idx[:]
        self.vertex_list.vertices = ver_pts_idx
        self.vertex_list.tex_coords = tex_pts_idx
#        self.vertex_list.colors = (255,255,255,255) * (self.grid.x+1) * (self.grid.y+1)
 
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

                # building the vertex and texture points
                for i in range( len(l1) ):
                    vertex_points_idx[ l1[i] ] = l2[i].x
                    vertex_points_idx[ l1[i] + 1 ] = l2[i].y

                    texture_points_idx[ l1[i] ] = l2[i].x / w
                    texture_points_idx[ l1[i] + 1 ] = l2[i].y / h

        return ( index_points, vertex_points_idx, texture_points_idx )

class TiledGrid(GridBase):
    '''`TiledGrid` is a 2D grid implementation. It differs from `Grid` in that
    the tiles can be separated from the grid. 

    The vertex array will be built with::

        self.vertex_list.vertices: x,y (ints)   
        self.vertex_list.tex_coords: x,y (floats)
        self.vertex_list.colors: RGBA, with values from 0 - 255
    '''
    def _init( self ):
        # calculate vertex, textures depending on screen size
        ver_pts, tex_pts = self._calculate_vertex_points()

       # Generates a grid of independent quads (think of tiles)
        self.vertex_list = pyglet.graphics.vertex_list(self.grid.x * self.grid.y * 4,
                            "t2f", "v2i/stream")
        self.vertex_points = ver_pts[:]
        self.vertex_list.vertices = ver_pts
        self.vertex_list.tex_coords = tex_pts
#        self.vertex_list.colors = (255,255,255,255) * self.grid.x * self.grid.y * 4  

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
              
                # Building the tiles' vertex and texture points
                vertex_points += [x1, y1, x2, y1, x2, y2, x1, y2]
                texture_points += [x1/w, y1/h, x2/w, y1/h, x2/w, y2/h, x1/w, y2/h]

        # Generates a quad for each tile, to perform tiles effect
        return (vertex_points, texture_points)

class Grid3D(GridBase):
    '''`Grid3D` is a 3D grid implementation. Each vertex has 3 dimensions: x,y,z
    
    The vertex array will be built with::

        self.vertex_list.vertices: x,y,z (floats)   
        self.vertex_list.tex_coords: x,y,z (floats)
        self.vertex_list.colors: RGBA, with values from 0 - 255
    '''

    def _init( self ):
        # calculate vertex, textures depending on screen size
        idx_pts, ver_pts_idx, tex_pts_idx = self._calculate_vertex_points()

        # Generates a grid of joint quads
        self.vertex_list = pyglet.graphics.vertex_list_indexed( (self.grid.x+1) * (self.grid.y+1), 
                            idx_pts, "t2f", "v3f/stream")
        self.vertex_points = ver_pts_idx[:]
        self.vertex_list.vertices = ver_pts_idx
        self.vertex_list.tex_coords = tex_pts_idx
#        self.vertex_list.colors = (255,255,255,255) * (self.grid.x+1) * (self.grid.y+1)
 
    def _blit(self ):

        # go to 3D
        self._set_3d_projection()

        # center the image
        glLoadIdentity()
        width, height = director.get_window_size()
        gluLookAt( width // 2, height // 2, 240.0,   # eye
                   width // 2, height // 2, 0.0,   # center
                   0.0, 1.0, 0.0    # up
                   )
       
       # blit
        self.vertex_list.draw(pyglet.gl.GL_TRIANGLES)

        # go back to 2D
        glLoadIdentity()
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -100, 100)
        glMatrixMode(GL_MODELVIEW)


    def _on_resize(self, xsteps, ysteps, txz, tyz):
        tex_idx = [] 
        for x in range(self.grid.x+1):
            for y in range(self.grid.y+1):
                tex_idx += [ txz + x*xsteps, tyz+y*ysteps]
        self.vertex_list.tex_coords = tex_idx

        self._set_3d_projection()

    def _set_3d_projection(self):
        width, height = director.window.width, director.window.height
#        width, height = director.get_window_size()

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, 1.0*width/height, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    
    def _calculate_vertex_points(self):        
        w = float(self.texture.width)
        h = float(self.texture.height)

        index_points = []
        vertex_points_idx = []
        texture_points_idx = []

        for x in range(0,self.grid.x+1):
            for y in range(0,self.grid.y+1):
                vertex_points_idx += [-1,-1,-1]
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

                l1 = ( a*3, b*3, c*3, d*3 )
                l2 = ( Point3(x1,y1,0), Point3(x2,y1,0), Point3(x2,y2,0), Point3(x1,y2,0) )

                #  building the vertex
                for i in range( len(l1) ):
                    vertex_points_idx[ l1[i] ] = l2[i].x
                    vertex_points_idx[ l1[i] + 1 ] = l2[i].y
                    vertex_points_idx[ l1[i] + 2 ] = l2[i].z

                # building the texels
                tex1 = ( a*2, b*2, c*2, d*2 )
                tex2 = ( Point2(x1,y1), Point2(x2,y1), Point2(x2,y2), Point2(x1,y2) )

                for i in range( len(tex1)):
                    texture_points_idx[ tex1[i] ] = tex2[i].x / w
                    texture_points_idx[ tex1[i] + 1 ] = tex2[i].y / h
 
        return ( index_points, vertex_points_idx, texture_points_idx )
