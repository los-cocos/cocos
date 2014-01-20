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

rec = []
next_done=0 #bitflags

class UAction(ac.Action):
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

class Test_Spawn_Action:

    def test_instantiation(self):
        global rec, next_done
        name1 = '1'
        name2 = '2'
        a1 = UAction(name1)
        assert isinstance(a1, ac.Action)
        a2 = UAction(name2)

        rec = []
        composite = ac.spawn(a1, a2)
        assert isinstance(composite, ac.Action)
        assert len(rec)==0

    def test_start(self):
        global rec, next_done
        next_done=0
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UAction(name1)
        a2 = UAction(name2)
        composite = ac.spawn(a1, a2)

        rec = []
        node.do(composite)
        print('start rec:', rec)
        assert rec[0]==(name1, 'start')
        assert rec[0]==(name1, 'start')
        assert len(rec)==2

    def test_target_set(self):
        global rec, next_done
        next_done=0
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UAction(name1)
        a2 = UAction(name2)
        composite = ac.spawn(a1, a2)

        rec = []
        a_copy = node.do(composite)
        assert a_copy.actions[0].target==node
        assert a_copy.actions[1].target==node
            

    def test_step_before_any_done(self):
        global rec, next_done
        next_done=0
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UAction(name1)
        a2 = UAction(name2)
        composite = ac.spawn(a1, a2)
        a_copy = node.do(composite)
        dt = 0.1
        rec = []
        node._step(dt)
        assert rec[0]==(name1, 'step', dt)
        assert rec[0]==(name1, 'step', dt)
        assert not a_copy.done()
        assert len(rec)==2

    def test_step_setting_done1(self):
        global rec, next_done
        next_done=0
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UAction(name1)
        a2 = UAction(name2)
        composite = ac.spawn(a1, a2)
        a_copy = node.do(composite)
        dt = 0.1
        rec = []
        next_done = 1
        node._step(dt)
        print(rec)
        recx = [e for e in rec if e[0]==name1]
        assert recx[0][1]== 'step'
        assert recx[1][1]=='stop'
        assert len(recx)==2

        recx = [e for e in rec if e[0]==name2]
        assert recx[0][1]== 'step'
        assert len(recx)==1

        assert not a_copy.done()

        rec = []
        node._step(dt)
        len([e for e in rec if e[0]==name1])==0
        recx = [e for e in rec if e[0]==name2]
        assert recx[0][1]== 'step'
        assert not a_copy.done()

    def test_step_setting_done2(self):
        global rec, next_done
        next_done=0
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UAction(name1)
        a2 = UAction(name2)
        composite = ac.spawn(a1, a2)
        a_copy = node.do(composite)
        dt = 0.1
        rec = []
        next_done = 2
        node._step(dt)
#        print rec

        recx = [e for e in rec if e[0]==name1]
        assert rec[0][1]== 'step'
        assert len(recx)==1

        recx = [e for e in rec if e[0]==name2]
        assert recx[0][1]=='step'
        assert recx[1][1]=='stop'
        assert len(recx)==2

        assert not a_copy.done()
        
        rec = []
        node._step(dt)
        print(rec)
        assert len([e for e in rec if rec[0]==name2])==0
        recx = [e for e in rec if e[0]==name1]
        assert len(recx)==1
        assert recx[0][1]=='step'
        assert not a_copy.done()
        

    def test_step_setting_done1_done2(self):
        global rec, next_done
        next_done=0
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UAction(name1)
        a2 = UAction(name2)
        composite = ac.spawn(a1, a2)
        a_copy = node.do(composite)
        dt = 0.1
        rec = []
        next_done = 3
        node._step(dt)
        print(rec)

        recx = [e for e in rec if e[0]==name1]
        assert recx[0][1]== 'step'
        assert recx[1][1]=='stop'
        assert len(recx)==2

        recx = [e for e in rec if e[0]==name2]
        assert recx[0][1]=='step'
        assert recx[1][1]=='stop'
        assert len(recx)==2

        assert a_copy.done()
        rec = []
        node._step(dt)
        assert len(rec)==0
        assert len(node.actions)==0

    def test_receiving_stop_async_before_done1_done2(self):
        global rec, next_done
        next_done=0
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UAction(name1)
        a2 = UAction(name2)
        composite = ac.spawn(a1, a2)
        a_copy = node.do(composite)

        rec=[]
        a_copy.stop()
        assert rec[0]==(name1, 'stop')
        assert rec[1]==(name2, 'stop')
        assert len(rec)==2

    def test_receiving_stop_async_after_done1_before_done2(self):
        global rec, next_done
        next_done=0
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UAction(name1)
        a2 = UAction(name2)
        composite = ac.spawn(a1, a2)
        a_copy = node.do(composite)
        dt = 0.1
        next_done = 1
        node._step(dt)

        rec=[]
        print(rec)
        a_copy.stop()
        assert rec[0]==(name2, 'stop')
        assert len(rec)==1

    def test_receiving_stop_async_after_done2_before_done1(self):
        global rec, next_done
        next_done=0
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UAction(name1)
        a2 = UAction(name2)
        composite = ac.spawn(a1, a2)
        a_copy = node.do(composite)
        dt = 0.1
        next_done = 2
        node._step(dt)

        rec=[]
        print(rec)
        a_copy.stop()
        assert rec[0]==(name1, 'stop')
        assert len(rec)==1
