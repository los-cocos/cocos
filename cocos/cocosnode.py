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
"""
CocosNode: the basic element of cocos2d
"""

from __future__ import division, print_function, unicode_literals
from six import string_types

__docformat__ = 'restructuredtext'

import copy
import math
import weakref

import pyglet
from pyglet import gl

from cocos.director import director
from cocos.camera import Camera
from cocos import euclid

__all__ = ['CocosNode']


class CocosNode(object):
    """
    Cocosnode is the main element. Anything thats gets drawn or contains things that get drawn is a cocosnode.
    The most popular cocosnodes are scenes, layers and sprites.

    The main features of a cocosnode are:
        - They can contain other cocos nodes (add, get, remove, etc)
        - They can schedule periodic callback (schedule, schedule_interval, etc)
        - They can execute actions (do, pause, stop, etc)

    Some cocosnodes provide extra functionality for them or their children.

    Subclassing a cocosnode usually means (one/all) of:
        - overriding __init__ to initialize resources and schedule calbacks
        - create callbacks to handle the advancement of time
        - overriding draw to render the node
    """
    def __init__(self):
        # composition stuff

        #: list of (int, child-reference) where int is the z-order, sorted by ascending z (back to front order)
        self.children = []

        #: dictionary that maps children names with children references
        self.children_names = {}

        self._parent = None

        # drawing stuff

        #: x-position of the object relative to its parent's children_anchor_x value.
        #: Default: 0
        self._x = 0

        #: y-position of the object relative to its parent's children_anchor_y value.
        #: Default: 0
        self._y = 0

        #: a float, alters the scale of this node and its children.
        #: Default: 1.0
        self._scale = 1.0

        #: a float, alters the horizontal scale of this node and its children.
        #: total scale along x axis is _scale_x * _scale
        #: Default: 1.0
        self._scale_x = 1.0

        #: a float, alters the vertical scale of this node and its children.
        #: total scale along y axis is _scale_y * _scale
        #: Default: 1.0
        self._scale_y = 1.0

        #: a float, in degrees, alters the rotation of this node and its children.
        #: Default: 0.0
        self._rotation = 0.0

        #: eye, center and up vector for the `Camera`.
        #: gluLookAt() is used with these values.
        #: Default: FOV 60, center of the screen.
        #: IMPORTANT: The camera can perform exactly the same
        #: transformation as ``scale``, ``rotation`` and the
        #: ``x``, ``y`` attributes (with the exception that the
        #: camera can modify also the z-coordinate)
        #: In fact, they all transform the same matrix, so
        #: use either the camera or the other attributes, but not both
        #: since the camera will be overridden by the transformations done
        #: by the other attributes.
        #: You can change the camera manually or by using the `Camera3DAction`
        #: action.
        self.camera = Camera()

        #: offset from (x,0) from where rotation and scale will be applied.
        #: Default: 0
        self.transform_anchor_x = 0

        #: offset from (0,y) from where rotation and scale will be applied.
        #: Default: 0
        self.transform_anchor_y = 0

        #: whether of not the object and his childrens are visible.
        #: Default: True
        self.visible = True

        #: the grid object for the grid actions.
        #: This can be a `Grid3D` or a `TiledGrid3D` object depending
        #: on the action.
        self.grid = None

        # actions stuff
        #: list of `Action` objects that are running
        self.actions = []

        #: list of `Action` objects to be removed
        self.to_remove = []

        #: whether or not the next frame will be skipped
        self.skip_frame = False

        # schedule stuff
        self.scheduled = False          # deprecated, soon to be removed
        self.scheduled_calls = []       #: list of scheduled callbacks
        self.scheduled_interval_calls = []  #: list of scheduled interval callbacks
        self.is_running = False         #: whether of not the object is running

        # matrix stuff
        self.is_transform_dirty = False
        self.transform_matrix = euclid.Matrix3().identity()
        self.is_inverse_transform_dirty = False
        self.inverse_transform_matrix = euclid.Matrix3().identity()

    def make_property(attr):
        types = {'anchor_x': "int", 'anchor_y': "int", "anchor": "(int, int)"}

        def set_attr():
            def inner(self, value):
                setattr(self, "transform_" + attr, value)
            return inner

        def get_attr():
            def inner(self):
                return getattr(self, "transform_" + attr)
            return inner
        return property(
            get_attr(),
            set_attr(),
            doc="""a property to get fast access to transform_%s

            :type: %s""" % (attr, types[attr]))

    #: Anchor point of the object.
    #: Children will be added at this point
    #: and transformations like scaling and rotation will use this point
    #: as the center
    anchor = make_property("anchor")

    #: Anchor x value for transformations and adding children
    anchor_x = make_property("anchor_x")

    #: Anchor y value for transformations and adding children
    anchor_y = make_property("anchor_y")

    def make_property(attr):
        def set_attr():
            def inner(self, value):
                setattr(self, attr + "_x", value[0])
                setattr(self, attr + "_y", value[1])
            return inner

        def get_attr(self):
            return getattr(self, attr + "_x"),  getattr(self, attr + "_y")
        return property(
            get_attr,
            set_attr(),
            doc='''a property to get fast access to "+attr+"_[x|y]

            :type: (int,int)
            ''')

    #: Transformation anchor point.
    #: Transformations like scaling and rotation
    #: will use this point as it's center
    transform_anchor = make_property("transform_anchor")
    del make_property

    def schedule_interval(self, callback, interval, *args, **kwargs):
        """
        Schedule a function to be called every `interval` seconds.

        Specifying an interval of 0 prevents the function from being
        called again (see `schedule` to call a function as often as possible).

        The callback function prototype is the same as for `schedule`.

        :Parameters:
            `callback` : function
                The function to call when the timer lapses.
            `interval` : float
                The number of seconds to wait between each call.

        This function is a wrapper to pyglet.clock.schedule_interval.
        It has the additional benefit that all calllbacks are paused and
        resumed when the node leaves or enters a scene.

        You should not have to schedule things using pyglet by yourself.
        """
        if self.is_running:
            pyglet.clock.schedule_interval(callback, interval, *args, **kwargs)
        self.scheduled_interval_calls.append(
            (callback, interval, args, kwargs)
            )

    def schedule(self, callback, *args, **kwargs):
        """
        Schedule a function to be called every frame.

        The function should have a prototype that includes ``dt`` as the
        first argument, which gives the elapsed time, in seconds, since the
        last clock tick.  Any additional arguments given to this function
        are passed on to the callback::

            def callback(dt, *args, **kwargs):
                pass

        :Parameters:
            `callback` : function
                The function to call each frame.

        This function is a wrapper to pyglet.clock.schedule.
        It has the additional benefit that all calllbacks are paused and
        resumed when the node leaves or enters a scene.

        You should not have to schedule things using pyglet by yourself.
        """
        if self.is_running:
            pyglet.clock.schedule(callback, *args, **kwargs)
        self.scheduled_calls.append(
            (callback, args, kwargs)
            )

    def unschedule(self, callback):
        """
        Remove a function from the schedule.

        If the function appears in the schedule more than once, all occurances
        are removed.  If the function was not scheduled, no error is raised.

        :Parameters:
            `callback` : function
                The function to remove from the schedule.

        This function is a wrapper to pyglet.clock.unschedule.
        It has the additional benefit that all calllbacks are paused and
        resumed when the node leaves or enters a scene.

        You should not unschedule things using pyglet that where scheduled
        by node.schedule/node.schedule_interface.
        """

        self.scheduled_calls = [
            c for c in self.scheduled_calls if c[0] != callback
            ]
        self.scheduled_interval_calls = [
            c for c in self.scheduled_interval_calls if c[0] != callback
            ]

        if self.is_running:
            pyglet.clock.unschedule(callback)

    def resume_scheduler(self):
        """
        Time will continue/start passing for this node and callbacks
        will be called, worker actions will be called
        """
        for c, i, a, k in self.scheduled_interval_calls:
            pyglet.clock.schedule_interval(c, i, *a, **k)
        for c, a, k in self.scheduled_calls:
            pyglet.clock.schedule(c, *a, **k)

    def pause_scheduler(self):
        """
        Time will stop passing for this node: scheduled callbacks will
        not be called, worker actions will not be called
        """
        for f in set(
                [x[0] for x in self.scheduled_interval_calls] +
                [x[0] for x in self.scheduled_calls]
                ):
            pyglet.clock.unschedule(f)
        for arg in self.scheduled_calls:
            pyglet.clock.unschedule(arg[0])

    def _get_parent(self):
        if self._parent is None:
            return None
        else:
            return self._parent()

    def _set_parent(self, parent):
        if parent is None:
            self._parent = None
        else:
            self._parent = weakref.ref(parent)

    parent = property(_get_parent, _set_parent, doc='''The parent of this object.

    :type: object
    ''')

    def get_ancestor(self, klass):
        """
        Walks the nodes tree upwards until it finds a node of the class `klass`
        or returns None

        :rtype: `CocosNode` or None
        """
        if isinstance(self, klass):
            return self
        parent = self.parent
        if parent:
            return parent.get_ancestor(klass)

    #
    # Transform properties
    #
    def _get_x(self):
        return self._x

    def _set_x(self, x):
        self._x = x
        self.is_transform_dirty = True
        self.is_inverse_transform_dirty = True
    x = property(_get_x, lambda self, x: self._set_x(x), doc="The x coordinate of the object")

    def _get_y(self):
        return self._y

    def _set_y(self, y):
        self._y = y
        self.is_transform_dirty = True
        self.is_inverse_transform_dirty = True
    y = property(_get_y, lambda self, y: self._set_y(y), doc="The y coordinate of the object")

    def _get_position(self):
        return (self._x, self._y)

    def _set_position(self, pos):
        self._x, self._y = pos
        self.is_transform_dirty = True
        self.is_inverse_transform_dirty = True

    position = property(_get_position, lambda self, p: self._set_position(p),
                        doc='''The (x, y) coordinates of the object.

    :type: (int, int)
    ''')

    def _get_scale(self):
        return self._scale

    def _set_scale(self, s):
        self._scale = s
        self.is_transform_dirty = True
        self.is_inverse_transform_dirty = True

    scale = property(_get_scale, lambda self, scale: self._set_scale(scale))

    def _get_scale_x(self):
        return self._scale_x

    def _set_scale_x(self, s):
        self._scale_x = s
        self.is_transform_dirty = True
        self.is_inverse_transform_dirty = True

    scale_x = property(_get_scale_x, lambda self, scale: self._set_scale_x(scale))

    def _get_scale_y(self):
        return self._scale_y

    def _set_scale_y(self, s):
        self._scale_y = s
        self.is_transform_dirty = True
        self.is_inverse_transform_dirty = True

    scale_y = property(_get_scale_y, lambda self, scale: self._set_scale_y(scale))

    def _get_rotation(self):
        return self._rotation

    def _set_rotation(self, a):
        self._rotation = a
        self.is_transform_dirty = True
        self.is_inverse_transform_dirty = True

    rotation = property(_get_rotation, lambda self, angle: self._set_rotation(angle))

    def add(self, child, z=0, name=None):
        """Adds a child and if it becomes part of the active scene calls its on_enter method

        :Parameters:
            `child` : CocosNode
                object to be added
            `z` : float
                the z index of self
            `name` : str
                Name of the child

        :rtype: `CocosNode` instance
        :return: self

        """
        # child must be a subclass of supported_classes
        # if not isinstance( child, self.supported_classes ):
        #    raise TypeError("%s is not instance of: %s" % (type(child), self.supported_classes) )

        if name:
            if name in self.children_names:
                raise Exception("Name already exists: %s" % name)
            self.children_names[name] = child

        child.parent = self

        elem = z, child

        # inlined and customized bisect.insort_right, the stock one fails in py3
        lo = 0
        hi = len(self.children)
        a = self.children
        while lo < hi:
            mid = (lo+hi) // 2
            if z < a[mid][0]:
                hi = mid
            else:
                lo = mid + 1
        self.children.insert(lo, elem)

        if self.is_running:
            child.on_enter()
        return self

    def kill(self):
        """Remove this object from its parent, and thus most likely from
        everything.
        """
        self.parent.remove(self)

    def remove(self, obj):
        """Removes a child given its name or object

        If the node was added with name, it is better to remove by name, else
        the name will be unavailable for further adds ( and will raise Exception
        if add with this same name is attempted)

        If the node was part of the active scene, its on_exit method will be called.

        :Parameters:
            `obj` : string or object
                name of the reference to be removed
                or object to be removed
        """
        if isinstance(obj, string_types):
            if obj in self.children_names:
                child = self.children_names.pop(obj)
                self._remove(child)
            else:
                raise Exception("Child not found: %s" % obj)
        else:
            self._remove(obj)

    def _remove(self, child):
        l_old = len(self.children)
        self.children = [(z, c) for (z, c) in self.children if c != child]

        if l_old == len(self.children):
            raise Exception("Child not found: %s" % str(child))

        if self.is_running:
            child.on_exit()

    def get_children(self):
        """Return a list with the node's childs, order is back to front

        :rtype: list of CocosNode
        :return: childs of this node, ordered back to front

        """
        return [c for (z, c) in self.children]

    def __contains__(self, child):
        return child in self.get_children()

    def get(self, name):
        """Gets a child given its name

        :Parameters:
            `name` : string
                name of the reference to be get

        :rtype: CocosNode
        :return: the child named 'name'. Will raise Exception if not present

        Warning: if a node is added with name, then removed not by name, the name
        cannot be recycled: attempting to add other node with this name will
        produce an Exception.
        """
        if name in self.children_names:
            return self.children_names[name]
        else:
            raise Exception("Child not found: %s" % name)

    def on_enter(self):
        """
        Called every time just before the node enters the stage.

        scheduled calls and worker actions begins or continues to perform

        Good point to do .push_handlers if you have custom ones
        Rule: a handler pushed there is near certain to require a .pop_handlers
        in the .on_exit method (else it will be called even after removed from
        the active scene, or, if going on stage again will be called multiple
        times for each event ocurrence)
        """
        self.is_running = True

        # start actions
        self.resume()
        # resume scheduler
        self.resume_scheduler()

        # propagate
        for c in self.get_children():
            c.on_enter()

    def on_exit(self):
        """
        Called every time just before the node leaves the stage

        scheduled calls and worker actions are suspended, that is, will not
        be called until an on_enter event happens.

        Most of the time you will want to .pop_handlers for all explicit
        .push_handlers found in on_enter

        Consider to release here openGL resources created by this node, like
        compiled vertex lists
        """
        self.is_running = False

        # pause actions
        self.pause()
        # pause callbacks
        self.pause_scheduler()

        # propagate
        for c in self.get_children():
            c.on_exit()

    def transform(self):
        """
        Apply ModelView transformations

        you will most likely want to wrap calls to this function with
        glPushMatrix/glPopMatrix
        """
        x, y = director.get_window_size()

        if not(self.grid and self.grid.active):
            # only apply the camera if the grid is not active
            # otherwise, the camera will be applied inside the grid
            self.camera.locate()

        gl.glTranslatef(self.position[0], self.position[1], 0)
        gl.glTranslatef(self.transform_anchor_x, self.transform_anchor_y, 0)

        if self.rotation != 0.0:
            gl.glRotatef(-self._rotation, 0, 0, 1)

        if self.scale != 1.0 or self.scale_x != 1.0 or self.scale_y != 1.0:
            gl.glScalef(self._scale * self._scale_x, self._scale * self._scale_y, 1)

        if self.transform_anchor != (0, 0):
            gl.glTranslatef(
                -self.transform_anchor_x,
                -self.transform_anchor_y,
                0)

    def walk(self, callback, collect=None):
        """
        Executes callback on all the subtree starting at self.
        returns a list of all return values that are not none

        :Parameters:
            `callback` : function
                callable, takes a cocosnode as argument
            `collect` : list
                list of visited nodes

        :rtype: list
        :return: the list of not-none return values

        """
        if collect is None:
            collect = []

        r = callback(self)
        if r is not None:
            collect.append(r)

        for node in self.get_children():
            node.walk(callback, collect)

        return collect

    def visit(self):
        """
        This function *visits* it's children in a recursive
        way.

        It will first *visit* the children that
        that have a z-order value less than 0.

        Then it will call the `draw` method to
        draw itself.

        And finally it will *visit* the rest of the
        children (the ones with a z-value bigger
        or equal than 0)

        Before *visiting* any children it will call
        the `transform` method to apply any possible
        transformation.
        """
        if not self.visible:
            return

        position = 0

        if self.grid and self.grid.active:
            self.grid.before_draw()

        # we visit all nodes that should be drawn before ourselves

        if self.children and self.children[0][0] < 0:
            gl.glPushMatrix()
            self.transform()
            for z, c in self.children:
                if z >= 0:
                    break
                position += 1
                c.visit()

            gl.glPopMatrix()

        # we draw ourselves
        self.draw()

        # we visit all the remaining nodes, that are over ourselves
        if position < len(self.children):
            gl.glPushMatrix()
            self.transform()
            for z, c in self.children[position:]:
                c.visit()
            gl.glPopMatrix()

        if self.grid and self.grid.active:
            self.grid.after_draw(self.camera)

    def draw(self, *args, **kwargs):
        """
        This is the function you will have to override if you want your
        subclassed to draw something on screen.

        You *must* respect the position, scale, rotation and anchor attributes.
        If you want OpenGL to do the scaling for you, you can::

            def draw(self):
                glPushMatrix()
                self.transform()
                # ... draw ..
                glPopMatrix()
        """
        pass

    def do(self, action, target=None):
        """Executes an *action*.
        When the action finished, it will be removed from the node's actions
        container.

        :Parameters:
            `action` : an `Action` instance
                Action that will be executed.
        :rtype: `Action` instance
        :return: A clone of *action*

        to remove an action you must use the .do return value to
        call .remove_action
        """
        a = copy.deepcopy(action)

        if target is None:
            a.target = self
        else:
            a.target = target

        a.start()
        self.actions.append(a)

        if not self.scheduled:
            if self.is_running:
                self.scheduled = True
                pyglet.clock.schedule(self._step)
        return a

    def remove_action(self, action):
        """Removes an action from the node actions container, potentially calling action.stop()

        If action was running, action.stop is called
        Mandatory interfase to remove actions in the node actions container.
        When skipping this there is the posibility to double call the action.stop

        :Parameters:
            `action` : Action
                Action to be removed
                Must be the return value for a .do(...) call
        """
        assert action in self.actions
        if not action.scheduled_to_remove:
            action.scheduled_to_remove = True
            action.stop()
            action.target = None
            self.to_remove.append(action)

    def pause(self):
        """
        Suspends the execution of actions.
        """
        if not self.scheduled:
            return
        self.scheduled = False
        pyglet.clock.unschedule(self._step)

    def resume(self):
        """
        Resumes the execution of actions.
        """
        if self.scheduled:
            return
        self.scheduled = True
        pyglet.clock.schedule(self._step)
        self.skip_frame = True

    def stop(self):
        """
        Removes all actions from the running action list

        For each action running the stop method will be called,
        and the action will be retired from the actions container.
        """
        for action in self.actions:
            self.remove_action(action)

    def are_actions_running(self):
        """
        Determine whether any actions are running.
        """
        return bool(set(self.actions) - set(self.to_remove))

    def _step(self, dt):
        """pumps all the actions in the node actions container

            The actions scheduled to be removed are removed
            Then an action.step() is called for each action in the
            node actions container, and if the action doenst need any more step
            calls will be scheduled to remove. When scheduled to remove,
            the stop method for the action is called.

        :Parameters:
            `dt` : delta_time
                The time that elapsed since that last time this functions was called.
        """
        for x in self.to_remove:
            if x in self.actions:
                self.actions.remove(x)
        self.to_remove = []

        if self.skip_frame:
            self.skip_frame = False
            return

        if len(self.actions) == 0:
            self.scheduled = False
            pyglet.clock.unschedule(self._step)

        for action in self.actions:
            if not action.scheduled_to_remove:
                action.step(dt)
                if action.done():
                    self.remove_action(action)

    # world to local / local to world methods
    def get_local_transform(self):
        """returns an euclid.Matrix3 with the local transformation matrix

        :rtype: euclid.Matrix3
        """
        if self.is_transform_dirty:

            matrix = euclid.Matrix3().identity()

            matrix.translate(self._x, self._y)
            matrix.translate(self.transform_anchor_x, self.transform_anchor_y)
            matrix.rotate(math.radians(-self.rotation))
            matrix.scale(self._scale * self._scale_x, self._scale * self._scale_y)
            matrix.translate(-self.transform_anchor_x, -self.transform_anchor_y)

            self.is_transform_dirty = False

            self.transform_matrix = matrix

        return self.transform_matrix

    def get_world_transform(self):
        """returns an euclid.Matrix3 with the world transformation matrix

        :rtype: euclid.Matrix3
        """
        matrix = self.get_local_transform()

        p = self.parent
        while p is not None:
            matrix = p.get_local_transform() * matrix
            p = p.parent

        return matrix

    def point_to_world(self, p):
        """returns an euclid.Vector2 converted to world space

        :rtype: euclid.Vector2
        """
        v = euclid.Point2(p[0], p[1])
        matrix = self.get_world_transform()
        return matrix * v

    def get_local_inverse(self):
        """returns an euclid.Matrix3 with the local inverse transformation matrix

        :rtype: euclid.Matrix3
        """
        if self.is_inverse_transform_dirty:

            matrix = self.get_local_transform().inverse()
            self.inverse_transform_matrix = matrix
            self.is_inverse_transform_dirty = False

        return self.inverse_transform_matrix

    def get_world_inverse(self):
        """returns an euclid.Matrix3 with the world inverse transformation matrix

        :rtype: euclid.Matrix3
        """
        matrix = self.get_local_inverse()

        p = self.parent
        while p is not None:
            matrix = matrix * p.get_local_inverse()
            p = p.parent

        return matrix

    def point_to_local(self, p):
        """returns an euclid.Vector2 converted to local space

        :rtype: euclid.Vector2
        """
        v = euclid.Point2(p[0], p[1])
        matrix = self.get_world_inverse()
        return matrix * v
