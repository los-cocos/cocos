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
"""Grid Actions

Grid Actions
============

There are 2 kinds of grids:

  - `Grid3D` : A 3D grid with x,y and z coordinates
  - `TiledGrid3D` : A 3D grid with x,y and z coordinates, composed
     with independent tiles


Hence, there are 2 kinds of grid actions:

  - `Grid3DAction`
  - `TiledGrid3DAction`

The `Grid3DAction` can modify any of vertex of the grid in any direction (x,y or z).
The `TiledGrid3DAction` can modify any tile of the grid without modifying the adjacent tiles.

To understand visually the difference between these 2 kinds of grids, try these examples:

  - run ``test/test_shakytiles3d.py`` to see a `TiledGrid3DAction` example 
  - run ``test/test_shaky3d.py`` to see the `Grid3DAction` counterpart
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

from cocos.grid import Grid3D, TiledGrid3D
from cocos.director import director
from cocos.euclid import *
from .base_actions import *

__all__ = ['GridException',            # Grid Exceptions
           'GridBaseAction',               # Base classes
           'Grid3DAction',
           'TiledGrid3DAction',
            
           'AccelAmplitude',           # Amplitude modifiers
           'DeccelAmplitude',
           'AccelDeccelAmplitude',
            
           'StopGrid',
           'ReuseGrid', ]


class GridException(Exception):
    pass


class GridBaseAction(IntervalAction):
    """GridBaseAction is the base class of all Grid Actions."""
    def init(self, grid=(4, 4), duration=5):
        """Initialize the Grid Action

        :Parameters:
            `grid` : (int,int)
                Number of horizontal and vertical quads in the grid
            `duration` : int 
                Number of seconds that the action will last
        """
        self.duration = duration
        if not isinstance(grid, Point2):
            grid = Point2(*grid)
        self.grid = grid

    def start(self):
        new_grid = self.get_grid()

        if self.target.grid and self.target.grid.reuse_grid > 0:                
            # Reusing the grid 
            if self.target.grid.active \
                    and self.grid == self.target.grid.grid \
                    and type(new_grid) == type(self.target.grid):
                # since we are reusing the grid,
                # we must "cheat" the action that the original vertex coords are
                # the ones that were inherited.
                self.target.grid.vertex_points = self.target.grid.vertex_list.vertices[:]
                self.target.grid.reuse_grid -= 1
                self.target.grid.reuse_grid = max(0, self.target.grid.reuse_grid)
            else:
                # condition are not met
                raise GridException("Cannot reuse grid. class grid or grid size did not match: %s vs %s and %s vs %s"
                                    % (str(self.grid), str(self.target.grid.grid),
                                       type(new_grid), type(self.target.grid)))
        else:
            # Not reusing the grid
            if self.target.grid and self.target.grid.active:
                self.target.grid.active = False
            self.target.grid = new_grid
            self.target.grid.init(self.grid)
            self.target.grid.active = True

        x, y = director.get_window_size()
        self.size_x = x // self.grid.x
        self.size_y = y // self.grid.y
      
    def __reversed__(self):
        return _ReverseTime(self)
 
 
class Grid3DAction(GridBaseAction):
    """Action that does transformations
    to a 3D grid ( `Grid3D` )"""

    def get_grid(self):
        return Grid3D()
    
    def get_vertex(self, x, y):
        """Get the current vertex coordinate

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (float, float, float)
        """
        return self.target.grid.get_vertex(x, y)

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
        return self.target.grid.get_original_vertex(x, y)

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
        return self.target.grid.set_vertex(x, y, v)


class TiledGrid3DAction(GridBaseAction):
    """Action that does transformations
    to a grid composed of tiles ( `TiledGrid3D` ).
    You can transform each tile individually"""

    def get_grid(self):
        return TiledGrid3D()
    
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
        return self.target.grid.set_tile(x, y, coords)
    
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
        return self.target.grid.get_original_tile(x, y)

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
        return self.target.grid.get_tile(x, y)
        

class AccelDeccelAmplitude(IntervalAction):
    """
    Increases and Decreases the amplitude of Wave
    
    Example::

        # when t=0 and t=1 the amplitude will be 0
        # when t=0.5 (half time), the amplitude will be 40
        action = AccellDeccelAmplitude( Wave3D( waves=4, amplitude=40, duration=6) )
        scene.do( action )
    """
    def init(self, other, rate=1.0):
        """Init method.

        :Parameters:
            `other` : `IntervalAction`
                The action that will be affected
            `rate` : float
                The acceleration rate. 1 is linear (default value)
        """
        if not hasattr(other, 'amplitude'):
            raise GridException("Invalid Composition: IncAmplitude needs an action with amplitude")

        self.other = other
        self.rate = rate
        self.duration = other.duration

    def start(self):
        self.other.target = self.target
        self.other.start()

    def update(self, t):
        f = t * 2
        if f > 1:
            f -= 1
            f = 1 - f

        self.other.amplitude_rate = f ** self.rate
        self.other.update(t)

    def __reversed__(self):
        return AccelDeccelAmplitude(Reverse(self.other))


class AccelAmplitude(IntervalAction):
    """
    Increases the waves amplitude from 0 to self.amplitude
    
    Example::

        # when t=0 the amplitude will be 0
        # when t=1 the amplitude will be 40
        action = AccelAmplitude( Wave3D( waves=4, amplitude=40, duration=6), rate=1.0 )
        scene.do( action )
    """
    def init(self, other, rate=1):
        """Init method.

        :Parameters:
            `other` : `IntervalAction`
                The action that will be affected
            `rate` : float
                The acceleration rate. 1 is linear (default value)
        """
        if not hasattr(other, 'amplitude'):
            raise GridException("Invalid Composition: IncAmplitude needs an action with amplitude")
        
        self.other = other
        self.duration = other.duration
        self.rate = rate

    def start(self):
        self.other.target = self.target
        self.other.start()

    def update(self, t):
        self.other.amplitude_rate = (t ** self.rate)
        self.other.update(t)

    def __reversed__(self):
        return DeccelAmplitude(Reverse(self.other), rate=self.rate)


class DeccelAmplitude(AccelAmplitude):
    """
    Decreases the waves amplitude from self.amplitude to 0
    
    Example::

        # when t=1 the amplitude will be 0
        # when t=0 the amplitude will be 40
        action = DeccelAmplitude( Wave3D( waves=4, amplitude=40, duration=6), rate=1.0 )
        scene.do( action )
    """

    def update(self, t):
        self.other.amplitude_rate = ((1-t) ** self.rate)
        self.other.update(t)

    def __reversed__(self):
        return AccelAmplitude(Reverse(self.other), rate=self.rate)


class StopGrid(InstantAction):
    """StopGrid disables the current grid.
    Every grid action, after finishing, leaves the screen with a certain grid figure.
    This figure will be displayed until StopGrid or another Grid action is executed.
    
    Example::
    
        scene.do( Waves3D( duration=2) + StopGrid() )
    """
    def start(self):
        if self.target.grid and self.target.grid.active:
            self.target.grid.active = False


class ReuseGrid(InstantAction):
    """Will reuse the current grid for the next grid action.
    The next grid action must have these properties:
    
        - Be of the same class as the current one ( `Grid3D` or `TiledGrid3D` )
        - Have the same size
    
    If these condition are met, then the next grid action will receive as the ``original vertex``
    or ``original tiles`` the current ones.
    
    Example::
    
        scene.do( Waves3D( duration=2) + ReuseGrid() + Lens3D(duration=2) )
    """
    def init(self, reuse_times=1):
        """
        :Parameters:
            `reuse_times` : int
                Number of times that the current grid will be reused by Grid actions. Default: 1
        """
        self.reuse_times = reuse_times

    def start(self):
        if self.target.grid and self.target.grid.active:
            self.target.grid.reuse_grid += self.reuse_times
        else:
            raise GridException("ReuseGrid must be used when a grid is still active")
