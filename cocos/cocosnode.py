#
# Cocos
# http://code.google.com/p/los-cocos
#
"""
CocosNode: the basic element of cocos
"""

__docformat__ = 'restructuredtext'

import bisect, copy

import pyglet
from pyglet.gl import *

from director import director
from grid import Grid

import weakref


__all__ = ['CocosNode']

class CocosNode(object):
    def __init__(self):
        # composition stuff
        self.children = []
        self.children_names = {}
        self._parent = None
        
        # drawing stuff
        self.x, self.y = (0,0)
        self.scale = 1.0
        self.rotation = 0.0
        self.children_anchor_x = 0
        self.children_anchor_y = 0
        self.transform_anchor_x = 0
        self.transform_anchor_y = 0
        self.color = (255,255,255)
        self.opacity = 255
        self.grid = None
        self.visible = True

        # actions stuff
        self.actions = []
        self.to_remove = []
        self.skip_frame = False
        
        # schedule stuff
        self.scheduled = False # deprecated, soon to be removed
        self.scheduled_calls = []
        self.scheduled_interval_calls = []
        self.is_running = False
        
    
    def make_property(attr):
        def set_attr():
            def inner(self, value):
                setattr(self, "children_"+attr,value)
                setattr(self, "transform_"+attr,value)
            return inner
        def get_attr():
            def inner(self, value):
                if getattr(self,"children_"+attr) != getattr(self, "transform_"+attr):
                    raise Exception("no consistent value for "+attr)
                return getattr(self,"children_"+attr)
            return inner
        return property(
            get_attr(),
            set_attr(),
            doc="""a property to get fast access to [transform_|children_]"""+attr )

    anchor = make_property("anchor")
    anchor_x = make_property("anchor_x")
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
            doc="a property to get fast access to "+attr+"_[x|y]" )

    children_anchor = make_property("children_anchor")
    transform_anchor = make_property("transform_anchor")

        
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
        if total_len == len(
                self.scheduled_calls + self.scheduled_interval_calls
                ):
            raise Exception("Call not scheduled")
            
        if self.is_running:
            pyglet.clock.unschedule( callback )
           
    def resume_scheduler(self):
        for c, i, a, k in self.scheduled_interval_calls:
            pyglet.clock.schedule_interval(c, i, *a, **k)  
        for c, a, k in self.scheduled_calls:
            pyglet.clock.schedule(c, *a, **k)  
            
    def pause_scheduler(self):
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
        
    parent = property(_get_parent, _set_parent)
        
    def get(self, klass):
        """
        Walks the nodes tree upwards until it finds a node of the class `klass`
        or returns None
        """
        if isinstance(self, klass):
            return self
        parent = self.parent
        if parent:
            return parent.get( klass )
            
    def _get_position(self):
        return (self.x, self.y)
    def _set_position(self, (x,y)):
        self.x, self.y = x,y
        
    position = property(_get_position, _set_position, doc="Get an (x,y) tuple")
        
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
        
    def remove( self, child ):
        """Removes a child from the container

        :Parameters:
            `child` : object
                object to be removed
        """
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

    def remove_by_name( self, name ):
        """Removes a child from the container given its name

        :Parameters:
            `name` : string
                name of the reference to be removed
        """
        if name in self.children_names:
            child = self.children_names.pop( name )
            self.remove( child )
        else:
            raise Exception("Child not found: %s" % name )

    def get_by_name( self, name ):
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
        """Apply ModelView transformations"""
        x,y = director.get_window_size()

        color = tuple(self.color) + (self.opacity,)
        if color != (255,255,255,255):
            color = [ int(c) for c in color ]
            glColor4ub( * color )
            
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
            if self.transform_anchor == self.children_anchor:
                glTranslatef( 
                    self.transform_anchor_x, 
                    self.transform_anchor_y,
                     0 )
            else:
                glTranslatef( 
                    self.children_anchor_x - self.transform_anchor_x, 
                    self.children_anchor_y - self.transform_anchor_y,
                     0 )            
        elif self.children_anchor != (0,0):
            glTranslatef( 
                self.children_anchor_x, 
                self.children_anchor_y,
                 0 )


    def walk(self, callback, collect=None):
        """
        Executes callback on all the subtree starting at self.
        returns a list of all return values that are not none
        
        :Parameters:
            `callback` : callable, takes a cocosnode as argument

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
        self.on_draw()
        
        # we visit all the remaining nodes, that are over ourselves
        if position < len(self.children):
            glPushMatrix()
            self.transform()
            for z,c in self.children[position:]:
                c.visit()
            glPopMatrix()
        
        if self.grid and self.grid.active:
            self.grid.after_draw()

        
    def on_draw(self, *args, **kwargs):
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
        if not self.scheduled:
            return
        self.scheduled = False
        pyglet.clock.unschedule( self._step )

    def resume(self):
        if self.scheduled:
            return
        self.scheduled = True
        pyglet.clock.schedule( self._step )
        self.skip_frame = True

    def stop(self):
        """Removes running actions from the queue"""
        for action in self.actions:
            self.to_remove.append( action )

    def actions_running(self):
        """Determine whether any actions are running."""
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
        

