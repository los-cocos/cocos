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
"""Interval Action

Interval Actions
================

An interval action is an action that takes place within a certain period of time.
It has an start time, and a finish time. The finish time is the parameter
``duration`` plus the start time.

These `IntervalAction` have some interesting properties, like:

  - They can run normally (default)
  - They can run reversed with the `Reverse` action.
  - They can run with the time altered with the `Accelerate`, `AccelDeccel` and
    `Speed` actions.

For example, you can simulate a Ping Pong effect running the action normally and
then running it again in Reverse mode.

Example::

    ping_pong_action = action + Reverse(action)


Available IntervalActions
=========================

  * `MoveTo`
  * `MoveBy`
  * `JumpTo`
  * `JumpBy`
  * `Bezier`
  * `Blink`
  * `RotateTo`
  * `RotateBy`
  * `ScaleTo`
  * `ScaleBy`
  * `FadeOut`
  * `FadeIn`
  * `FadeTo`
  * `Delay`
  * `RandomDelay`


Modifier actions
================

  * `Accelerate`
  * `AccelDeccel`
  * `Speed`


Examples::

    move = MoveBy((200,0), duration=5)  # Moves 200 pixels to the right in 5 seconds.

    move = MoveTo((320,240), duration=5) # Moves to the pixel (320,240) in 5 seconds

    jump = JumpBy((320,0), 100, 5, duration=5) # Jumps to the right 320 pixels
                                                # doing 5 jumps of 100 pixels
                                                # of height in 5 seconds

    accel_move = Accelerate(move)               # accelerates action move
"""

from __future__ import division, print_function, unicode_literals


__docformat__ = 'restructuredtext'

import random
import copy
import math

from .base_actions import *
from cocos.euclid import *

__all__ = ['Lerp',                                  # interpolation
           'MoveTo', 'MoveBy',                      # movement actions
           'Jump', 'JumpTo', 'JumpBy',
           'Bezier',                                # complex movement actions
           'Rotate', "RotateTo", "RotateBy",        # object rotation
           'ScaleTo', 'ScaleBy',                    # object scale
           'Delay', 'RandomDelay',                  # Delays
           'FadeOut', 'FadeIn', 'FadeTo',           # Fades in/out action
           'Blink',                                 # Blink action
           'Accelerate', 'AccelDeccel', 'Speed', ]  # Time alter actions


class Lerp(IntervalAction):
    """
    Interpolate between values for some specified attribute

    """
    def init(self, attrib, start, end, duration):
        """Init method.

        :Parameters:
            `attrib` : string
                The name of the attrbiute where the value is stored
            `start`  : float
                The start value
            `end`    : float
                The end value
            `duration` : float
                Duration time in seconds
        """
        self.attrib = attrib
        self.duration = duration
        self.start_p = start
        self.end_p = end
        self.delta = end-start

    def update(self, t):
        setattr(self.target, self.attrib,
                self.start_p + self.delta*t)

    def __reversed__(self):
        return Lerp(self.attrib, self.end_p, self.start_p, self.duration)


class RotateBy(IntervalAction):
    """Rotates a `CocosNode` object clockwise a number of degrees
    by modiying it's rotation attribute.

    Example::

        # rotates the sprite 180 degrees in 2 seconds
        action = RotateBy(180, 2)
        sprite.do(action)
    """
    def init(self, angle, duration):
        """Init method.

        :Parameters:
            `angle` : float
                Degrees that the sprite will be rotated.
                Positive degrees rotates the sprite clockwise.
            `duration` : float
                Duration time in seconds
        """
        self.angle = angle          #: Quantity of degrees to rotate
        self.duration = duration    #: Duration in seconds

    def start(self):
        self.start_angle = self.target.rotation

    def update(self, t):
        self.target.rotation = (self.start_angle + self.angle*t) % 360

    def __reversed__(self):
        return RotateBy(-self.angle, self.duration)

Rotate = RotateBy


