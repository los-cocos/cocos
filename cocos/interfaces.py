#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
"""Interfaces uses internally by Sprites, Layers and Scenes"""

import bisect

__all__ = ['IContainer']


class IContainer( object ):

    supported_classes = (object,)

    def __init__( self, *children ):
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

    def add( self, child, name='', z=0, position=(0,0), rotation=0.0, scale=1.0, color=(255,255,255), opacity=255):  
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
        """
        # child must be a subclass of supported_classes
        if not isinstance( child, self.supported_classes ):
            raise TypeError("%s is not istance of: %s" % (type(child), self.supported_classes) )

        properties = {'position' : position,
                      'rotation' : rotation,
                      'scale' : scale,
                      'color' : color,
                      'opacity' : opacity }

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
