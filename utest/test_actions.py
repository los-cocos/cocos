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
    def test_delete(self):
        node = CocosNode()
        self.assertTrue(len(node.actions)==0)
        action = ac.Action()
        node.do(action)
        self.assertTrue(len(node.actions)==1)
        node.remove_action(action)
        self.assertTrue(len(node.actions)==0)

if __name__ == '__main__':
    unittest.main()