class RotateTo(IntervalAction):
    """Rotates a `CocosNode` object to a certain angle by modifying it's
    rotation attribute.
    The direction will be decided by the shortest angle.

    Example::

        # rotates the sprite to angle 180 in 2 seconds
        action = RotateTo(180, 2)
        sprite.do(action)
    """
    def init(self, angle, duration):
        """Init method.

        :Parameters:
            `angle` : float
                Destination angle in degrees.
            `duration` : float
                Duration time in seconds
        """
        self.angle = angle % 360      #: Destination angle in degrees
        self.duration = duration    #: Duration in seconds

    def start(self):
        ea = self.angle
        sa = self.start_angle = (self.target.rotation % 360)
        self.angle = ((ea % 360) - (sa % 360))
        if self.angle > 180:
            self.angle = -360 + self.angle
        if self.angle < -180:
            self.angle = 360 + self.angle

    def update(self, t):
        self.target.rotation = (self.start_angle + self.angle*t) % 360

    def __reversed__(self):
        return RotateTo(-self.angle, self.duration)


class Speed(IntervalAction):
    """
    Changes the speed of an action, making it take longer (speed>1)
    or less (speed<1)

    Example::

        # rotates the sprite 180 degrees in 1 secondclockwise
        action = Speed(Rotate(180, 2), 2)
        sprite.do(action)
    """
    def init(self, other, speed):
        """Init method.

        :Parameters:
            `other` : IntervalAction
                The action that will be affected
            `speed` : float
                The speed change. 1 is no change.
                2 means twice as fast, takes half the time
                0.5 means half as fast, takes double the time
        """
        self.other = other
        self.speed = speed
        self.duration = other.duration/speed

    def start(self):
        self.other.target = self.target
        self.other.start()

    def update(self, t):
        self.other.update(t)

    def __reversed__(self):
        return Speed(Reverse(self.other), self.speed)


class Accelerate(IntervalAction):
    """
    Changes the acceleration of an action

    Example::

        # rotates the sprite 180 degrees in 2 seconds clockwise
        # it starts slow and ends fast
        action = Accelerate(Rotate(180, 2), 4)
        sprite.do(action)
    """
    def init(self, other, rate=2):
        """Init method.

        :Parameters:
            `other` : IntervalAction
                The action that will be affected
            `rate` : float
                The acceleration rate. 1 is linear.
                the new t is t**rate
        """
        self.other = other
        self.rate = rate
        self.duration = other.duration

    def start(self):
        self.other.target = self.target
        self.other.start()

    def update(self, t):
        self.other.update(t ** self.rate)

    def __reversed__(self):
        return Accelerate(Reverse(self.other), 1.0 / self.rate)


class AccelDeccel(IntervalAction):
    """
    Makes an action change the travel speed but retain near normal
    speed at the beginning and ending.

    Example::

        # rotates the sprite 180 degrees in 2 seconds clockwise
        # it starts slow, gets fast and ends slow
        action = AccelDeccel(RotateBy(180, 2))
        sprite.do(action)
    """
    def init(self, other):
        """Init method.

        :Parameters:
            `other` : IntervalAction
                The action that will be affected
        """
        self.other = other
        self.duration = other.duration

    def start(self):
        self.other.target = self.target
        self.other.start()

    def update(self, t):
        if t != 1.0:
            ft = (t - 0.5) * 12
            t = 1./(1. + math.exp(-ft))
        self.other.update(t)

    def __reversed__(self):
        return AccelDeccel(Reverse(self.other))


class MoveTo(IntervalAction):
    """Moves a `CocosNode` object to the position x,y. x and y are absolute coordinates
    by modifying it's position attribute.

    Example::

        # Move the sprite to coords x=50, y=10 in 8 seconds

        action = MoveTo((50,10), 8)
        sprite.do(action)
    """
    def init(self, dst_coords, duration=5):
        """Init method.

        :Parameters:
            `dst_coords` : (x,y)
                Coordinates where the sprite will be placed at the end of the action
            `duration` : float
                Duration time in seconds
        """

        self.end_position = Point2(*dst_coords)
        self.duration = duration

    def start(self):
        self.start_position = self.target.position
        self.delta = self.end_position-self.start_position

    def update(self, t):
        self.target.position = self.start_position + self.delta * t


