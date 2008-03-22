#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
"""Interfaces uses internally by Sprites, Layers and Scenes"""

import bisect

__all__ = ['IContainer']


class IContainer( object ):

    supported_classes = (object)

    def __init__( self, *children ):
        self.children = []
        self.children_names = {}

        self.add_children( *children )


    def add( self, child, *args, **kwargs ):
        """Adds a child to the container

        :Parameters:
            `child` : object
                object to be added
        """
        name = ''
        z = 0

        # child must be a subclass of supported_classes
        if not isinstance( child, self.supported_classes ):
            raise TypeError("%s is not istance of: %s" % (type(child), self.supported_classes) )

        if 'name' in kwargs:
            name = kwargs.pop('name')
        if 'z' in kwargs:
            z = kwargs.pop('z')                            

        elem = z, child
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


if __name__ == '__main__':
    c = IContainer()
    for i in range(15):
        c.add(i)
    expected_result = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (0, 13), (0, 14)]
    if c.children != expected_result:
        print 'add(c): FAILED'
    else:
        print 'add(c): OK'

    c = IContainer()
    for i in range(15):
        c.add(i,z=i%3,name="%s" % i)
    expected_result = [(0, 0), (0, 3), (0, 6), (0, 9), (0, 12), (1, 1), (1, 4), (1, 7), (1, 10), (1, 13), (2, 2), (2, 5), (2, 8), (2, 11), (2, 14)]
    if c.children != expected_result:
        print 'add(c,z,name): FAILED'
    else:
        print 'add(c,z,name): OK'

    c = IContainer()
    for i in range(15):
        c.add(i,z=i%3,name="%s" % i)
    c.remove(3)
    expected_result = [(0, 0), (0, 6), (0, 9), (0, 12), (1, 1), (1, 4), (1, 7), (1, 10), (1, 13), (2, 2), (2, 5), (2, 8), (2, 11), (2, 14)]    
    if c.children != expected_result:
        print 'remove(): FAILED'
    else:
        print 'remove(): OK'

    c = IContainer()
    for i in range(15):
        c.add(i,z=i%3,name="%s" % i)
    c.remove_by_name('7')
    expected_result = [(0, 0), (0, 3), (0, 6), (0, 9), (0, 12), (1, 1), (1, 4), (1, 10), (1, 13), (2, 2), (2, 5), (2, 8), (2, 11), (2, 14)]
    if c.children != expected_result:
        print 'remove_by_name(): FAILED'
    else:
        print 'remove_by_name(): OK'

    try:
        c = IContainer()
        c.supported_classes= (tuple,dict)
        for i in range(15):
            c.add(i,z=i%3,name="%s" % i)
    except TypeError, e:
        print 'add unsupported types: OK'
    else:
        print 'add unsupported types: FAILED'
