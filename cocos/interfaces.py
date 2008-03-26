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


    def add( self, child, name='', z=0,  *args, **kwargs ):
        """Adds a child to the container

        :Parameters:
            `child` : object
                object to be added
        """
        # child must be a subclass of supported_classes
        if not isinstance( child, self.supported_classes ):
            raise TypeError("%s is not istance of: %s" % (type(child), self.supported_classes) )

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


def test_add():
    c = IContainer()
    for i in range(15):
        c.add(i)
    expected_result = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (0, 13), (0, 14)]

    assert c.children == expected_result

def test_add_z_name():
    c = IContainer()
    for i in range(15):
        c.add(i,z=i%3,name="%s" % i)
    expected_result = [(0, 0), (0, 3), (0, 6), (0, 9), (0, 12), (1, 1), (1, 4), (1, 7), (1, 10), (1, 13), (2, 2), (2, 5), (2, 8), (2, 11), (2, 14)]

    assert c.children == expected_result

def test_remove():
    c = IContainer()
    for i in range(15):
        c.add(i,z=i%3,name="%s" % i)
    c.remove(3)
    expected_result = [(0, 0), (0, 6), (0, 9), (0, 12), (1, 1), (1, 4), (1, 7), (1, 10), (1, 13), (2, 2), (2, 5), (2, 8), (2, 11), (2, 14)]    

    assert c.children == expected_result

def test_remove_by_name():
    c = IContainer()
    for i in range(15):
        c.add(i,z=i%3,name="%s" % i)
    c.remove_by_name('7')
    expected_result = [(0, 0), (0, 3), (0, 6), (0, 9), (0, 12), (1, 1), (1, 4), (1, 10), (1, 13), (2, 2), (2, 5), (2, 8), (2, 11), (2, 14)]

    assert c.children == expected_result

def test_add_unsupported_types():
    try:
        c = IContainer()
        c.supported_classes= (tuple,dict)
        for i in range(15):
            c.add(i,z=i%3,name="%s" % i)
    except TypeError, e:
        print 'add unsupported types: OK'
        assert 1 == 1
    else:
        print 'add unsupported types: FAILED'
        assert 1 == 2

if __name__ == '__main__':

    test_add()
    test_add_z_name()
    test_remove()
    test_remove_by_name()
    test_add_unsupported_types()
