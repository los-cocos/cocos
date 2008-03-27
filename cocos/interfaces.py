#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
"""Interfaces uses internally by Sprites, Layers and Scenes"""

import bisect, copy

from pyglet.gl import *

from director import director
__all__ = ['IContainer']


class IContainer( object ):

    supported_classes = (object,)

    def __init__( self, *children ):

        super( IContainer, self).__init__()

        self.children = []
        self.children_names = {}

        self.add_children( *children )

        self.position = (0,0)
        self.scale = 1.0
        self.rotation = 0.0
        self.anchor_x = 0.5
        self.ancho_y = 0.5
        self.color = (255,255,255)
        self.opacity = 255
        self.mesh = None

    def add( self, child, name='', z=0, position=(0,0), rotation=0.0, scale=1.0, color=(255,255,255), opacity=255, anchor_x=0.5, anchor_y=0.5):  
        """Adds a child to the container

        :Parameters:
            `child` : object
                object to be added
            `name` : str
                Name of the child
            `position` : tuple
                 this is the lower left corner by default
            `rotation` : int
                the rotation (degrees)
            `scale` : int
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

        properties = {'position' : position,
                      'rotation' : rotation,
                      'scale' : scale,
                      'color' : color,
                      'opacity' : opacity,
                      'anchor_x' : anchor_x,
                      'anchor_y' : anchor_y,
                      }

        elem = z, child, properties
        bisect.insort( self.children,  elem )

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
        self.children = [ (z,c,p) for (z,c,p) in self.children if c != child ]


    def remove_by_name( self, name ):
        """Removes a child from the container given its name

        :Parameters:
            `name` : string
                name of the reference to be removed
        """
        if name in self.children_names:
            child = self.children_names.pop( name )
            self.remove( child )


    def apply_transformation( self, color=(255,255,255), opacity=255, scale=1.0, rotation=0.0, position=(0,0), anchor_x=0.5, anchor_y=0.5 ):
        """Apply a GL transformation

        :Parameters:
            `position` : tuple
                 this is the lower left corner by default
            `rotation` : int
                the rotation (degrees)
            `scale` : int
                the zoom factor
            `color` : tuple
                the color to colorize the child (RGB 3-tuple)
            `opacity` : int
                the opacity (0=transparent, 255=opaque)
            `anchor_x` : float
                x-point from where the image will be rotated / scaled. Value goes from 0 to 1
            `anchor_y` : float
                y-point from where the image will be rotated / scaled. Value goes from 0 to 1
        """

        x,y = director.get_window_size()

        c = color + (opacity,)
        if c != (255,255,255,255):
            glColor4ub( * c )

        # Anchor point for scaling and rotation
        if self.anchor_x != 0 or self.anchor_y != 0:
            rel_x = self.anchor_x * x
            rel_y = self.anchor_x * y
            glTranslatef( rel_x, rel_y, 0 )

        if scale != 1.0:
            glScalef( scale, scale, 1)

        if rotation != 0.0:
            glRotatef( -rotation, 0, 0, 1)

        if self.anchor_x != 0 or self.anchor_y != 0:
            glTranslatef( -rel_x, -rel_y, 0 )

        if position != (0,0):
            glTranslatef( position[0], position[1], 0 )

class IActionTarget:
    def __init__(self):
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
            pyglet.clock.schedule( self.step )
        return a

    def remove(self, action ):
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
        pyglet.clock.unschedule( self.step )
        
    def resume(self):
        if self.scheduled:
            return
        self.scheduled = True
        pyglet.clock.schedule( self.step )
        self.skip_frame = True
        
        
    def flush(self):
        """Removes running actions from the queue"""
        for action in self.actions:
            self.to_remove.append( action )

    def step(self, dt):
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
            pyglet.clock.unschedule( self.step )

        for action in self.actions:
            action.step(dt)
            if action.done():
                self.remove( action )
                

