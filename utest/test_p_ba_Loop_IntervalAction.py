from __future__ import division, print_function, unicode_literals

# parametrized test, using py.test 
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

fe = 1.0e-6 # used to compare floats; a==b <-> abs(a-b)<fe

director.init()

rec = []
class UIntervalAction(ac.IntervalAction):
    def init(self, name, duration):
        rec.append((name, 'init'))
        self.duration = duration
        self.name = name

    def start(self):
        rec.append((self.name, 'start'))

    def step(self, dt):
        rec.append((self.name, 'step', dt))
        super(UIntervalAction, self).step(dt)

    def update(self, fraction):
        rec.append((self.name, 'update', fraction))

    def stop(self):
        rec.append((self.name, 'stop'))

##    def done(self):
##        rec.append((self.name, 'done', 

class Test_Loop_IntervalAction:
    def test_instantiation(self):
        global rec
        name1 = '1'
        duration1 = 3.0
        times = 2
        a1 = UIntervalAction(name1, duration1)
        assert isinstance(a1, ac.IntervalAction)

        rec = []
        composite = ac.loop(a1, times)
        assert isinstance(composite, ac.IntervalAction)
        assert composite.duration == (duration1 * times)
        assert len(rec)==0

    def test_target_set(self):
        global rec
        node = CocosNode()
        name1 = '1'
        duration1 = 3.0
        times = 2
        a1 = UIntervalAction(name1, duration1)
        composite = ac.loop(a1, times)

        rec = []
        a_copy = node.do(composite)
        assert a_copy.current_action.target==node

    def test_life_cycle_when_duration_gt_0(self):
        global rec, next_done
        next_done=0
        name1 = '1'
        duration1 = 3.0
        times = 2
        a1 = UIntervalAction(name1, duration1)
        node = CocosNode()
        composite = ac.loop(a1, times)
        elapsed = 0.0
        
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
        print('rec 1st repetition:',rec)
        elapsed += dt
        rec = [e for e in rec if e[1]!='step'] 
        assert rec[0]==(name1, 'update', elapsed/duration1) 
        assert len(rec)==1
        assert not a_copy.done()

        #termination first repetion, start second repetition
        next_elapsed = duration1*1.5
        dt = next_elapsed - elapsed
        rec = []
        node._step(dt)
        elapsed = next_elapsed
        rec = [e for e in rec if e[1]!='step'] 
        print ('rec end 1st reptition:', rec)
        assert rec[0]==(name1, 'update', 1.0) 
        assert rec[1]==(name1, 'stop')
        assert rec[2]==(name1, 'start')
        assert rec[3]==(name1, 'update', (elapsed-duration1)/duration1) 
        assert len(rec)==4
        assert not a_copy.done()

        #step in second repetition
        dt = 0.1
        rec = []
        node._step(dt)
        print('rec 1st repetition:', rec)
        elapsed += dt
        rec = [e for e in rec if e[1]!='step'] 
        assert rec[0]==(name1, 'update', (elapsed-duration1)/duration1) 
        assert len(rec)==1
        assert not a_copy.done()
        
        #terminatation last repetition
        next_elapsed = times*duration1*1.1
        dt = next_elapsed - elapsed
        rec = []
        node._step(dt)
        rec = [e for e in rec if e[1]!='step'] 
        print('rec end 1st reptition:', rec)
        assert rec[0]==(name1, 'update', 1.0) 
        assert rec[1]==(name1, 'stop')
        assert len(rec)==2

        assert a_copy.done()

