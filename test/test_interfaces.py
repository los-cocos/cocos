# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

from cocos.interfaces import *

def test_add():
    c = IContainer()
    for i in range(7):
        c.add(i)
    expected_result = [(0, 0, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 1, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 2, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 3, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 4, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 5, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 6, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5})]

    assert c.children == expected_result

def test_add_z_name():
    c = IContainer()
    for i in range(7):
        c.add(i,z=i%3,name="%s" % i)
    expected_result = [(0, 0, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 3, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 6, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (1, 1, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (1, 4, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (2, 2, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (2, 5, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5})]

    assert c.children == expected_result

def test_remove():
    c = IContainer()
    for i in range(7):
        c.add(i,z=i%3,name="%s" % i)
    c.remove(3)
    expected_result = [(0, 0, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 6, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (1, 1, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (1, 4, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (2, 2, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (2, 5, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5})]

    assert c.children == expected_result

def test_remove_by_name():
    c = IContainer()
    for i in range(7):
        c.add(i,z=i%3,name="%s" % i)
    c.remove_by_name('5')
    expected_result = [(0, 0, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 3, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (0, 6, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (1, 1, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (1, 4, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5}), (2, 2, {'opacity': 255, 'scale': 1.0, 'color': (255, 255, 255), 'position': (0, 0), 'rotation': 0.0, 'anchor_y': 0.5, 'anchor_x': 0.5})]

    assert c.children == expected_result

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
