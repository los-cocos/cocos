#
# Cocos Mesh Actions
#

'''Mesh Actions

Mesh Actions
============

'''

__docformat__ = 'restructuredtext'

import math
import random
rr = random.randrange

from cocos.director import director
from cocos.mesh import TILES_MODE, GRID_MODE
from cocos.euclid import *
from base_actions import *

__all__ = [ 'MeshAction',               # Base classes
            'MeshTilesAction', 'MeshGridAction',
            'QuadMoveBy',               # Basic class for skews, etc...

            'ShakyTiles',               # Tiles Actions
            'ShuffleTiles',
            'Shaky',                    # Trembling actions
            'Liquid','Sin',             # Liquid and Sin
            'Lens',                     # Lens effect (magnifying)
            'GridNop',                  # Grid None Effect - For testing
            ]

class MeshAction( IntervalAction ):
    '''MeshAction is the base class of all Mesh Actions.'''
    def init( self, x_quads=4, y_quads=4, duration=5):
        """Initialize the Mesh Action
        :Parameters:
            `x_quads` : int 
                Number of horizontal quads in the mesh
            `y_quads` : int
                Number of vertical quads in the mesh
            `duration` : int 
                Number of seconds that the action will last
        """
        self.duration = duration
        self.x_quads = x_quads
        self.y_quads = y_quads

    def start( self ):
        self.target.mesh.init( self.x_quads, self.y_quads )
        self.target.mesh.active = True

        x,y = director.get_window_size()
        self.size_x = x // self.x_quads
        self.size_y = y // self.y_quads
        

    def done( self ):
        r = super(MeshAction,self).done()
        if r:
            self.target.mesh.active = False
        return r

    def set_vertex( self, x, y, v):
        raise NotImplementedError("abstract")

    def get_vertex( self, x, y):
        raise NotImplementedError("abstract")


class MeshGridAction( MeshAction ):
    '''A MeshGrid action is an action that does transformations
    to a grid.'''
    def start( self ):
        super( MeshGridAction, self ).start()
        self.target.mesh.mesh_mode = GRID_MODE

    def get_vertex( self, x, y):
        '''Get the current vertex point value

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (int,int)
        '''
        idx = (x * (self.x_quads+1) + y) * 2
        x = self.target.mesh.vertex_list_idx.vertices[idx]
        y = self.target.mesh.vertex_list_idx.vertices[idx+1]
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
        idx = (x * (self.x_quads+1) + y) * 2
        self.target.mesh.vertex_list_idx.vertices[idx] = int(v[0])
        self.target.mesh.vertex_list_idx.vertices[idx+1] = int(v[1])


class MeshTilesAction( MeshAction ):
    '''A MeshTiles action is an action that does transformations
    to a grid composed of tiles. You can transform each tile individually'''
    def start( self ):
        super( MeshTilesAction, self ).start()
        self.target.mesh.mesh_mode = TILES_MODE

    def _get_vertex_idx( self, i, j, k ):
        if i==0 and j==0:
            idx = 0
        elif i==0 and j>0:
            idx = ( (j-1)*4 + 3 ) * 2
        elif i>0 and j==0:
            idx = ((i-1) * 4 * self.y_quads + 1 ) * 2
        else:
            idx = ((i-1) * 4 * self.y_quads + (j-1) * 4 + k) * 2

        return idx

    def _set_vertex( self, i, j, k, v ):
        if i < 0 or i > self.x_quads:
            return
        if j < 0 or j > self.y_quads:
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

class ShakyTiles( MeshTilesAction ):
    '''ShakyTiles simulates a shaky floor composed of tiles

       scene.do( ShakyTiles( randrange=6, x_quads=4, y_quads=4, duration=10) )
    '''

    def init( self, randrange=6, *args, **kw ):
        super(ShakyTiles,self).init(*args,**kw)
        self.randrange = randrange

    def update( self, t ):
        for i in range(0, self.x_quads):
            for j in range(0, self.y_quads):
                for k in range(0,4):

                    idx = (i * 4 * self.y_quads + j * 4 + k) * 2
                    x = self.target.mesh.vertex_points[idx]
                    y = self.target.mesh.vertex_points[idx+1]

                    x += rr(-self.randrange, self.randrange)
                    y += rr(-self.randrange, self.randrange)

                    self.target.mesh.vertex_list.vertices[idx] = int(x)
                    self.target.mesh.vertex_list.vertices[idx+1] = int(y)
                
    def __reversed__(self):
        return ShakyTiles( randrange=self.randrange, x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)

