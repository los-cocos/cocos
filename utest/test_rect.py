from __future__ import division, print_function, unicode_literals

# that simplifies the pyglet mockup needed
# remember to erase or set to zero for normal runs
import os
assert os.environ['cocos_utest']

# set the desired pyglet mockup
import sys
sys.path.insert(0,'pyglet_mockup1')
import pyglet
assert pyglet.mock_level == 1

# will use the cocos in the same checkout, except if you move this file.
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.rect import Rect

def test_clippedBy__disjoint():
    r1 = Rect(0, 0, 10, 10)
    r2 = Rect(20, 20, 10, 10)
    assert r1.clippedBy(r2)

def test_clippedBy__encompassing():
    r1 = Rect(0, 0, 10, 10)
    r2 = Rect(0, 0, 10, 10)
    assert not r1.clippedBy(r2)

def test_clippedBy__partial_overlappinng():
    r1 = Rect(0, 0, 10, 10)
    r2 = Rect(5, 5, 10, 10)
    assert r1.clippedBy(r2)



