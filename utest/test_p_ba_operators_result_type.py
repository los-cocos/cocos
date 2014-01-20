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

from cocos.director import director
from cocos.cocosnode import CocosNode
import cocos.actions as ac

import sys

director.init()

class Test_sequence_result_type:
    """
    Expected result table  
    openrand_2 ->   |Action      IntervalAction  InstantAction
    operand_1       |
    ----------------------------------------------------------
    Action          |Action     Action              Action
    IntervalAction  |Action     IntervalAction      IntervalAction
    InstantAction   |Action     IntervalAction      InstantAction
    """
    def test_action_action_action(self):
        a = ac.Action()
        b = ac.Action()
        res = a + b
        assert isinstance(res, ac.Action)
        assert not isinstance(res, ac.IntervalAction)

    def test_action_interval_action(self):
        a = ac.Action()
        b = ac.IntervalAction()
        b.duration = 3.0
        res = a + b
        assert isinstance(res, ac.Action)
        assert not isinstance(res, ac.IntervalAction)

    def test_action_instant_action(self):
        a = ac.Action()
        b = ac.InstantAction()
        res = a + b
        assert isinstance(res, ac.Action)
        assert not isinstance(res, ac.IntervalAction)

    def test_interval_action_action(self):
        a = ac.Action()
        b = ac.IntervalAction()
        b.duration = 3.0
        res = b + a
        assert isinstance(res, ac.Action)
        assert not isinstance(res, ac.IntervalAction)

    def test_instant_action_action(self):
        a = ac.Action()
        b = ac.InstantAction()
        res = b + a
        assert isinstance(res, ac.Action)
        assert not isinstance(res, ac.IntervalAction)

    def test_interval_interval_interval(self):
        a = ac.IntervalAction()
        a.duration = 3.0
        b = ac.IntervalAction()
        b.duration = 5.0
        res = a + b
        assert isinstance(res, ac.IntervalAction)
        assert not isinstance(res, ac.InstantAction)

    def test_interval_instant_interval(self):        
        a = ac.IntervalAction()
        a.duration = 3.0
        b = ac.InstantAction()
        assert b.duration==0.0
        res = a + b
        assert isinstance(res, ac.IntervalAction)
        assert not isinstance(res, ac.InstantAction)

    def test_instant_interval_interval(self):        
        a = ac.IntervalAction()
        a.duration = 3.0
        b = ac.InstantAction()
        res = b + a
        assert isinstance(res, ac.IntervalAction)
        assert not isinstance(res, ac.InstantAction)

    def test_instant_instant_instant(self):
        a = ac.InstantAction()
        b = ac.InstantAction()
        res = a + b
        assert isinstance(res, ac.InstantAction)
        

class Test_spawn_result_type:
    """
    Expected result table  
    openrand_2 ->   |Action      IntervalAction  InstantAction
    operand_1       |
    ----------------------------------------------------------
    Action          |Action     Action              Action
    IntervalAction  |Action     IntervalAction      IntervalAction
    InstantAction   |Action     IntervalAction      InstantAction
    """
    def test_action_action_action(self):
        a = ac.Action()
        b = ac.Action()
        res = a | b
        assert isinstance(res, ac.Action)
        assert not isinstance(res, ac.IntervalAction)

    def test_action_interval_action(self):
        a = ac.Action()
        b = ac.IntervalAction()
        b.duration = 3.0
        res = a | b
        assert isinstance(res, ac.Action)
        assert not isinstance(res, ac.IntervalAction)

    def test_action_instant_action(self):
        a = ac.Action()
        b = ac.InstantAction()
        res = a | b
        assert isinstance(res, ac.Action)
        assert not isinstance(res, ac.IntervalAction)

    def test_interval_action_action(self):
        a = ac.Action()
        b = ac.IntervalAction()
        b.duration = 3.0
        res = b | a
        assert isinstance(res, ac.Action)
        assert not isinstance(res, ac.IntervalAction)

    def test_instant_action_action(self):
        a = ac.Action()
        b = ac.InstantAction()
        res = b | a
        assert isinstance(res, ac.Action)
        assert not isinstance(res, ac.IntervalAction)

    def test_interval_interval_interval(self):
        a = ac.IntervalAction()
        a.duration = 3.0
        b = ac.IntervalAction()
        b.duration = 5.0
        res = a | b
        assert isinstance(res, ac.IntervalAction)
        assert not isinstance(res, ac.InstantAction)

    def test_interval_instant_interval(self):        
        a = ac.IntervalAction()
        a.duration = 3.0
        b = ac.InstantAction()
        assert b.duration==0.0
        res = a | b
        assert isinstance(res, ac.IntervalAction)
        assert not isinstance(res, ac.InstantAction)

    def test_instant_interval_interval(self):        
        a = ac.IntervalAction()
        a.duration = 3.0
        b = ac.InstantAction()
        res = b | a
        assert isinstance(res, ac.IntervalAction)
        assert not isinstance(res, ac.InstantAction)

    def test_instant_instant_instant(self):
        a = ac.InstantAction()
        b = ac.InstantAction()
        res = a | b
        assert isinstance(res, ac.InstantAction)

        
