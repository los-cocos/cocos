# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2019  Richard Jones, Claudio Canepa
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
"""Support for handling collisions between an actor and a container of objects"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'


class RectMapCollider(object):
    """Helper to handle collisions between an actor and objects in a RectMapLayer

    Arguments:
        velocity_on_bump (str) : one of ``"bounce"``, ``"stick"``, ``"slide"``.
            selects which of the predefined on_bump handlers will be used
    Attributes:
        on_bump_handler : method to change velocity when a collision was detected
        bumped_x (bool) : True if collide_map detected collision in the x-axis
        bumped_y (bool) : True if collide_map detected collision in the y-axis

    The code that updates actor position and velocity would call
    method :meth:`collide_map` to account for collisions

    There are basically two ways to include this functionality into an
    actor class

        - as a component, essentially passing (mapcollider, maplayer) in
          the actor's __init__
        - mixin style, by using RectMapCollider or a subclass as a secondary
          base class for actor.

    Component way is more decoupled, Mixin style is more powerful because
    the collision code will have access to the entire actor trough his 'self'.

    To have a working instance the behavior of velocity in a collision must be
    defined, and that's the job of method `on_bump_handler`

        - if one of the stock on_bump_<variant> suits the requirements, suffices
            `mapcollider.on_bump_handler = mapcollider.on_bump_<desired variant>`
          or passing a selector at instantiation time
            `mapcollider = MapCollider(<desired variant>)`

        - for custom behavior define on_bump_handler in a subclass and instantiate it.

    """
    def __init__(self, velocity_on_bump=None):
        if velocity_on_bump is not None:
            self.on_bump_handler = getattr(self, 'on_bump_' + velocity_on_bump)

    # collide_<side>: do something when actor collides 'obj' from side <side>

    def collide_bottom(self, obj):
        """placeholder, called when collision with obj's bottom side detected"""
        pass

    def collide_left(self, obj):
        """placeholder, called when collision with obj's left side detected"""
        pass

    def collide_right(self, obj):
        """placeholder, called when collision with obj's right side detected"""
        pass

    def collide_top(self, obj):
        """placeholder, called when collision with obj's top side detected"""
        pass

    # on_bump_<bump_style>: stock velocity changers when collision happened

    def on_bump_bounce(self, vx, vy):
        """Bounces when a wall is touched.

        Example use case: bouncing projectiles.
        """
        if self.bumped_x:
            vx = -vx
        if self.bumped_y:
            vy = -vy
        return vx, vy

    def on_bump_stick(self, vx, vy):
        """Stops all movement when any wall is touched.

        Example use case: sticky bomb, hook weapon projectile.
        """
        if self.bumped_x or self.bumped_y:
            vx = vy = 0.0
        return vx, vy

    def on_bump_slide(self, vx, vy):
        """Blocks movement only in the axis that touched a wall.

        Example use case: player in a platformer game.
        """
        if self.bumped_x:
            vx = 0.0
        if self.bumped_y:
            vy = 0.0
        return vx, vy

    # placeholder
    def on_bump_handler(self, vx, vy):
        """Returns velocity after all collisions considered by collide_map

        Arguments:
            vx (float) : velocity in x-axis before collision
            vy (float) : velocity in y-axis before collision

        Returns:
            (vx, vx) : velocity after all collisions considered in collide_map

        This is a placeholder, either define a custom one or replace with one
        of the stock on_bump_<bump_style> methods
        """
        raise ValueError(self.__class__.__name__ +
                '.on_bump_handler must be set to a real handler before calling.')
        # real code modifies vx, vy and
        return vx, vy

    def collide_map(self, maplayer, last, new, vx, vy):
        """Constrains a movement ``last`` -> ``new`` by considering collisions

        Arguments:
            maplayer (RectMapLayer) : layer with solid objects to collide with.
            last (Rect) : actor rect before step.
            new (Rect): tentative rect after the stepm will be adjusted.
            vx (float) : velocity in x-axis used to calculate 'last' -> 'new'
            vy (float) : velocity in y-axis used to calculate 'last' -> 'new'

        Returns:
            (vx, vy) (float, float) : the possibly modified (vx, vy).

        Assumes:
            'last' does not collide with any object.

            The dt involved in 'last' -> 'new' is small enough that no object
            can entirely fit between 'last' and 'new'.

        Side effects:
            ``new`` eventually modified to not be into forbidden area.
            For each collision with one object's side detected, the method
            ``self.collide_<side>(obj)`` is called.

        if rect ``new`` does not overlap any object in maplayer, the method
            - does not modify ``new``.
            - returns unchanged (vx, vy).
            - no method ``self.collide_<side>`` is called.
            - ``self.bumped_x`` and ``self.bumped_y`` both will be ``False``.

        if rect ``new`` does overlaps any object in maplayer, the method:
            - modifies ``new`` to be the nearest rect to the original ``new``
              rect that it is still outside any maplayer object.
            - returns a modified (vx, vy) as specified by self.on_bump_handler.
            - after return self.bumped_x  (resp self.bumped_y) will be True if
              an horizontal (resp vertical) collision happened.
            - if the movement from ``last`` to the original ``new`` was stopped
              by side <side> of object <obj>, then self.collide_<side>(obj) will be called.

        Implementation details

        Adjusts ``new`` in two passes against each object in maplayer.

        In pass one, ``new`` is collision tested against each object in maplayer:
            - if collides only in one axis, ``new`` is adjusted as close as possible but not overlapping object
            - if not overlapping, nothing is done
            - if collision detected on both axis, let second pass handle it

        In pass two, ``new`` is collision tested against the objects with double collisions in pass one:
            - if a collision is detected, adjust ``new`` as close as possible but not overlapping object,
              ie. use the smallest displacement on either X or Y axis. If they are both equal, move on
              both axis.
        """
        self.bumped_x = False
        self.bumped_y = False
        objects = maplayer.get_in_region(*(new.bottomleft + new.topright))
        # first pass, adjust for collisions in only one axis
        collide_later = set()
        for obj in objects:
            # the if is not superfluous in the loop because 'new' can change
            if obj is None or obj.tile is None or not obj.intersects(new):
                continue
            dx_correction, dy_correction = self.detect_collision(obj, last, new)
            if dx_correction == 0.0 or dy_correction == 0.0:
                self.resolve_collision(obj, new, dx_correction, dy_correction)
            else:
                collide_later.add(obj)

        # second pass, for objs that initially collided in both axis
        for obj in collide_later:
            if obj.intersects(new):
                dx_correction, dy_correction = self.detect_collision(obj, last, new)
                if abs(dx_correction) < abs(dy_correction):
                    # do correction only on X (below)
                    dy_correction = 0.0
                elif abs(dy_correction) < abs(dx_correction):
                    # do correction only on Y (below)
                    dx_correction = 0.0
                self.resolve_collision(obj, new, dx_correction, dy_correction)

        vx, vy = self.on_bump_handler(vx, vy)

        return vx, vy

    def detect_collision(self, obj, last, new):
        """returns minimal correction in each axis to not collide with obj

        Arguments:
            obj : object in a MapLayer
            last (Rect) : starting rect for the actor step
            new (Rect) : tentative actor's rect after step

        Decides if there is a collision with obj when moving ``last`` -> ``new``
        and then returns the minimal correctioin in each axis as to not collide.
        
        It can be overridden to be more selective about when a collision exists
        (see the matching method in :class:`RectMapWithPropsCollider` for example).
        """
        dx_correction = dy_correction = 0.0
        if last.bottom >= obj.top > new.bottom:
            dy_correction = obj.top - new.bottom
        elif last.top <= obj.bottom < new.top:
            dy_correction = obj.bottom - new.top
        if last.right <= obj.left < new.right:
            dx_correction = obj.left - new.right
        elif last.left >= obj.right > new.left:
            dx_correction = obj.right - new.left
        return dx_correction, dy_correction

    def resolve_collision(self, obj, new, dx_correction, dy_correction):
        """Corrects ``new`` to just avoid collision with obj, does side effects.

        Arguments:
            obj (obj) : the object colliding with ``new``.
            new (Rect) : tentative actor position before considering
                collision with ``obj``.
            dx_correction (float) : smallest correction needed on
                ``new`` x position not to collide ``obj``.
            dy_correction (float) : smallest correction needed on
            ``new`` y position not to collide ``obj``.

        The correction is applied to ``new`` position.

        If a collision along the x-axis (respectively y-axis) was detected,
        the flag ``self.bumped_x`` (resp y) is set.

        If the movement towards the original ``new`` was stopped by side <side>
        of object <obj>, then ``self.collide_<side>(obj)`` will be called.
        """
        if dx_correction != 0.0:
            # Correction on X axis
            self.bumped_x = True
            new.left += dx_correction
            if dx_correction > 0.0:
                self.collide_left(obj)
            else:
                self.collide_right(obj)
        if dy_correction != 0.0:
            # Correction on Y axis
            self.bumped_y = True
            new.top += dy_correction
            if dy_correction > 0.0:
                self.collide_bottom(obj)
            else:
                self.collide_top(obj)


