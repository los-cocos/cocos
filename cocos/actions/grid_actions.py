#
# Cocos:
# http://code.google.com/p/los-cocos/
#
'''Implementation of `GridAction` actions
'''
__docformat__ = 'restructuredtext'

import math
import random

from cocos.director import director
from cocos.euclid import *
from basegrid_actions import *

rr = random.randrange


__all__ = [ 'Shaky',
           'Liquid',
           'Waves',
           'QuadMoveBy',
           'MoveCornerUp',
           'MoveCornerDown',
           'CornerSwap',
           'Flip',
           'FlipX',
           'FlipY',
           'SkewHorizontal',
           'SkewVertical',
           ]

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
                x,y = self.get_original_vertex(i,j)
                x += rr( -self.randrange, self.randrange )
                y += rr( -self.randrange, self.randrange )

                self.set_vertex( i,j, (x,y) )

class Liquid( GridAction ):
    '''Liquid simulates a liquid effect using the math.sin() function

       scene.do( Liquid( waves=5, amplitude=40, grid=(16,16), duration=10) )
    '''
    def init( self, waves=4, amplitude=20, *args, **kw ):
        '''
        :Parameters:
            `waves` : int
                Number of waves (2 * pi) that the action will perform. Default is 4
            `amplitude` : int
                Wave amplitude (height). Default is 20
        '''
        super(Liquid, self).init( *args, **kw )
        self.waves=waves
        self.amplitude=amplitude
        #: amplitude rate. Default: 1.0
        #: This value is modified by other actions like `AccelAmplitude`.
        self.amplitude_rate = 1.0

    def update( self, t ):
            
        for i in range(1, self.grid.x):
            for j in range(1, self.grid.y):
                x,y = self.get_original_vertex(i,j)
                xpos = (x + (math.sin(t*math.pi*self.waves*2 + x * .01) * self.amplitude * self.amplitude_rate))
                ypos = (y + (math.sin(t*math.pi*self.waves*2 + y * .01) * self.amplitude * self.amplitude_rate)) 
                self.set_vertex( i,j, (xpos,ypos) )


class Waves( GridAction ):
    '''Waves simulates waves using the math.sin() function both in the vertical and horizontal axis

        Example::

            scene.do( Waves( waves=4, vertical_sin=True, horizontal_sin=False, grid=(16,16), duration=10) )
    '''

    def init( self, waves=4, amplitude=20, horizontal_sin=True, vertical_sin=True, *args, **kw ):
        '''Initializes the Waves actions

        :Parameters:
            `waves` : int
                Number of waves (2 * pi) that the action will perform. Default is 4
            `amplitude` : int
                Wave amplitude (height). Default is 20
            `horizontal_sin` : bool
                whether or not in will perform horizontal waves. Default is True
            `vertical_sin` : bool
                whether or not in will perform vertical waves. Default is True
        '''
        super(Waves, self).init( *args, **kw )
        self.horizontal_sin = horizontal_sin
        self.vertical_sin = vertical_sin
        self.waves=waves
        self.amplitude=amplitude
        #: amplitude rate. Default: 1.0
        #: This value is modified by other actions like `AccelAmplitude`.
        self.amplitude_rate = 1.0

    def update( self, t ):        
        for i in range(0, self.grid.x+1):
            for j in range(0, self.grid.y+1):
                x,y = self.get_original_vertex(i,j)
                if self.vertical_sin:
                    xpos = (x + (math.sin(t*math.pi*self.waves*2 + y * .01) * self.amplitude * self.amplitude_rate))
                else:
                    xpos = x

                if self.horizontal_sin:
                    ypos = (y + (math.sin(t*math.pi*self.waves*2 + x * .01) * self.amplitude * self.amplitude_rate)) 
                else:
                    ypos = y

                self.set_vertex( i,j, (xpos,ypos) )


class QuadMoveBy( GridAction ):
    '''QuadMoveBy moves each vertex of the grid. The size of the grid is (1,1)

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
                Initial value for the bottom-right coordinate. Default is (win_size_x,0)
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

