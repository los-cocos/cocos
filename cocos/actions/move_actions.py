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
"""Actions for moving things around based on their velocity and
acceleration.

The simplest usage:

    sprite = cocos.sprite.Sprite('ship.png')
    sprite.velocity = (100, 100)
    sprite.do(Move())

This will move the sprite (100, 100) pixels per second indefinitely.

Typically the sprite would be controlled by the user, so something like::

 keys = <standard pyglet keyboard state handler>

 class MoveShip(Move):
    def step(self, dt):
        super(MoveShip, self).step(dt)
        self.target.dr = (keys[key.RIGHT] - keys[key.LEFT]) * 360
        rotation = math.pi * self.target.rotation / 180.0
        rotation_x = math.cos(-rotation)
        rotation_y = math.sin(-rotation)
        if keys[key.UP]:
            self.target.acceleration = (200 * rotation_x, 200 * rotation_y)

 ship.do(MoveShip())

"""

from __future__ import division, print_function, unicode_literals


__docformat__ = 'restructuredtext'

__all__ = ['Move', 'WrappedMove', 'BoundedMove', 'Driver', ]

import math

from .base_actions import Action


class Move(Action):
    """Move the target based on parameters on the target.

    For movement the parameters are::

        target.position = (x, y)
        target.velocity = (dx, dy)
        target.acceleration = (ddx, ddy) = (0, 0)
        target.gravity = 0

    And rotation::

        target.rotation
        target.dr
        target.ddr
    """
    def step(self, dt):
        x, y = self.target.position
        dx, dy = self.target.velocity
        ddx, ddy = getattr(self.target, 'acceleration', (0, 0))
        gravity = getattr(self.target, 'gravity', 0)
        dx += ddx * dt
        dy += (ddy + gravity) * dt
        self.target.velocity = (dx, dy)
        x += dx * dt
        y += dy * dt
        self.target.position = (x, y)
        dr = getattr(self.target, 'dr', 0)
        ddr = getattr(self.target, 'ddr', 0)
        if dr or ddr:
            dr = self.target.dr = dr + ddr*dt
        if dr:
            self.target.rotation += dr * dt


class WrappedMove(Move):
    """Move the target but wrap position when it hits certain bounds.

    Wrap occurs outside of 0 < x < width and 0 < y < height taking into
    account the dimenstions of the target.
    """
    def init(self, width, height):
        """Init method.

        :Parameters:
            `width` : integer
                The width to wrap position at.
            `height` : integer
                The height to wrap position at.
        """
        self.width, self.height = width, height

    def step(self, dt):
        super(WrappedMove, self).step(dt)
        x, y = self.target.position
        w, h = self.target.width, self.target.height
        # XXX assumes center anchor
        if x > self.width + w/2:
            x -= self.width + w
        elif x < 0 - w/2:
            x += self.width + w
        if y > self.height + h/2:
            y -= self.height + h
        elif y < 0 - h/2:
            y += self.height + h
        self.target.position = (x, y)


class BoundedMove(Move):
    """Move the target but limit position when it hits certain bounds.

    Position is bounded to 0 < x < width and 0 < y < height taking into
    account the dimenstions of the target.
    """
    def init(self, width, height):
        """Init method.

        :Parameters:
            `width` : integer
                The width to bound position at.
            `height` : integer
                The height to bound position at.
        """
        self.width, self.height = width, height

    def step(self, dt):
        super(BoundedMove, self).step(dt)
        x, y = self.target.position
        w, h = self.target.width, self.target.height
        # XXX assumes center anchor
        if x > self.width - w/2:
            x = self.width - w/2
        elif x < w/2:
            x = w/2
        if y > self.height - h/2:
            y = self.height - h/2
        elif y < h/2:
            y = h/2
        self.target.position = (x, y)


class Driver(Action):
    """Drive a `CocosNode` object around like a car in x, y according to
    a direction and speed.

    Example::

        # control the movement of the given sprite
        sprite.do(Driver())

        ...
        sprite.rotation = 45
        sprite.speed = 100
        ...

    The sprite MAY have these parameters (beyond the standard position
    and rotation):

        `speed` : float
            Speed to move at in pixels per second in the direction of
            the target's rotation.
        `acceleration` : float
            If specified will automatically be added to speed.
            Specified in pixels per second per second.
        `max_forward_speed` : float (default None)
            Limits to apply to speed when updating with acceleration.
        `max_reverse_speed` : float (default None)
            Limits to apply to speed when updating with acceleration.
    """
    def step(self, dt):
        accel = getattr(self.target, 'acceleration', 0)
        speed = getattr(self.target, 'speed', 0)
        max_forward = getattr(self.target, 'max_forward_speed', None)
        max_reverse = getattr(self.target, 'max_reverse_speed', None)
        if accel:
            speed += dt * accel
            if max_forward is not None and self.target.speed > max_forward:
                speed = max_forward
            if max_reverse is not None and self.target.speed < max_reverse:
                speed = max_reverse

        r = math.radians(self.target.rotation)
        s = dt * speed
        x, y = self.target.position
        self.target.position = (x + math.sin(r)*s, y + math.cos(r)*s)
        self.target.speed = speed
