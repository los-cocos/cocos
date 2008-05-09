# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008 Daniel Moisset, Ricardo Quesada, Rayentray Tappa, Lucio Torre
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
'''Camera Actions

Actions that moves the OpenGL camera.
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
        if not (self.target.grid and self.target.grid.active):
            raise CameraException("An active Grid is needed to run a Camera3DAction")

        self.camera_eye_orig =  self.target.grid.camera_eye
        self.camera_center_orig = self.target.grid.camera_center
        self.camera_up_orig = self.target.grid.camera_up

    def stop( self ):
        super(Camera3DAction, self).stop()
        self.target.grid.camera_eye = self.camera_eye_orig
        self.target.grid.camera_center = self.camera_center_orig
        self.target.grid.camera_up = self.camera_up_orig

    def __reversed__( self ):
        return _ReverseTime( self )


class OrbitCamera( Camera3DAction ):
    '''Orbits the camera around the center of the screen using spherical coordinates
    It doesn't transform a grid, but it needs that a grid is active to work, otherwise
    it will raise an exception.
    '''
    def init( self, radius=1, delta_radius=0, angle_z=0, delta_z=0, angle_x=0, delta_x=0, *args, **kw ):
        '''Initialize the camera with spherical coordinates

        :Parameters:
            `radius` : float
                Radius of the orbit. Default: best distance for the current fov
            `delta_radius` : float
                Radius of the orbit. Default: best distance for the current fov
            `angle_z` : float
                The zenith angle of the spherical coordinate in degrees. Default: 0
            `delta_z` : float
                Relative movement of the zenith angle. Default: 0
            `angle_x` : float
                The azimuth angle of the spherical coordinate in degrees. Default: 0
            `delta_x` : float
                Relative movement of the azimuth angle. Default: 0
                

        For more information regarding spherical coordinates, read this:
            http://en.wikipedia.org/wiki/Spherical_coordinates

        '''
        super( OrbitCamera, self ).init( *args, **kw )

        width, height = director.get_window_size()

        self.radius = radius
        self.delta_radius = delta_radius
        self.rad_x = math.radians( angle_x )
        self.rad_z = math.radians( angle_z )
        self.rad_delta_x= math.radians( delta_x )
        self.rad_delta_z = math.radians( delta_z )

    def start( self ):
        super( OrbitCamera, self).start()

        if self.radius == -1:
            self.radius = self.target.grid.get_z_eye()

    def update( self, t ):
        r = (self.radius + self.delta_radius * t) * self.target.grid.get_z_eye()
        z_angle = self.rad_z + self.rad_delta_z * t
        x_angle = self.rad_x + self.rad_delta_x * t

        # using spherical coordinates
        p = Point3( math.sin(z_angle) * math.cos(x_angle),
                    math.sin(z_angle) * math.sin(x_angle),
                    math.cos(z_angle) )

        p = p * r
        d = p + self.camera_center_orig
        self.target.grid.camera_eye = d