class RectMapWithPropsCollider(RectMapCollider):
    """Helper to handle collisions between an actor and objects in a RectMapLayer

    Same as RectMapCollider except that collision detection is more fine grained.
    Collision happens only on objects sides with prop(<side>) set.

    Look at :class:`RectMapCollider` for details
    """

    def detect_collision(self, obj, last, new):
        """Returns minimal correction in each axis to not collide with obj

        Collision happens only on objects sides with prop <side> set.
        """
        # shorthand for getting a prop from obj
        g = obj.get
        dx_correction = dy_correction = 0.0
        if g('top') and last.bottom >= obj.top > new.bottom:
            dy_correction = obj.top - new.bottom
        elif g('bottom') and last.top <= obj.bottom < new.top:
            dy_correction = obj.bottom - new.top
        if g('left') and last.right <= obj.left < new.right:
            dx_correction = obj.left - new.right
        elif g('right') and last.left >= obj.right > new.left:
            dx_correction = obj.right - new.left
        return dx_correction, dy_correction


class TmxObjectMapCollider(RectMapCollider):
    """Helper to handle collisions between an actor and objects in a TmxObjectLayer

    Same as RectMapCollider except maplayer is expected to be a :class:`TmxObjectLayer`, so
    the objects to collide are TmxObject instances.

    Look at :class:`RectMapCollider` for details
    """
    def collide_map(self, maplayer, last, new, vx, vy):
        """Constrains a movement ``last`` -> ``new`` by considering collisions

        Arguments:
            maplayer (RectMapLayer) : layer with solid objects to collide with.
            last (Rect) : actor rect before step.
            new (Rect): tentative rect after the stepm will be adjusted.
            vx (float) : velocity in x-axis used to calculate 'last' -> 'new'
            vy (float) : velocity in y-axis used to calculate 'last' -> 'new'

        Returns:
            vx, vy (float, float) : the possibly modified (vx, vy).

        See :meth:`RectMapCollider.collide_map` for side effects and details
        """
        self.bumped_x = False
        self.bumped_y = False
        objects = maplayer.get_in_region(*(new.bottomleft + new.topright))
        # first pass, adjust for collisions in only one axis
        collide_later = set()
        for obj in objects:
            # the if is not superfluous in the loop because 'new' can change
            if not obj.intersects(new):
                continue
            dx_correction, dy_correction = self.detect_collision(obj, last, new)
            if dx_correction == 0.0 or dy_correction == 0.0:
                self.resolve_collision(obj, new, dx_correction, dy_correction)
            else:
                collide_later.add(obj)

        # second pass, for objs that initially collided in both axis
        for obj in collide_later:
            if obj.intersects(new):
                dx_correction, dy_correction = self.detect_collision(obj, last, new)
                if abs(dx_correction) < abs(dy_correction):
                    # do correction only on X (below)
                    dy_correction = 0.0
                elif abs(dy_correction) < abs(dx_correction):
                    # do correction only on Y (below)
                    dx_correction = 0.0
                self.resolve_collision(obj, new, dx_correction, dy_correction)

        vx, vy = self.on_bump_handler(vx, vy)

        return vx, vy


def make_collision_handler(collider, maplayer):
    """Returns ``f = collider.collide_map(maplayer, ...)``

    Returns:
        f : ``(last, new, vx, vy)`` -> ``(vx, vy)``

    Utility function to create a collision handler by combining

    Arguments:
       maplayer : tells the objects to collide with.
       collider : tells how velocity changes on collision and resolves
           actual collisions.
    """

    def collision_handler(last, new, vx, vy):
        return collider.collide_map(maplayer, last, new, vx, vy)

    return collision_handler