class MoveBy(MoveTo):
    """Moves a `CocosNode` object x,y pixels by modifying it's
    position attribute.
    x and y are relative to the position of the object.
    Duration is is seconds.

    Example::

        # Move the sprite 50 pixels to the left in 8 seconds
        action = MoveBy((-50,0), 8)
        sprite.do(action)
    """
    def init(self, delta, duration=5):
        """Init method.

        :Parameters:
            `delta` : (x,y)
                Delta coordinates
            `duration` : float
                Duration time in seconds
        """
        self.delta = Point2(*delta)
        self.duration = duration

    def start(self):
        self.start_position = self.target.position
        self.end_position = self.start_position + self.delta

    def __reversed__(self):
        return MoveBy(-self.delta, self.duration)


class FadeOut(IntervalAction):
    """Fades out a `CocosNode` object by modifying it's opacity attribute.

    Example::

        action = FadeOut(2)
        sprite.do(action)
    """
    def init(self, duration):
        """Init method.

        :Parameters:
            `duration` : float
                Seconds that it will take to fade
        """
        self.duration = duration

    def update(self, t):
        self.target.opacity = 255 * (1 - t)

    def __reversed__(self):
        return FadeIn(self.duration)


class FadeTo(IntervalAction):
    """Fades a `CocosNode` object to a specific alpha value by modifying it's opacity attribute.

    Example::

        action = FadeTo(128, 2)
        sprite.do(action)
    """
    def init(self, alpha, duration):
        """Init method.

        :Parameters:
            `alpha` : float
                0-255 value of opacity
            `duration` : float
                Seconds that it will take to fade
        """
        self.alpha = alpha
        self.duration = duration

    def start(self):
        self.start_alpha = self.target.opacity

    def update(self, t):
        self.target.opacity = self.start_alpha + (
            self.alpha - self.start_alpha) * t


class FadeIn(FadeOut):
    """Fades in a `CocosNode` object by modifying it's opacity attribute.

    Example::

        action = FadeIn(2)
        sprite.do(action)
    """
    def update(self, t):
        self.target.opacity = 255 * t

    def __reversed__(self):
        return FadeOut(self.duration)


class ScaleTo(IntervalAction):
    """Scales a `CocosNode` object to a zoom factor by modifying it's scale attribute.

    Example::

        # scales the sprite to 5x in 2 seconds
        action = ScaleTo(5, 2)
        sprite.do(action)
    """
    def init(self, scale, duration=5):
        """Init method.

        :Parameters:
            `scale` : float
                scale factor
            `duration` : float
                Duration time in seconds
        """
        self.end_scale = scale
        self.duration = duration

    def start(self):
        self.start_scale = self.target.scale
        self.delta = self.end_scale - self.start_scale

    def update(self, t):
        self.target.scale = self.start_scale + self.delta*t


class ScaleBy(ScaleTo):
    """Scales a `CocosNode` object a zoom factor by modifying it's scale attribute.

    Example::

        # scales the sprite by 5x in 2 seconds
        action = ScaleBy(5, 2)
        sprite.do(action)
    """

    def start(self):
        self.start_scale = self.target.scale
        self.delta = self.start_scale*self.end_scale - self.start_scale

    def __reversed__(self):
        return ScaleBy(1.0 / self.end_scale, self.duration)


class Blink(IntervalAction):
    """Blinks a `CocosNode` object by modifying it's visible attribute

    The action ends with the same visible state than at the start time.

    Example::

        # Blinks 10 times in 2 seconds
        action = Blink(10, 2)
        sprite.do(action)
    """

    def init(self, times, duration):
        """Init method.

        :Parameters:
            `times` : integer
                Number of times to blink
            `duration` : float
                Duration time in seconds
        """
        self.times = times
        self.duration = duration

    def start(self):
        self.end_invisible = not self.target.visible

    def update(self, t):
        slice = 1.0 / self.times
        m = t % slice
        self.target.visible = self.end_invisible ^ (m < slice/2.0)

    def __reversed__(self):
        return self


class Bezier(IntervalAction):
    """Moves a `CocosNode` object through a bezier path by modifying it's position attribute.

    Example::

        action = Bezier(bezier_conf.path1, 5)   # Moves the sprite using the
        sprite.do(action)                       # bezier path 'bezier_conf.path1'
                                                  # in 5 seconds
    """
    def init(self, bezier, duration=5, forward=True):
        """Init method

        :Parameters:
            `bezier` : bezier_configuration instance
                A bezier configuration
            `duration` : float
                Duration time in seconds
        """
        self.duration = duration
        self.bezier = bezier
        self.forward = forward

    def start(self):
        self.start_position = self.target.position

    def update(self, t):
        if self.forward:
            p = self.bezier.at(t)
        else:
            p = self.bezier.at(1 - t)
        self.target.position = (self.start_position + Point2(*p))

    def __reversed__(self):
        return Bezier(self.bezier, self.duration, not self.forward)


