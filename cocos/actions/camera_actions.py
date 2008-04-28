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
            'OrbitCamera',
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

class OrbitCamera( Camera3DAction ):
    '''Orbits the camera around the center of the screen using spherical coordinates'''
    def init( self, radius=1, delta_radius=0, angle_z=0, delta_z=0, angle_x=0, delta_x=0, *args, **kw ):
        '''Initialize the camera with spherical coordinates

        :Parameters:
            `radius` : float
                Radius of the orbit. Default: best distance for the current fov
            `delta_radius` : float
                Radius of the orbit. Default: best distance for the current fov
            `angle_z` : float
                The zenith angle of the spherical coordinate in degress. Default: 0
            `delta_z` : float
                Relative movement of the zenith angle. Default: 0
            `angle_x` : float
                The tita angle of the spherical coordinate in degress. Default: 0
            `delta_x` : float
                Relative movement of the tita angle. Default: 0
                

        For more information on spherical coordinates, read this:
            http://en.wikipedia.org/wiki/Polar_coordinates#Spherical_coordinates

        '''
        super( OrbitCamera, self ).init( *args, **kw )

        width, height = director.get_window_size()
        if radius==-1:
            radius=415

        self.radius = radius
        self.delta_radius = delta_radius
        self.rad_x = math.radians( angle_x )
        self.rad_z = math.radians( angle_z )
        self.rad_delta_x= math.radians( delta_x )
        self.rad_delta_z = math.radians( delta_z )

    def update( self, t ):
        r = (self.radius + self.delta_radius * t) * 415
        z_angle = self.rad_z + self.rad_delta_z * t
        x_angle = self.rad_x + self.rad_delta_x * t

        # using spherical coordinates, ofcourse
        p = Point3( math.sin(z_angle) * math.cos(x_angle),
                    math.sin(z_angle) * math.sin(x_angle),
                    math.cos(z_angle) )

        p = p * r
        d = p + self.camera_center_orig
        self.target.grid.camera_eye = d
