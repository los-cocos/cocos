#
# Cocos:
# http://code.google.com/p/los-cocos/
#
'''Camera Actions
'''

__docformat__ = 'restructuredtext'

from cocos.grid import Grid3D
from cocos.director import director
from cocos.euclid import *
from base_actions import *

import math

__all__ = [ 'CameraException',            # Camera Exceptions
           
            'Camera3DAction',
            'RotateCamera',
            ]

class CameraException( Exception ):
    pass

class Camera3DAction( IntervalAction ):
    def init( self,  duration=2):
        """Initialize the Camera Action

        :Parameters:
            `duration` : int 
                Number of seconds that the action will last
        """
        self.duration = duration

    def start( self ):        
        super(Camera3DAction, self).start()
        if not (self.target.grid and self.target.grid.active and isinstance(self.target.grid,Grid3D)):
            raise CameraException("An active Grid3D is needed to run a Camera3DAction")

        self.camera_eye_orig =  self.target.grid.camera_eye
        self.camera_center_orig = self.target.grid.camera_center
        self.camera_up_orig = self.target.grid.camera_up

    def stop( self ):
        super(Camera3DAction, self).stop()
        self.target.grid.camera_eye = self.camera_eye_orig
        self.target.grid.camera_center = self.camera_center_orig
        self.target.grid.camera_up = self.camera_up_orig

    def __reversed__( self ):
        return ReverseTime( self )

class RotateCamera( Camera3DAction ):
    '''Moves the camera around a 3D circle'''
    def init( self, eye=(-1,-1,-1), direction=45, degrees=360, *args, **kw ):
        '''Initialize the camera

        :Parameters:
            `eye` : (float,float,float)
                x,y,z coordiantes of the eye of the camera. Default(width/2, height/2, 415)
            `direction` : (float, float)
                vector (x,y) that defines the direction of the camera. Default: (1,0)
            `degrees` : float
                Determines how many degrees the camera will move. Default: (360)
        '''
        super( RotateCamera, self ).init( *args, **kw )

        width, height = director.get_window_size()
        if eye==(-1,-1,-1):
            eye = (width/2, height/2, 415)

        if not isinstance(eye, Point3):
            eye = Point3( *eye )

        self.eye = eye
        self.direction = math.radians(direction)
        self.degrees = degrees
        self.radians = math.radians(degrees)

    def start(self):
        super( RotateCamera, self).start()
        self.eye_len = abs( self.eye - Point3( *self.camera_center_orig) )

    def update( self, t ):
        # tenuki's formula to navigate the circle
        # r' = sen(a) * r
        # punto = (cos(a)*r, cos(b) * r' , sin(b)*r' )

        angle = self.radians * t

        r2 = math.sin(self.radians * t ) * self.eye_len
        z,y,x = math.cos(angle) * self.eye_len, math.cos( self.direction) * r2, math.sin(self.direction) * r2

        if z < 0:
            self.target.grid.camera_up = Point3( 0, -1, 0 )
        else:
            self.target.grid.camera_up = Point3( 0, 1, 0 )

        v = Point3(x,y,z)
        
        print v

        d = v + self.camera_center_orig
        self.target.grid.camera_eye = d
