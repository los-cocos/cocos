# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2011 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
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
'''Particle system engine'''

__docformat__ = 'restructuredtext'

import random
import pyglet
from pyglet.gl import *
import math
import copy
import numpy
import ctypes

from cocosnode import CocosNode
from euclid import Point2

class ExceptionNoEmptyParticle(Exception):
    """particle system have no room for another particle"""
    pass

rand = lambda: random.random() * 2 - 1

# PointerToNumpy by Gary Herron
# from pyglet's user list
def PointerToNumpy(a, ptype=ctypes.c_float):
    a = numpy.ascontiguousarray(a)           # Probably a NO-OP, but perhaps not
    return a.ctypes.data_as(ctypes.POINTER(ptype)) # Ugly and undocumented! 

class Color( object ):
    def __init__( self, r,g,b,a ):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_array(self):
        return self.r, self.g, self.b, self.a


class ParticleSystem( CocosNode ):

    # type of particle
    POSITION_FREE, POSITION_GROUPED = range(2)

    #: is the particle system active ?
    active = True

    #: duration in seconds of the system. -1 is infinity
    duration = 0

    #: time elapsed since the start of the system (in seconds)
    elapsed = 0

    #: Gravity of the particles
    gravity = Point2(0.0, 0.0)

    #: position is from "superclass" CocosNode
    #: Position variance
    pos_var = Point2(0.0, 0.0)

    #: The angle (direction) of the particles measured in degrees
    angle = 0.0
    #: Angle variance measured in degrees;
    angle_var = 0.0

    #: The speed the particles will have.
    speed = 0.0
    #: The speed variance
    speed_var = 0.0

    #: Tangential acceleration
    tangential_accel = 0.0
    #: Tangential acceleration variance
    tangential_accel_var = 0.0

    #: Radial acceleration
    radial_accel = 0.0
    #: Radial acceleration variance
    radial_accel_var = 0.0

    #: Size of the particles
    size = 0.0
    #: Size variance
    size_var = 0.0

    #: How many seconds will the particle live
    life = 0
    #: Life variance
    life_var = 0

    #: Start color of the particles
    start_color = Color(0.0,0.0,0.0,0.0)
    #: Start color variance
    start_color_var = Color(0.0,0.0,0.0,0.0)
    #: End color of the particles
    end_color = Color(0.0,0.0,0.0,0.0)
    #: End color variance
    end_color_var = Color(0.0,0.0,0.0,0.0)

    #: Maximum particles
    total_particles = 0

    #:texture of the particles
    texture = pyglet.resource.image('fire.png').texture

    #:blend additive
    blend_additive = False

    #:color modulate
    color_modulate = True

    # position type
    position_type = POSITION_GROUPED

    def __init__(self):
        super(ParticleSystem,self).__init__()

        # particles
        # position x 2
        self.particle_pos = numpy.zeros( (self.total_particles, 2), numpy.float32 )
        # direction x 2
        self.particle_dir = numpy.zeros( (self.total_particles, 2), numpy.float32 )
        # rad accel x 1
        self.particle_rad = numpy.zeros( (self.total_particles, 1), numpy.float32 )
        # tan accel x 1
        self.particle_tan = numpy.zeros( (self.total_particles, 1), numpy.float32 )
        # gravity x 2
        self.particle_grav = numpy.zeros( (self.total_particles, 2), numpy.float32 )
        # colors x 4
        self.particle_color = numpy.zeros( (self.total_particles, 4), numpy.float32 )
        # delta colors x 4
        self.particle_delta_color = numpy.zeros( (self.total_particles, 4), numpy.float32 )
        # life x 1
        self.particle_life = numpy.zeros( (self.total_particles, 1), numpy.float32 )
        self.particle_life.fill(-1.0)
        # size x 1
        self.particle_size = numpy.zeros( (self.total_particles, 1), numpy.float32 )
        # start position
        self.start_pos = numpy.zeros( (self.total_particles, 2), numpy.float32 )

        #: How many particles can be emitted per second
        self.emit_counter = 0
        
        #: Count of particles
        self.particle_count = 0

        #: auto remove when particle finishes
        self.auto_remove_on_finish = False

        self.schedule( self.step )

    def on_enter( self ):
        super( ParticleSystem, self).on_enter()
        #self.add_particle()

    def draw( self ):
        glPushMatrix()
        self.transform()

        glPointSize( self.size )

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id )

        glEnable(GL_POINT_SPRITE)
        glTexEnvi( GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE )


        glEnableClientState(GL_VERTEX_ARRAY)
        vertex_ptr = PointerToNumpy( self.particle_pos )
        glVertexPointer(2,GL_FLOAT,0,vertex_ptr);

        glEnableClientState(GL_COLOR_ARRAY)
        color_ptr = PointerToNumpy( self.particle_color)
        glColorPointer(4,GL_FLOAT,0,color_ptr);

        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        if self.blend_additive:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE);
        else:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

#        mode = GLint()
#        glTexEnviv( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, mode )
#
#        if self.color_modulate:
#            glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE )
#        else:
#            glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE )


        glDrawArrays(GL_POINTS, 0, self.total_particles);

        # un -blend
        glPopAttrib()