class ShuffleTiles( MeshTilesAction ):
    '''ShuffleTiles moves the tiles randomly across the screen and then put
    them back into the original place.
       scene.do( ShuffleTiles( x_quads=4, y_quads=4, duration=10) )
    '''

    def start(self):
        super(ShuffleTiles,self).start()
        self.tiles = {}
        self.dst_tiles = {}
        for i in range(self.x_quads):
            for j in range(self.y_quads):
                self.tiles[(i,j)] = Tile( position = Point2(i,j), 
                                          start_position = Point2(i,j), 
                                          delta= self._get_delta(i,j) )

    def place_tile(self, i, j):
        t = self.tiles[(i,j)]

        for k in range(0,4):
            idx = (i * 4 * self.y_quads + j * 4 + k) * 2

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
            self.phase_sleep()
        else:
            self.phase_shuffle_back( (t-2.0/3) / (1.0/3) )

    def phase_shuffle(self, t ):
        for i in range(0, self.x_quads):
            for j in range(0, self.y_quads):
                self.tiles[(i,j)].position = self.tiles[(i,j)].start_position + self.tiles[(i,j)].delta * t
                self.place_tile(i,j)
   
    def phase_shuffle_back(self, t):
        for i in range(0, self.x_quads):
            for j in range(0, self.y_quads):
                self.tiles[(i,j)].position = self.tiles[(i,j)].start_position + self.tiles[(i,j)].delta * (1-t)
                self.place_tile(i,j)
                
    def phase_sleep(self):
        return
                
    def __reversed__(self):
        return ShuffleTiles( x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)

    # private method
    def _get_delta(self, x, y):
        a = rr(0, self.x_quads), rr(0, self.y_quads)  
        if not self.dst_tiles.get(a, False):
            self.dst_tiles[ a ] = True
            return Point2(*a)-Point2(x,y)
        for i in range(a[0], self.x_quads):
            for j in range(self.y_quads):
                if not self.dst_tiles.get( (i,j), False):
                    self.dst_tiles[ (i,j) ] = True
                    return Point2(i,j)-Point2(x,y)
        for i in range(a[0]):
            for j in range(self.y_quads):
                if not self.dst_tiles.get( (i,j), False):
                    self.dst_tiles[ (i,j) ] = True
                    return Point2(i,j)-Point2(x,y)
        raise Exception("_get_delta() algorithm needs to be improved!. Blame the authors")

class Shaky( MeshGridAction):
    '''Shaky simulates an earthquake

       scene.do( Shaky( randrange=6, x_quads=4, y_quads=4, duration=10) )
    '''
    def init( self, randrange=6, *args, **kw ):
        super(Shaky,self).init(*args,**kw)
        self.randrange = randrange

    def update( self, t ):
        for i in range(0, self.x_quads+1):
            for j in range(0, self.y_quads+1):

                x = i* self.size_x
                y = j* self.size_y

                x += rr( -self.randrange, self.randrange )
                y += rr( -self.randrange, self.randrange )

                self.set_vertex( i,j, (x,y) )

    def __reversed__(self):
        return Shaky( randrange=self.randrage, x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)

class Liquid( MeshGridAction ):
    '''Liquid simulates the liquid effect

       scene.do( Liquid(x_quads=16, y_quads=16, duration=10) )
    '''

    def update( self, t ):
        elapsed = t * self.duration
            
        for i in range(1, self.x_quads):
            for j in range(1, self.y_quads):
                x = i* self.size_x
                y = j* self.size_y
                xpos = (x + (math.sin(elapsed*2 + x * .01) * self.size_x))
                ypos = (y + (math.sin(elapsed*2 + y * .01) * self.size_y)) 
                self.set_vertex( i,j, (xpos,ypos) )

    def __reversed__(self):
        return Liquid( x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)


class Sin( MeshGridAction ):
    '''Sin simulates math.sin effect both in the vertical and horizontal axis

       scene.do( Sin( vertical_sin=True, horizontal_sin=False, x_quads=16, y_quads=16, duration=10) )
    '''

    def init( self, horizontal_sin=True, vertical_sin=True, *args, **kw ):
        super(Sin, self).init( *args, **kw )
        self.horizontal_sin = horizontal_sin
        self.vertical_sin = vertical_sin

    def update( self, t ):
        elapsed = t * self.duration
        
        for i in range(0, self.x_quads+1):
            for j in range(0, self.y_quads+1):
                x = i* self.size_x
                y = j* self.size_y

                if self.vertical_sin:
                    xpos = (x + (math.sin(elapsed*2 + y * .01) * self.size_x))
                else:
                    xpos = x

                if self.horizontal_sin:
                    ypos = (y + (math.sin(elapsed*2 + x * .01) * self.size_y)) 
                else:
                    ypos = y

                self.set_vertex( i,j, (xpos,ypos) )

    def __reversed__(self):
        return Sin( horizontal_sin=self.horizontal_sin, vertical_sin=self.vertical_sin,
                    x_quads=self.x_quads, y_quads=self.y_quads,
                    duration=self.duration)


