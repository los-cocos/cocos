#
# Cocos:
# http://code.google.com/p/los-cocos/
#
'''Grid Actions

Grid Actions
============

There are 3 kinds of grids::

    `Grid`
    `TiledGrid`
    `Grid3D`

Hence, there are 3 kinds of grid actions::

    `GridAction`
    `TiledGridAction`
    `Grid3DAction`

The `Grid` is a 2D grid. If you move 1 vertex, the surrounding tiles will be altered.
The `TiledGrid` is a 2D grid that is composed of individual tiles. Each tile can be manipulated individually.These tiles can be separated from the grid.
The `Grid3D` is like the `Grid` with the difference that it also supports z-axis vertex.
'''

__docformat__ = 'restructuredtext'

from pyglet.gl import *

from cocos.grid import TiledGrid, Grid, Grid3D
from cocos.director import director
from cocos.euclid import *
from base_actions import *

__all__ = [ 'GridException',            # Grid Exceptions
            'GridBaseAction',               # Base classes
            'TiledGridAction',
            'GridAction',
            'Grid3DAction',
            
            'AccelAmplitude',           # Amplitude modifiers
            'DeccelAmplitude',
            'AccelDeccelAmplitude',
            
            'StopGrid',
            'ReuseGrid',
            ]

class GridException( Exception ):
    pass
    
class GridBaseAction( IntervalAction ):
    '''GridBaseAction is the base class of all Grid Actions.'''
    def init( self, grid=(4,4), duration=5):
        """Initialize the Grid Action

        :Parameters:
            `grid` : (int,int)
                Number of horizontal and vertical quads in the grid
            `duration` : int 
                Number of seconds that the action will last
        """
        self.duration = duration
        if not isinstance(grid,Point2):
            grid = Point2( *grid)
        self.grid = grid

    def start( self ):        
        new_grid = self.get_grid()

        if self.target.grid and self.target.grid.reuse_grid > 0:                
            # Reusing the grid 
            if self.target.grid.active \
                    and self.grid == self.target.grid.grid \
                    and type(new_grid) == type(self.target.grid):
                # since we are reusing the grid,
                # we must "cheat" the action that the original vertex coords are
                # the ones that were inhereted.
                self.target.grid.vertex_points = self.target.grid.vertex_list.vertices[:]
                self.target.grid.reuse_grid -= 1
                self.target.grid.reuse_grid = max(0, self.target.grid.reuse_grid)
            else:
                # condition are not met
                raise GridException("Cannot reuse grid. class grid or grid size did not match: %s vs %s and %s vs %s"
                                    % ( str(self.grid), str(self.target.grid.grid), type(new_grid), type(self.target.grid) ) )
        else:
            # Not reusing the grid
            if self.target.grid and self.target.grid.active:
                self.target.grid.active = False
            self.target.grid = new_grid
            self.target.grid.init( self.grid )
            self.target.grid.active = True

        x,y = director.get_window_size()
        self.size_x = x // self.grid.x
        self.size_y = y // self.grid.y
      
    def set_vertex( self, x, y, v):
        raise NotImplementedError("abstract")

    def get_vertex( self, x, y):
        raise NotImplementedError("abstract")
    
    def get_original_vertex(self, x, y):
        raise NotImplementedError("abstract")
    
    def get_grid(self):
        return NotImplementedError('abstract')

    def __reversed__(self):
        return ReverseTime(self)
 
class GridAction( GridBaseAction ):
    '''A GridAction is an action that does transformations
    to a grid.'''

    def get_grid(self):
        return Grid()
    
    def get_vertex( self, x, y):
        '''Get the current vertex coordinate

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (int,int)
        '''
        idx = (x * (self.grid.y+1) + y) * 2
        x = self.target.grid.vertex_list.vertices[idx]
        y = self.target.grid.vertex_list.vertices[idx+1]
        return (x,y)
    
    def get_original_vertex( self, x, y):
        '''Get the original vertex coordinate

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (int,int)
        '''
        idx = (x * (self.grid.y+1) + y) * 2
        x = self.target.grid.vertex_points[idx]
        y = self.target.grid.vertex_points[idx+1]
        return (x,y)

    def set_vertex( self, x, y, v):
        '''Set a vertex with a certain coordinate

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex
            `v` : (int, int)
                tuple value for the vertex
        '''
        idx = (x * (self.grid.y+1) + y) * 2
        self.target.grid.vertex_list.vertices[idx] = int(v[0])
        self.target.grid.vertex_list.vertices[idx+1] = int(v[1])


