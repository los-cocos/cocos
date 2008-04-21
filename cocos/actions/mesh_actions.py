#
# Cocos Mesh Actions
#

'''Grid Actions

Grid Actions
============

These are the actions that are performed transforming a grid.

There are 3 kinds of grids::

    `TiledGrid`
    `Grid`
    `Grid3D`

The `TiledGrid` is a grid that is composed of individual tiles. Each tile can be manipulated individually.
Each tile has its own vertices. The vertices are not shared among the other tiles.
The `Grid` is a grid that is composed of a grid with shared vertices, and the `Grid3D` is like
`Grid` but it also support z-axis vertices.
'''

__docformat__ = 'restructuredtext'

import math
import random
rr = random.randrange

from pyglet.gl import *

from cocos.mesh import TiledGrid, Grid, Grid3D
from cocos.director import director
from cocos.euclid import *
from base_actions import *

__all__ = [ 'GridException',            # Mesh Exceptions
            'GridBaseAction',               # Base classes
            'TiledGridAction',
            'GridAction',
            'Grid3DAction',
            'QuadMoveBy',               # Basic class for skews, etc...

            'ShakyTiles',               # Tiles Actions
            'ShuffleTiles',
            'ShatteredTiles',
            'FadeOutTiles',

            'MoveCornerUp',             # QuadMoveBy Actions
            'MoveCornerDown',
            'SkewHorizontal',
            'SkewVertical',
            'Flip','FlipX','FlipY',
            'CornerSwap',         
            
            'Shaky',                    # Trembling actions
            'Liquid','Waves',           # Liquid and Waves
            
            'Waves3D',                  # Waves in z-axis
            'FlipX3D',
            'FlipY3D',
            'Lens3D',
            
            'AccelAmplitude',           # Amplitude modifiers
            'DeccelAmplitude',
            'AccelDeccelAmplitude',

            ]

class GridException( Exception ):
    pass
    
