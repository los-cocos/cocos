# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2015  Richard Jones, Claudio Canepa
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
"""Particle system engine"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import random
import math
import numpy
import ctypes

import pyglet
from pyglet import gl

from cocos.cocosnode import CocosNode
from cocos.euclid import Point2
from cocos.director import director
from cocos.shader import ShaderProgram

# for dev and diagnostic, None means real automatic, True / False means
# return this value inconditionally
forced_point_sprites = None


def point_sprites_available():
    """returns a bool telling if point sprites are available

    For development and diagonostic cocos.particle.forced_point_sprites could
    be set to force the desired return value
    """
    if forced_point_sprites is not None:
        return forced_point_sprites
    have_point_sprites = True
    try:
        gl.glEnable(gl.GL_POINT_SPRITE)
        gl.glDisable(gl.GL_POINT_SPRITE)
    except:
        have_point_sprites = False
    return have_point_sprites


class ExceptionNoEmptyParticle(Exception):
    """particle system have no room for another particle"""
    pass

rand = lambda: random.random() * 2 - 1


# PointerToNumpy by Gary Herron
# from pyglet's user list
def PointerToNumpy(a, ptype=ctypes.c_float):
    a = numpy.ascontiguousarray(a)           # Probably a NO-OP, but perhaps not
    return a.ctypes.data_as(ctypes.POINTER(ptype))  # Ugly and undocumented!


class Color(object):
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_array(self):
        return self.r, self.g, self.b, self.a


class ParticleSystem(CocosNode):
    """
    Base class for many flawors of cocos particle systems

    The most easy way to customize is subclass and redefine some class members;
    see particle_systems by example.

    If you want to use a custom texture remember it should hold only one image,
    so don't use texture = pyglet.resource.image(...) (it would produce an atlas,
    ie multiple images in a texture); using texture = pyglet.image.load(...) is fine
    """

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
    start_color = Color(0.0, 0.0, 0.0, 0.0)
    #: Start color variance
    start_color_var = Color(0.0, 0.0, 0.0, 0.0)
    #: End color of the particles
    end_color = Color(0.0, 0.0, 0.0, 0.0)
    #: End color variance
    end_color_var = Color(0.0, 0.0, 0.0, 0.0)

    #: Maximum particles
    total_particles = 0

    #: texture for the particles. Lazy loaded because Intel weakness, #235
    texture = None

    #: blend additive
    blend_additive = False

    #: color modulate
    color_modulate = True

    # position type
    position_type = POSITION_GROUPED

    def __init__(self, fallback=None):
        """
        fallback can be None, True, False; default is None
            False: use point sprites, faster, not always availabel
            True: use quads, slower but always available)
            None: autodetect, use the faster available

        """
        super(ParticleSystem, self).__init__()

        # particles
        # position x 2
        self.particle_pos = numpy.zeros((self.total_particles, 2), numpy.float32)
        # direction x 2
        self.particle_dir = numpy.zeros((self.total_particles, 2), numpy.float32)
        # rad accel x 1
        self.particle_rad = numpy.zeros((self.total_particles, 1), numpy.float32)
        # tan accel x 1
        self.particle_tan = numpy.zeros((self.total_particles, 1), numpy.float32)
        # gravity x 2
        self.particle_grav = numpy.zeros((self.total_particles, 2), numpy.float32)
        # colors x 4
        self.particle_color = numpy.zeros((self.total_particles, 4), numpy.float32)
        # delta colors x 4
        self.particle_delta_color = numpy.zeros((self.total_particles, 4), numpy.float32)
        # life x 1
        self.particle_life = numpy.zeros((self.total_particles, 1), numpy.float32)
        self.particle_life.fill(-1.0)
        # size x 1
        self.particle_size = numpy.zeros((self.total_particles, 1), numpy.float32)
        # particle size in respect to node scaling and window resizing
        self.particle_size_scaled = self.particle_size
        # start position
        self.start_pos = numpy.zeros((self.total_particles, 2), numpy.float32)

        #: How many particles can be emitted per second
        self.emit_counter = 0

        #: Count of particles
        self.particle_count = 0

        #: auto remove when particle finishes
        self.auto_remove_on_finish = False

        self.load_texture()

        #: rendering mode; True is quads, False is point_sprites, None is auto fallback
        if fallback is None:
            fallback = not point_sprites_available()
        self.fallback = fallback
        if fallback:
            self._fallback_init()
            self.draw = self.draw_fallback
        else:
            self._init_shader()

        self.schedule(self.step)

    def _init_shader(self):
        vertex_code = """
        #version 120
        attribute float particle_size;

        void main()
        {
            gl_PointSize = particle_size;
            gl_Position = ftransform();
            gl_FrontColor = gl_Color;
        }
        """
        frag_code = """
        #version 120
        uniform sampler2D sprite_texture;

        void main()
        {
            gl_FragColor = gl_Color * texture2D(sprite_texture, gl_PointCoord);
        }
        """
        self.sprite_shader = ShaderProgram.simple_program('sprite', vertex_code, frag_code)
        self.particle_size_idx = gl.glGetAttribLocation(self.sprite_shader.program, b'particle_size')

    def load_texture(self):
        if self.texture is None:
            pic = pyglet.image.load('fire.png', file=pyglet.resource.file('fire.png'))
            self.__class__.texture = pic.get_texture()

    def on_enter(self):
        super(ParticleSystem, self).on_enter()
        director.push_handlers(self)
        # self.add_particle()

    def on_exit(self):
        super(ParticleSystem, self).on_exit()
        director.remove_handlers(self)

    def on_cocos_resize(self, usable_width, usable_height):
        self._scale_particle_size()

    @CocosNode.scale.setter
    def scale(self, s):
        # Extend CocosNode scale setter property
        # The use of super(CocosNode, CocosNode).name.__set__(self, s) in the setter function is no mistake.
        # To delegate to the previous implementation of the setter, control needs to pass
        # through the __set__() method of the previously defined name property. However, the
        # only way to get to this method is to access it as a class variable instead of an instance
        # variable. This is what happens with the super(CocosNode, CocosNode) operation.
        super(ParticleSystem, ParticleSystem).scale.__set__(self, s)
        self._scale_particle_size()

    def _scale_particle_size(self):
        """Resize the particles in respect to node scaling and window resize;
        only used when rendering with shaders.
        """
        node = self
        scale = 1.0
        while node.parent:
            scale *= node.scale
            node = node.parent
        if director.autoscale:
            scale *= 1.0 * director._usable_width / director._window_virtual_width
        self.particle_size_scaled = self.particle_size * scale

    def draw(self):
        gl.glPushMatrix()
        self.transform()

        # color preserve - at least nvidia 6150SE needs that
        gl.glPushAttrib(gl.GL_CURRENT_BIT)
        # glPointSize(self.get_scaled_particle_size())

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
        # glBindTexture(GL_TEXTURE_2D, self.texture.id)


        gl.glEnable(gl.GL_POINT_SPRITE)
        gl.glTexEnvi(gl.GL_POINT_SPRITE, gl.GL_COORD_REPLACE, gl.GL_TRUE)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        vertex_ptr = PointerToNumpy(self.particle_pos)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, vertex_ptr)

        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        color_ptr = PointerToNumpy(self.particle_color)
        gl.glColorPointer(4, gl.GL_FLOAT, 0, color_ptr)

        gl.glEnableVertexAttribArray(self.particle_size_idx)

        size_ptr = PointerToNumpy(self.particle_size_scaled)
        gl.glVertexAttribPointer(self.particle_size_idx, 1, gl.GL_FLOAT,
            False, 0, size_ptr)

        gl.glPushAttrib(gl.GL_COLOR_BUFFER_BIT)
        gl.glEnable(gl.GL_BLEND)
        if self.blend_additive:
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
        else:
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # mode = GLint()
        # glTexEnviv( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, mode )
        #
        # if self.color_modulate:
        #   glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE )
        # else:
        #   glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE )

        self.sprite_shader.install()
        self.sprite_shader.usetTex('sprite_texture', 0, 
            gl.GL_TEXTURE_2D, self.texture.id)

        gl.glDrawArrays(gl.GL_POINTS, 0, self.total_particles)

        self.sprite_shader.uninstall()
        # un -blend
        gl.glPopAttrib()

        # color restore
        gl.glPopAttrib()

        # restore env mode
        # glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, mode)

        # disable states
        gl.glDisableVertexAttribArray(self.particle_size_idx)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

        gl.glDisable(gl.GL_POINT_SPRITE)
        gl.glDisable(gl.GL_PROGRAM_POINT_SIZE)
        gl.glDisable(gl.GL_TEXTURE_2D)

        gl.glPopMatrix()

    def step(self, delta):

        # update particle count
        self.particle_count = numpy.sum(self.particle_life >= 0)

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

        self.update_particles(delta)

        if (not self.active and
                self.particle_count == 0 and self.auto_remove_on_finish is True):
                self.unschedule(self.step)
                self.parent.remove(self)

    def add_particle(self):
        """
        Code calling add_particle must be either:
          be sure there is room for the particle
          or
          be prepared to catch the exception ExceptionNoEmptyParticle
          It is acceptable to try: ... except...: pass
        """
        self.init_particle()
        self.particle_count += 1

    def stop_system(self):
        self.active = False
        self.elapsed = self.duration
        self.emit_counter = 0

    def reset_system(self):
        self.elapsed = self.duration
        self.emit_counter = 0

    def update_particles(self, delta):
        # radial: posx + posy
        norm = numpy.sqrt(self.particle_pos[:, 0] ** 2 + self.particle_pos[:, 1] ** 2)
        # XXX prevent div by 0
        norm = numpy.select([norm == 0], [0.0000001], default=norm)
        posx = self.particle_pos[:, 0] / norm
        posy = self.particle_pos[:, 1] / norm

        radial = numpy.array([posx, posy])
        tangential = numpy.array([-posy, posx])

        # update dir
        radial = numpy.swapaxes(radial, 0, 1)
        radial *= self.particle_rad
        tangential = numpy.swapaxes(tangential, 0, 1)
        tangential *= self.particle_tan

        self.particle_dir += (tangential + radial + self.particle_grav) * delta

        # update pos with updated dir
        self.particle_pos += self.particle_dir * delta

        # life
        self.particle_life -= delta

        # position: free or grouped
        if self.position_type == self.POSITION_FREE:
            tuple = numpy.array([self.x, self.y])
            tmp = tuple - self.start_pos
            self.particle_pos -= tmp

        # color
        self.particle_color += self.particle_delta_color * delta

        # if life < 0, set alpha in 0
        self.particle_color[:, 3] = numpy.select([self.particle_life[:, 0] < 0], [0],
                                                 default=self.particle_color[:, 3])

        # print self.particles[0]
        # print self.pas[0,0:4]

    def init_particle(self):
        # position
        # p=self.particles[idx]

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

        a = math.radians(self.angle + self.angle_var * rand())
        v = Point2(math.cos(a), math.sin(a))
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
        self._scale_particle_size()

        # gravity
        self.particle_grav[idx][0] = self.gravity.x
        self.particle_grav[idx][1] = self.gravity.y

    # Below only fallback functionality.
    # It uses quads instehad of point sprites, doing a transformation
    # point sprites buffers -> quads buffer, so any change in point sprite mode
    # is automatically reflects in the fallback mode (except for changes in the
    # draw method which should be manually adapted

    def _fallback_init(self):
        self.vertexs = numpy.zeros((self.total_particles, 4, 2), numpy.float32)
        tex_coords_for_quad = numpy.array([[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0]], numpy.float32)
        self.tex_coords = numpy.zeros((self.total_particles, 4, 2), numpy.float32)
        self.tex_coords[:] = tex_coords_for_quad[numpy.newaxis, :, :]
        self.per_vertex_colors = numpy.zeros((self.total_particles, 4, 4), numpy.float32)
        self.delta_pos_to_vertex = numpy.zeros((self.total_particles, 4, 2), numpy.float32)

    def draw_fallback(self):
        self.make_delta_pos_to_vertex()
        self.update_vertexs_from_pos()
        self.update_per_vertex_colors()

        gl.glPushMatrix()
        self.transform()

        # color preserve - at least intel 945G needs that
        gl.glPushAttrib(gl.GL_CURRENT_BIT)

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture.id)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        vertexs_ptr = PointerToNumpy(self.vertexs)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, vertexs_ptr)

        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        color_ptr = PointerToNumpy(self.per_vertex_colors)
        # gl.glColorPointer(4, gl.GL_UNSIGNED_BYTE, 0, color_ptr)
        gl.glColorPointer(4, gl.GL_FLOAT, 0, color_ptr)

        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        tex_coord_ptr = PointerToNumpy(self.tex_coords)
        gl.glTexCoordPointer(2, gl.GL_FLOAT, 0, tex_coord_ptr)

        gl.glPushAttrib(gl.GL_COLOR_BUFFER_BIT)
        gl.glEnable(gl.GL_BLEND)
        if self.blend_additive:
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
        else:
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        gl.glDrawArrays(gl.GL_QUADS, 0, len(self.vertexs) * 4)

        # un -blend
        gl.glPopAttrib()

        # color restore
        gl.glPopAttrib()

        # disable states
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_TEXTURE_2D)

        gl.glPopMatrix()

    def update_vertexs_from_pos(self):
        vertexs = self.vertexs
        delta = self.delta_pos_to_vertex
        pos = self.particle_pos
        vertexs[:] = delta + pos[:, numpy.newaxis, :]

    def update_per_vertex_colors(self):
        colors = self.particle_color
        per_vertex_colors = self.per_vertex_colors
        per_vertex_colors[:] = colors[:, numpy.newaxis, :]

    def make_delta_pos_to_vertex(self):
        size2 = self.particle_size / 2.0

        # counter-clockwise
        self.delta_pos_to_vertex[:,0] = numpy.array([-size2, +size2]).T  # NW
        self.delta_pos_to_vertex[:,1] = numpy.array([-size2, -size2]).T  # SW
        self.delta_pos_to_vertex[:,2] = numpy.array([+size2, -size2]).T  # SE
        self.delta_pos_to_vertex[:,3] = numpy.array([+size2, +size2]).T  # NE
