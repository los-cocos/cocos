# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2015  Richard Jones, Claudio Canepa
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
"""Grid data structure"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import pyglet
from pyglet import image
from pyglet import gl

from cocos.euclid import Point2, Point3
from cocos.director import director
from cocos import framegrabber

__all__ = ['GridBase',
           'Grid3D',
           'TiledGrid3D', ]


class GridBase(object):
    """
    A Scene that takes two scenes and makes a transition between them
    """
    texture = None

    def __init__(self):
        super(GridBase, self).__init__()
        self._active = False
        self.reuse_grid = 0     # ! Number of times that this grid will be reused

    def init(self, grid):
        """Initializes the grid creating both a vertex_list for an independent-tiled grid
        and creating also a vertex_list_indexed for a "united" (non independent tile) grid.

        :Parameters:
            `grid` : euclid.Point2
                size of a 2D grid
        """

        #: size of the grid. (rows, columns)
        self.grid = grid

        width, height = director.get_window_size()

        if self.texture is None:
            self.texture = image.Texture.create_for_size(
                gl.GL_TEXTURE_2D, width,
                height, gl.GL_RGBA)

        self.grabber = framegrabber.TextureGrabber()
        self.grabber.grab(self.texture)

        #: x pixels between each vertex (int)
        self.x_step = width // self.grid.x
        #: y pixels between each vertex (int)
        self.y_step = height // self.grid.y

        self._init()

    def before_draw(self):
        """Binds the framebuffer to a texture
        and set a 2d projection before binding
        to prevent calculating a new texture
        """

        self._set_2d_projection()

        # capture before drawing
        self.grabber.before_render(self.texture)

    def after_draw(self, camera):
        """Called by CocosNode when the texture is already grabbed.
        The FrameBuffer will be unbound and the texture will be drawn

        :Parameters:
            `camera` : `Camera`
                The target's camera object.
        """

        # capture after drawing
        self.grabber.after_render(self.texture)

        # after unbinding
        # set a 3d projection
        self._set_3d_projection()

        # and center the camera
        camera.locate(force=True)

        # blit
        gl.glEnable(self.texture.target)
        gl.glBindTexture(self.texture.target, self.texture.id)

        gl.glPushAttrib(gl.GL_COLOR_BUFFER_BIT)

        self._blit()

        gl.glPopAttrib()
        gl.glDisable(self.texture.target)

    def _set_active(self, bool):
        if self._active == bool:
            return
        self._active = bool
        if self._active is True:
            pass
        elif self._active is False:
            self.vertex_list.delete()
            # to restore the camera to default position
            director.set_projection()
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

    @classmethod
    def _set_3d_projection(cls):
        gl.glViewport(director._offset_x, director._offset_y, director._usable_width, director._usable_height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(60, 1.0 * director._usable_width / director._usable_height, 0.1, 3000.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    @classmethod
    def _set_2d_projection(cls):

        # director.set_2d_projection()
        width, height = director.get_window_size()
        gl.glLoadIdentity()
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, width, 0, height, -100, 100)
        gl.glMatrixMode(gl.GL_MODELVIEW)


class Grid3D(GridBase):
    """`Grid3D` is a 3D grid implementation. Each vertex has 3 dimensions: x,y,z

    The indexed vertex array will be built with::

        self.vertex_list.vertices: x,y,z (floats)
        self.vertex_list.tex_coords: x,y,z (floats)
        self.vertex_list.colors: RGBA, with values from 0 - 255
    """

    def _init(self):
        # calculate vertex, textures depending on screen size
        idx_pts, ver_pts_idx, tex_pts_idx = self._calculate_vertex_points()

        #: indexed vertex array that can be transformed.
        #: it has these attributes:
        #:
        #:    - vertices
        #:    - colors
        #:    - tex_coords
        #:
        #: for more information refer to pyglet's documentation: pyglet.graphics.vertex_list_indexed
        self.vertex_list = pyglet.graphics.vertex_list_indexed((self.grid.x + 1) * (self.grid.y + 1),
                                                               idx_pts, "t2f", "v3f/stream", "c4B")

        #: original vertex array of the grid. (read-only)
        self.vertex_points = ver_pts_idx[:]
        self.vertex_list.vertices = ver_pts_idx
        self.vertex_list.tex_coords = tex_pts_idx
        self.vertex_list.colors = (255, 255, 255, 255) * (self.grid.x + 1) * (self.grid.y + 1)

    def _blit(self):
        self.vertex_list.draw(pyglet.gl.GL_TRIANGLES)

    def _calculate_vertex_points(self):
        w = float(self.texture.width)
        h = float(self.texture.height)

        index_points = []
        vertex_points_idx = []
        texture_points_idx = []

        for x in range(0, self.grid.x + 1):
            for y in range(0, self.grid.y + 1):
                vertex_points_idx += [-1, -1, -1]
                texture_points_idx += [-1, -1]

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
                a = x * (self.grid.y + 1) + y
                b = (x + 1) * (self.grid.y + 1) + y
                c = (x + 1) * (self.grid.y + 1) + (y + 1)
                d = x * (self.grid.y + 1) + (y + 1)

                # 2 triangles: a-b-d, b-c-d
                index_points += [a, b, d, b, c, d]    # triangles

                l1 = (a * 3, b * 3, c * 3, d * 3)
                l2 = (Point3(x1, y1, 0), Point3(x2, y1, 0), Point3(x2, y2, 0), Point3(x1, y2, 0))

                #  building the vertex
                for i in range(len(l1)):
                    vertex_points_idx[l1[i]] = l2[i].x
                    vertex_points_idx[l1[i] + 1] = l2[i].y
                    vertex_points_idx[l1[i] + 2] = l2[i].z

                # building the texels
                tex1 = (a * 2, b * 2, c * 2, d * 2)
                tex2 = (Point2(x1, y1), Point2(x2, y1), Point2(x2, y2), Point2(x1, y2))

                for i in range(len(tex1)):
                    texture_points_idx[tex1[i]] = tex2[i].x / w
                    texture_points_idx[tex1[i] + 1] = tex2[i].y / h

        return index_points, vertex_points_idx, texture_points_idx

    def get_vertex(self, x, y):
        """Get the current vertex coordinate

        :Parameters:
            `x` : int
               x-vertex
            `y` : int
               y-vertex

        :rtype: (float, float, float)
        """
        idx = (x * (self.grid.y + 1) + y) * 3
        x = self.vertex_list.vertices[idx]
        y = self.vertex_list.vertices[idx+1]
        z = self.vertex_list.vertices[idx+2]
        return x, y, z

    def get_original_vertex(self, x, y):
        """Get the original vertex coordinate.
        The original vertices are the ones weren't modified by the current action.

        :Parameters:
            `x` : int
               x-vertex
            `y` : int
               y-vertex

        :rtype: (float, float, float)
        """
        idx = (x * (self.grid.y + 1) + y) * 3
        x = self.vertex_points[idx]
        y = self.vertex_points[idx + 1]
        z = self.vertex_points[idx + 2]

        return x, y, z

    def set_vertex(self, x, y, v):
        """Set a vertex point is a certain value

        :Parameters:
            `x` : int
               x-vertex
            `y` : int
               y-vertex
            `v` : (float, float, float)
                tuple value for the vertex
        """
        idx = (x * (self.grid.y + 1) + y) * 3
        self.vertex_list.vertices[idx] = int(v[0])
        self.vertex_list.vertices[idx+1] = int(v[1])
        self.vertex_list.vertices[idx+2] = int(v[2])


class TiledGrid3D(GridBase):
    """`TiledGrid3D` is a 3D grid implementation. It differs from `Grid3D` in that
    the tiles can be separated from the grid.

    The vertex array will be built with::

        self.vertex_list.vertices: x,y,z (floats)
        self.vertex_list.tex_coords: x,y (floats)
        self.vertex_list.colors: RGBA, with values from 0 - 255
    """
    def _init(self):
        # calculate vertex, textures depending on screen size
        ver_pts, tex_pts = self._calculate_vertex_points()

        #: vertex array that can be transformed.
        #: it has these attributes:
        #:
        #:    - vertices
        #:    - colors
        #:    - tex_coords
        #:
        #: for more information refer to pyglet's documentation: pyglet.graphics.vertex_list
        self.vertex_list = pyglet.graphics.vertex_list(self.grid.x * self.grid.y * 4,
                                                       "t2f", "v3f/stream", "c4B")
        #: original vertex array of the grid. (read-only)
        self.vertex_points = ver_pts[:]
        self.vertex_list.vertices = ver_pts
        self.vertex_list.tex_coords = tex_pts
        self.vertex_list.colors = (255, 255, 255, 255) * self.grid.x * self.grid.y * 4

    def _blit(self):
        self.vertex_list.draw(pyglet.gl.GL_QUADS)

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
                vertex_points += [x1, y1, 0, x2, y1, 0, x2, y2, 0, x1, y2, 0]
                texture_points += [x1 / w, y1 / h, x2 / w, y1 / h, x2 / w, y2 / h, x1 / w, y2 / h]

        # Generates a quad for each tile, to perform tiles effect
        return vertex_points, texture_points

    def set_tile(self, x, y, coords):
        """Set the 4 tile coordinates

        Coordinates positions::

            3 <-- 2
                  ^
                  |
            0 --> 1

        :Parameters:
            `x` : int
                x coodinate of the tile
            `y` : int
                y coordinate of the tile
            `coords` : [ float, float, float, float, float, float, float, float, float, float, float, float ]
                The 4 coordinates in the format (x0, y0, z0, x1, y1, z1,..., x3, y3, z3)
        """
        idx = (self.grid.y * x + y) * 4 * 3
        self.vertex_list.vertices[idx:idx + 12] = coords

    def get_original_tile(self, x, y):
        """Get the 4-original tile coordinates.

        Coordinates positions::

            3 <-- 2
                  ^
                  |
            0 --> 1

        :Parameters:
            `x` : int
                x coordinate of the tile
            `y` : int
                y coordinate of the tile

        :rtype: [ float, float, float, float, float, float, float, float, float, float, float, float ]
        :returns: The 4 coordinates with the following order: x0, y0, z0, x1, y1, z1,...,x3, y3, z3
        """
        idx = (self.grid.y * x + y) * 4 * 3
        return self.vertex_points[idx:idx + 12]

    def get_tile(self, x, y):
        """Get the current tile coordinates.

        Coordinates positions::

            3 <-- 2
                  ^
                  |
            0 --> 1

        :Parameters:
            `x` : int
                x coordinate of the tile
            `y` : int
                y coordinate of the tile

        :rtype: [ float, float, float, float, float, float, float, float, float, float, float, float ]
        :returns: The 4 coordinates with the following order: x0, y0, z0, x1, y1, z1,...,x3, y3, z3
        """
        idx = (self.grid.y * x + y) * 4 * 3
        return self.vertex_list.vertices[idx:idx + 12]
