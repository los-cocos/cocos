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
    expected_result = [(0, 0, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 1, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 2, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 3, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 4, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 5, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 6, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 7, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 8, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 9, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 10, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 11, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 12, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 13, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 14, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255})]

    assert c.children == expected_result

def test_add_z_name():
    c = IContainer()
    for i in range(15):
        c.add(i,z=i%3,name="%s" % i)
    expected_result =[(0, 0, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 3, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 6, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 9, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 12, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 1, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 4, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 7, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 10, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 13, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 2, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 5, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 8, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 11, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 14, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255})]

    assert c.children == expected_result

def test_remove():
    c = IContainer()
    for i in range(15):
        c.add(i,z=i%3,name="%s" % i)
    c.remove(3)
    expected_result = [(0, 0, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 6, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 9, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 12, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 1, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 4, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 7, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 10, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 13, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 2, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 5, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 8, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 11, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 14, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255})]

    assert c.children == expected_result

def test_remove_by_name():
    c = IContainer()
    for i in range(15):
        c.add(i,z=i%3,name="%s" % i)
    c.remove_by_name('7')
    expected_result = [(0, 0, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 3, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 6, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 9, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (0, 12, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 1, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 4, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 10, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (1, 13, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 2, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 5, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 8, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 11, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255}), (2, 14, {'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0, 'scale': 1, 'opacity': 255})]

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
