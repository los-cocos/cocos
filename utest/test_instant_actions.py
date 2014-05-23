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

import cocos
import cocos.actions.instant_actions
from cocos.cocosnode import CocosNode
from cocos.director import director

director.init()

def test_Loop_InstantAction():
    rec = []
    def f(x):
       rec.append(x)
    node = CocosNode()
    template_action = cocos.actions.instant_actions.CallFunc(f, 1)
    n = 5
    action = template_action * n
    node.do(action)
    assert rec == [1] * n


