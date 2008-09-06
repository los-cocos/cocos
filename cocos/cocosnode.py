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
"""
CocosNode: the basic element of cocos2d
"""

__docformat__ = 'restructuredtext'

import bisect, copy

import pyglet
from pyglet.gl import *

from director import director
from camera import Camera

import weakref


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

        #: list of children. each item is (int, child-reference) where int is the z-order
        self.children = []

        #: dictionary that maps children names with children references
        self.children_names = {}

        self._parent = None

        # drawing stuff

        #: x-position of the object relative to its parent's children_anchor_x value.
        #: Default: 0
        self.x = 0

        #: y-position of the object relative to its parent's children_anchor_y value.
        #: Default: 0
        self.y = 0

        #: a float, alters the scale of this node and its children.
        #: Default: 1.0
        self.scale = 1.0

        #: a float, in degrees, alters the rotation of this node and its children.
        #: Default: 0.0
        self.rotation = 0.0

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


        #: offset from (x,0) from where children will have its (0,0) coordinate.
        #: Default: 0
        self.children_anchor_x = 0

        #: offset from (x,y) from where children will have its (0,0) coordinate.
        #: Default: 0
        self.children_anchor_y = 0

        #: offset from (x,0) from where rotation and scale will be applied.
        #: Default: 0
        self.transform_anchor_x = 0

        #: offset from (0,y) from where rotation and scale will be applied.
        #: Default: 0
        self.transform_anchor_y = 0

        #: whether of not the object is visible.
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


    def make_property(attr):
        def set_attr():
            def inner(self, value):
                setattr(self, "children_"+attr,value)
                setattr(self, "transform_"+attr,value)
            return inner
        def get_attr():
            def inner(self):
                if getattr(self,"children_"+attr) != getattr(self, "transform_"+attr):
                    raise Exception("no consistent value for "+attr)
                return getattr(self,"children_"+attr)
            return inner
        return property(
            get_attr(),
            set_attr(),
            doc="""a property to get fast access to [transform_|children_]

            :type: (int,int)
            """+attr )

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
                setattr(self, attr+"_x",value[0])
                setattr(self, attr+"_y",value[1])
            return inner
        def get_attr(self):
            return getattr(self,attr+"_x"),  getattr(self,attr+"_y")
        return property(
            get_attr,
            set_attr(),
            doc='''a property to get fast access to "+attr+"_[x|y]

            :type: (int,int)
            ''')

    #: Children anchor point.
    #: Children will be added relative to this point
    children_anchor = make_property("children_anchor")

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

        total_len = len(self.scheduled_calls + self.scheduled_interval_calls)
        self.scheduled_calls = [
                c for c in self.scheduled_calls if c[0] != callback
                ]
        self.scheduled_interval_calls = [
                c for c in self.scheduled_interval_calls if c[0] != callback
                ]

        if self.is_running:
            pyglet.clock.unschedule( callback )

    def resume_scheduler(self):
        """
        Time will continue/start passing for this node and callbacks
        will be called.
        """
        for c, i, a, k in self.scheduled_interval_calls:
            pyglet.clock.schedule_interval(c, i, *a, **k)
        for c, a, k in self.scheduled_calls:
            pyglet.clock.schedule(c, *a, **k)

    def pause_scheduler(self):
        """
        Time will stop passing for this node and callbacks will
        not be called
        """
        for f in set(
                [ x[0] for x in self.scheduled_interval_calls ] +
                [ x[0] for x in self.scheduled_calls ]
                ):
            pyglet.clock.unschedule(f)
        for arg in self.scheduled_calls:
            pyglet.clock.unschedule(arg[0])

    def _get_parent(self):
        if self._parent is None: return None
        else: return self._parent()

    def _set_parent(self, parent):
        if parent is None: self._parent = None
        else: self._parent = weakref.ref(parent)

    parent = property(_get_parent, _set_parent, doc='''The parent of this object.

    :type: object
    ''')

    def get_ancestor(self, klass):
        """
        Walks the nodes tree upwards until it finds a node of the class `klass`
        or returns None
        """
        if isinstance(self, klass):
            return self
        parent = self.parent
        if parent:
            return parent.get_ancestor( klass )

    def _get_position(self):
        return (self.x, self.y)
    def _set_position(self, (x,y)):
        self.x, self.y = x,y

    position = property(_get_position, _set_position,
                        doc='''The (x, y) coordinates of the object.

    :type: (int, int)
    ''')

    def add(self, child, z=0, name=None ):
        """Adds a child to the container

        :Parameters:
            `child` : object
                object to be added
            `z` : float
                the z index of self
            `name` : str
                Name of the child
        """
        # child must be a subclass of supported_classes
        #if not isinstance( child, self.supported_classes ):
        #    raise TypeError("%s is not instance of: %s" % (type(child), self.supported_classes) )

        if name:
            if name in self.children_names:
                raise Exception("Name already exists: %s" % name )
            self.children_names[ name ] = child

        child.parent = self

        elem = z, child
        bisect.insort( self.children,  elem )
        if self.is_running:
            child.on_enter()
        return self

    def remove( self, obj ):
        """Removes a child from the container given its name or object

        :Parameters:
            `obj` : string or object
                name of the reference to be removed
                or object to be removed
        """
        if isinstance(obj, str):
            if obj in self.children_names:
                child = self.children_names.pop( obj )
                self._remove( child )
            else:
                raise Exception("Child not found: %s" % obj )
        else:
            self._remove(obj)

    def _remove( self, child ):
        l_old = len(self.children)
        self.children = [ (z,c) for (z,c) in self.children if c != child ]

        if l_old == len(self.children):
            raise Exception("Child not found: %s" % str(child) )

        if self.is_running:
            child.on_exit()

    def get_children(self):
        return [ c for (z, c) in self.children ]

    def __contains__(self, child):
        return  c in self.get_children()

    def get( self, name ):
        """Gets a child from the container given its name

        :Parameters:
            `name` : string
                name of the reference to be get
        """
        if name in self.children_names:
            return self.children_names[ name ]
        else:
            raise Exception("Child not found: %s" % name )

    def on_enter( self ):
        """
        Called every time just before the node enters the stage.
        """
        self.is_running = True

        # start actions
        self.resume()
        # resume scheduler
        self.resume_scheduler()

        # propagate
        for c in self.get_children():
            c.on_enter()


    def on_exit( self ):
        """
        Called every time just before the node leaves the stage
        """
        self.is_running = False

        # pause actions
        self.pause()
        # pause callbacks
        self.pause_scheduler()

        # propagate
        for c in self.get_children():
            c.on_exit()


    def transform( self ):
        """
        Apply ModelView transformations
        you will most likely want to wrap calls to this function with
        glPushMatrix/glPopMatrix
        """
        x,y = director.get_window_size()

        if not(self.grid and self.grid.active):
            # only apply the camera if the grid is not active
            # otherwise, the camera will be applied inside the grid
            self.camera.locate()

        if self.transform_anchor != (0,0):
            glTranslatef(
                self.position[0] + self.transform_anchor_x,
                self.position[1] + self.transform_anchor_y,
                 0 )
        elif self.position != (0,0):
            glTranslatef( self.position[0], self.position[1], 0 )


        if self.scale != 1.0:
            glScalef( self.scale, self.scale, 1)

        if self.rotation != 0.0:
            glRotatef( -self.rotation, 0, 0, 1)

        if self.transform_anchor != (0,0):
            if self.transform_anchor != self.children_anchor:
                glTranslatef(
                    self.children_anchor_x - self.transform_anchor_x,
                    self.children_anchor_y - self.transform_anchor_y,
                     0 )
        #elif self.children_anchor != (0,0):
        #    glTranslatef(
        #        self.children_anchor_x,
        #        self.children_anchor_y,
        #         0 )


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
            collect.append( r )

        for node in self.get_children():
            node.walk(callback, collect)

        return collect

    def visit(self):
        '''
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
        '''

        if not self.visible:
            return

        position = 0

        if self.grid and self.grid.active:
            self.grid.before_draw()

        # we visit all nodes that should be drawn before ourselves
        if self.children and self.children[0][0] < 0:
            glPushMatrix()
            self.transform()
            for z,c in self.children:
                if z >= 0: break
                position += 1
                c.visit()

            glPopMatrix()

        # we draw ourselves
        self.draw()

        # we visit all the remaining nodes, that are over ourselves
        if position < len(self.children):
            glPushMatrix()
            self.transform()
            for z,c in self.children[position:]:
                c.visit()
            glPopMatrix()

        if self.grid and self.grid.active:
            self.grid.after_draw( self.camera )


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

    def do( self, action, target=None ):
        '''Executes an *action*.
        When the action finished, it will be removed from the sprite's queue.

        :Parameters:
            `action` : an `Action` instance
                Action that will be executed.
        :rtype: `Action` instance
        :return: A clone of *action*
        '''
        a = copy.deepcopy( action )

        if target is None:
            a.target = self
        else:
            a.target = target

        a.start()
        self.actions.append( a )

        if not self.scheduled:
            if self.is_running:
                self.scheduled = True
                pyglet.clock.schedule( self._step )
        return a

    def remove_action(self, action ):
        """Removes an action from the queue

        :Parameters:
            `action` : Action
                Action to be removed
        """
        self.to_remove.append( action )

    def pause(self):
        """
        Suspends the execution of actions.
        """
        if not self.scheduled:
            return
        self.scheduled = False
        pyglet.clock.unschedule( self._step )

    def resume(self):
        """
        Resumes the execution of actions.
        """
        if self.scheduled:
            return
        self.scheduled = True
        pyglet.clock.schedule( self._step )
        self.skip_frame = True

    def stop(self):
        """
        Removes all actions from the running action list
        """
        for action in self.actions:
            self.to_remove.append( action )

    def are_actions_running(self):
        """
        Determine whether any actions are running.
        """
        return bool(set(self.actions) - set(self.to_remove))

    def _step(self, dt):
        """This method is called every frame.

        :Parameters:
            `dt` : delta_time
                The time that elapsed since that last time this functions was called.
        """
        for x in self.to_remove:
            if x in self.actions:
                self.actions.remove( x )
        self.to_remove = []

        if self.skip_frame:
            self.skip_frame = False
            return

        if len( self.actions ) == 0:
            self.scheduled = False
            pyglet.clock.unschedule( self._step )

        for action in self.actions:
            action.step(dt)
            if action.done():
                action.stop()
                self.remove_action( action )


