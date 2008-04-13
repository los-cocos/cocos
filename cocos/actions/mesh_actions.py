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

from cocos.director import director
from cocos.euclid import *
from base_actions import *

__all__ = [ 'MeshAction','QuadMoveBy',  # Base classes

            'Shaky','ShakyTiles',       # Trembling actions
            'Liquid','Sin',             # liquid action
            'Lens','Twist',             # lens & Twist actions
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
        :returns: Returns the current value of x,y
        '''
        idx = self._get_vertex_idx( x,y,2 )
        x = self.target.mesh.vertex_list.vertices[idx]
        y = self.target.mesh.vertex_list.vertices[idx+1]
        return (x,y)

    def get_vertex_orig( self, x, y):
        '''Get the original vertex point value

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (int,int)
        :returns: Returns the original value of x,y
        '''
        idx = self._get_vertex_idx( i,j,2 )

        x = self.target.mesh.vertex_points[idx]
        y = self.target.mesh.vertex_points[idx+1]

        return (x,y)

class ShakyTiles( MeshAction ):
    '''ShakyTiles simulates a shaky floor composed of tiles

       scene.do( ShakyTiles( randrange=6, x_quads=4, y_quads=4, duration=10) )
    '''

    def init( self, randrange=6, *args, **kw ):
        super(ShakyTiles,self).init(*args,**kw)
        self.randrange = randrange

    def update( self, t ):
        rr = random.randrange

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
        return ShakyTiles( x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)

class Shaky( ShakyTiles ):
    '''Shaky simulates an earthquake

       scene.do( Shaky( randrange=6, x_quads=4, y_quads=4, duration=10) )
    '''

    def update( self, t ):
        rr = random.randrange
        for i in range(0, self.x_quads+1):
            for j in range(0, self.y_quads+1):

                x = i* self.size_x
                y = j* self.size_y

                x += rr( -self.randrange, self.randrange )
                y += rr( -self.randrange, self.randrange )

                self.set_vertex( i,j, (x,y) )

    def __reversed__(self):
        return Shaky( x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)

class Liquid( MeshAction ):
    '''Liquid simulates the liquid effect

       scene.do( Liquid(x_quads=16, y_quads=16, duration=10) )
    '''

    def update( self, t ):
        for i in range(1, self.x_quads):
            for j in range(1, self.y_quads):
                x = i* self.size_x
                y = j* self.size_y
                xpos = (x + (math.sin(self.elapsed*2 + x * .01) * self.size_x))
                ypos = (y + (math.sin(self.elapsed*2 + y * .01) * self.size_y)) 
                self.set_vertex( i,j, (xpos,ypos) )

    def __reversed__(self):
        return Liquid( x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)


class Sin( MeshAction ):
    '''Sin simulates math.sin effect both in the vertical and horizontal axis

       scene.do( Sin( vertical_sin=True, horizontal_sin=False, x_quads=16, y_quads=16, duration=10) )
    '''

    def init( self, horizontal_sin=True, vertical_sin=True, *args, **kw ):
        super(Sin, self).init( *args, **kw )
        self.horizontal_sin = horizontal_sin
        self.vertical_sin = vertical_sin

    def update( self, t ):
        for i in range(0, self.x_quads+1):
            for j in range(0, self.y_quads+1):
                x = i* self.size_x
                y = j* self.size_y
                if not self.vertical_sin:
                    xpos = x
                else:
                    xpos = (x + (math.sin(self.elapsed*2 + y * .01) * self.size_x))

                if not self.horizontal_sin:
                    ypos = y
                else:
                    ypos = (y + (math.sin(self.elapsed*2 + x * .01) * self.size_y)) 

                self.set_vertex( i,j, (xpos,ypos) )

    def __reversed__(self):
        return Liquid( x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)


class Lens( MeshAction ):
    '''Liquid simulates the liquid effect

       scene.do( Lens(x_quads=16, y_quads=16, duration=10) )
    '''

    def start( self ):
        super(Lens,self).start()
        self.center_x= 320
        self.center_y= 240
        self.radius = 80
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
                        pre_log = 0.00001
                    l = math.log( pre_log )*self.lens_effect
                    r = math.exp( l ) * self.radius

                    vect.normalize()
                    new_vect = vect * r

                    x -= new_vect.x
                    y -= new_vect.y

                self.set_vertex( i,j, (x,y) )

        if self.go_left:
            self.center_x -= 2.5 
            if self.center_x < 40:
                self.go_left = False
        else:
            self.center_x += 2.5 
            if self.center_x > 620:
                self.go_left = True

    def __reversed__(self):
        return Lens( x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)

class Twist( MeshAction ):
    '''Liquid simulates the liquid effect

       scene.do( Twist(x_quads=16, y_quads=16, duration=10) )
    '''

    def start( self ):
        super(Twist,self).start()
        self.center_x= 320
        self.center_y= 240
        self.radius = 180
        self.twist_effect = 0.1

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


                    angle = math.atan2(vect.x, vect.y) + self.radius * self.twist_effect

                    x += (r * math.cos(angle))
                    y += (r * math.sin(angle))

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
        return Twist( x_quads=self.x_quads, y_quads=self.y_quads, duration=self.duration)

class QuadMoveBy( MeshAction ):
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
