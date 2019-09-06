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
"""This module defines the :class:`ScrollableLayer` and 
:class:`ScrollingManager` classes.

This module helps to handle what will be visible on screen when the game world
does not fit in the window area.

It models this concept: the game world is a big volume. We have a camera
that follows the actor moving parallel to one of the volume faces, without 
rotations. What the camera sees is what  will be seen on the app window. Also, 
the camera's movements can be restricted in order not to show parts outside 
of the world. This technique is usually named *'scrolling'*.

It has support for parallax rendering, that is, faking perspective by using
layers that slide slower the farther they are.

The important concepts are:
  - The coordinator, implemented as :class:`ScrollingManager` which enforces the
    view limits imposed by the managed layers, accounts for layer's parallax.

  - The managed layers, implemented each by a :class:`ScrollableLayer`, which as
    a group holds all the entities in the world and each one can define what
    area of the x-y plane should be shown on camera.

  -The focus, tied to ScrollingManager ``fx`` and ``fy`` attributes, which 
    indicates that point (fx, fy) in world coordinates is the point of interest,
    and should show at the center of the *screen view* if no restriction is
    violated.
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import warnings

from cocos.director import director
from .base_layers import Layer
import pyglet
from pyglet import gl


class ScrollableLayer(Layer):
    """Layer that supports scrolling.

    If ``px_width`` is defined, then ``px_height`` must also be defined; scrolling
    will be limited to only show areas with origin_x <= x < = px_width and
    origin_y <= y <= px_height).

    If ``px_width`` is not defined, then the layer will not limit the scrolling.

    A layer may have a ``parallax`` value which is used to scale the position
    (and not the dimensions) of the view for the layer - the layer's view
    (x, y) coordinates are calculated as::

       my_view_x = parallax * passed_view_x
       my_view_y = parallax * passed_view_y

    The scrolling is managed by the parent node of :class:`ScrollingManager` 
    class.

    .. Warning::
        Don't change ``scale_x`` , ``scale_y`` from the default 1.0 or scrolling and
        coordinate changes will fail.

    Arguments:
        parallax (float): the parallax for this layer. Defaults to 1.
    """

    def __init__(self, parallax=1):
        super(ScrollableLayer, self).__init__()
        self.parallax = parallax

        # force (cocos) transform anchor to be 0 so we don't OpenGL
        # glTranslate() and screw up our pixel alignment on screen
        self.transform_anchor_x = 0
        self.transform_anchor_y = 0

        # XXX batch eh?
        self.batch = pyglet.graphics.Batch()

        # The view x position
        self.view_x = 0
        # The view y position
        self.view_y = 0
        # The view width
        self.view_w = 0
        # The view height
        self.view_h = 0

        self.origin_x = self.origin_y = self.origin_z = 0

    def on_enter(self):
        """Called every time just before the node enters the stage."""
        director.push_handlers(self.on_cocos_resize)
        super(ScrollableLayer, self).on_enter()

    def on_exit(self):
        """Called every time just before the node exits the stage."""
        super(ScrollableLayer, self).on_exit()
        director.pop_handlers()

    def set_view(self, x, y, w, h, viewport_ox=0, viewport_oy=0):
        """Sets the position of the viewport for this layer.

        Arguments:
            x (float): The view x position
            y (float): The view y position
            w (float): The width of the view
            h (float): The height of the view
            viewport_ox (float) : The viewport x origin
            viewport_oy (float) : The viewport y origin
        """
        x *= self.parallax
        y *= self.parallax
        self.view_x, self.view_y = x, y
        self.view_w, self.view_h = w, h
        x -= self.origin_x
        y -= self.origin_y
        x -= viewport_ox
        y -= viewport_oy
        self.position = (-x, -y)

    def draw(self):
        """Draws itself"""
        # invoked by Cocos machinery
        super(ScrollableLayer, self).draw()

        # XXX overriding draw eh?
        gl.glPushMatrix()
        self.transform()
        self.batch.draw()
        gl.glPopMatrix()

    def set_dirty(self):
        """The viewport has changed in some way.
        """
        pass

    def on_cocos_resize(self, usable_width, usable_height):
        """Event handler for window resizing."""
        self.set_dirty()


class ScrollingManager(Layer):
    """Handles scrolling for his children, which should be ScrollableLayer 
    instances.

    Restricts the scrolling so that all the visibility restriction imposed by
    the children are honored; at least one child should define a constraint for 
    the scrolling to be limited.

    The drawing can be limited to a specific window's rectangle by passing the
    ``viewport`` parameter.

    The scrolling manager also provides coordinate changes between screen coords
    and world coords.

    Args:
        viewport (Rect): A rectangle defining the viewport. [Optional]
        do_not_scale (bool): Whether the :class:`ScrollingManager` should scale
            the view during Window resizes. (Defaults to None, meaning it takes
            the same value as ``director.autoscale``)
    """
    def __init__(self, viewport=None, do_not_scale=None):
        if do_not_scale is None:
            do_not_scale = not director.autoscale
        self.autoscale = not do_not_scale and director.autoscale

        self.viewport = viewport

        # These variables define the Layer-space pixel view which is mapping
        # to the viewport. If the Layer is not scrolled or scaled then this
        # will be a one to one mapping.
        self.view_x, self.view_y = 0, 0
        self.view_w, self.view_h = 1, 1
        self.childs_ox = 0
        self.childs_oy = 0

        # Focal point on the Layer
        self.fx = self.fy = 0

        super(ScrollingManager, self).__init__()

        # always transform about 0,0
        self.transform_anchor_x = 0
        self.transform_anchor_y = 0

        self._old_focus = None

    def on_enter(self):
        """"Called every time just before the node enters the stage."""
        super(ScrollingManager, self).on_enter()
        director.push_handlers(self.on_cocos_resize)
        self.update_view_size()
        self.refresh_focus()

    def on_exit(self):
        """Called every time just before the node exits the stage."""
        director.pop_handlers()
        super(ScrollingManager, self).on_exit()

    def update_view_size(self):
        """Updates the view size based on the director usable width and height,
        and on the optional viewport.
        """
        if self.viewport is not None:
            self.view_w, self.view_h = self.viewport.width, self.viewport.height
            self.view_x, self.view_y = getattr(self.viewport, 'position', (0, 0))
            if not director.autoscale:
                self._scissor_flat = (self.view_x, self.view_y,
                                      self.view_w, self.view_h)
            else:
                w, h = director.get_window_size()
                sx = director._usable_width / w
                sy = director._usable_height / h
                self._scissor_flat = (int(self.view_x * sx), int(self.view_y * sy),
                                      int(self.view_w * sx), int(self.view_h * sy))
        elif self.autoscale:
            self.view_w, self.view_h = director.get_window_size()
        else:
            self.view_w = director._usable_width
            self.view_h = director._usable_height

    def on_cocos_resize(self, usable_width, usable_height):
        """Event handler for Window resize."""
        # when using an explicit viewport you should adjust the viewport for
        # resize changes here, before the lines that follows.
        # Also, if your app performs other changes in viewport it should
        # use the lines that follows to update viewport-related internal state
        self.update_view_size()
        self.refresh_focus()

    def refresh_focus(self):
        """Resets the focus at the focus point."""
        if self.children:
            self._old_focus = None  # disable NOP check
            self.set_focus(self.fx, self.fy)

    def _set_scale(self, scale):
        self._scale = 1.0 * scale
        self.refresh_focus()

    scale = property(lambda s: s._scale, _set_scale, 
        doc = """The scaling factor of the object.

        :type: float
        """)

    def add(self, child, z=0, name=None):
        """Add the child and then update the manager's focus / viewport.

        Args:
            child (CocosNode): The node to add. Normally it's a
                :class:`ScrollableLayer`.
            z (int) : z-order for this child.
            name (str) : The name of this child. [Optional]
        """
        super(ScrollingManager, self).add(child, z=z, name=name)
        # set the focus again and force it so we don't just skip because the
        # focal point hasn't changed
        self.set_focus(self.fx, self.fy, force=True)

    def pixel_from_screen(self, x, y):
        """deprecated, was renamed as screen_to_world"""
        warnings.warn("Cocos Deprecation Warning: ScrollingManager.pixel_from_screen "
                      "was renamed to Scrolling Manager.screen_to_world; the"
                      " former will disappear in future cocos releases")
        return self.screen_to_world(x, y)

    def screen_to_world(self, x, y):
        """Translates screen coordinates to world coordinates.

        Account for viewport, layer and screen transformations.

        Arguments:
            x (int): x coordinate in screen space
            y (int): y coordinate in screen space

        Returns:
            tuple[int, int]: coordinates in world-space
        """
        # director display scaling
        if director.autoscale:
            x, y = director.get_virtual_coordinates(x, y)

        # normalise x,y coord
        ww, wh = director.get_window_size()
        sx = x / self.view_w
        sy = y / self.view_h

        # get the map-space dimensions
        vx, vy = self.childs_ox, self.childs_oy

        # get our scaled view size
        w = int(self.view_w / self.scale)
        h = int(self.view_h / self.scale)

        # convert screen pixel to map pixel
        return int(vx + sx * w), int(vy + sy * h)

    def pixel_to_screen(self, x, y):
        """deprecated, was renamed as world_to_screen"""
        warnings.warn("Cocos Deprecation Warning: ScrollingManager.pixel_to_screen "
                      "was renamed to Scrolling Manager.world_to_screen; the"
                      " former will disappear in future cocos releases")
        return self.world_to_screen(x, y)

    def world_to_screen(self, x, y):
        """Translates world coordinates to screen coordinates.

        Account for viewport, layer and screen transformations.

        Arguments:
            x (int): x coordinate in world space
            y (int): y coordinate in world space

        Returns:
            tuple[int, int]: coordinates in screen space
        """
        screen_x = self.scale * (x - self.childs_ox)
        screen_y = self.scale * (y - self.childs_oy)
        return int(screen_x), int(screen_y)

    def set_focus(self, fx, fy, force=False):
        """Makes the point (fx, fy) show as near the view's center as possible.

        Changes his children so that the point (fx, fy) in world coordinates
        will be seen as near the view center as possible, while at the
        same time not displaying out-of-bounds areas in the children.

        Args:
            fx (int): the focus point x coordinate
            fy (int): the focus point y coordinate
            force (bool): If True, forces the update of the focus, eventhough the
                focus point or the scale did not change. Defaults to False.
        """
        # if no child specifies dimensions then just force the focus
        if not [l for z, l in self.children if hasattr(l, 'px_width')]:
            return self.force_focus(fx, fy)

        # This calculation takes into account the scaling of this Layer (and
        # therefore also its children).
        # The result is that all chilren will have their viewport set, defining
        # which of their pixels should be visible.
        self.fx, self.fy = fx, fy

        a = (fx, fy, self.scale)

        # check for NOOP (same arg passed in)
        if not force and self._old_focus == a:
            return
        self._old_focus = a

        # collate children dimensions
        x1 = []
        y1 = []
        x2 = []
        y2 = []
        for z, layer in self.children:
            if not hasattr(layer, 'px_width'):
                continue
            x1.append(layer.origin_x)
            y1.append(layer.origin_y)
            x2.append(layer.origin_x + layer.px_width)
            y2.append(layer.origin_y + layer.px_height)

        # figure the child layer min/max bounds
        b_min_x = min(x1)
        b_min_y = min(y1)
        b_max_x = max(x2)
        b_max_y = max(y2)

        # get our viewport information, scaled as appropriate
        w = self.view_w / self.scale
        h = self.view_h / self.scale
        w2, h2 = w / 2, h / 2

        if (b_max_x - b_min_x) <= w:
            # this branch for prety centered view and no view jump when
            # crossing the center; both when world width <= view width
            restricted_fx = (b_max_x + b_min_x) / 2
        else:
            if (fx - w2) < b_min_x:
                restricted_fx = b_min_x + w2       # hit minimum X extent
            elif (fx + w2) > b_max_x:
                restricted_fx = b_max_x - w2       # hit maximum X extent
            else:
                restricted_fx = fx
        if (b_max_y - b_min_y) <= h:
            # this branch for pretty centered view and no view jump when
            # crossing the center; both when world height <= view height
            restricted_fy = (b_max_y + b_min_y) / 2
        else:
            if (fy - h2) < b_min_y:
                restricted_fy = b_min_y + h2       # hit minimum Y extent
            elif (fy + h2) > b_max_y:
                restricted_fy = b_max_y - h2       # hit maximum Y extent
            else:
                restricted_fy = fy

        # ... and this is our focus point, center of screen
        self.restricted_fx = restricted_fx
        self.restricted_fy = restricted_fy

        # determine child view bounds to match that focus point
        x, y = (restricted_fx - w2), (restricted_fy - h2)

        childs_scroll_x = x  # - self.view_x/self.scale
        childs_scroll_y = y  # - self.view_y/self.scale
        self.childs_ox = childs_scroll_x - self.view_x/self.scale
        self.childs_oy = childs_scroll_y - self.view_y/self.scale

        for z, layer in self.children:
            layer.set_view(childs_scroll_x, childs_scroll_y, w, h,
                           self.view_x / self.scale, self.view_y / self.scale)

    def force_focus(self, fx, fy):
        """Force the manager to focus on a point, regardless of any managed layer
        visible boundaries.

        Args:
            fx (int): the focus point x coordinate
            fy (int): the focus point y coordinate
        """
        # This calculation takes into account the scaling of this Layer (and
        # therefore also its children).
        # The result is that all children will have their viewport set, defining
        # which of their pixels should be visible.

        self.fx, self.fy = map(int, (fx, fy))
        self.fx, self.fy = fx, fy

        # get our scaled view size
        w = int(self.view_w / self.scale)
        h = int(self.view_h / self.scale)
        w2, h2 = w // 2, h // 2

        # bottom-left corner of the
        x, y = fx - w2, fy - h2

        childs_scroll_x = x  # - self.view_x/self.scale
        childs_scroll_y = y  # - self.view_y/self.scale
        self.childs_ox = childs_scroll_x - self.view_x/self.scale
        self.childs_oy = childs_scroll_y - self.view_y/self.scale

        for z, layer in self.children:
            layer.set_view(childs_scroll_x, childs_scroll_y, w, h,
                           self.view_x / self.scale, self.view_y / self.scale)

    def set_state(self):
        """Sets OpenGL state for using scissor test."""
        # preserve gl scissors info
        self._scissor_enabled = gl.glIsEnabled(gl.GL_SCISSOR_TEST)
        self._old_scissor_flat = (gl.GLint * 4)()  # 4-tuple
        gl.glGetIntegerv(gl.GL_SCISSOR_BOX, self._old_scissor_flat)

        # set our scissor
        if not self._scissor_enabled:
            gl.glEnable(gl.GL_SCISSOR_TEST)

        gl.glScissor(*self._scissor_flat)

    def unset_state(self):
        """Unsets OpenGL state for using scissor test."""
        # restore gl scissors info
        gl.glScissor(*self._old_scissor_flat)
        if not self._scissor_enabled:
            gl.glDisable(gl.GL_SCISSOR_TEST)

    def visit(self):
        """Draws itself and its children into the viewport area.

        Same as in :meth:`.CocosNode.visit`, but will restrict drawing
        to the rect viewport.
        """
        if self.viewport is not None:
            self.set_state()
            super(ScrollingManager, self).visit()
            self.unset_state()
        else:
            super(ScrollingManager, self).visit()