class Grid3DAction( GridBaseAction ):
    '''A Grid3DAction is an action that does transformations
    to a 3D grid.'''

    def get_grid(self):
        return Grid3D()
    
    def get_vertex( self, x, y):
        '''Get the current vertex coordinate

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (int,int)
        '''
        idx = (x * (self.grid.y+1) + y) * 3
        x = self.target.grid.vertex_list.vertices[idx]
        y = self.target.grid.vertex_list.vertices[idx+1]
        z = self.target.grid.vertex_list.vertices[idx+2]
        return (x,y,z)

    def get_original_vertex( self, x, y):
        '''Get the original vertex coordinate

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (int,int)
        '''
        idx = (x * (self.grid.y+1) + y) * 3
        x = self.target.grid.vertex_points[idx]
        y = self.target.grid.vertex_points[idx+1]
        z = self.target.grid.vertex_points[idx+2]

        return (x,y,z)


    def set_vertex( self, x, y, v):
        '''Set a vertex point is a certain value

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex
            `v` : (int, int, int)
                tuple value for the vertex
        '''
        idx = (x * (self.grid.y+1) + y) * 3
        self.target.grid.vertex_list.vertices[idx] = int(v[0])
        self.target.grid.vertex_list.vertices[idx+1] = int(v[1])
        self.target.grid.vertex_list.vertices[idx+2] = int(v[2])


class TiledGridAction( GridBaseAction ):
    '''A TiledGrid action is an action that does transformations
    to a grid composed of tiles. You can transform each tile individually'''

    def get_grid(self):
        return TiledGrid()
    
    def set_vertex(self, i,j ):
        raise GridException("Use set_tile() instead")

    def get_vertex(self, i, j):
        raise GridException("Use get_tile() instead")
    
    def get_original_vertex(self, i, j):
        raise GridException("Use get_original_tile() instead")

    def set_tile(self, x, y, coords):
        '''Set the 4 tile coordinates

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex
            `coords` : [ int, int, int, int, int, int, int, int ]
                The 4 coordinates
        '''
        idx = (self.grid.y * x + y) * 4 * 2        
        self.target.grid.vertex_list.vertices[idx:idx+8] = coords
    
    def get_original_tile(self, x, y):
        '''Get the 4-original tile coordinates

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: [ int, int, int, int, int, int, int, int ]
        '''
        idx = (self.grid.y * x + y) * 4 * 2        
        return self.target.grid.vertex_points[idx:idx+8]
        

class AccelDeccelAmplitude( IntervalAction ):
    """
    Increases and Decreases the amplitude of Wave
    
    Example::
        # when t=0 and t=1 the amplitude will be 0
        # when t=0.5 (half time), the amplitude will be 40
        action = IncDecAmplitude( Wave3D( waves=4, amplitude=40, duration=6) )
        scene.do( action )
    """
    def init(self, other, rate=1.0 ):
        """Init method.

        :Parameters:
            `other` : `IntervalAction`
                The action that will be affected
            `rate`: float
                The acceleration rate. 1 is linear (default value)
        """
        if not hasattr(other,'amplitude'):
            raise GridAction("Invalid Composition: IncAmplitude needs an action with amplitude")

        self.other = other
        self.rate = rate
        self.duration = other.duration

    def start(self):
        self.other.target = self.target
        self.other.start()

    def update(self, t):
        f = t*2
        if f > 1:
            f -= 1
            f = 1 -f  

        self.other.amplitude_rate = f**self.rate
        self.other.update( t )

    def __reversed__(self):
        return AccelDeccelAmplitude( Reverse(self.other) )

class AccelAmplitude( IntervalAction ):
    """
    Increases the waves amplitude from 0 to self.amplitude
    
    Example::
        # when t=0 the amplitude will be 0
        # when t=1 the amplitude will be 40
        action = IncAmplitude( Wave3D( waves=4, amplitude=40, duration=6), rate=1.0 )
        scene.do( action )
    """
    def init(self, other, rate=1 ):
        """Init method.

        :Parameters:
            `other` : `IntervalAction`
                The action that will be affected
            `rate`: float
                The acceleration rate. 1 is linear (default value)
        """
        if not hasattr(other,'amplitude'):
            raise GridAction("Invalid Composition: IncAmplitude needs an action with amplitude")
        
        self.other = other
        self.duration = other.duration
        self.rate = rate

    def start(self):
        self.other.target = self.target
        self.other.start()

    def update(self, t):
        self.other.amplitude_rate = (t ** self.rate)
        self.other.update( t )

    def __reversed__(self):
        return DeccelAmplitude( Reverse(self.other), rate=self.rate )


class DeccelAmplitude( AccelAmplitude ):
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
        self.other.update( t )

    def __reversed__(self):
        return AccelAmplitude( Reverse(self.other), rate=self.rate )


class StopGrid( InstantAction ):
    """StopGrid disables the current grid.
    Every grid action, after finishing, leaves the screen with a certain grid figure.
    This figure will be displayed until StopGrid or another Grid action is executed.
    
    Example::
    
        scene.do( Waves3D( duration=2) + StopGrid() )
    """
    def update(self, t):
        if self.target.grid and self.target.grid.active:
            self.target.grid.active = False

class ReuseGrid( InstantAction ):
    """ReuseGrid will reuse the current grid for the next grid action.
    
    Example::
    
        scene.do( Waves3D( duration=2) + ReuseGrid() + Lens3D(duration=2) )
    """
    def init(self, reuse_times=1):
        '''
        :Parameters:
            `reuse_times` : int
                Number of times that the current grid will be reused by Grid actions. Default: 1
        '''
        self.reuse_times = reuse_times
    def start(self):
        if self.target.grid and self.target.grid.active:
            self.target.grid.reuse_grid += self.reuse_times
        else:
            raise GridException("ReuseGrid must be used when a grid is still active")
