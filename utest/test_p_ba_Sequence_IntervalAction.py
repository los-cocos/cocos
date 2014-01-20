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

def pytest_generate_tests(metafunc):
    param_names = ['duration1', 'duration2']
    values = [  (0.0, 0.0),
                (0.0, 3.0),
                (3.0, 0.0),
                (3.0, 5.0)
                ]
    scenarios = {}
    for v in values:
        name = ' '.join(['%s'%e for e in v])
        scenarios[name] = dict(zip(param_names, v))
    for k in scenarios:
        metafunc.addcall(id=k, funcargs=scenarios[k])

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

class Test_Sequence_IntervalAction:
    def test_instantiation(self, duration1, duration2):
        global rec
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        assert isinstance(a1, ac.IntervalAction)
        assert a1.duration == duration1
        a2 = UIntervalAction(name2, duration2)

        rec = []
        composite = ac.sequence(a1, a2)
        assert isinstance(composite, ac.IntervalAction)
        assert composite.duration == (duration1 + duration2)
        assert len(rec)==0

    def test_start(self, duration1, duration2):
        global rec
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.sequence(a1, a2)

        rec = []
        node.do(composite)
        print('start rec:', rec)
        num = 0
        assert rec[num]==(name1, 'start')
        if duration1==0.0:
            assert rec[num + 1]==(name1, 'update', 1.0)
            assert rec[num + 2]==(name1, 'stop')
            assert rec[num + 3]==(name2, 'start')
            num = num + 3
        assert len(rec)==num+1
            
    def test_target_set(self, duration1, duration2):
        global rec, next_done
        next_done=0
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.sequence(a1, a2)

        rec = []
        a_copy = node.do(composite)
        assert a_copy.one.target==node
        assert a_copy.two.target==node

    def test_update_below_duration1(self, duration1, duration2):
        global rec

        if duration1==0.0:
            return

        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.sequence(a1, a2)
        node.do(composite)
        elapsed = 0.0
        # check cases 1st step and not 1st step
        for next_elapsed in [ duration1*0.5, duration1*0.75]:
            dt = next_elapsed - elapsed
            rec = []
            node._step(dt)
            rec = [ e for e in rec if e[1]!='step' ]
            print(rec)
            assert rec[0][1]=='update' and abs(rec[0][2]-next_elapsed/duration1)<fe
            assert len(rec)==1
            elapsed = next_elapsed

    def test_update_crossing_duration1_not_duration_at_1st_step(self, duration1, duration2):
        global rec

        if duration2==0.0:
            return

        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.sequence(a1, a2)
        rec = []
        node.do(composite)
        elapsed = 0.0
        next_elapsed = (duration1 + duration2)/2.0
        dt = next_elapsed - elapsed
        node._step(dt)

        #expect start, update(1), stop for action 1, start + update(x) for action2
        recx = [ e for e in rec if e[1]!='step' ]
        rec = [ e for e in recx if e[0]==name1]
        print('rec', rec)
        assert rec[0][1]=='start'
        assert rec[1][1]=='update' and rec[1][2]==1.0
        assert rec[2][1]=='stop'
        assert len(rec)==3

        rec = [ e for e in recx if e[0]==name2]
        print('rec', rec)
        assert rec[0][1]=='start'
        assert rec[1][1]=='update'
        assert abs(rec[1][2]-(next_elapsed-duration1)/duration2)<fe
        assert len(rec)==2


    def test_update_crossing_duration1_not_duration_not_at_1st_step(self, duration1, duration2):
        global rec

        if duration1==0.0 or duration2==0.0:
            return

        # todo
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.sequence(a1, a2)
        rec = []
        node.do(composite)
        elapsed = 0.0
        next_elapsed = duration1/2.0
        dt = next_elapsed - elapsed
        node._step(dt)
        elapsed = next_elapsed
        next_elapsed = (duration1+duration2)/2.0
        dt = next_elapsed - elapsed
        rec = []
        node._step(dt)

        #expect update(1), stop for action 1, start + update(x) for action2
        recx = [ e for e in rec if e[1]!='step' ]
        rec = [ e for e in recx if e[0]==name1]
        print('rec', rec)
        assert rec[0][1]=='update' and rec[0][2]==1.0
        assert rec[1][1]=='stop'
        assert len(rec)==2

        rec = [ e for e in recx if e[0]==name2]
        print('rec', rec)
        assert rec[0][1]=='start'
        assert rec[1][1]=='update'
        assert abs(rec[1][2]-(next_elapsed-duration1)/duration2)<fe
        assert len(rec)==2

    def test_updating_above_duration1_below_duration(self, duration1, duration2):
        global rec

        if duration2==0.0:
            return

        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.sequence(a1, a2)
        node.do(composite)
        elapsed = 0.0
        next_elapsed = (duration1 + duration2)/2.0
        dt = next_elapsed - elapsed
        node._step(dt)
        elapsed = next_elapsed
        next_elapsed = (next_elapsed + composite.duration)/2.0
        dt = next_elapsed - elapsed
        rec = []
        node._step(dt)

        assert len([e for e in rec if e[0]==name1])==0
        rec = [ e for e in rec if e[1]!='step' ]
        print(rec)
        assert rec[0][1]=='update'
        assert abs(rec[0][2]-(next_elapsed-duration1)/duration2)<fe
        assert len(rec)==1

    def test_update_crossing_total_duration_at_1st_step(self, duration1, duration2):
        # elapsed==0, next_elapsed>=duration1 + duration2
        global rec
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        elapsed = 0.0
        rec = []
        composite = ac.sequence(a1, a2)
        node.do(composite)
        next_elapsed = duration1 + duration2 +fe
        dt = next_elapsed - elapsed
        node._step(dt)
        # expected: for both actions start-update(1)-stop called, in that order
        recx = [ e for e in rec if e[1]!='step' ]
        rec = [ e for e in recx if e[0]==name1]
        print('rec', rec)
        assert len(rec)==3
        assert rec[0][1]=='start'
        assert rec[1][1]=='update' and rec[1][2]==1.0
        assert rec[2][1]=='stop'

        rec = [ e for e in recx if e[0]==name2]
        print('rec', rec)
        assert len(rec)==3
        assert rec[0][1]=='start'
        assert rec[1][1]=='update' and rec[1][2]==1.0
        assert rec[2][1]=='stop'

    def test_test_receiving_stop_async_before_duration1(self, duration1, duration2):
        #0<duration1
        global rec

        if duration1==0.0:
            return
        
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        elapsed = 0.0
        rec = []
        composite = ac.sequence(a1, a2)
        a_copy = node.do(composite)

        rec = []
        a_copy.stop()
        assert rec[0]==(name1, 'stop')
        assert len(rec)==1

    def test_test_receiving_stop_async_after_duration1_before_duration2(self, duration1, duration2):
        #0<duration2
        global rec

        if duration2==0.0:
            return
        
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        elapsed = 0.0
        rec = []
        composite = ac.sequence(a1, a2)
        a_copy = node.do(composite)
        next_elapsed = (duration1+duration2)/2.0
        dt = next_elapsed - elapsed
        node._step(dt)

        rec = []
        a_copy.stop()
        assert rec[0]==(name2, 'stop')
        assert len(rec)==1
        