class Jump(IntervalAction):
    """Moves a `CocosNode` object simulating a jump movement by modifying it's position attribute.

    Example::

        action = Jump(50,200, 5, 6)    # Move the sprite 200 pixels to the right
        sprite.do(action)            # in 6 seconds, doing 5 jumps
                                       # of 50 pixels of height
    """

    def init(self, y=150, x=120, jumps=1, duration=5):
        """Init method

        :Parameters:
            `y` : integer
                Height of jumps
            `x` : integer
                horizontal movement relative to the startin position
            `jumps` : integer
                quantity of jumps
            `duration` : float
                Duration time in seconds
        """

        import warnings
        warnings.warn('Deprecated "Jump" action. Consider using JumpBy instead', DeprecationWarning)

        self.y = y
        self.x = x
        self.duration = duration
        self.jumps = jumps

    def start(self):
        self.start_position = self.target.position

    def update(self, t):
        y = int(self.y * abs(math.sin(t * math.pi * self.jumps)))

        x = self.x * t
        self.target.position = self.start_position + Point2(x, y)

    def __reversed__(self):
        return Jump(self.y, -self.x, self.jumps, self.duration)


class JumpBy(IntervalAction):
    """Moves a `CocosNode` object simulating a jump movement by modifying it's position attribute.

    Example::

        # Move the sprite 200 pixels to the right and up
        action = JumpBy((100,100),200, 5, 6)
        sprite.do(action)            # in 6 seconds, doing 5 jumps
                                       # of 200 pixels of height
    """

    def init(self, position=(0, 0), height=100, jumps=1, duration=5):
        """Init method

        :Parameters:
            `position` : integer x integer tuple
                horizontal and vertical movement relative to the
                starting position
            `height` : integer
                Height of jumps
            `jumps` : integer
                quantity of jumps
            `duration` : float
                Duration time in seconds
        """
        self.position = position
        self.height = height
        self.duration = duration
        self.jumps = jumps

    def start(self):
        self.start_position = self.target.position
        self.delta = Vector2(*self.position)

    def update(self, t):
        y = self.height * abs(math.sin(t * math.pi * self.jumps))
        y = int(y + self.delta[1]*t)
        x = self.delta[0] * t
        self.target.position = self.start_position + Point2(x, y)

    def __reversed__(self):
        return JumpBy((-self.position[0], -self.position[1]), self.height, self.jumps, self.duration)


class JumpTo(JumpBy):
    """Moves a `CocosNode` object to a position simulating a jump movement by modifying
    it's position attribute.

    Example::

        action = JumpTo(50,200, 5, 6)  # Move the sprite 200 pixels to the right
        sprite.do(action)            # in 6 seconds, doing 5 jumps
                                       # of 50 pixels of height
    """

    def start(self):
        self.start_position = self.target.position
        self.delta = Vector2(*self.position) - self.start_position


class Delay(IntervalAction):
    """Delays the action a certain amount of seconds

   Example::

        action = Delay(2.5)
        sprite.do(action)
    """
    def init(self, delay):
        """Init method

        :Parameters:
            `delay` : float
                Seconds of delay
        """
        self.duration = delay

    def __reversed__(self):
        return self


class RandomDelay(Delay):
    """Delays the actions between *min* and *max* seconds

   Example::

        action = RandomDelay(2.5, 4.5)      # delays the action between 2.5 and 4.5 seconds
        sprite.do(action)
    """
    def init(self, low, hi):
        """Init method

        :Parameters:
            `low` : float
                Minimun seconds of delay
            `hi` : float
                Maximun seconds of delay
        """
        self.low = low
        self.hi = hi

    def __deepcopy__(self, memo):
        new = copy.copy(self)
        new.duration = self.low + (random.random()*(self.hi - self.low))
        return new

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        if other <= 1:
            return self
        return RandomDelay(self.low * other, self.hi * other)
