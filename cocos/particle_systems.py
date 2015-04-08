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
"""Pre-defined Particle Systems"""

from __future__ import division, print_function, unicode_literals

__all__ = ['Fireworks', 'Spiral', 'Meteor', 'Sun', 'Fire', 'Galaxy', 'Flower', 'Explosion', 'Smoke']

from cocos.particle import ParticleSystem, Color
from cocos.euclid import Point2


class Fireworks(ParticleSystem):

    # total particles
    total_particles = 3000

    # duration
    duration = -1

    # gravity
    gravity = Point2(0, -90)

    # angle
    angle = 90
    angle_var = 20

    # radial
    radial_accel = 0
    radial_accel_var = 0

    # speed of particles
    speed = 180
    speed_var = 50

    # emitter variable position
    pos_var = Point2(0, 0)

    # life of particles
    life = 3.5
    life_var = 1

    # emits per frame
    emission_rate = total_particles / life

    # color of particles
    start_color = Color(0.5, 0.5, 0.5, 1.0)
    start_color_var = Color(0.5, 0.5, 0.5, 1.0)
    end_color = Color(0.1, 0.1, 0.1, 0.2)
    end_color_var = Color(0.1, 0.1, 0.1, 0.2)

    # size, in pixels
    size = 8.0
    size_var = 2.0

    # blend additive
    blend_additive = False

    # color modulate
    color_modulate = True


class Explosion(ParticleSystem):

    # total particle
    total_particles = 700

    # duration
    duration = 0.1

    # gravity
    gravity = Point2(0, -90)

    # angle
    angle = 90.0
    angle_var = 360.0

    # radial
    radial_accel = 0
    radial_accel_var = 0

    # speed of particles
    speed = 70.0
    speed_var = 40.0

    # emitter variable position
    pos_var = Point2(0, 0)

    # life of particles
    life = 5.0
    life_var = 2.0

    # emits per frame
    emission_rate = total_particles / duration

    # color of particles
    start_color = Color(0.7, 0.2, 0.1, 1.0)
    start_color_var = Color(0.5, 0.5, 0.5, 0.0)
    end_color = Color(0.5, 0.5, 0.5, 0.0)
    end_color_var = Color(0.5, 0.5, 0.5, 0.0)

    # size, in pixels
    size = 15.0
    size_var = 10.0

    # blend additive
    blend_additive = False

    # color modulate
    color_modulate = True


class Fire(ParticleSystem):

    # total particles
    total_particles = 250

    # duration
    duration = -1

    # gravity
    gravity = Point2(0, 0)

    # angle
    angle = 90.0
    angle_var = 10.0

    # radial
    radial_accel = 0
    radial_accel_var = 0

    # speed of particles
    speed = 60.0
    speed_var = 20.0

    # emitter variable position
    pos_var = Point2(40, 20)

    # life of particles
    life = 3.0
    life_var = 0.25

    # emits per frame
    emission_rate = total_particles / life

    # color of particles
    start_color = Color(0.76, 0.25, 0.12, 1.0)
    start_color_var = Color(0.0, 0.0, 0.0, 0.0)
    end_color = Color(0.0, 0.0, 0.0, 1.0)
    end_color_var = Color(0.0, 0.0, 0.0, 0.0)

    # size, in pixels
    size = 100.0
    size_var = 10.0

    # blend additive
    blend_additive = True

    # color modulate
    color_modulate = True


class Flower(ParticleSystem):

    # total particles
    total_particles = 500

    # duration
    duration = -1

    # gravity
    gravity = Point2(0, 0)

    # angle
    angle = 90.0
    angle_var = 360.0

    # speed of particles
    speed = 80.0
    speed_var = 10.0

    # radial
    radial_accel = -60
    radial_accel_var = 0

    # tangential
    tangential_accel = 15.0
    tangential_accel_var = 0.0

    # emitter variable position
    pos_var = Point2(0, 0)

    # life of particles
    life = 4.0
    life_var = 1.0

    # emits per frame
    emission_rate = total_particles / life

    # color of particles
    start_color = Color(0.5, 0.5, 0.5, 1.0)
    start_color_var = Color(0.5, 0.5, 0.5, 0.0)
    end_color = Color(0.0, 0.0, 0.0, 1.0)
    end_color_var = Color(0.0, 0.0, 0.0, 0.0)

    # size, in pixels
    size = 30.0
    size_var = 0.0

    # blend additive
    blend_additive = True

    # color modulate
    color_modulate = True


