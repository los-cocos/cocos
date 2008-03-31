#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
"""Interfaces uses internally by Sprites, Layers and Scenes"""

import bisect, copy

from pyglet.gl import *

from director import director
from mesh import Mesh

__all__ = ['IContainer','IActionTarget',]


class IContainer( object ):

    supported_classes = (object,)

    def __init__( self, *children ):

        super( IContainer, self).__init__()

        self.children = []
        self.children_names = {}

        self.position = (0,0)
        self.scale = 1.0
        self.rotation = 0.0
        self.anchor_x = 0.5
        self.anchor_y = 0.5
        self.color = (255,255,255)
        self.opacity = 255
        self.mesh = Mesh()

        self.batch  = None

        self.add_children( *children )


    def add( self, child, position=(0,0), rotation=0.0, scale=1.0, color=(255,255,255), opacity=255, anchor_x=0.5, anchor_y=0.5, name=None, z=0 ):  
        """Adds a child to the container

        :Parameters:
            `child` : object
                object to be added
            `name` : str
                Name of the child
            `position` : tuple
                 this is the lower left corner by default
            `rotation` : float 
                the rotation (degrees)
            `scale` : float
                the zoom factor
            `opacity` : int
                the opacity (0=transparent, 255=opaque)
            `color` : tuple
                the color to colorize the child (RGB 3-tuple)
            `anchor_x` : float
                x-point from where the image will be rotated / scaled. Value goes from 0 to 1
            `anchor_y` : float
                y-point from where the image will be rotated / scaled. Value goes from 0 to 1
        """
        # child must be a subclass of supported_classes
        if not isinstance( child, self.supported_classes ):
            raise TypeError("%s is not istance of: %s" % (type(child), self.supported_classes) )

        if self.batch:
            child.batch = self.batch

        properties = {'position' : position,
                      'rotation' : rotation,
                      'scale' : scale,
                      'color' : color,
                      'opacity' : opacity,
                      'anchor_x' : anchor_x,
                      'anchor_y' : anchor_y,
                      }

        elem = z, child 
        bisect.insort( self.children,  elem )

        for k,v in properties.items():
            setattr(child, k, v)

        if name:
            self.children_names[ name ] = child

    def add_children( self, *children ):
        """Adds a list of children to the container

        :Parameters:
            `children` : list of objects
                objects to be added
        """
        for c in children:
            self.add( c )

    def remove( self, child ): 
        """Removes a child from the container

        :Parameters:
            `child` : object
                object to be removed
        """
        self.children = [ (z,c) for (z,c) in self.children if c != child ]



    def remove_by_name( self, name ):
        """Removes a child from the container given its name

        :Parameters:
            `name` : string
                name of the reference to be removed
        """
        if name in self.children_names:
            child = self.children_names.pop( name )
            self.remove( child )

    def transform( self ):
        """Apply ModelView transformations"""

        x,y = director.get_window_size()

        color = tuple(self.color) + (self.opacity,)
        if color != (255,255,255,255):
            glColor4ub( * color )

        if self.anchor_x != 0 or self.anchor_y != 0:
            rel_x = self.anchor_x * x + self.position[0]
            rel_y = self.anchor_y * y + self.position[1]
            glTranslatef( rel_x, rel_y, 0 )

        if self.scale != 1.0:
            glScalef( self.scale, self.scale, 1)

        if self.rotation != 0.0:
            glRotatef( -self.rotation, 0, 0, 1)

        if self.anchor_x != 0 or self.anchor_y != 0:
            glTranslatef( -rel_x, -rel_y, 0 )

        if self.position != (0,0):
            glTranslatef( self.position[0], self.position[1], 0 )

class IActionTarget(object):
    def __init__(self):

        super( IActionTarget, self).__init__()

        self.actions = []
        self.to_remove = []
        self.scheduled = False
        self.skip_frame = False


    def do( self, action ):
        '''Executes an *action*.
        When the action finished, it will be removed from the sprite's queue.

        :Parameters:
            `action` : an `Action` instance
                Action that will be executed.
        :rtype: `Action` instance
        :return: A clone of *action*
        '''
        a = copy.deepcopy( action )
        
        a.target = self
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
        
        
    def flush(self):
        """Removes running actions from the queue"""
        for action in self.actions:
            self.to_remove.append( action )

    def _step(self, dt):
        """This method is called every frame.

        :Parameters:
            `dt` : delta_time
                The time that elapsed since that last time this functions was called.
        """
        for x in self.to_remove:
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
                self.remove_action( action )
                
    
