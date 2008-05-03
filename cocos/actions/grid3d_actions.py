#
# Cocos:
# http://code.google.com/p/los-cocos/
#
'''Implementation of `Grid3DAction` actions
'''
__docformat__ = 'restructuredtext'

import math
import random

from cocos.director import director
from cocos.euclid import *
from basegrid_actions import *

rr = random.randrange


__all__ = [
           'Waves3D',   # 3d actions that modifies the z-coordinate
           'FlipX3D',
           'FlipY3D',
           'Lens3D',
           'Shaky3D',

           'Liquid',    # 3d actions that don't modify the z-coordinate
           'Waves',

           ]

class Waves3D( Grid3DAction ):
    '''Simulates waves using the math.sin() function in the z-axis

       scene.do( Waves3D( waves=5, amplitude=40, grid=(16,16), duration=10) )
    '''

    def init( self, waves=4, amplitude=20, *args, **kw ):
        '''
        :Parameters:
            `waves` : int
                Number of waves (2 * pi) that the action will perform. Default is 4
            `amplitude` : int
                Wave amplitude (height). Default is 20
        '''
        super(Waves3D, self).init( *args, **kw )

        #: Total number of waves to perform
        self.waves=waves
  
        #: amplitude rate. Default: 1.0
        #: This value is modified by other actions like `AccelAmplitude`.
        self.amplitude_rate = 1.0
        self.amplitude=amplitude

    def update( self, t ):
        for i in range(0, self.grid.x+1):
            for j in range(0, self.grid.y+1):
                x,y,z = self.get_original_vertex(i,j)

                z += (math.sin(t*math.pi*self.waves*2 + (y+x) * .01) * self.amplitude * self.amplitude_rate )

                self.set_vertex( i,j, (x, y, z) )

 
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

        x0,y,z = self.get_original_vertex(1,1)
        x1,y,z = self.get_original_vertex(0,0)
        
        if x0 > x1:
            # Normal Grid
            a = (0,0)
            b = (0,1)
            c = (1,0)
            d = (1,1)
            x = x0
        else:
            # Reversed Grid
            c = (0,0)
            d = (0,1)
            a = (1,0)
            b = (1,1)
            x = x1

        diff_x = x - x * mx
        diff_z = abs( (x * mz) // 4.0 )
 
        # bottom-left
        x,y,z = self.get_original_vertex(*a)
        self.set_vertex(a[0],a[1],(diff_x,y,z+diff_z))

        # upper-left
        x,y,z = self.get_original_vertex(*b)
        self.set_vertex(b[0],b[1],(diff_x,y,z+diff_z))

        # bottom-right
        x,y,z = self.get_original_vertex(*c)
        self.set_vertex(c[0],c[1],(x-diff_x,y,z-diff_z))

        # upper-right
        x,y,z = self.get_original_vertex(*d)
        self.set_vertex(d[0],d[1],(x-diff_x,y,z-diff_z))
    

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

        x,y0,z = self.get_original_vertex(1,1)
        x,y1,z = self.get_original_vertex(0,0)
        
        if y0 > y1:
            # Normal Grid
            a = (0,0)
            b = (0,1)
            c = (1,0)
            d = (1,1)
            y = y0
        else:
            # Reversed Grid
            b = (0,0)
            a = (0,1)
            d = (1,0)
            c = (1,1)
            y = y1

        diff_y = y - y * my
        diff_z = abs( (y * mz) // 4.0 )
 
        # bottom-left
        x,y,z = self.get_original_vertex(*a)
        self.set_vertex(a[0],a[1],(x,diff_y,z+diff_z))

        # upper-left
        x,y,z = self.get_original_vertex(*b)
        self.set_vertex(b[0],b[1],(x,y-diff_y,z-diff_z))

        # bottom-right
        x,y,z = self.get_original_vertex(*c)
        self.set_vertex(c[0],c[1],(x,diff_y,z+diff_z))

        # upper-right
        x,y,z = self.get_original_vertex(*d)
        self.set_vertex(d[0],d[1],(x,y-diff_y,z-diff_z))


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
            
        #: position of the center of the len. Type: (int,int)
        #: This value can be modified by other actions, like `JumpBy` to simulate a jumping lens
        self.position = Point2( center[0]+1, center[1]+1 )  

        #: radius of the lens. Type: float
        self.radius = radius

        #: lens effect factor. Type: float        
        self.lens_effect = lens_effect
       
        self._last_position = (-1000,-1000)          # dirty vrbl
        
    def update( self, t ):
        if self.position != self._last_position:
            for i in range(0, self.grid.x+1):
                for j in range(0, self.grid.y+1):
        
                    x,y,z = self.get_original_vertex(i,j)
                    
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
                    
                    # set all vertex, not only the on the changed
                    # since we want to 'fix' possible moved vertex
                    self.set_vertex( i,j, (x,y,z) )
            self._last_position = self.position

class Shaky3D( Grid3DAction):
    '''Shaky simulates an earthquake modifying randomly the x,y and z coordinates

       scene.do( Shaky3D( randrange=6, grid=(4,4), duration=10) )
    '''
    def init( self, randrange=6, *args, **kw ):
        '''
        :Parameters:
            `randrange` : int
                Number that will be used in random.randrange( -randrange, randrange) to do the effect
        '''
        super(Shaky3D,self).init(*args,**kw)
        self.randrange = randrange

    def update( self, t ):
        for i in range(0, self.grid.x+1):
            for j in range(0, self.grid.y+1):
                x,y,z = self.get_original_vertex(i,j)
                x += rr( -self.randrange, self.randrange )
                y += rr( -self.randrange, self.randrange )
                z += rr( -self.randrange, self.randrange )

                self.set_vertex( i,j, (x,y,z) )

class Liquid( Grid3DAction ):
    '''Simulates a liquid effect using the math.sin() function modifying the x and y coordinates.
        The z coordinate is not modified.

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
                x,y,z = self.get_original_vertex(i,j)
                xpos = (x + (math.sin(t*math.pi*self.waves*2 + x * .01) * self.amplitude * self.amplitude_rate))
                ypos = (y + (math.sin(t*math.pi*self.waves*2 + y * .01) * self.amplitude * self.amplitude_rate)) 
                self.set_vertex( i,j, (xpos,ypos,z) )


class Waves( Grid3DAction ):
    '''Simulates waves using the math.sin() function both in the vertical and horizontal axis.
    The z coordinate is not modified.

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
                x,y,z = self.get_original_vertex(i,j)
                if self.vertical_sin:
                    xpos = (x + (math.sin(t*math.pi*self.waves*2 + y * .01) * self.amplitude * self.amplitude_rate))
                else:
                    xpos = x

                if self.horizontal_sin:
                    ypos = (y + (math.sin(t*math.pi*self.waves*2 + x * .01) * self.amplitude * self.amplitude_rate)) 
                else:
                    ypos = y

                self.set_vertex( i,j, (xpos,ypos,z) )
