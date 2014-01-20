from __future__ import division, print_function, unicode_literals

# parametrized test, using py.test 
# see _parametric_test_t_demo.py for a skeletal.

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
                (3.0, 3.0),
                (3.0, 5.0),
                (5.0, 3.0)
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

class Test_Spawn_IntervalAction:
    def test_instantiation(self, duration1, duration2):
        global rec
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        assert isinstance(a1, ac.IntervalAction)
        assert a1.duration == duration1
        a2 = UIntervalAction(name2, duration2)

        rec = []
        composite = ac.spawn(a1, a2)
        assert isinstance(composite, ac.IntervalAction)
        assert composite.duration == max(duration1, duration2)
        assert len(rec)==0

    def test_start(self, duration1, duration2):
        global rec
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.spawn(a1, a2)

        rec = []
        node.do(composite)
        assert [e for e in rec if e[0]==name1][0]==(name1, 'start') 
        assert [e for e in rec if e[0]==name2][0]==(name2, 'start')

    def test_target_set(self, duration1, duration2):
        global rec
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.spawn(a1, a2)

        rec = []
        a_copy = node.do(composite)
        assert a_copy.actions[0].target==node
        assert a_copy.actions[1].target==node

    def test_updating_below_min(self, duration1, duration2):
        # next_elapsed < min(duration1, duration2)
        global rec

        # only applies if min(duration1, duration2)>=epsilon >0.0 , 1.0/epsilon
        # well defined 
        need_test = True
        try:
            a = 1.0/duration1
            b = 1.0/duration2
        except ZeroDivisionError:
            need_test = False
        if not need_test:
            # the test dont make sense for the parameters received, skip
            return

        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.spawn(a1, a2)
        node.do(composite)
        elapsed = 0.0
        
        min_duration = min(duration1, duration2)
        for next_elapsed in [ min_duration/3.0, min_duration/2.0]:
            dt = next_elapsed - elapsed
            rec = []
            node._step(dt)
            
            rec = [ e for e in rec if e[1]!='step' ]
            rec1 = [ e for e in rec if e[0]==name1]
            assert len(rec1)==1
            assert (rec1[0][1]=='update' and
                    abs(rec1[0][2]-next_elapsed/duration1)<fe
                    )
            rec2 = [ e for e in rec if e[0]==name2]
            assert len(rec2)==1
            assert(rec2[0][1]=='update' and
                   abs(rec2[0][2]-next_elapsed/duration2)<fe
                   )
            elapsed = next_elapsed

    def test_update_crossing_min_not_max_at_1st_step(self, duration1, duration2):
        # min< next_elapsed < max
        global rec
        # expect start, [xxx,]update(1), stop for shortest action

        # only applies if min<max
        need_test = (duration1 < duration2)
        if not need_test:
            return
        
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.spawn(a1, a2)
        rec = []
        node.do(composite)
        elapsed = 0.0
        # between duration1 and duration2
        next_elapsed = (duration1 + duration2)/2.0
        dt = next_elapsed - elapsed
        node._step(dt)
        
        print('rec:', rec)
        rec = [ e for e in rec if e[1]!='step' ]
        if duration1 < duration2:
            oname1 = name1
            oduration1 = duration1
            oname2 = name2
            oduration2 = duration2
        else:
            oname1 = name2
            oduration1 = duration2
            oname2 = name1
            oduration2 = duration1
        orec1 = [ e for e in rec if e[0]==oname1 ]
        print(orec1)
        assert orec1[0]==(oname1, 'start')
        assert orec1[1]==(oname1, 'update', 1.0)
        assert orec1[2]==(oname1, 'stop')
        assert len(orec1)==3
        
        orec2 = [ e for e in rec if e[0]==oname2 ]
        print(orec2)
        assert len(orec2)==2
        assert orec2[0]==(oname2, 'start')
        assert orec2[1][1]=='update'
        assert abs(orec2[1][2] - next_elapsed/oduration2)<fe

    def test_update_crossing_min_not_max_not_at_1st_step(self, duration1, duration2):
        # 0< min< next_elapsed < max
        global rec
                
        # only applies if min(duration1, duration2)>=epsilon >0.0 , 1.0/epsilon
        # well defined 
        try:
            need_test = (duration1!=duration2)
            a = 1.0/duration1
            b = 1.0/duration2
        except ZeroDivisionError:
            need_test = False
        if not need_test:
            # the test dont make sense for the parameters received, skip
            return

        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.spawn(a1, a2)
        node.do(composite)
        elapsed = 0.0
        dt = min(duration1, duration2)/2.0
        node._step(dt)
        elapsed += dt # below min
        
        # between duration1 and duration2
        next_elapsed = (duration1 + duration2)/2.0
        dt = next_elapsed - elapsed
        rec = []
        node._step(dt)

        rec = [ e for e in rec if e[1]!='step' ]
        # expected:
        # the action with min duration will only call .update(1.0) and
        # .stop(), in that order
        # the action with max duraction will only call .update with apropiate t
        if duration1 < duration2:
            oname1 = name1
            oduration1 = duration1
            oname2 = name2
            oduration2 = duration2
        else:
            oname1 = name2
            oduration1 = duration2
            oname2 = name1
            oduration2 = duration1
        orec1 = [ e for e in rec if e[0]==oname1 ]
        assert orec1[0]==(oname1, 'update', 1.0)
        assert orec1[1]==(oname1, 'stop')
        assert len(orec1)==2
        
        orec2 = [ e for e in rec if e[0]==oname2 ]
        assert len(orec2)==1
        assert orec2[0][1]=='update'
        assert abs(orec2[0][2] - next_elapsed/oduration2)<fe

    def test_update_crossing_max_at_1st_step(self, duration1, duration2):
        # next_elapsed > max(duration1, duration2)
        global rec

        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.spawn(a1, a2)
        rec = []
        node.do(composite)
        elapsed = 0.0
        next_elapsed = max(duration1, duration2)*1.1 # above max
        dt = next_elapsed - elapsed
        node._step(dt)

        recx = [ e for e in rec if e[1]!='step' ]
        rec = [ e for e in recx if e[0]==name1]
        print('rec', rec)
        assert rec[0][1]=='start'
        assert rec[1][1]=='update' and rec[1][2]==1.0
        assert rec[2][1]=='stop'
        assert len(rec)==3

        rec = [ e for e in recx if e[0]==name2]
        print ('rec:', rec)
        assert rec[0][1]=='start'
        assert rec[1][1]=='update' and rec[1][2]==1.0
        assert rec[2][1]=='stop'
        assert len(rec)==3

    def update_crossing_max_from_below_min(self, duration1, duration2):
        # elapsed < min <= max < next_elapsed
        global rec

        need_test = True
        try:
            a = 1.0/duration1
            b = 1.0/duration2
        except ZeroDivisionError:
            need_test = False
        if not need_test:
            # the test dont make sense for the parameters received, skip
            return

        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.spawn(a1, a2)
        node.do(composite)
        elapsed = 0.0
        next_elapsed = min(duration1, duration2)/2.0 # above 0, below min
        dt = next_elapsed - elapsed
        node._step(dt)
        next_elapsed = max(duration1, duration2)*1.1 # above max
        dt = next_elapsed - elapsed
        rec = []
        node._step(dt)

        # expected: for each action .update(1.0) and stop() called, in that order
        # nothing more
        # ? maybe step
        recx = [ e for e in rec if e[1]!='step' ]
        rec = [ e for e in recx if e[0]==name1]
        assert len(rec)==2
        assert rec[0][1]=='update' and rec[0][2]==1.0
        assert rec[1][1]=='stop'

        rec = [ e for e in recx if e[0]==name2]
        assert len(rec)==2
        assert rec[0][1]=='update' and rec[0][2]==1.0
        assert rec[1][1]=='stop'

    def test_update_crossing_max_from_above_min(self, duration1, duration2):
        # min < elapsed < max < next_elapsed
        global rec
        
        need_test = (duration1!=duration2)
        if not need_test:
            return

        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.spawn(a1, a2)
        node.do(composite)
        elapsed = 0.0
        next_elapsed = (duration1 + duration2)/2.0 # above min, below max
        dt = next_elapsed - elapsed
        node._step(dt)
        elapsed = next_elapsed
        next_elapsed = max(duration1, duration2)*1.1 # above max
        dt = next_elapsed - elapsed
        rec = []
        node._step(dt)
        # expected: no call from action with min duration, two calls from the
        # action with max duration: .update(1) and .stop() in that order
        if duration1 < duration2:
            oname1 = name1
            oname2 = name2
        else:
            oname1 = name2
            oname2 = name1
        rec_lo = [ e for e in rec if e[0]==oname1]
        print('rec_lo:', rec_lo)
        assert len(rec_lo)==0

        rec = [ e for e in rec if e[0]==oname2]
        rec = [ e for e in rec if e[1]!='step' ]
        print('rec hi:', rec)
        assert rec[0][1]=='update' and rec[0][2]==1.0
        assert rec[1][1]=='stop'
        assert len(rec)==2

    def test_updating_above_min_below_max(self, duration1, duration2):
        # min < elapsed < next_elapsed < max
        global rec


        need_test = (duration1!=duration2)
        if not need_test:
            return

        node = CocosNode()
        name1 = '1'
        name2 = '2'
        a1 = UIntervalAction(name1, duration1)
        a2 = UIntervalAction(name2, duration2)
        composite = ac.spawn(a1, a2)
        node.do(composite)
        elapsed = 0.0
        next_elapsed = (duration1 + duration2)/2.0 # above min, below max
        dt = next_elapsed - elapsed
        node._step(dt)
        elapsed = next_elapsed
        next_elapsed = (elapsed + max(duration1, duration2))/2.0
        dt = next_elapsed - elapsed
        rec = []
        node._step(dt)

        # expected:
        # no call from the action with min duration
        # only one call from the action with max duration and will be .update
        if duration1 < duration2:
            oname1 = name1
            oname2 = name2
        else:
            oname1 = name2
            oname2 = name1
        rec_lo = [ e for e in rec if e[0]==oname1]
        print('rec_lo:', rec_lo)
        assert len(rec_lo)==0

        rec = [ e for e in rec if e[0]==oname2]
        rec = [ e for e in rec if e[1]!='step' ]
        print('rec hi:', rec)
        assert len(rec)==1
        assert (rec[0][1]=='update' and
                abs(rec[0][2] - next_elapsed/max(duration1, duration2))<fe)


# faltaria algun test especifico para el caso duration1==duration2 ?
# revisar que aseguremos start es el primer call en la serie y que stop
# es el ultimo (la prueba start tiene que ir antes de borrar ningun registro)
