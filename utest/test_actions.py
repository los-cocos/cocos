from __future__ import division, print_function, unicode_literals

# important: set cocos_utest=1 in the environment before run.
# that simplifies the pyglet mockup needed
# remember to erase or set to zero for normal runs
import os
assert os.environ['cocos_utest']

# set the desired pyglet mockup
import sys
sys.path.insert(0,'pyglet_mockup1')
import pyglet
assert pyglet.mock_level == 1 

import unittest
from cocos.director import director
from cocos.cocosnode import CocosNode
import cocos.actions as ac

import sys

director.init()

class Actions1(unittest.TestCase):
    def test_remove_action(self):
        node = CocosNode()
        self.assertTrue(len(node.actions)==0)
        action = ac.Action()
        a_copy = node.do(action)
        self.assertTrue(len(node.actions)==1)
        node.remove_action(a_copy)
        dt = 0.1
        node._step(dt)# needed to complete delete, will traceback if remove failed
        self.assertTrue(len(node.actions)==0)

if __name__ == '__main__':
    unittest.main()