class Lens( MeshGridAction ):
    '''Liquid simulates the liquid effect

       scene.do( Lens(x_quads=16, y_quads=16, duration=10) )
    '''

    def start( self ):
        super(Lens,self).start()
        self.center_x= 320
        self.center_y= 240
        self.radius = 160
        self.lens_effect = 0.1

        self.go_left = True


    def update( self, t ):
        center_point = Point2( self.center_x, self.center_y)

        for i in range(0, self.x_quads+1):
            for j in range(0, self.y_quads+1):

                x = i* self.size_x
                y = j* self.size_y
                p = Point2( x,y )

                vect = center_point - p
                r = abs(vect)

                if r < self.radius:

                    pre_log = r/self.radius
                    if pre_log == 0:
                        pre_log = 0.001
                    l = math.log( pre_log )*self.lens_effect
                    r = math.exp( l ) * self.radius

                    vect.normalize()
                    new_vect = vect * r

                    x -= new_vect.x
                    y -= new_vect.y

                self.set_vertex( i,j, (x,y) )

#        if self.go_left:
#            self.center_x -= 2.5 
#            if self.center_x < 40:
#                self.go_left = False
#        else:
#            self.center_x += 2.5 
#            if self.center_x > 620:
#                self.go_left = True

    def __reversed__(self):
        return Lens( x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)

class GridNop( MeshGridAction ):
    '''Liquid simulates the liquid effect

       scene.do( Twist(x_quads=16, y_quads=16, duration=10) )
    '''

    def nop_update( self, t ):
        for i in range(0, self.x_quads+1):
            for j in range(0, self.y_quads+1):
                x = i* self.size_x
                y = j* self.size_y
                self.set_vertex( i,j, (x,y) )
    def __reversed__(self):
        return Twist( x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)

class QuadMoveBy( MeshGridAction ):
    '''QuadMoveBy moves each vertex of the quad

       scene.do( QuadMoveBy( vertex0, vertex1, vertex2, vertex3, duration) )

       Vertex positions::

            vertex3 --<-- vertex2
                |            |
                v            ^
                |            |
            vertex0 -->-- vertex1
       '''

    def init( self, vertex0=(0,0), vertex1=(0,0), vertex2=(0,0), vertex3=(0,0), x_quads=1, y_quads=1, *args, **kw ):
        '''Initializes the QuadMoveBy

        :Parameters:
            `vertex0` : (x,y)
                The bottom-left relative coordinate
            `vertex1` : (x,y)
                The bottom-right relative coordinate
            `vertex2` : (x,y)
                The top-right relative coordinate
            `vertex3` : (x,y)
                The top-left relative coordinate
        '''
        super( QuadMoveBy, self).init( x_quads, y_quads, *args, **kw )
        self.delta0 = Point2( *vertex0 )
        self.delta1 = Point2( *vertex1 )
        self.delta2 = Point2( *vertex2 )
        self.delta3 = Point2( *vertex3 )

    def start( self ):
        super(QuadMoveBy,self).start()
        self.start_position0 = self.get_vertex( 0, 0)
        self.start_position1 = self.get_vertex( 1, 0)
        self.start_position2 = self.get_vertex( 1, 1)
        self.start_position3 = self.get_vertex( 0, 1)
        
    def update( self, t ):
        new_pos0 = self.start_position0 + self.delta0 * t
        new_pos1 = self.start_position1 + self.delta1 * t
        new_pos2 = self.start_position2 + self.delta2 * t
        new_pos3 = self.start_position3 + self.delta3 * t

        self.set_vertex( 0,0, new_pos0 )
        self.set_vertex( 1,0, new_pos1 )
        self.set_vertex( 1,1, new_pos2 )
        self.set_vertex( 0,1, new_pos3 )

    def __reversed__(self):
        return QuadMoveBy(-self.delta0, -self.delta1, -self.delta2, -self.delta3, self.x_quads, self.y_quads, self.duration)
