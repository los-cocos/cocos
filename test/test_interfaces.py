# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

from cocos.interfaces import *

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