class Sun(ParticleSystem):

    # total particles
    total_particles = 350

    # duration
    duration = -1

    # gravity
    gravity = Point2(0, 0)

    # angle
    angle = 90.0
    angle_var = 360.0

    # speed of particles
    speed = 20.0
    speed_var = 5.0

    # radial
    radial_accel = 0
    radial_accel_var = 0

    # tangential
    tangential_accel = 0.0
    tangential_accel_var = 0.0

    # emitter variable position
    pos_var = Point2(0, 0)

    # life of particles
    life = 1.0
    life_var = 0.5

    # emits per frame
    emission_rate = total_particles / life

    # color of particles
    start_color = Color(0.75, 0.25, 0.12, 1.0)
    start_color_var = Color(0.0, 0.0, 0.0, 0.0)
    end_color = Color(0.0, 0.0, 0.0, 0.0)
    end_color_var = Color(0.0, 0.0, 0.0, 0.0)

    # size, in pixels
    size = 40.0
    size_var = 00.0

    # blend additive
    blend_additive = True

    # color modulate
    color_modulate = True


class Spiral(ParticleSystem):

    # total paticles
    total_particles = 500

    # duration
    duration = -1

    # gravity
    gravity = Point2(0, 0)

    # angle
    angle = 90.0
    angle_var = 0.0

    # speed of particles
    speed = 150.0
    speed_var = 0.0

    # radial
    radial_accel = -380
    radial_accel_var = 0

    # tangential
    tangential_accel = 45.0
    tangential_accel_var = 0.0

    # emitter variable position
    pos_var = Point2(0, 0)

    # life of particles
    life = 12.0
    life_var = 0.0

    # emits per frame
    emission_rate = total_particles / life

    # color of particles
    start_color = Color(0.5, 0.5, 0.5, 1.0)
    start_color_var = Color(0.5, 0.5, 0.5, 0.0)
    end_color = Color(0.5, 0.5, 0.5, 1.0)
    end_color_var = Color(0.5, 0.5, 0.5, 0.0)

    # size, in pixels
    size = 20.0
    size_var = 10.0

    # blend additive
    blend_additive = True

    # color modulate
    color_modulate = True


class Meteor(ParticleSystem):

    # total particles
    total_particles = 150

    # duration
    duration = -1

    # gravity
    gravity = Point2(-200, 100)

    # angle
    angle = 90.0
    angle_var = 360.0

    # speed of particles
    speed = 15.0
    speed_var = 5.0

    # radial
    radial_accel = 0
    radial_accel_var = 0

    # tangential
    tangential_accel = 0.0
    tangential_accel_var = 0.0

    # emitter variable position
    pos_var = Point2(0, 0)

    # life of particles
    life = 2.0
    life_var = 1.0

    # size, in pixels
    size = 60.0
    size_var = 10.0

    # emits per frame
    emission_rate = total_particles / life

    # color of particles
    start_color = Color(0.2, 0.7, 0.7, 1.0)
    start_color_var = Color(0.0, 0.0, 0.0, 0.2)
    end_color = Color(0.0, 0.0, 0.0, 1.0)
    end_color_var = Color(0.0, 0.0, 0.0, 0.0)

    # blend additive
    blend_additive = True

    # color modulate
    color_modulate = True


class Galaxy(ParticleSystem):

    # total particles
    total_particles = 200

    # duration
    duration = -1

    # gravity
    gravity = Point2(0, 0)

    # angle
    angle = 90.0
    angle_var = 360.0

    # speed of particles
    speed = 60.0
    speed_var = 10.0

    # radial
    radial_accel = -80.0
    radial_accel_var = 0

    # tangential
    tangential_accel = 80.0
    tangential_accel_var = 0.0

    # emitter variable position
    pos_var = Point2(0, 0)

    # life of particles
    life = 4.0
    life_var = 1.0

    # size, in pixels
    size = 37.0
    size_var = 10.0

    # emits per frame
    emission_rate = total_particles / life

    # color of particles
    start_color = Color(0.12, 0.25, 0.76, 1.0)
    start_color_var = Color(0.0, 0.0, 0.0, 0.0)
    end_color = Color(0.0, 0.0, 0.0, 0.0)
    end_color_var = Color(0.0, 0.0, 0.0, 0.0)

    # blend additive
    blend_additive = True

    # color modulate
    color_modulate = True


class Smoke(ParticleSystem):

    # total particles
    total_particles = 80

    # duration
    duration = -1

    # gravity
    gravity = Point2(0, 0)

    # angle
    angle = 90.0
    angle_var = 10.0

    # speed of particles
    speed = 25.0
    speed_var = 10.0

    # radial
    radial_accel = 5
    radial_accel_var = 0

    # tangential
    tangential_accel = 0.0
    tangential_accel_var = 0.0

    # emitter variable position
    pos_var = Point2(0.1, 0)

    # life of particles
    life = 4.0
    life_var = 1.0

    # size, in pixels
    size = 40.0
    size_var = 10.0

    # emits per frame
    emission_rate = total_particles / life

    start_color = Color(0.5, 0.5, 0.5, 0.1)
    start_color_var = Color(0, 0, 0, 0.1)
    end_color = Color(0.5, 0.5, 0.5, 0.1)
    end_color_var = Color(0, 0, 0, 0.1)

    # blend additive
    blend_additive = True

    # color modulate
    color_modulate = False
