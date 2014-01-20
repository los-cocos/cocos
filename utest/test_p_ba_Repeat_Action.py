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


class Test_Repeat_Action:

    def test_instantiation(self):
        global rec, next_done
        name1 = '1'
        a1 = UAction(name1)
        assert isinstance(a1, ac.Action)

        rec = []
        composite = ac.Repeat(a1)
        assert isinstance(composite, ac.Action)
        assert composite.duration is None
        assert len(rec)==0

    def test_target_set(self):
        global rec, next_done
        node = CocosNode()
        name1 = '1'
        a1 = UAction(name1)
        composite = ac.Repeat(a1)

        rec = []
        a_copy = node.do(composite)
        assert a_copy.action.target==node

    def test_target_set_next_time(self):
        global rec, next_done
        node = CocosNode()
        name1 = '1'
        a1 = UAction(name1)
        composite = ac.Repeat(a1)

        a_copy = node.do(composite)
        dt = 0.1
        next_done=1
        node._step(dt)
        assert a_copy.action.target==node


    def test_life_cycle(self):
        global rec, next_done
        next_done=0
        name1 = '1'
        a1 = UAction(name1)
        node = CocosNode()
        composite = ac.Repeat(a1)
        
        #1st start
        rec = []
        a_copy = node.do(composite)
        assert rec[0]==(name1, 'start')
        assert len(rec)==1
        assert not a_copy.done()

        #step in first repetition
        dt = 0.1
        next_done=0
        rec = []
        node._step(dt)
        assert rec[0]==(name1, 'step', dt) 
        assert len(rec)==1
        assert not a_copy.done()

        #termination first repetion, start second repetition
        next_done = 1
        rec = []
        node._step(dt)
        assert rec[0]==(name1, 'step', dt) 
        assert rec[1]==(name1, 'stop')
        assert rec[2]==(name1, 'start')
        assert len(rec)==3
        assert not a_copy.done()

        #step in second repetition
        next_done=0
        rec = []
        node._step(dt)
        assert rec[0]==(name1, 'step', dt) 
        assert len(rec)==1
        assert not a_copy.done()