class GridBaseAction( IntervalAction ):
    '''GridBaseAction is the base class of all Mesh Actions.'''
    def init( self, grid=(4,4), duration=5):
        """Initialize the Mesh Action
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
        self.target.mesh.init( self.grid )
        self.target.mesh.active = True

        x,y = director.get_window_size()
        self.size_x = x // self.grid.x
        self.size_y = y // self.grid.y

        
    def stop( self ):
        self.target.mesh.vertex_list.delete()
        self.target.mesh.active = False

    def set_vertex( self, x, y, v):
        raise NotImplementedError("abstract")

    def get_vertex( self, x, y):
        raise NotImplementedError("abstract")


class GridAction( GridBaseAction ):
    '''A GridAction is an action that does transformations
    to a grid.'''
    def start( self ):
        self.target.mesh = Grid()
        super( GridAction, self ).start()

    def get_vertex( self, x, y):
        '''Get the current vertex point value

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (int,int)
        '''
        idx = (x * (self.grid.y+1) + y) * 2
        x = self.target.mesh.vertex_list.vertices[idx]
        y = self.target.mesh.vertex_list.vertices[idx+1]
        return (x,y)

    def set_vertex( self, x, y, v):
        '''Set a vertex point is a certain value

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex
            `v` : (int, int)
                tuple value for the vertex
        '''
        idx = (x * (self.grid.y+1) + y) * 2
        self.target.mesh.vertex_list.vertices[idx] = int(v[0])
        self.target.mesh.vertex_list.vertices[idx+1] = int(v[1])

class Grid3DAction( GridBaseAction ):
    '''A Grid3DAction is an action that does transformations
    to a 3D grid.'''
    def start( self ):
        self.target.mesh = Grid3D()
        super( Grid3DAction, self ).start()                

    def get_vertex( self, x, y):
        '''Get the current vertex point value

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (int,int)
        '''
        idx = (x * (self.grid.y+1) + y) * 3
#        x = self.target.mesh.vertex_list.vertices[idx]
#        y = self.target.mesh.vertex_list.vertices[idx+1]
#        z = self.target.mesh.vertex_list.vertices[idx+2]
        x = self.target.mesh.vertex_points[idx]
        y = self.target.mesh.vertex_points[idx+1]
        z = self.target.mesh.vertex_points[idx+2]

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
        self.target.mesh.vertex_list.vertices[idx] = int(v[0])
        self.target.mesh.vertex_list.vertices[idx+1] = int(v[1])
        self.target.mesh.vertex_list.vertices[idx+2] = int(v[2])



class TiledGridAction( GridBaseAction ):
    '''A TiledGrid action is an action that does transformations
    to a grid composed of tiles. You can transform each tile individually'''
    def start( self ):
        self.target.mesh = TiledGrid()
        super( TiledGridAction, self ).start()
        
 
    def _get_vertex_idx( self, i, j, k ):
        if i==0 and j==0:
            idx = 0
        elif i==0 and j>0:
            idx = ( (j-1)*4 + 3 ) * 2
        elif i>0 and j==0:
            idx = ((i-1) * 4 * self.grid.y + 1 ) * 2
        else:
            idx = ((i-1) * 4 * self.grid.y + (j-1) * 4 + k) * 2

        return idx

    def _set_vertex( self, i, j, k, v ):
        if i < 0 or i > self.grid.x:
            return
        if j < 0 or j > self.grid.y:
            return
        if k< 0 or k >=4:
            return

        idx = self._get_vertex_idx( i,j,k)

        self.target.mesh.vertex_list.vertices[idx] = int(v[0])
        self.target.mesh.vertex_list.vertices[idx+1] = int(v[1])

    def set_vertex( self, x, y, v):
        '''Set a vertex point is a certain value

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex
            `v` : (int, int)
                tuple value for the vertex
        '''
        self._set_vertex( x, y, 2, v)
        self._set_vertex( x+1, y, 3, v)
        self._set_vertex( x+1, y+1, 0, v)
        self._set_vertex( x, y+1, 1, v)

    def get_vertex( self, x, y):
        '''Get the current vertex point value

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (int,int)
        '''
        idx = self._get_vertex_idx( x,y,2 )
        x = self.target.mesh.vertex_list.vertices[idx]
        y = self.target.mesh.vertex_list.vertices[idx+1]
        return (x,y)

# Don't export this class
class Tile(object):
    def __init__(self, position=(0,0), start_position=(0,0), delta=(0,0) ):
        super(Tile,self).__init__()
        self.position = position
        self.start_position = start_position
        self.delta = delta

    def __repr__(self):
        return "(start_pos: %s  pos: %s   delta:%s)" % (self.start_position, self.position, self.delta)

class ShakyTiles( TiledGridAction ):
    '''ShakyTiles simulates a shaky floor composed of tiles

       scene.do( ShakyTiles( randrange=6, grid=(4,4), duration=10) )
    '''

    def init( self, randrange=6, *args, **kw ):
        '''
        :Parameters:
            `randrange` : int
                Number that will be used in random.randrange( -randrange, randrange) to do the effect
        '''
        super(ShakyTiles,self).init(*args,**kw)
        self.randrange = randrange

    def update( self, t ):
        for i in range(0, self.grid.x):
            for j in range(0, self.grid.y):
                for k in range(0,4):

                    idx = (i * 4 * self.grid.y + j * 4 + k) * 2
                    x = self.target.mesh.vertex_points[idx]
                    y = self.target.mesh.vertex_points[idx+1]

                    x += rr(-self.randrange, self.randrange)
                    y += rr(-self.randrange, self.randrange)

                    self.target.mesh.vertex_list.vertices[idx] = int(x)
                    self.target.mesh.vertex_list.vertices[idx+1] = int(y)
                
    def __reversed__(self):
        # self
        return ShakyTiles( randrange=self.randrange, grid=self.grid, y_quads=self.grid.y, duration=self.duration)

class ShatteredTiles( TiledGridAction ):
    '''ShatterTiles shatters the tiles according to a random value.
    It is similar to shakes (see `ShakyTiles`) the tiles just one frame, and then continue with
    that state for duration time.
    '''

    def init( self, randrange=6, *args, **kw ):
        '''
        :Parameters:
            `randrange` : int
                Number that will be used in random.randrange( -randrange, randrange) to do the effect
        '''
        super(ShatteredTiles,self).init(*args,**kw)
        self.randrange = randrange
        self._once = False

    def update( self, t ):
        if not self._once:
            for i in range(0, self.grid.x):
                for j in range(0, self.grid.y):
                    for k in range(0,4):
    
                        idx = (i * 4 * self.grid.y + j * 4 + k) * 2
                        x = self.target.mesh.vertex_points[idx]
                        y = self.target.mesh.vertex_points[idx+1]
    
                        x += rr(-self.randrange, self.randrange)
                        y += rr(-self.randrange, self.randrange)
    
                        self.target.mesh.vertex_list.vertices[idx] = int(x)
                        self.target.mesh.vertex_list.vertices[idx+1] = int(y)
            self._once = True
                
    def __reversed__(self):
        # Reverse(Shattered) == Normal Tiles
        return ShatteredTiles( randrange=0, grid=self.grid, duration=self.duration)

class ShuffleTiles( TiledGridAction ):
    '''ShuffleTiles moves the tiles randomly across the screen and then put
    them back into the original place.
       scene.do( ShuffleTiles( grid=(4,4), duration=10) )
    '''

    def start(self):
        super(ShuffleTiles,self).start()
        self.tiles = {}
        self.dst_tiles = {}
        self._once = False
        for i in range(self.grid.x):
            for j in range(self.grid.y):
                self.tiles[(i,j)] = Tile( position = Point2(i,j), 
                                          start_position = Point2(i,j), 
                                          delta= self._get_delta(i,j) )

        
    def place_tile(self, i, j):
        t = self.tiles[(i,j)]

        for k in range(0,4):
            idx = (i * 4 * self.grid.y + j * 4 + k) * 2

            x=0
            y=0
            
            if k==1 or k==2:
                x = self.target.mesh.x_step
            if k==2 or k==3:
                y = self.target.mesh.y_step
                
            x += t.position.x * self.target.mesh.x_step
            y += t.position.y * self.target.mesh.y_step
            
            self.target.mesh.vertex_list.vertices[idx] = int(x)
            self.target.mesh.vertex_list.vertices[idx+1] = int(y)
        
    def update( self, t ):
        if t < 1.0/3:
            self.phase_shuffle(t/ (1.0/3) )
        elif t < 2.0/3:
            if self._once is False:
                self.phase_shuffle(1)
                self._once = True
        else:
            self.phase_shuffle_back( (t-2.0/3) / (1.0/3) )

    def phase_shuffle(self, t ):
        for i in range(0, self.grid.x):
            for j in range(0, self.grid.y):
                self.tiles[(i,j)].position = self.tiles[(i,j)].start_position + self.tiles[(i,j)].delta * t
                self.place_tile(i,j)
   
    def phase_shuffle_back(self, t):
        for i in range(0, self.grid.x):
            for j in range(0, self.grid.y):
                self.tiles[(i,j)].position = self.tiles[(i,j)].start_position + self.tiles[(i,j)].delta * (1-t)
                self.place_tile(i,j)                
                
    # private method
    def _get_delta(self, x, y):
        a = rr(0, self.grid.x), rr(0, self.grid.y)  
        if not self.dst_tiles.get(a, False):
            self.dst_tiles[ a ] = True
            return Point2(*a)-Point2(x,y)
        for i in range(a[0], self.grid.x):
            for j in range(self.grid.y):
                if not self.dst_tiles.get( (i,j), False):
                    self.dst_tiles[ (i,j) ] = True
                    return Point2(i,j)-Point2(x,y)
        for i in range(a[0]):
            for j in range(self.grid.y):
                if not self.dst_tiles.get( (i,j), False):
                    self.dst_tiles[ (i,j) ] = True
                    return Point2(i,j)-Point2(x,y)
        raise GridException("_get_delta() error")

    def __reversed__(self):
        # revere is self, since it will perform the same action
        return ShuffleTiles( grid=self.grid, duration=self.duration)


class FadeOutTiles( TiledGridAction ):
    '''FadeOutTiles fades out each tile following a diagonal path until all the tiles are faded out.
       scene.do( FadeOutTiles( grid=(16,16), duration=10) )
    '''

    def start(self):
        super(FadeOutTiles,self).start()
        self.tiles = {}
        self.dst_tiles = {}
        for i in range(self.grid.x):
            for j in range(self.grid.y):
                self.tiles[(i,j)] = Tile( position = Point2(i,j), 
                                          start_position = Point2(i,j), 
                                          delta=Point2(0,-j) )

    def update( self, t ):
        x,y = t * self.grid
                
        # direction right - up
        for i in range(self.grid.x):
            for j in range(self.grid.y):
                if i+j <= x+y+8:
                    for k in range(0,4):
                        idx =     (i * 4 * self.grid.y + j * 4 + k) * 2
                        idx_dst = (i * 4 * self.grid.y + j * 4 + 2) * 2   # k==2 is coord 'c'

                        vx = self.target.mesh.vertex_list.vertices[idx]
                        vy = self.target.mesh.vertex_list.vertices[idx+1]
                        
                        x_dst = self.target.mesh.vertex_points[idx_dst]
                        y_dst = self.target.mesh.vertex_points[idx_dst+1]

                        if k==1 or k==0:    # coord 'a' or 'b'
                            vy = 1 + vy + (y_dst - vy) / 16
                        if k==3 or k==0:    # coord 'a' or 'd'
                            vx = 1 + vx + (x_dst - vx) / 16
                             
                        if vx >= x_dst:
                            vx = x_dst
                        if vy >= y_dst:
                            vy = y_dst
                                
                        self.target.mesh.vertex_list.vertices[idx] = int(vx)
                        self.target.mesh.vertex_list.vertices[idx+1] = int(vy)
               
    def __reversed__(self):
        raise NotImplementedError('FadeInTiles not implemented yet!')
#        return FadeOutTiles( grid=self.grid, duration=self.duration)

class Shaky( GridAction):
    '''Shaky simulates an earthquake

       scene.do( Shaky( randrange=6, grid=(4,4), duration=10) )
    '''
    def init( self, randrange=6, *args, **kw ):
        '''
        :Parameters:
            `randrange` : int
                Number that will be used in random.randrange( -randrange, randrange) to do the effect
        '''        
        super(Shaky,self).init(*args,**kw)
        self.randrange = randrange

    def update( self, t ):
        for i in range(0, self.grid.x+1):
            for j in range(0, self.grid.y+1):

                x = i* self.size_x
                y = j* self.size_y

                x += rr( -self.randrange, self.randrange )
                y += rr( -self.randrange, self.randrange )

                self.set_vertex( i,j, (x,y) )

    def __reversed__(self):
        return Shaky( randrange=self.randrage, grid=self.grid, duration=self.duration)

class Liquid( GridAction ):
    '''Liquid simulates a liquid effect using the math.sin() function

       scene.do( Liquid( waves=5, grid=(16,16), duration=10) )
    '''
    def init( self, waves=4, *args, **kw ):
        '''
        :Parameters:
            `waves` : int
                Number of waves (2 * pi) that the action will perform.
        '''
        super(Liquid, self).init( *args, **kw )
        self.waves=waves

    def update( self, t ):
            
        for i in range(1, self.grid.x):
            for j in range(1, self.grid.y):
                x = i* self.size_x
                y = j* self.size_y
                xpos = (x + (math.sin(t*math.pi*self.waves*2 + x * .01) * self.size_x))
                ypos = (y + (math.sin(t*math.pi*self.waves*2 + y * .01) * self.size_y)) 
                self.set_vertex( i,j, (xpos,ypos) )

    def __reversed__(self):
        # almost self
        return Liquid( waves=self.waves, grid=self.grid, duration=self.duration)

class Waves( GridAction ):
    '''Waves simulates waves using the math.sin() function both in the vertical and horizontal axis

       scene.do( Waves( waves=4, vertical_sin=True, horizontal_sin=False, grid=(16,16), duration=10) )
    '''

    def init( self, waves=4, horizontal_sin=True, vertical_sin=True, *args, **kw ):
        '''
        :Parameters:
            `waves` : int
                Number of waves (2 * pi) that the action will perform.
            `horizontal_sin` : bool
                whether or not in will perform horizontal waves
            `vertical_sin` : bool
                whether or not in will perform vertical waves
        '''
        super(Waves, self).init( *args, **kw )
        self.horizontal_sin = horizontal_sin
        self.vertical_sin = vertical_sin
        self.waves=waves

    def update( self, t ):        
        for i in range(0, self.grid.x+1):
            for j in range(0, self.grid.y+1):
                x = i* self.size_x
                y = j* self.size_y

                if self.vertical_sin:
                    xpos = (x + (math.sin(t*math.pi*self.waves*2 + y * .01) * self.size_x))
                else:
                    xpos = x

                if self.horizontal_sin:
                    ypos = (y + (math.sin(t*math.pi*self.waves*2 + x * .01) * self.size_y)) 
                else:
                    ypos = y

                self.set_vertex( i,j, (xpos,ypos) )

    def __reversed__(self):
        # almost self
        return Waves( waves=self.waves, 
                   horizontal_sin=self.horizontal_sin, vertical_sin=self.vertical_sin,
                    grid=self.grid,
                    duration=self.duration)

class Waves3D( Grid3DAction ):
    '''Waves3D simulates waves using the math.sin() function both in the z-axis

       scene.do( Waves3D( waves=5, amplitude=40, grid=(16,16), duration=10) )
    '''

    def init( self, waves=4, amplitude=20, *args, **kw ):
        '''
        :Parameters:
            `waves` : int
                Number of waves (2 * pi) that the action will perform.
            `amplitude`: int
                Wave amplitude (height). Default is 20
        '''
        super(Waves3D, self).init( *args, **kw )
        self.waves=waves
        self.amplitude_rate = 1.0         # can be modified by other actions
        self.amplitude=amplitude

    def update( self, t ):
        for i in range(0, self.grid.x+1):
            for j in range(0, self.grid.y+1):
                x = i* self.size_x
                y = j* self.size_y

                z = (math.sin(t*math.pi*self.waves*2 + (y+x) * .01) * self.amplitude * self.amplitude_rate )

                self.set_vertex( i,j, (x, y, z) )

    def __reversed__(self):
        # almost self
        return Waves3D( waves=self.waves,
                    amplitude=self.amplitude, 
                    grid=self.grid,
                    duration=self.duration)

class FlipX3D( Grid3DAction ):
    '''FlipX3D flips the screen using the Y-axis'''

    def init(self, grid=(1,1), *args, **kw):
        if grid != (1,1):
            raise GridException("Invalid grid size.")
        super(FlipX3D,self).init(grid=grid,*args,**kw)

    def update( self, t ):
        angle = math.pi * t     # 180 degrees
        mz = math.sin( angle )
        angle = angle / 2.0     # x calculates degrees from 0 to 90
        mx = math.cos( angle )

        x,y,z = self.get_vertex(1,1)

        diff_x = x - x * mx
        diff_z = abs( (x * mz) // 4.0 )
 
        # bottom-left
        x,y,z = self.get_vertex(0,0)
        self.set_vertex(0,0,(diff_x,y,z+diff_z))

        # upper-left
        x,y,z = self.get_vertex(0,1)
        self.set_vertex(0,1,(diff_x,y,z+diff_z))

        # bottom-right
        x,y,z = self.get_vertex(1,0)
        self.set_vertex(1,0,(x-diff_x,y,z-diff_z))

        # upper-right
        x,y,z = self.get_vertex(1,1)
        self.set_vertex(1,1,(x-diff_x,y,z-diff_z))

class FlipY3D( Grid3DAction ):
    '''FlipY3D flips the screen using the X-axis'''

    def init(self, grid=(1,1), *args, **kw):
        if grid != (1,1):
            raise GridException("Invalid grid size.")
        super(FlipY3D,self).init(grid=grid,*args,**kw)

    def update( self, t ):
        angle = math.pi * t     # 180 degrees
        mz = math.sin( angle )
        angle = angle / 2.0     # x calculates degrees from 0 to 90
        my = math.cos( angle )

        x,y,z = self.get_vertex(1,1)

        diff_y = y - y * my
        diff_z = abs( (y * mz) // 4.0 )
 
        # bottom-left
        x,y,z = self.get_vertex(0,0)
        self.set_vertex(0,0,(x,diff_y,z+diff_z))

        # upper-left
        x,y,z = self.get_vertex(0,1)
        self.set_vertex(0,1,(x,y-diff_y,z-diff_z))

        # bottom-right
        x,y,z = self.get_vertex(1,0)
        self.set_vertex(1,0,(x,diff_y,z+diff_z))

        # upper-right
        x,y,z = self.get_vertex(1,1)
        self.set_vertex(1,1,(x,y-diff_y,z-diff_z))



    def __reversed__(self):
        raise NotImplementedError('Reverse(FlipY3d) not implemented yet')

class Lens3D( Grid3DAction ):
    '''Lens simulates a Lens / Magnifying glass effect

       scene.do( Lens3D(center=(320,240), radius=150, grid=(16,16), duration=10) )
    '''

    def init(self, center=(-1,-1), radius=160, lens_effect=0.7, *args, **kw):
        '''
        :Parameters:
            `center` : (int,int)
                Center of the lens. Default: (win_size_width /2, win_size_height /2 )
            `radius` : int
                Radius of the lens.
            `lens_effect` : float
                How strong is the lens effect. Default: 0.7. 0 is no effect at all, 1 is a very strong lens effect.
        '''
        super(Lens3D,self).init( *args, **kw)
        
        x,y = director.get_window_size()
        if center==(-1,-1):
            center=(x//2, y//2)
        self.position = Point2( center[0]+1, center[1]+1 )
        self.radius = radius
        self.lens_effect = lens_effect
       
        self._last_position = self.position
        
    def update( self, t ):
        if self._last_position != self.position:
            for i in range(0, self.grid.x+1):
                for j in range(0, self.grid.y+1):
        
                    x,y,z = self.get_vertex(i,j)
                    
                    p = Point2( x,y )
                    vect = self.position - p
                    r = abs(vect)
                    
                    if r < self.radius:
        
                        r = self.radius - r
                        pre_log = r/self.radius
                        if pre_log == 0:
                            pre_log = 0.001
                        l = math.log( pre_log )*self.lens_effect
                        new_r = math.exp( l ) * self.radius
        
                        vect.normalize()
                        new_vect = vect * new_r

                        z += abs(new_vect) * self.lens_effect    # magic vrbl        
                    self.set_vertex( i,j, (x,y,z) )
            self._last_position = self.position

    def __reversed__(self):
        # self
        return Lens3D( lens_effect=self.lens_effect, radius=self.radius, center=self.position, grid=self.grid, duration=self.duration )

class QuadMoveBy( GridAction ):
    '''QuadMoveBy moves each vertex of the quad

       scene.do( QuadMoveBy( src0, src1, src2, src3,
               delta0, delta1, delta2, delta3,
               duration) )

       Vertex positions::

            vertex3 --<-- vertex2
                |            |
                v            ^
                |            |
            vertex0 -->-- vertex1
        
        The vertices will move from the origin (src parameters) a relative distance (delta parameters) in duration time.
       '''

    def init( self, 
              src0=(0,0), src1=(-1,-1), src2=(-1,-1), src3=(-1,-1),
              delta0=(0,0), delta1=(0,0), delta2=(0,0), delta3=(0,0),
              grid=(1,1),
              *args, **kw ):
        '''Initializes the QuadMoveBy
        
        :Parameters:
             `src0` : (int, int)
                 Initial value for the bottom-left coordinate. Default is (0,0)
             `src1` : (int, int)
                 Initial value for the bottom-rifht coordinate. Default is (win_size_x,0)
             `src2` : (int, int)
                 Initial value for the upper-right coordinate. Default is (win_size_x, win_size_y)
             `src3` : (int, int)
                 Initial value for the upper-left coordinate. Default is (0, win_size_y)
            `delta0` : (int, int)
                The bottom-left relative coordinate. Default is (0,0)
            `delta1` : (int, int)
                The bottom-right relative coordinate. Default is (0,0)
            `delta2` : (int, int)
                The upper-right relative coordinate. Default is (0,0)
            `delta3` : (int, int)
                The upper-left relative coordinate. Default is (0,0)
        '''

        if grid != (1,1):
            raise GridException("Invalid grid size.")

        super( QuadMoveBy, self).init( grid, *args, **kw )
        
        x,y = director.get_window_size()
        
        if src1 == (-1,-1):
            src1 = ( x,0 )
        if src2 == (-1,-1):
            src2 = (x,y)
        if src3 == (-1,-1):
            src3 = (0,y)  

        self.src0 = Point2( *src0 )
        self.src1 = Point2( *src1 )  
        self.src2 = Point2( *src2 )
        self.src3 = Point2( *src3 )
        self.delta0 = Point2( *delta0 )
        self.delta1 = Point2( *delta1 )
        self.delta2 = Point2( *delta2 )
        self.delta3 = Point2( *delta3 )
       
    def update( self, t ):
        new_pos0 = self.src0 + self.delta0 * t
        new_pos1 = self.src1 + self.delta1 * t
        new_pos2 = self.src2 + self.delta2 * t
        new_pos3 = self.src3 + self.delta3 * t

        self.set_vertex( 0,0, new_pos0 )
        self.set_vertex( 1,0, new_pos1 )
        self.set_vertex( 1,1, new_pos2 )
        self.set_vertex( 0,1, new_pos3 )

    def __reversed__(self):
        return QuadMoveBy( self.src0 + self.delta0, self.src1 + self.delta1, self.src2 + self.delta2, self.src3 + self.delta3,
                           -self.delta0, -self.delta1, -self.delta2, -self.delta3,
                           self.grid, duration=self.duration )
    
class MoveCornerUp( QuadMoveBy ):
    '''MoveCornerUp moves the bottom-right corner to the upper-left corner in duration time'''
    def __init__(self, *args, **kw):
        x,y = director.get_window_size()
        super(MoveCornerUp, self).__init__( delta1=(-x,y), *args, **kw )

class MoveCornerDown( QuadMoveBy ):
    '''MoveCornerDown moves the upper-left corner to the bottom-right corner in duration time'''
    def __init__(self, *args, **kw):
        x,y = director.get_window_size()
        super(MoveCornerDown, self).__init__( delta3=(x,-y), *args, **kw )

class CornerSwap( QuadMoveBy ):
    '''CornerSwap moves the upper-left corner to the bottom-right corner in vice-versa in duration time.
    The resulting effect is a reflection + rotation.
    '''
    def __init__(self, *args, **kw):
        x,y = director.get_window_size()
        super(CornerSwap, self).__init__( delta1=(-x,y), delta3=(x,-y), *args, **kw )

class Flip( QuadMoveBy ):
    '''Flip moves the upper-left corner to the bottom-left corner and vice-versa, and
    moves the upper-right corner to the bottom-left corner and vice-versa, flipping the
    window upside-down, and right-left.
    '''
    def __init__(self, *args, **kw):
        x,y = director.get_window_size()
        super(Flip, self).__init__( delta0=(x,y), delta1=(-x,y), delta2=(-x,-y), delta3=(x,-y), *args, **kw )

class FlipX( QuadMoveBy ):
    '''FlipX flips the screen horizontally, moving the left corners to the right, and vice-versa.
    '''
    def __init__(self, *args, **kw):
        x,y = director.get_window_size()
        super(FlipX, self).__init__( delta0=(x,0), delta1=(-x,0), delta2=(-x,0), delta3=(x,0), *args, **kw )

class FlipY( QuadMoveBy ):
    '''FlipY flips the screen vertically, moving the upper corners to the bottom, and vice-versa.
    '''
    def __init__(self, *args, **kw):
        x,y = director.get_window_size()
        super(FlipY, self).__init__( delta0=(0,y), delta1=(0,y), delta2=(0,-y), delta3=(0,-y), *args, **kw )

class SkewHorizontal( QuadMoveBy ):
    '''SkewHorizontal skews the screen horizontally. default skew: x/3'''
    def __init__(self, delta=None, *args, **kw):
        x,y = director.get_window_size()
        if delta==None:
            delta=x//3
        super(SkewHorizontal, self).__init__( delta1=(-delta,0), delta3=(delta,0), *args, **kw )

class SkewVertical( QuadMoveBy ):
    '''SkewVertical skews the screen vertically. default skew: y/3'''
    def __init__(self, delta=None, *args, **kw):
        x,y = director.get_window_size()
        if delta==None:
            delta=y//3
        super(SkewVertical, self).__init__( delta0=(0,delta), delta2=(0,-delta), *args, **kw )

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