#        # restore env mode
#        glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, mode)

        # disable states
        glDisableClientState(GL_COLOR_ARRAY);
        glDisableClientState(GL_VERTEX_ARRAY);
        glDisable(GL_POINT_SPRITE);
        glDisable(GL_TEXTURE_2D);

        glPopMatrix()


    def step( self, delta ):

        # update particle count
        self.particle_count = numpy.sum( self.particle_life >= 0 )

        if self.active:
            rate = 1.0 / self.emission_rate
            self.emit_counter += delta

#            if random.random() < 0.01:
#                delta += 0.5

            while self.particle_count < self.total_particles and self.emit_counter > rate:
                self.add_particle()
                self.emit_counter -= rate

            self.elapsed += delta

            if self.duration != -1 and self.duration < self.elapsed:
                self.stop_system()

        self.update_particles( delta )

        if (not self.active and
            self.particle_count == 0 and self.auto_remove_on_finish == True):
            self.unschedule( self.step )
            self.parent.remove( self )

    def add_particle( self ):
        """
        Code calling add_particle must be either:
          be sure there is room for the particle
          or
          be prepared to catch the exception ExceptionNoEmptyParticle
          It is acceptable to try: ... except...: pass
        """
        self.init_particle()
        self.particle_count += 1

    def stop_system( self ):
        self.active = False
        self.elapsed= self.duration
        self.emit_counter = 0

    def reset_system( self ):
        self.elapsed= self.duration
        self.emit_counter = 0

    def update_particles( self, delta ):
        # radial: posx + posy
        norm = numpy.sqrt( self.particle_pos[:,0] ** 2 + self.particle_pos[:,1] ** 2 )
        # XXX prevent div by 0
        norm = numpy.select( [norm==0], [0.0000001], default=norm )
        posx = self.particle_pos[:,0] / norm
        posy = self.particle_pos[:,1] / norm

        radial = numpy.array( [posx, posy] )
        tangential = numpy.array( [-posy, posx] )

        # update dir
        radial = numpy.swapaxes(radial,0,1)
        radial *= self.particle_rad
        tangential = numpy.swapaxes(tangential,0,1)
        tangential *= self.particle_tan

        self.particle_dir +=  (tangential + radial + self.particle_grav) * delta

        # update pos with updated dir
        self.particle_pos += self.particle_dir * delta

        # life
        self.particle_life -= delta


        # position: free or grouped
        if self.position_type == self.POSITION_FREE:
            tuple = numpy.array( [self.x, self.y] )
            tmp = tuple - self.start_pos
            self.particle_pos -= tmp


        # color
        self.particle_color += self.particle_delta_color * delta

        # if life < 0, set alpha in 0
        self.particle_color[:,3] = numpy.select( [self.particle_life[:,0] < 0], [0], default=self.particle_color[:,3] )

#        print self.particles[0]
#        print self.pas[0,0:4]

    def init_particle( self ):
        # position
#        p=self.particles[idx]

        a = self.particle_life < 0
        idxs = a.nonzero()

        idx = -1

        if len(idxs[0]) > 0:
            idx = idxs[0][0] 
        else:
            raise ExceptionNoEmptyParticle()

        # position
        self.particle_pos[idx][0] = self.pos_var.x * rand()
        self.particle_pos[idx][1] = self.pos_var.y * rand()

        # start position
        self.start_pos[idx][0] = self.x
        self.start_pos[idx][1] = self.y

        a = math.radians( self.angle + self.angle_var * rand() )
        v = Point2( math.cos( a ), math.sin( a ) )
        s = self.speed + self.speed_var * rand()

        dir = v * s

        # direction
        self.particle_dir[idx][0] = dir.x
        self.particle_dir[idx][1] = dir.y

        # radial accel
        self.particle_rad[idx] = self.radial_accel + self.radial_accel_var * rand()


        # tangential accel
        self.particle_tan[idx] = self.tangential_accel + self.tangential_accel_var * rand()
        
        # life
        life = self.particle_life[idx] = self.life + self.life_var * rand()

        # Color
        # start
        sr = self.start_color.r + self.start_color_var.r * rand()
        sg = self.start_color.g + self.start_color_var.g * rand()
        sb = self.start_color.b + self.start_color_var.b * rand()
        sa = self.start_color.a + self.start_color_var.a * rand()

        self.particle_color[idx][0] = sr
        self.particle_color[idx][1] = sg
        self.particle_color[idx][2] = sb
        self.particle_color[idx][3] = sa

        # end
        er = self.end_color.r + self.end_color_var.r * rand()
        eg = self.end_color.g + self.end_color_var.g * rand()
        eb = self.end_color.b + self.end_color_var.b * rand()
        ea = self.end_color.a + self.end_color_var.a * rand()

        delta_color_r = (er - sr) / life
        delta_color_g = (eg - sg) / life
        delta_color_b = (eb - sb) / life
        delta_color_a = (ea - sa) / life

        self.particle_delta_color[idx][0] = delta_color_r
        self.particle_delta_color[idx][1] = delta_color_g
        self.particle_delta_color[idx][2] = delta_color_b
        self.particle_delta_color[idx][3] = delta_color_a

        # size
        self.particle_size[idx] = self.size + self.size_var * rand()

        # gravity
        self.particle_grav[idx][0] = self.gravity.x
        self.particle_grav[idx][1] = self.gravity.y
