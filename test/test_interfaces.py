# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

from cocos.interfaces import *

class AddMe( object ):
    def __init__( self, value ):
        self.value = value

    def __repr__( self ):
        return str(self.value)

def test_add():
    c = IContainer()
    for i in range(7):
        c.add( AddMe(i ) )

    expected_result = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6)]
    assert repr(c.children) == repr(expected_result)

def test_add_z_name():
    c = IContainer()
    for i in range(7):
        c.add( AddMe(i),z=i%3,name="%s" % i)

    expected_result = [(0, 0), (0, 3), (0, 6), (1, 1), (1, 4), (2, 2), (2, 5)]
    assert repr(c.children) == repr(expected_result)

def test_remove():
    c = IContainer()
    f = AddMe(99)
    for i in range(7):
        c.add( AddMe(i),z=i%3,name="%s" % i)
    c.add(f,z=1)
    c.remove(f)
    expected_result = [(0, 0), (0, 3), (0, 6), (1, 1), (1, 4), (2, 2), (2, 5)]
    assert repr(c.children) == repr(expected_result)

def test_remove_by_name():
    c = IContainer()
    for i in range(7):
        c.add(AddMe(i),z=i%3,name="%s" % i)
    c.remove_by_name('5')
    expected_result = [(0, 0), (0, 3), (0, 6), (1, 1), (1, 4), (2, 2)]
    assert repr(c.children) == repr(expected_result)

def test_add_unsupported_types():
    try:
        c = IContainer()
        c.supported_classes= (tuple,dict)
        for i in range(7):
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
