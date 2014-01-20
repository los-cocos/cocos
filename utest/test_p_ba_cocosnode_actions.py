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

rec = []
next_done=0 #bitflags

class UAction(ac.Action):
##use actions names 1, 2 or '1', '2' ; then you instruct the .step method
##to set ._done using the global next_done
    def init(self, name):
        rec.append((name, 'init'))
        self.name = name

    def start(self):
        rec.append((self.name, 'start'))

    def step(self, dt):
        global rec, next_done
        rec.append((self.name, 'step', dt))
        if int(self.name) & next_done:
            print('setting %s _done to True'%self.name)
            self._done = True

    def stop(self):
        rec.append((self.name, 'stop'))

##    def done(self):
##        rec.append((self.name, 'done', 

class Test_cocosnode_actions_functionality:
    def test_initial_actions_container_empty(self):
        node = CocosNode()
        assert len(node.actions)==0

    def test_do_inmediate_effects1(self):
        # do called without an explicit target
        global rec, next_done
        next_done = 0
        node = CocosNode()
        name1 = '1'
        action = UAction(name1)
        rec = []
        a_copy = node.do(action)
        assert a_copy.target == node
        assert a_copy in node.actions
        assert len(node.actions)==1
        assert rec[0]==(name1, 'start')
        assert len(rec)==1

    def test_do_inmediate_effects2(self):
        # do called with an explicit target
        global rec, next_done
        next_done = 0
        node = CocosNode()
        name1 = '1'
        action = UAction(name1)
        my_target = 'zptx'
        rec = []
        a_copy = node.do(action, target=my_target)
        assert a_copy.target == my_target
        assert a_copy in node.actions
        assert len(node.actions)==1
        assert rec[0]==(name1, 'start')
        assert len(rec)==1

    def test_actions_stepping_without_completion(self):
        global rec, next_done
        next_done = 0
        node = CocosNode()
        name1 = '1'
        action1 = UAction(name1)
        name2 = '2'
        action2 = UAction(name2)
        a1_copy = node.do(action1)
        a2_copy = node.do(action2)

        rec = []
        dt = 0.1
        node._step(dt)
        recx = [e for e in rec if e[0]==name1]
        assert recx[0]==(name1, 'step', dt)
        assert len(recx)==1

        recx = [e for e in rec if e[0]==name2]
        assert recx[0]==(name2, 'step', dt)
        assert len(recx)==1

# the alternate do call, with an explicit target needs some thinking.        

    def test_remove_action(self):
        global rec, next_done
        next_done = 0
        node = CocosNode()
        name1 = '1'
        action1 = UAction(name1)
        name2 = '2'
        action2 = UAction(name2)
        a1_copy = node.do(action1)
        a2_copy = node.do(action2)
        assert len(node.actions)==2
        rec = []
        node.remove_action(a1_copy)

        recx = [ e for e in rec if e[0]==name1]
        assert recx[0]==(name1, 'stop')
        assert len(recx)==1

        rec =[]
        dt = 0.1
        node._step(dt)# needed to complete delete, will traceback if remove failed
        assert len(node.actions)==1
        assert a2_copy in node.actions
        recx = [ e for e in rec if e[0]==name1]
        assert len(recx)==0

    def test_node_stop_calls_remove_and_not_anything_in_action(self):
        global rec, next_done
        next_done = 0
        node = CocosNode()
        name1 = '1'
        action1 = UAction(name1)
        name2 = '2'
        action2 = UAction(name2)
        a1_copy = node.do(action1)
        a2_copy = node.do(action2)

#    def test_stepping_and_one_action_reach_normal_termination(self):
        
